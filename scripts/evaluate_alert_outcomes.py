from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from src.db.connection import connect


METRIC_BY_ALERT_TYPE = {
    "RR_EXTREME": "rr25_mid",
    "FLY_EXTREME": "fly25_mid",
    "TERM_KINK": "term_slope_mid",
}


def _reversion_ratio(base_value: float, resolved_value: float) -> float:
    denom = abs(base_value)
    if denom == 0.0:
        return 0.0
    improvement = abs(base_value) - abs(resolved_value)
    return float(improvement / denom)


def evaluate_alert_outcomes(horizon_days: int = 5, overwrite: bool = False) -> int:
    conn = connect()
    evaluated_at = datetime.now(timezone.utc)
    try:
        if overwrite:
            conn.execute("DELETE FROM alert_outcomes WHERE horizon_days = ?", (horizon_days,))

        rows = conn.execute(
            """
            SELECT
              a.alert_id,
              a.alert_type,
              a.expiry_bucket,
              a.snapshot_id,
              s.ts,
              s.underlying
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            ORDER BY a.alert_id
            """
        ).fetchall()

        inserted = 0
        for alert_id, alert_type, expiry_bucket, snapshot_id, snapshot_ts, underlying in rows:
            metric_col = METRIC_BY_ALERT_TYPE.get(str(alert_type))
            if metric_col is None:
                continue

            exists = conn.execute(
                "SELECT 1 FROM alert_outcomes WHERE alert_id = ? AND horizon_days = ?",
                (alert_id, horizon_days),
            ).fetchone()
            if exists:
                continue

            base_row = conn.execute(
                f"""
                SELECT {metric_col}
                FROM surface_metrics
                WHERE snapshot_id = ? AND expiry_bucket = ?
                LIMIT 1
                """,
                (snapshot_id, expiry_bucket),
            ).fetchone()
            if not base_row or base_row[0] is None:
                continue
            base_metric = float(base_row[0])

            resolved_row = conn.execute(
                f"""
                SELECT sm.snapshot_id, s.ts, sm.{metric_col}
                FROM snapshots s
                JOIN surface_metrics sm ON sm.snapshot_id = s.snapshot_id
                WHERE s.ts >= (? + (? * INTERVAL '1 day'))
                  AND s.underlying = ?
                  AND sm.expiry_bucket = ?
                  AND sm.{metric_col} IS NOT NULL
                ORDER BY s.ts ASC
                LIMIT 1
                """,
                (snapshot_ts, horizon_days, underlying, expiry_bucket),
            ).fetchone()
            if not resolved_row:
                continue

            resolved_snapshot_id = int(resolved_row[0])
            resolved_ts = resolved_row[1]
            resolved_metric = float(resolved_row[2])
            ratio = _reversion_ratio(base_metric, resolved_metric)
            outcome_label = "tp" if ratio >= 0.5 else "fp"

            conn.execute(
                """
                INSERT INTO alert_outcomes (
                    alert_id,
                    horizon_days,
                    outcome_label,
                    resolved_snapshot_id,
                    resolved_ts,
                    base_metric_value,
                    resolved_metric_value,
                    reversion_ratio,
                    outcome_source,
                    evaluated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert_id,
                    horizon_days,
                    outcome_label,
                    resolved_snapshot_id,
                    resolved_ts,
                    base_metric,
                    resolved_metric,
                    ratio,
                    "surface_reversion_v1",
                    evaluated_at,
                ),
            )
            inserted += 1

        return inserted
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate alert outcomes for ablation gates")
    parser.add_argument("--horizon-days", type=int, default=5)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    inserted = evaluate_alert_outcomes(horizon_days=args.horizon_days, overwrite=args.overwrite)
    print(f"alert_outcomes_inserted={inserted}")


if __name__ == "__main__":
    main()
