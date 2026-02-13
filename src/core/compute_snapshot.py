from __future__ import annotations

from datetime import datetime

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

import pandas as pd

from src.core.config import load_config
from src.core.metrics import compute_iv_points, compute_surface_metrics
from src.core.alerts import compute_alerts
from src.db.connection import connect


def _load_snapshot(conn, snapshot_id: int) -> tuple[datetime, float]:
    row = conn.execute(
        "SELECT ts, spot FROM snapshots WHERE snapshot_id = ?",
        (snapshot_id,),
    ).fetchone()
    if not row:
        raise ValueError("snapshot not found")
    return row[0], float(row[1])


def compute_for_snapshot(snapshot_id: int) -> None:
    config = load_config()
    buckets = config["metrics"]["expiry_buckets_days"]
    window = config["metrics"]["zscore_window_days"]
    threshold = config["alerts"]["z_threshold"]
    persistence = config["alerts"]["persistence_snapshots"]
    spread_gate_pct = config["quality"]["spread_gate_pct"]

    conn = connect()
    try:
        ts, spot = _load_snapshot(conn, snapshot_id)
        regime_row = conn.execute(
            """
            SELECT regime_label FROM regime_state
            WHERE regime_date <= ?
            ORDER BY regime_date DESC
            LIMIT 1
            """,
            (ts.date(),),
        ).fetchone()
        regime_label = regime_row[0] if regime_row else "Neutral"
        quotes = conn.execute(
            "SELECT expiry, strike, option_right, bid, ask FROM option_quotes WHERE snapshot_id = ?",
            (snapshot_id,),
        ).fetchdf()

        iv_points = compute_iv_points(quotes, ts, spot, spread_gate_pct)
        for point in iv_points:
            conn.execute(
                """
                INSERT INTO iv_points (
                    iv_id, snapshot_id, expiry, delta_bucket, iv_mid, iv_bid, iv_ask,
                    solve_status, quality_score
                ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    point.expiry,
                    point.delta_bucket,
                    point.iv_mid,
                    point.iv_bid,
                    point.iv_ask,
                    point.solve_status,
                    point.quality_score,
                ),
            )

        metrics = compute_surface_metrics(iv_points, ts, buckets)
        tier_by_bucket = {m["expiry_bucket"]: m.get("tier") for m in metrics}
        for m in metrics:
            conn.execute(
                """
                INSERT INTO surface_metrics (
                    metric_id, snapshot_id, expiry_bucket,
                    atm_iv_mid, rr25_mid, rr10_mid, fly25_mid, fly10_mid,
                    term_slope_mid,
                    atm_iv_worst, rr25_worst, rr10_worst, fly25_worst, fly10_worst,
                    term_slope_worst
                ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    m["expiry_bucket"],
                    m["atm_iv_mid"],
                    m["rr25_mid"],
                    m["rr10_mid"],
                    m["fly25_mid"],
                    m["fly10_mid"],
                    m.get("term_slope_mid"),
                    m.get("atm_iv_worst"),
                    m.get("rr25_worst"),
                    m.get("rr10_worst"),
                    m.get("fly25_worst"),
                    m.get("fly10_worst"),
                    m.get("term_slope_worst"),
                ),
            )

        metric_series = conn.execute(
            """
            SELECT s.ts, m.expiry_bucket, m.rr25_mid, m.fly25_mid, m.term_slope_mid,
                   m.rr25_worst, m.fly25_worst, m.term_slope_worst
            FROM surface_metrics m
            JOIN snapshots s ON s.snapshot_id = m.snapshot_id
            """
        ).fetchdf()
        alerts = compute_alerts(metric_series, window, threshold, persistence)
        for alert in alerts:
            tier = tier_by_bucket.get(alert["expiry_bucket"])
            if tier is None:
                continue
            if alert["alert_type"] == "RR_EXTREME" and regime_label == "Stress":
                continue
            conn.execute(
                """
                INSERT INTO alerts (
                    alert_id, snapshot_id, alert_type, expiry_bucket, severity,
                    zscore_mid, zscore_worst, tradability_score,
                    confidence_tier, persistence_count, regime_label, explain
                ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    alert["alert_type"],
                    alert["expiry_bucket"],
                    abs(alert["zscore_mid"]),
                    alert["zscore_mid"],
                    alert["zscore_worst"],
                    1.0 if tier == "Full" else 0.5,
                    tier,
                    alert["persistence"],
                    regime_label,
                    "{}",
                ),
            )
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    compute_for_snapshot(int(sys.argv[1]))
