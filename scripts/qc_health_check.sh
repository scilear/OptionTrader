#!/usr/bin/env bash
set -euo pipefail

WINDOW_HOURS=1
THRESHOLD=0.20
CONSECUTIVE=3
MIN_SNAPSHOTS=30
UNDERLYING="SPX"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --window-hours)
      WINDOW_HOURS="$2"
      shift 2
      ;;
    --threshold)
      THRESHOLD="$2"
      shift 2
      ;;
    --consecutive)
      CONSECUTIVE="$2"
      shift 2
      ;;
    --min-snapshots)
      MIN_SNAPSHOTS="$2"
      shift 2
      ;;
    --underlying)
      UNDERLYING="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

python - "$WINDOW_HOURS" "$THRESHOLD" "$CONSECUTIVE" "$MIN_SNAPSHOTS" "$UNDERLYING" <<'PY'
from __future__ import annotations

import json
import sys

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.db.connection import connect


def main() -> int:
    window_hours = int(sys.argv[1])
    threshold = float(sys.argv[2])
    consecutive = int(sys.argv[3])
    min_snapshots = int(sys.argv[4])
    underlying = str(sys.argv[5])

    if window_hours != 1:
        raise ValueError("Only 1-hour windows are supported in S3.2 contract (use --window-hours 1)")

    conn = connect()
    try:
        window_rows = conn.execute(
            """
            WITH per_snapshot AS (
              SELECT
                s.snapshot_id,
                date_trunc('hour', s.ts) AS hour_bucket,
                MAX(CASE WHEN m.qc_pass = FALSE THEN 1 ELSE 0 END) AS blocked
              FROM snapshots s
              LEFT JOIN surface_metrics m ON m.snapshot_id = s.snapshot_id
              WHERE s.underlying = ?
              GROUP BY 1, 2
            )
            SELECT
              hour_bucket,
              COUNT(*) AS snapshot_count,
              SUM(blocked) AS blocked_snapshots,
              CAST(SUM(blocked) AS DOUBLE) / NULLIF(COUNT(*), 0) AS block_rate
            FROM per_snapshot
            GROUP BY 1
            ORDER BY hour_bucket DESC
            """,
            (underlying,),
        ).fetchall()

        reason_rows = conn.execute(
            """
            WITH exploded AS (
              SELECT
                CAST(s.ts AS DATE) AS snapshot_date,
                m.expiry_bucket,
                reason.value::VARCHAR AS reason_code
              FROM surface_metrics m
              JOIN snapshots s ON s.snapshot_id = m.snapshot_id
              JOIN LATERAL json_each(COALESCE(m.qc_reason_codes, '[]')) AS reason ON TRUE
              WHERE s.underlying = ?
                AND m.qc_pass = FALSE
            )
            SELECT
              snapshot_date,
              expiry_bucket,
              reason_code,
              COUNT(*) AS reason_count
            FROM exploded
            GROUP BY 1, 2, 3
            ORDER BY snapshot_date DESC, reason_count DESC, expiry_bucket
            """,
            (underlying,),
        ).fetchall()
    finally:
        conn.close()

    print("QC window summary (hourly):")
    print("hour_bucket\tsnapshot_count\tblocked_snapshots\tblock_rate")
    for hour_bucket, snapshot_count, blocked_snapshots, block_rate in window_rows[:48]:
        rate = float(block_rate or 0.0)
        print(
            f"{hour_bucket}\t{int(snapshot_count)}\t{int(blocked_snapshots or 0)}\t{rate:.4f}"
        )

    print("\nQC reason-code frequency:")
    if reason_rows:
        print("snapshot_date\texpiry_bucket\treason_code\treason_count")
        for snapshot_date, expiry_bucket, reason_code, reason_count in reason_rows[:200]:
            reason_label = str(reason_code).strip('"')
            print(
                f"{snapshot_date}\t{expiry_bucket}\t{reason_label}\t{int(reason_count)}"
            )
    else:
        print("No failing QC reason codes found.")

    breach_streak = 0
    max_breach_streak = 0
    for _, snapshot_count, _, block_rate in window_rows:
        meets_sample = int(snapshot_count) >= min_snapshots
        exceeds_threshold = float(block_rate or 0.0) > threshold
        if meets_sample and exceeds_threshold:
            breach_streak += 1
            max_breach_streak = max(max_breach_streak, breach_streak)
        else:
            breach_streak = 0

    status = {
        "underlying": underlying,
        "window_hours": window_hours,
        "threshold": threshold,
        "consecutive": consecutive,
        "min_snapshots": min_snapshots,
        "max_breach_streak": max_breach_streak,
    }
    print("\nhealth_check_status=")
    print(json.dumps(status, indent=2, sort_keys=True))

    if max_breach_streak >= consecutive:
        print(
            "FAIL: sustained qc block-rate breach "
            f"(threshold>{threshold:.2f}, min_snapshots>={min_snapshots}, "
            f"consecutive={consecutive})"
        )
        return 1

    print("PASS: no sustained qc block-rate breach")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
