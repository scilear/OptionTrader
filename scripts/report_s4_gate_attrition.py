from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.db.connection import connect
from src.db.init_db import init_db


DEFAULT_OUTPUT = "docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report.md"


def _run_meta(underlying: str, start_ts: str, end_ts: str, lineage_prefix: str) -> dict:
    conn = connect()
    try:
        row = conn.execute(
            """
            SELECT pr.run_id, pr.code_version, pr.config_hash
            FROM pipeline_runs pr
            JOIN snapshots s ON s.run_id = pr.run_id
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND pr.code_version LIKE ?
            GROUP BY pr.run_id, pr.code_version, pr.config_hash
            ORDER BY pr.run_id DESC
            LIMIT 1
            """,
            (underlying, start_ts, end_ts, f"{lineage_prefix}%"),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return {
            "run_id": None,
            "code_version": None,
            "config_hash": None,
            "profile_id": None,
        }
    run_id, code_version, config_hash = row
    profile_id = None
    marker = "+profile:"
    if code_version and marker in str(code_version):
        profile_id = str(code_version).split(marker, 1)[1]
    return {
        "run_id": int(run_id),
        "code_version": str(code_version),
        "config_hash": str(config_hash) if config_hash is not None else None,
        "profile_id": profile_id,
    }


def _count(conn, query: str, params: tuple) -> int:
    return int(conn.execute(query, params).fetchone()[0])


def _attrition_for_lineage(underlying: str, start_ts: str, end_ts: str, lineage_prefix: str) -> dict:
    conn = connect()
    try:
        params = (underlying, start_ts, end_ts, f"{lineage_prefix}%")
        snapshots = _count(
            conn,
            """
            SELECT COUNT(*)
            FROM snapshots s
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ? AND s.ts >= ? AND s.ts <= ? AND pr.code_version LIKE ?
            """,
            params,
        )
        surface_rows = _count(
            conn,
            """
            SELECT COUNT(*)
            FROM surface_metrics sm
            JOIN snapshots s ON s.snapshot_id = sm.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ? AND s.ts >= ? AND s.ts <= ? AND pr.code_version LIKE ?
            """,
            params,
        )
        qc_pass = _count(
            conn,
            """
            SELECT COUNT(*)
            FROM surface_metrics sm
            JOIN snapshots s ON s.snapshot_id = sm.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ? AND s.ts >= ? AND s.ts <= ? AND pr.code_version LIKE ?
              AND sm.qc_pass = TRUE
            """,
            params,
        )
        alerts_total = _count(
            conn,
            """
            SELECT COUNT(*)
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ? AND s.ts >= ? AND s.ts <= ? AND pr.code_version LIKE ?
            """,
            params,
        )
        zscore_pass = _count(
            conn,
            """
            SELECT COUNT(*)
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ? AND s.ts >= ? AND s.ts <= ? AND pr.code_version LIKE ?
              AND json_extract_string(a.explain, '$.gates.zscore.status') = 'PASS'
            """,
            params,
        )
        persistence_pass = _count(
            conn,
            """
            SELECT COUNT(*)
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ? AND s.ts >= ? AND s.ts <= ? AND pr.code_version LIKE ?
              AND json_extract_string(a.explain, '$.gates.persistence.status') = 'PASS'
            """,
            params,
        )
        regime_pass = _count(
            conn,
            """
            SELECT COUNT(*)
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ? AND s.ts >= ? AND s.ts <= ? AND pr.code_version LIKE ?
              AND json_extract_string(a.explain, '$.gates.regime.status') = 'PASS'
            """,
            params,
        )
        tradability_pass = _count(
            conn,
            """
            SELECT COUNT(*)
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ? AND s.ts >= ? AND s.ts <= ? AND pr.code_version LIKE ?
              AND json_extract_string(a.explain, '$.gates.tradability.status') = 'PASS'
            """,
            params,
        )
        execution_ready = _count(
            conn,
            """
            SELECT COUNT(*)
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ? AND s.ts >= ? AND s.ts <= ? AND pr.code_version LIKE ?
              AND a.signal_state = 'ExecutionReady'
            """,
            params,
        )
    finally:
        conn.close()

    return {
        "snapshots": snapshots,
        "surface_rows": surface_rows,
        "qc_pass": qc_pass,
        "zscore_pass": zscore_pass,
        "persistence_pass": persistence_pass,
        "regime_pass": regime_pass,
        "tradability_pass": tradability_pass,
        "execution_ready": execution_ready,
        "alerts_total": alerts_total,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate S4 gate attrition report")
    parser.add_argument("--start-ts", required=True)
    parser.add_argument("--end-ts", required=True)
    parser.add_argument("--underlying", default="SPX")
    parser.add_argument("--baseline-lineage", required=True)
    parser.add_argument("--candidate-lineage", required=True)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    init_db()
    baseline = _attrition_for_lineage(
        args.underlying,
        args.start_ts,
        args.end_ts,
        args.baseline_lineage,
    )
    candidate = _attrition_for_lineage(
        args.underlying,
        args.start_ts,
        args.end_ts,
        args.candidate_lineage,
    )
    baseline_meta = _run_meta(args.underlying, args.start_ts, args.end_ts, args.baseline_lineage)
    candidate_meta = _run_meta(args.underlying, args.start_ts, args.end_ts, args.candidate_lineage)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "window": {
            "underlying": args.underlying,
            "start_ts": args.start_ts,
            "end_ts": args.end_ts,
        },
        "baseline": {
            "lineage": args.baseline_lineage,
            "meta": baseline_meta,
            "attrition": baseline,
        },
        "candidate": {
            "lineage": args.candidate_lineage,
            "meta": candidate_meta,
            "attrition": candidate,
        },
    }

    lines = [
        "# OptionTrader S4-03 Gate Attrition Report",
        "",
        f"Generated at: {payload['generated_at']}",
        "",
        "## Window",
        "",
        f"- Underlying: `{args.underlying}`",
        f"- Start: `{args.start_ts}`",
        f"- End: `{args.end_ts}`",
        "",
        "## Baseline",
        "",
        f"- Lineage: `{args.baseline_lineage}`",
        f"- Run/Profile/Hash: `run_id={baseline_meta['run_id']}` `profile={baseline_meta['profile_id']}` `config_hash={baseline_meta['config_hash']}`",
        f"- Snapshots: `{baseline['snapshots']}`",
        f"- Surface rows: `{baseline['surface_rows']}`",
        f"- QC pass: `{baseline['qc_pass']}`",
        f"- Z-score pass: `{baseline['zscore_pass']}`",
        f"- Persistence pass: `{baseline['persistence_pass']}`",
        f"- Regime pass: `{baseline['regime_pass']}`",
        f"- Tradability pass: `{baseline['tradability_pass']}`",
        f"- ExecutionReady: `{baseline['execution_ready']}`",
        "",
        "## Candidate",
        "",
        f"- Lineage: `{args.candidate_lineage}`",
        f"- Run/Profile/Hash: `run_id={candidate_meta['run_id']}` `profile={candidate_meta['profile_id']}` `config_hash={candidate_meta['config_hash']}`",
        f"- Snapshots: `{candidate['snapshots']}`",
        f"- Surface rows: `{candidate['surface_rows']}`",
        f"- QC pass: `{candidate['qc_pass']}`",
        f"- Z-score pass: `{candidate['zscore_pass']}`",
        f"- Persistence pass: `{candidate['persistence_pass']}`",
        f"- Regime pass: `{candidate['regime_pass']}`",
        f"- Tradability pass: `{candidate['tradability_pass']}`",
        f"- ExecutionReady: `{candidate['execution_ready']}`",
        "",
        "## Raw Payload",
        "",
        "```json",
        json.dumps(payload, indent=2, sort_keys=True),
        "```",
    ]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    print(f"report_written={out}")


if __name__ == "__main__":
    main()
