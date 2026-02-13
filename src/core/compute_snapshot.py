from __future__ import annotations

from datetime import datetime

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

import pandas as pd

from src.core.config import load_config
from src.core.metrics import compute_iv_points, compute_surface_metrics, filter_quotes_by_dte
from src.core.tradability import compute_tradability_score
import json
import logging

import json

from src.core.alerts import compute_alerts
from src.core.trade_ideas import build_trade_ideas, IdeaContext
from src.db.connection import connect


def _load_snapshot(conn, snapshot_id: int) -> tuple[datetime, float]:
    row = conn.execute(
        "SELECT ts, spot FROM snapshots WHERE snapshot_id = ?",
        (snapshot_id,),
    ).fetchone()
    if not row:
        raise ValueError("snapshot not found")
    return row[0], float(row[1])


def _clear_snapshot_outputs(conn, snapshot_id: int) -> None:
    conn.execute(
        "DELETE FROM trade_ideas WHERE alert_id IN (SELECT alert_id FROM alerts WHERE snapshot_id = ?)",
        (snapshot_id,),
    )
    conn.execute("DELETE FROM alerts WHERE snapshot_id = ?", (snapshot_id,))
    conn.execute("DELETE FROM surface_metrics WHERE snapshot_id = ?", (snapshot_id,))
    conn.execute("DELETE FROM iv_points WHERE snapshot_id = ?", (snapshot_id,))


def compute_for_snapshot(snapshot_id: int, purge_existing: bool = True) -> None:
    logger = logging.getLogger("compute")
    config = load_config()
    buckets = config["metrics"]["expiry_buckets_days"]
    window = config["metrics"]["zscore_window_days"]
    threshold = config["alerts"]["z_threshold"]
    persistence = config["alerts"]["persistence_snapshots"]
    spread_gate_pct = config["quality"]["spread_gate_pct"]
    dte_min = config["data"]["dte_min"]
    dte_max = config["data"]["dte_max"]

    conn = connect()
    try:
        ts, spot = _load_snapshot(conn, snapshot_id)
        if purge_existing:
            _clear_snapshot_outputs(conn, snapshot_id)
        logger.info("snapshot_id=%s ts=%s spot=%s", snapshot_id, ts, spot)
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

        quotes = filter_quotes_by_dte(quotes, ts, dte_min, dte_max)
        tradability_score = compute_tradability_score(quotes, spread_gate_pct)

        iv_points = compute_iv_points(quotes, ts, spot, spread_gate_pct)
        logger.info("iv_points=%s", len(iv_points))
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
        logger.info("metrics_rows=%s", len(metrics))
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
        logger.info("alerts=%s", len(alerts))
        for alert in alerts:
            tier = tier_by_bucket.get(alert["expiry_bucket"])
            if tier is None:
                continue
            if alert["alert_type"] == "RR_EXTREME" and regime_label == "Stress":
                continue
            explain = {
                "alert_type": alert["alert_type"],
                "expiry_bucket": alert["expiry_bucket"],
                "z_threshold": threshold,
                "zscore_mid": alert["zscore_mid"],
                "zscore_worst": alert["zscore_worst"],
                "persistence": alert["persistence"],
                "regime_label": regime_label,
                "confidence_tier": tier,
                "tradability_score": tradability_score,
            }
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
                    tradability_score,
                    tier,
                    alert["persistence"],
                    regime_label,
                    json.dumps(explain),
                ),
            )

            alert_id = conn.execute("SELECT MAX(alert_id) FROM alerts").fetchone()[0]
            bucket_days = int(alert["expiry_bucket"].replace("D", ""))
            t_years = bucket_days / 365.0
            iv_mid = {}
            iv_bid = {}
            iv_ask = {}
            for point in iv_points:
                if point.delta_bucket == "ATM":
                    continue
                if point.delta_bucket == "+0.25C":
                    iv_mid[0.25] = point.iv_mid
                    iv_bid[0.25] = point.iv_bid
                    iv_ask[0.25] = point.iv_ask
                if point.delta_bucket == "-0.25P":
                    iv_mid[-0.25] = point.iv_mid
                    iv_bid[-0.25] = point.iv_bid
                    iv_ask[-0.25] = point.iv_ask
                if point.delta_bucket == "+0.10C":
                    iv_mid[0.10] = point.iv_mid
                    iv_bid[0.10] = point.iv_bid
                    iv_ask[0.10] = point.iv_ask
                if point.delta_bucket == "-0.10P":
                    iv_mid[-0.10] = point.iv_mid
                    iv_bid[-0.10] = point.iv_bid
                    iv_ask[-0.10] = point.iv_ask

            context = IdeaContext(
                spot=spot,
                t_years=t_years,
                rate=0.0,
                div=0.0,
                iv_mid=iv_mid,
                iv_bid=iv_bid,
                iv_ask=iv_ask,
            )
            ideas = build_trade_ideas(alert["alert_type"], alert["expiry_bucket"], context)
            for idea in ideas:
                conn.execute(
                    """
                    INSERT INTO trade_ideas (
                        trade_id, alert_id, template, legs, price_mid, price_worst,
                        greeks, scenarios, risk_flags
                    ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        alert_id,
                        idea["template"],
                        idea["legs"],
                        idea["price_mid"],
                        idea["price_worst"],
                        idea["greeks"],
                        idea["scenarios"],
                        idea["risk_flags"],
                    ),
                )
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    compute_for_snapshot(int(sys.argv[1]))
