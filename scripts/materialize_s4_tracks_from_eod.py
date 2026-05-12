from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import yaml

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.core.compute_snapshot import compute_for_snapshot
from src.core.config import config_digest, get_config_path
from src.core.regime import compute_regime_state
from src.db.connection import connect
from src.db.init_db import init_db


def _create_pipeline_run(conn, code_version: str, config_hash: str) -> int:
    row = conn.execute(
        """
        INSERT INTO pipeline_runs (
            run_id, started_at, finished_at, status, config_hash, code_version, error_message
        ) VALUES (DEFAULT, NOW(), NOW(), 'success', ?, ?, NULL)
        RETURNING run_id
        """,
        (config_hash, code_version),
    ).fetchone()
    return int(row[0])


def _resolve_commit(commit_ref: str) -> str:
    try:
        resolved = subprocess.run(
            ["git", "rev-parse", commit_ref],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return resolved or commit_ref
    except Exception:
        return commit_ref


def _deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        base_value = merged.get(key)
        if isinstance(base_value, dict) and isinstance(value, dict):
            merged[key] = _deep_merge(base_value, value)
        else:
            merged[key] = value
    return merged


def _build_profile_config(
    *,
    base_config_path: Path,
    profile_path: Path,
) -> tuple[Path, str, str]:
    profile_payload = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
    if not isinstance(profile_payload, dict):
        raise ValueError(f"Invalid profile file format: {profile_path}")

    profile_id = str(profile_payload.get("profile_id") or profile_path.stem)
    overrides = profile_payload.get("overrides", profile_payload)
    if not isinstance(overrides, dict):
        raise ValueError(f"Invalid overrides section in profile file: {profile_path}")

    base_cfg = yaml.safe_load(base_config_path.read_text(encoding="utf-8")) or {}
    merged_cfg = _deep_merge(base_cfg, overrides)
    digest = config_digest(merged_cfg)

    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=f"_{profile_id}.yaml",
        prefix="s4_track_profile_",
        delete=False,
        encoding="utf-8",
    )
    try:
        yaml.safe_dump(merged_cfg, tmp, sort_keys=False)
        tmp_path = Path(tmp.name)
    finally:
        tmp.close()
    return tmp_path, profile_id, digest


def _load_source_snapshots(conn, underlying: str, start_ts: str, end_ts: str) -> list[tuple[int, object, float]]:
    return conn.execute(
        """
        SELECT snapshot_id, ts, spot
        FROM snapshots
        WHERE underlying = ?
          AND ts >= ?
          AND ts <= ?
          AND source = 'eod'
          AND session_tag = 'eod'
        ORDER BY ts, snapshot_id
        """,
        (underlying, start_ts, end_ts),
    ).fetchall()


def _clone_snapshots_for_run(
    conn,
    source_snapshot_ids: list[int],
    run_id: int,
    underlying: str,
) -> list[int]:
    cloned_ids: list[int] = []
    for source_snapshot_id in source_snapshot_ids:
        source_row = conn.execute(
            """
            SELECT ts, spot
            FROM snapshots
            WHERE snapshot_id = ?
            """,
            (source_snapshot_id,),
        ).fetchone()
        if not source_row:
            continue
        ts, spot = source_row
        created = conn.execute(
            """
            INSERT INTO snapshots (
                snapshot_id, run_id, ts, underlying, spot, source, session_tag, notes
            ) VALUES (DEFAULT, ?, ?, ?, ?, 'eod', 'track', ?)
            RETURNING snapshot_id
            """,
            (run_id, ts, underlying, float(spot), f"track_from_snapshot_{source_snapshot_id}"),
        ).fetchone()
        snapshot_id = int(created[0])

        conn.execute(
            """
            INSERT INTO option_quotes (
                snapshot_id, expiry, strike, option_right,
                bid, ask, last, bid_size, ask_size, oi, volume, flags
            )
            SELECT
                ?,
                expiry,
                strike,
                option_right,
                bid,
                ask,
                last,
                bid_size,
                ask_size,
                oi,
                volume,
                flags
            FROM option_quotes
            WHERE snapshot_id = ?
            """,
            (snapshot_id, source_snapshot_id),
        )
        cloned_ids.append(snapshot_id)
    return cloned_ids


def _purge_existing_tracks(
    conn,
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    lineage_prefixes: list[str],
) -> None:
    for lineage in lineage_prefixes:
        conn.execute(
            """
            CREATE OR REPLACE TEMP TABLE _track_snapshot_ids AS
            SELECT s.snapshot_id
            FROM snapshots s
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND s.source = 'eod'
              AND s.session_tag = 'track'
              AND pr.code_version LIKE ?
            """,
            (underlying, start_ts, end_ts, f"{lineage}%"),
        )
        snapshot_count = int(conn.execute("SELECT COUNT(*) FROM _track_snapshot_ids").fetchone()[0])
        if snapshot_count == 0:
            continue
        conn.execute(
            """
            DELETE FROM alert_outcomes
            WHERE alert_id IN (
                SELECT a.alert_id
                FROM alerts a
                JOIN _track_snapshot_ids t ON t.snapshot_id = a.snapshot_id
            )
            """
        )
        conn.execute(
            """
            DELETE FROM trade_ideas
            WHERE alert_id IN (
                SELECT a.alert_id
                FROM alerts a
                JOIN _track_snapshot_ids t ON t.snapshot_id = a.snapshot_id
            )
            """
        )
        conn.execute(
            """
            DELETE FROM alerts
            WHERE snapshot_id IN (SELECT snapshot_id FROM _track_snapshot_ids)
            """
        )
        conn.execute(
            """
            DELETE FROM surface_metrics
            WHERE snapshot_id IN (SELECT snapshot_id FROM _track_snapshot_ids)
            """
        )
        conn.execute(
            """
            DELETE FROM iv_points
            WHERE snapshot_id IN (SELECT snapshot_id FROM _track_snapshot_ids)
            """
        )
        conn.execute(
            """
            DELETE FROM option_quotes
            WHERE snapshot_id IN (SELECT snapshot_id FROM _track_snapshot_ids)
            """
        )
        conn.execute(
            """
            DELETE FROM regime_snapshot_labels
            WHERE snapshot_id IN (SELECT snapshot_id FROM _track_snapshot_ids)
            """
        )
        conn.execute(
            """
            UPDATE snapshots
            SET run_id = NULL,
                source = 'eod_purged',
                session_tag = 'track_purged',
                notes = COALESCE(notes, '') || ' [track_purged]'
            WHERE snapshot_id IN (SELECT snapshot_id FROM _track_snapshot_ids)
            """
        )

    conn.execute(
        """
        DROP TABLE IF EXISTS _track_snapshot_ids
        """
    )


def materialize_s4_tracks_from_eod(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    baseline_lineage: str,
    candidate_lineage: str,
    baseline_profile_path: Path,
    candidate_profile_path: Path,
) -> dict:
    init_db()
    base_config_path = get_config_path().resolve()
    baseline_cfg_path, baseline_profile_id, baseline_cfg_hash = _build_profile_config(
        base_config_path=base_config_path,
        profile_path=baseline_profile_path,
    )
    candidate_cfg_path, candidate_profile_id, candidate_cfg_hash = _build_profile_config(
        base_config_path=base_config_path,
        profile_path=candidate_profile_path,
    )

    if baseline_cfg_hash == candidate_cfg_hash:
        raise ValueError(
            "Baseline and candidate profiles resolve to identical config hash; "
            "ablation requires behaviorally distinct profiles"
        )

    conn = connect()
    try:
        _purge_existing_tracks(
            conn,
            underlying=underlying,
            start_ts=start_ts,
            end_ts=end_ts,
            lineage_prefixes=[baseline_lineage, candidate_lineage],
        )
        source_rows = _load_source_snapshots(conn, underlying, start_ts, end_ts)
        source_snapshot_ids = [int(row[0]) for row in source_rows]
        if not source_snapshot_ids:
            raise ValueError("No source EOD snapshots found for requested window")

        baseline_code_version = f"{_resolve_commit(baseline_lineage)}+profile:{baseline_profile_id}"
        candidate_code_version = f"{_resolve_commit(candidate_lineage)}+profile:{candidate_profile_id}"

        baseline_run_id = _create_pipeline_run(conn, baseline_code_version, baseline_cfg_hash)
        candidate_run_id = _create_pipeline_run(conn, candidate_code_version, candidate_cfg_hash)

        baseline_snapshot_ids = _clone_snapshots_for_run(
            conn,
            source_snapshot_ids,
            baseline_run_id,
            underlying,
        )
        candidate_snapshot_ids = _clone_snapshots_for_run(
            conn,
            source_snapshot_ids,
            candidate_run_id,
            underlying,
        )
    finally:
        conn.close()

    original_config_env = os.environ.get("OPTIONTRADER_CONFIG")
    try:
        if baseline_cfg_path is not None:
            os.environ["OPTIONTRADER_CONFIG"] = str(baseline_cfg_path)
            compute_regime_state(run_id=baseline_run_id)
        for snapshot_id in baseline_snapshot_ids:
            compute_for_snapshot(snapshot_id, purge_existing=True, config_path=baseline_cfg_path)

        if candidate_cfg_path is not None:
            os.environ["OPTIONTRADER_CONFIG"] = str(candidate_cfg_path)
            compute_regime_state(run_id=candidate_run_id)
        for snapshot_id in candidate_snapshot_ids:
            compute_for_snapshot(snapshot_id, purge_existing=True, config_path=candidate_cfg_path)
    finally:
        if original_config_env is not None:
            os.environ["OPTIONTRADER_CONFIG"] = original_config_env
        elif "OPTIONTRADER_CONFIG" in os.environ:
            del os.environ["OPTIONTRADER_CONFIG"]
        baseline_cfg_path.unlink(missing_ok=True)
        candidate_cfg_path.unlink(missing_ok=True)

    result = {
        "underlying": underlying,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "source_snapshot_count": len(source_snapshot_ids),
        "baseline": {
            "lineage": baseline_lineage,
            "profile_id": baseline_profile_id,
            "config_hash": baseline_cfg_hash,
            "run_id": baseline_run_id,
            "snapshot_count": len(baseline_snapshot_ids),
            "first_snapshot_id": baseline_snapshot_ids[0] if baseline_snapshot_ids else None,
            "last_snapshot_id": baseline_snapshot_ids[-1] if baseline_snapshot_ids else None,
        },
        "candidate": {
            "lineage": candidate_lineage,
            "profile_id": candidate_profile_id,
            "config_hash": candidate_cfg_hash,
            "run_id": candidate_run_id,
            "snapshot_count": len(candidate_snapshot_ids),
            "first_snapshot_id": candidate_snapshot_ids[0] if candidate_snapshot_ids else None,
            "last_snapshot_id": candidate_snapshot_ids[-1] if candidate_snapshot_ids else None,
        },
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize S4 baseline/candidate tracks from EOD snapshots")
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--baseline-lineage", required=True)
    parser.add_argument("--candidate-lineage", required=True)
    parser.add_argument(
        "--baseline-profile",
        default="config/profile_s4_baseline.yaml",
        help="YAML profile with baseline overrides",
    )
    parser.add_argument(
        "--candidate-profile",
        default="config/profile_s4_candidate.yaml",
        help="YAML profile with candidate overrides",
    )
    parser.add_argument("--start-ts", required=True)
    parser.add_argument("--end-ts", required=True)
    parser.add_argument("--underlying", default="SPX")
    args = parser.parse_args()

    if args.db_path is not None:
        print(
            "warning: --db-path is informational; use OPTIONTRADER_CONFIG storage.path for active DB"
        )

    result = materialize_s4_tracks_from_eod(
        underlying=args.underlying,
        start_ts=args.start_ts,
        end_ts=args.end_ts,
        baseline_lineage=args.baseline_lineage,
        candidate_lineage=args.candidate_lineage,
        baseline_profile_path=Path(args.baseline_profile),
        candidate_profile_path=Path(args.candidate_profile),
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
