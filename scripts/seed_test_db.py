from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import duckdb


def init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    schema_path = Path("src/db/schema.sql")
    conn.execute(schema_path.read_text())


def seed(conn: duckdb.DuckDBPyConnection) -> None:
    # snapshots
    conn.execute(
        """
        INSERT INTO snapshots (snapshot_id, ts, underlying, spot, source, session_tag, notes)
        VALUES
          (DEFAULT, '2026-02-10 20:00:00', 'SPX', 5000, 'seed', 'eod', 'seed-1'),
          (DEFAULT, '2026-02-11 20:00:00', 'SPX', 5050, 'seed', 'eod', 'seed-2'),
          (DEFAULT, '2026-02-12 20:00:00', 'SPX', 5100, 'seed', 'eod', 'seed-3')
        """
    )

    snapshot_ids = [r[0] for r in conn.execute("SELECT snapshot_id FROM snapshots ORDER BY snapshot_id").fetchall()]

    # regime_state
    conn.execute(
        """
        INSERT INTO regime_state (regime_date, vix_percentile, rv20_percentile, drawdown_percent, regime_score, regime_label)
        VALUES
          ('2026-02-10', 30, 30, 2, 1, 'Calm'),
          ('2026-02-11', 55, 50, 6, 3, 'Transition'),
          ('2026-02-12', 85, 88, 12, 6, 'Stress')
        """
    )

    # surface_metrics for 30D bucket
    metrics = [
        (snapshot_ids[0], "30D", 0.20, -0.01, -0.02, 0.005, 0.006, -0.01, 0.21, -0.02, -0.03, 0.006, 0.007, -0.015),
        (snapshot_ids[1], "30D", 0.22, -0.03, -0.04, 0.010, 0.011, -0.015, 0.23, -0.04, -0.05, 0.012, 0.013, -0.020),
        (snapshot_ids[2], "30D", 0.24, -0.07, -0.08, 0.025, 0.026, -0.020, 0.26, -0.09, -0.10, 0.030, 0.031, -0.025),
    ]
    conn.executemany(
        """
        INSERT INTO surface_metrics (
            metric_id, snapshot_id, expiry_bucket,
            atm_iv_mid, rr25_mid, rr10_mid, fly25_mid, fly10_mid,
            term_slope_mid,
            atm_iv_worst, rr25_worst, rr10_worst, fly25_worst, fly10_worst,
            term_slope_worst
        ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        metrics,
    )

    # alerts on last snapshot
    explain_rr = json.dumps(
        {
            "alert_type": "RR_EXTREME",
            "expiry_bucket": "30D",
            "z_threshold": 2.0,
            "zscore_mid": 2.5,
            "zscore_worst": 2.1,
            "persistence": 2,
            "regime_label": "Transition",
            "confidence_tier": "Core",
            "tradability_score": 0.7,
        }
    )
    explain_fly = json.dumps(
        {
            "alert_type": "FLY_EXTREME",
            "expiry_bucket": "30D",
            "z_threshold": 2.0,
            "zscore_mid": 2.7,
            "zscore_worst": 2.2,
            "persistence": 2,
            "regime_label": "Transition",
            "confidence_tier": "Full",
            "tradability_score": 0.8,
        }
    )
    conn.execute(
        """
        INSERT INTO alerts (
            alert_id, snapshot_id, alert_type, expiry_bucket, severity,
            zscore_mid, zscore_worst, tradability_score,
            confidence_tier, persistence_count, regime_label, explain
        ) VALUES
          (DEFAULT, ?, 'RR_EXTREME', '30D', 2.5, 2.5, 2.1, 0.7, 'Core', 2, 'Transition', ?),
          (DEFAULT, ?, 'FLY_EXTREME', '30D', 2.7, 2.7, 2.2, 0.8, 'Full', 2, 'Transition', ?)
        """,
        (snapshot_ids[2], explain_rr, snapshot_ids[2], explain_fly),
    )

    alert_ids = [r[0] for r in conn.execute("SELECT alert_id FROM alerts ORDER BY alert_id").fetchall()]
    for alert_id in alert_ids:
        conn.execute(
            """
            INSERT INTO trade_ideas (
                trade_id, alert_id, template, legs, price_mid, price_worst, greeks, scenarios, risk_flags
            ) VALUES
              (DEFAULT, ?, 'SkewFade_PutSpread', ?, -2.1, -2.6, ?, ?, ?)
            """,
            (
                alert_id,
                json.dumps([
                    {"right": "P", "delta": -0.25, "action": "SELL", "strike": 4900, "expiry": "2026-03-13"},
                    {"right": "P", "delta": -0.10, "action": "BUY", "strike": 4750, "expiry": "2026-03-13"},
                ]),
                json.dumps({"delta": -0.1, "gamma": 0.01, "vega": 0.2}),
                json.dumps({}),
                json.dumps(["tail_risk", "liquidity"]),
            ),
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", default="data/test_optiontrader.duckdb")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if args.reset and db_path.exists():
        db_path.unlink()

    conn = duckdb.connect(str(db_path))
    try:
        init_schema(conn)
        seed(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
