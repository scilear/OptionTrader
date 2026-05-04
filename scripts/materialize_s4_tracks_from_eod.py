from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.core.compute_snapshot import compute_for_snapshot
from src.db.connection import connect
from src.db.init_db import init_db


def _create_pipeline_run(conn, code_version: str) -> int:
    row = conn.execute(
        """
        INSERT INTO pipeline_runs (
            run_id, started_at, finished_at, status, config_hash, code_version, error_message
        ) VALUES (DEFAULT, NOW(), NOW(), 'success', NULL, ?, NULL)
        RETURNING run_id
        """,
        (code_version,),
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
        snapshot_rows = conn.execute(
            """
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
        ).fetchall()
        snapshot_ids = [int(row[0]) for row in snapshot_rows]
        if not snapshot_ids:
            continue
        placeholders = ",".join(["?"] * len(snapshot_ids))
        alert_rows = conn.execute(
            f"SELECT alert_id FROM alerts WHERE snapshot_id IN ({placeholders})",
            snapshot_ids,
        ).fetchall()
        alert_ids = [int(row[0]) for row in alert_rows]
        if alert_ids:
            alert_ph = ",".join(["?"] * len(alert_ids))
            conn.execute(f"DELETE FROM alert_outcomes WHERE alert_id IN ({alert_ph})", alert_ids)
            conn.execute(f"DELETE FROM trade_ideas WHERE alert_id IN ({alert_ph})", alert_ids)
        conn.execute(f"DELETE FROM alerts WHERE snapshot_id IN ({placeholders})", snapshot_ids)
        conn.execute(f"DELETE FROM surface_metrics WHERE snapshot_id IN ({placeholders})", snapshot_ids)
        conn.execute(f"DELETE FROM iv_points WHERE snapshot_id IN ({placeholders})", snapshot_ids)
        conn.execute(f"DELETE FROM option_quotes WHERE snapshot_id IN ({placeholders})", snapshot_ids)
        conn.execute(f"DELETE FROM snapshots WHERE snapshot_id IN ({placeholders})", snapshot_ids)

    conn.execute(
        """
        DELETE FROM pipeline_runs
        WHERE run_id NOT IN (SELECT DISTINCT run_id FROM snapshots WHERE run_id IS NOT NULL)
        """
    )


def materialize_s4_tracks_from_eod(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    baseline_lineage: str,
    candidate_lineage: str,
) -> dict:
    init_db()
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

        baseline_run_id = _create_pipeline_run(conn, _resolve_commit(baseline_lineage))
        candidate_run_id = _create_pipeline_run(conn, _resolve_commit(candidate_lineage))

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

    for snapshot_id in baseline_snapshot_ids:
        compute_for_snapshot(snapshot_id, purge_existing=True)
    for snapshot_id in candidate_snapshot_ids:
        compute_for_snapshot(snapshot_id, purge_existing=True)

    result = {
        "underlying": underlying,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "source_snapshot_count": len(source_snapshot_ids),
        "baseline": {
            "lineage": baseline_lineage,
            "run_id": baseline_run_id,
            "snapshot_count": len(baseline_snapshot_ids),
            "first_snapshot_id": baseline_snapshot_ids[0] if baseline_snapshot_ids else None,
            "last_snapshot_id": baseline_snapshot_ids[-1] if baseline_snapshot_ids else None,
        },
        "candidate": {
            "lineage": candidate_lineage,
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
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
