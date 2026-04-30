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
from src.core.surface_qc import evaluate_surface_qc
from src.core.trade_ideas import IdeaContext, build_trade_ideas
from src.core.tradability import compute_tradability_score
from src.db.connection import connect


def _normalize_delta(value: float) -> float:
    return round(float(value), 2)


def _build_iv_lookup(
    iv_points,
    target_expiry,
) -> tuple[dict[float, float], dict[float, float], dict[float, float]]:
    iv_mid: dict[float, float] = {}
    iv_bid: dict[float, float] = {}
    iv_ask: dict[float, float] = {}
    for point in iv_points:
        if target_expiry and point.expiry != target_expiry:
            continue
        bucket = str(point.delta_bucket)
        if bucket == "ATM":
            if point.iv_mid is not None:
                iv_mid[0.5] = point.iv_mid
                iv_mid[-0.5] = point.iv_mid
            if point.iv_bid is not None:
                iv_bid[0.5] = point.iv_bid
                iv_bid[-0.5] = point.iv_bid
            if point.iv_ask is not None:
                iv_ask[0.5] = point.iv_ask
                iv_ask[-0.5] = point.iv_ask
            continue
        if len(bucket) < 3:
            continue
        side = bucket[-1]
        if side not in {"C", "P"}:
            continue
        try:
            magnitude = abs(float(bucket[:-1]))
        except ValueError:
            continue
        key = _normalize_delta(magnitude if side == "C" else -magnitude)
        if point.iv_mid is not None:
            iv_mid[key] = point.iv_mid
        if point.iv_bid is not None:
            iv_bid[key] = point.iv_bid
        if point.iv_ask is not None:
            iv_ask[key] = point.iv_ask
    return iv_mid, iv_bid, iv_ask


def _validate_structure_delta_support(
    context: IdeaContext,
    logger: logging.Logger,
    expiry_bucket: str,
) -> None:
    structures = context.config.get("structures", {}) if context.config else {}
    skew_cfg = structures.get("skew_fade", {})
    fly_cfg = structures.get("fly", {})
    expected = {
        _normalize_delta(float(skew_cfg.get("short_put_delta", -0.25))),
        _normalize_delta(float(skew_cfg.get("long_put_delta", -0.10))),
        _normalize_delta(-abs(float(fly_cfg.get("wing_delta", 0.25)))),
        _normalize_delta(-max(0.10, min(0.45, abs(float(fly_cfg.get("wing_delta", 0.25))) / 2.0))),
        0.5,
    }
    available = {
        _normalize_delta(value)
        for value in set(context.iv_mid.keys()) | set(context.iv_bid.keys()) | set(context.iv_ask.keys())
    }
    missing = sorted(expected - available)
    if missing:
        logger.warning(
            "Configured structure deltas missing IV support for bucket=%s: %s",
            expiry_bucket,
            ", ".join(f"{x:.2f}" for x in missing),
        )


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
    surface_qc_passed: bool,
    surface_qc_reasons: list[str],
    surface_quality_score: float,
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
    surface_qc_gate_pass = bool(surface_qc_passed)

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
            "surface_qc": {
                "status": "PASS" if surface_qc_gate_pass else "FAIL",
                "reason_code": "surface_qc_passed" if surface_qc_gate_pass else "surface_qc_failed",
                "surface_quality_score": surface_quality_score,
                "reasons": surface_qc_reasons,
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
    qc_cfg = config.get("qc", {})
    no_arb_epsilon = float(qc_cfg.get("no_arb_epsilon", 0.0))
    no_arb_epsilon_iv = float(qc_cfg.get("no_arb_epsilon_iv", no_arb_epsilon))
    no_arb_epsilon_var = float(qc_cfg.get("no_arb_epsilon_var", no_arb_epsilon))
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
                    solve_status, quality_score,
                    fit_model_id, fit_residual, fit_support, fit_confidence, fit_reason_codes
                ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    point.fit_model_id,
                    point.fit_residual,
                    point.fit_support,
                    point.fit_confidence,
                    json.dumps(list(point.fit_reason_codes)),
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
        surface_qc = evaluate_surface_qc(
            metrics,
            iv_points,
            no_arb_epsilon=no_arb_epsilon,
            iv_epsilon=no_arb_epsilon_iv,
            var_epsilon=no_arb_epsilon_var,
        )
        logger.info(
            "surface_qc_passed=%s reasons=%s quality=%.4f",
            surface_qc.passed,
            list(surface_qc.reason_codes),
            surface_qc.quality_score,
        )
        tier_by_bucket = {m["expiry_bucket"]: m.get("tier") for m in metrics}
        for m in metrics:
            point_rows = [
                p for p in iv_points if int((p.expiry - ts.date()).days) > 0 and m["expiry_bucket"] == f"{min(buckets, key=lambda b: abs((p.expiry - ts.date()).days - b))}D"
            ]
            fit_model_id = "mixed"
            fit_residual = None
            fit_support = 0
            fit_confidence = 0.0
            if point_rows:
                model_ids = {p.fit_model_id for p in point_rows if p.fit_model_id}
                fit_model_id = sorted(model_ids)[0] if len(model_ids) == 1 else "mixed"
                residuals = [p.fit_residual for p in point_rows if p.fit_residual is not None]
                fit_residual = max(residuals) if residuals else None
                fit_support = max((int(p.fit_support or 0) for p in point_rows), default=0)
                confidences = [float(p.fit_confidence or 0.0) for p in point_rows]
                fit_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            conn.execute(
                """
                INSERT INTO surface_metrics (
                    metric_id, snapshot_id, expiry_bucket,
                    atm_iv_mid, rr25_mid, rr10_mid, fly25_mid, fly10_mid,
                    term_slope_mid,
                    atm_iv_worst, rr25_worst, rr10_worst, fly25_worst, fly10_worst,
                    term_slope_worst,
                    fit_model_id, fit_residual, fit_support, fit_confidence,
                    surface_quality_score, qc_pass, qc_reason_codes
                ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    fit_model_id,
                    fit_residual,
                    fit_support,
                    fit_confidence,
                    surface_qc.quality_score,
                    surface_qc.passed,
                    json.dumps(list(surface_qc.reason_codes)),
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
            if not surface_qc.passed:
                continue
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
                surface_qc_passed=surface_qc.passed,
                surface_qc_reasons=list(surface_qc.reason_codes),
                surface_quality_score=surface_qc.quality_score,
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
            expiry_dates = sorted({p.expiry for p in iv_points})
            target_expiry = None
            if expiry_dates:
                target_expiry = min(
                    expiry_dates,
                    key=lambda d: abs((d - ts.date()).days - bucket_days),
                )

            iv_mid, iv_bid, iv_ask = _build_iv_lookup(iv_points, target_expiry)

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
            _validate_structure_delta_support(context, logger, alert["expiry_bucket"])
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
