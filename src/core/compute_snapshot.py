from __future__ import annotations

from datetime import datetime
import json
import logging

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

import pandas as pd

from src.core.alerts import compute_alerts
from src.core.config import load_config
from src.core.metrics import compute_iv_points, compute_surface_metrics, filter_quotes_by_dte
from src.core.regime import regime_params_from_config, regime_threshold_hash
from src.core.trade_ideas import IdeaContext, build_trade_ideas
from src.core.tradability import compute_tradability_score
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


def _build_explain_payload(
    alert: dict,
    threshold: float,
    persistence_required: int,
    tier: str | None,
    regime_label: str,
    tradability_score: float,
) -> dict:
    zscore_mid = alert.get("zscore_mid")
    zscore_worst = alert.get("zscore_worst")
    persistence = int(alert.get("persistence") or 0)
    zscore_pass = (
        zscore_mid is not None
        and zscore_worst is not None
        and abs(float(zscore_mid)) >= threshold
        and abs(float(zscore_worst)) >= threshold
    )
    persistence_pass = persistence >= persistence_required
    data_tier_pass = tier is not None
    regime_pass = not (
        alert.get("alert_type") == "RR_EXTREME" and regime_label == "Stress"
    )
    tradability_pass = tradability_score > 0.0

    return {
        "alert_type": alert.get("alert_type"),
        "expiry_bucket": alert.get("expiry_bucket"),
        "gates": {
            "zscore": {
                "status": "PASS" if zscore_pass else "FAIL",
                "reason_code": "threshold_met" if zscore_pass else "threshold_not_met",
                "threshold": threshold,
                "zscore_mid": zscore_mid,
                "zscore_worst": zscore_worst,
            },
            "persistence": {
                "status": "PASS" if persistence_pass else "FAIL",
                "reason_code": (
                    "persistence_met" if persistence_pass else "persistence_short"
                ),
                "required": persistence_required,
                "observed": persistence,
            },
            "data_tier_quality": {
                "status": "PASS" if data_tier_pass else "FAIL",
                "reason_code": "tier_available" if data_tier_pass else "tier_missing",
                "confidence_tier": tier,
            },
            "regime": {
                "status": "PASS" if regime_pass else "FAIL",
                "reason_code": (
                    "allowed"
                    if regime_pass
                    else "rr_extreme_blocked_in_stress"
                ),
                "regime_label": regime_label,
            },
            "tradability": {
                "status": "PASS" if tradability_pass else "FAIL",
                "reason_code": (
                    "positive_tradability" if tradability_pass else "non_positive_tradability"
                ),
                "tradability_score": tradability_score,
            },
        },
    }


def compute_for_snapshot(snapshot_id: int, purge_existing: bool = True) -> None:
    logger = logging.getLogger("compute")
    config = load_config()
    buckets = config["metrics"]["expiry_buckets_days"]
    window = config["metrics"]["zscore_window_days"]
    threshold = config["alerts"]["z_threshold"]
    persistence = config["alerts"]["persistence_snapshots"]
    pessimistic_gate = bool(config["alerts"].get("pessimistic_gate", True))
    spread_gate_pct = config["quality"]["spread_gate_pct"]
    min_valid_points_full = int(config["quality"]["min_valid_points_full"])
    min_valid_points_core = int(config["quality"]["min_valid_points_core"])
    dte_min = config["data"]["dte_min"]
    dte_max = config["data"]["dte_max"]
    delta_points = config["metrics"].get("delta_points", [0.10, 0.25])
    pricing = config.get("pricing", {})
    rate = float(pricing.get("rate", 0.0))
    dividend_yield = float(pricing.get("dividend_yield", 0.0))

    conn = connect()
    try:
        ts, spot = _load_snapshot(conn, snapshot_id)
        if purge_existing:
            _clear_snapshot_outputs(conn, snapshot_id)
        logger.info("snapshot_id=%s ts=%s spot=%s", snapshot_id, ts, spot)
        regime_row = conn.execute(
            """
            SELECT regime_label, regime_config_hash FROM regime_state
            WHERE regime_date <= ?
            ORDER BY regime_date DESC
            LIMIT 1
            """,
            (ts.date(),),
        ).fetchone()
        regime_label = regime_row[0] if regime_row else "Neutral"
        current_regime_hash = regime_threshold_hash(regime_params_from_config(config))
        persisted_regime_hash = regime_row[1] if regime_row and len(regime_row) > 1 else None
        if persisted_regime_hash and persisted_regime_hash != current_regime_hash:
            logger.warning(
                "Regime threshold hash mismatch for snapshot_id=%s. "
                "Recompute regime_state with current config before relying on history.",
                snapshot_id,
            )
        quotes = conn.execute(
            "SELECT expiry, strike, option_right, bid, ask FROM option_quotes WHERE snapshot_id = ?",
            (snapshot_id,),
        ).fetchdf()

        quotes = filter_quotes_by_dte(quotes, ts, dte_min, dte_max)
        tradability_score = compute_tradability_score(quotes, spread_gate_pct)

        iv_points = compute_iv_points(
            quotes,
            ts,
            spot,
            spread_gate_pct,
            delta_points=delta_points,
            rate=rate,
            div=dividend_yield,
        )
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

        metrics = compute_surface_metrics(
            iv_points,
            ts,
            buckets,
            min_valid_points_core=min_valid_points_core,
            min_valid_points_full=min_valid_points_full,
        )
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
        alerts = compute_alerts(
            metric_series,
            window,
            threshold,
            persistence,
            pessimistic_gate=pessimistic_gate,
        )
        logger.info("alerts=%s", len(alerts))
        for alert in alerts:
            tier = tier_by_bucket.get(alert["expiry_bucket"])
            if tier is None:
                continue
            if alert["alert_type"] == "RR_EXTREME" and regime_label == "Stress":
                continue
            explain = _build_explain_payload(
                alert=alert,
                threshold=threshold,
                persistence_required=persistence,
                tier=tier,
                regime_label=regime_label,
                tradability_score=tradability_score,
            )
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

            expiry_dates = sorted({p.expiry for p in iv_points})
            target_expiry = None
            if expiry_dates:
                target_expiry = min(
                    expiry_dates,
                    key=lambda d: abs((d - ts.date()).days - bucket_days),
                )

            for point in iv_points:
                if target_expiry and point.expiry != target_expiry:
                    continue
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
                rate=rate,
                div=dividend_yield,
                iv_mid=iv_mid,
                iv_bid=iv_bid,
                iv_ask=iv_ask,
                expiry=target_expiry,
                config=config,
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
