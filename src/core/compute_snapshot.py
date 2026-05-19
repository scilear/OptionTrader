from __future__ import annotations

from datetime import datetime
import json
import logging
from pathlib import Path

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


def _load_snapshot(conn, snapshot_id: int) -> tuple[datetime, float, int | None, str | None]:
    row = None
    try:
        row = conn.execute(
            "SELECT ts, spot, run_id, underlying FROM snapshots WHERE snapshot_id = ?",
            (snapshot_id,),
        ).fetchone()
    except Exception:
        try:
            row = conn.execute(
                "SELECT ts, spot, run_id FROM snapshots WHERE snapshot_id = ?",
                (snapshot_id,),
            ).fetchone()
        except Exception:
            row = conn.execute(
                "SELECT ts, spot FROM snapshots WHERE snapshot_id = ?",
                (snapshot_id,),
            ).fetchone()
    if not row:
        raise ValueError("snapshot not found")
    if len(row) >= 4:
        return row[0], float(row[1]), row[2], row[3]
    if len(row) >= 3:
        return row[0], float(row[1]), row[2], None
    return row[0], float(row[1]), None, None


def _resolve_regime_for_snapshot(
    conn,
    *,
    snapshot_id: int,
    ts: datetime,
    run_id: int | None,
) -> tuple[str, str | None]:
    row = conn.execute(
        """
        SELECT regime_label, regime_config_hash
        FROM regime_snapshot_labels
        WHERE snapshot_id = ?
        """,
        (snapshot_id,),
    ).fetchone()
    if row:
        return str(row[0]), str(row[1]) if row[1] is not None else None

    if run_id is not None:
        row = conn.execute(
            """
            SELECT regime_label, regime_config_hash
            FROM regime_snapshot_labels
            WHERE run_id = ?
              AND regime_date <= ?
            ORDER BY regime_date DESC
            LIMIT 1
            """,
            (run_id, ts.date()),
        ).fetchone()
        if row:
            return str(row[0]), str(row[1]) if row[1] is not None else None

    return "Unknown", None


def _clear_snapshot_outputs(conn, snapshot_id: int) -> None:
    conn.execute(
        "DELETE FROM trade_ideas WHERE alert_id IN (SELECT alert_id FROM alerts WHERE snapshot_id = ?)",
        (snapshot_id,),
    )
    conn.execute("DELETE FROM alerts WHERE snapshot_id = ?", (snapshot_id,))
    conn.execute("DELETE FROM surface_metrics WHERE snapshot_id = ?", (snapshot_id,))
    conn.execute("DELETE FROM iv_points WHERE snapshot_id = ?", (snapshot_id,))


def _worst_case_coherent(
    zscore_mid: float | None,
    zscore_worst: float | None,
    threshold: float,
) -> bool:
    if zscore_mid is None or zscore_worst is None:
        return False
    mid = float(zscore_mid)
    worst = float(zscore_worst)
    if abs(worst) < threshold:
        return False
    if mid == 0.0:
        return True
    return (mid > 0.0) == (worst > 0.0)


def _determine_signal_state(
    alert: dict,
    tier: str | None,
    regime_label: str,
    tradability_score: float,
    surface_qc_passed: bool,
    surface_quality_score: float,
    threshold: float,
    regime_hash_mismatch: bool,
    min_fit_confidence_validated: float,
    min_fit_confidence_execution: float,
    require_full_tier_for_execution: bool,
) -> dict:
    alert_type = str(alert.get("alert_type") or "")
    zscore_mid = alert.get("zscore_mid")
    zscore_worst = alert.get("zscore_worst")

    quality_blockers: list[str] = []
    if tier is None:
        quality_blockers.append("tier_missing")
    if regime_label == "Unknown":
        quality_blockers.append("regime_missing")
    if not surface_qc_passed:
        quality_blockers.append("surface_qc_failed")
    if regime_hash_mismatch:
        quality_blockers.append("regime_hash_mismatch")
    if alert_type == "RR_EXTREME" and regime_label == "Stress":
        quality_blockers.append("rr_extreme_blocked_in_stress")
    worst_case_ok = _worst_case_coherent(zscore_mid, zscore_worst, threshold)
    if not worst_case_ok:
        quality_blockers.append("worst_case_incoherent")
    if surface_quality_score < min_fit_confidence_validated:
        quality_blockers.append("fit_confidence_below_validated")

    uncertainty_score = 0.0
    if not worst_case_ok:
        uncertainty_score += 0.35
    if tier is None:
        uncertainty_score += 0.20
    elif tier == "Core":
        uncertainty_score += 0.10
    if not surface_qc_passed:
        uncertainty_score += 0.35
    if regime_hash_mismatch:
        uncertainty_score += 0.25
    if surface_quality_score < min_fit_confidence_validated:
        uncertainty_score += 0.20
    uncertainty_score = min(1.0, uncertainty_score)

    if quality_blockers:
        return {
            "signal_state": "Candidate",
            "transition_reason_code": quality_blockers[0],
            "quality_blockers": quality_blockers,
            "execution_blockers": [],
            "worst_case_coherent": worst_case_ok,
            "uncertainty_score": uncertainty_score,
        }

    execution_blockers: list[str] = []
    if tradability_score <= 0.0:
        execution_blockers.append("non_positive_tradability")
    if surface_quality_score < min_fit_confidence_execution:
        execution_blockers.append("fit_confidence_below_execution")
    if require_full_tier_for_execution and tier != "Full":
        execution_blockers.append("tier_not_full")

    if execution_blockers:
        return {
            "signal_state": "Validated",
            "transition_reason_code": execution_blockers[0],
            "quality_blockers": [],
            "execution_blockers": execution_blockers,
            "worst_case_coherent": worst_case_ok,
            "uncertainty_score": uncertainty_score,
        }

    return {
        "signal_state": "ExecutionReady",
        "transition_reason_code": "execution_ready",
        "quality_blockers": [],
        "execution_blockers": [],
        "worst_case_coherent": worst_case_ok,
        "uncertainty_score": uncertainty_score,
    }


def _resolve_regime_override_threshold(
    config: dict,
    regime_label: str,
    alert_type: str,
) -> float | None:
    alerts_cfg = config.get("alerts", {}) if isinstance(config, dict) else {}
    overrides = alerts_cfg.get("regime_overrides", {}) if isinstance(alerts_cfg, dict) else {}
    if not isinstance(overrides, dict):
        return None
    regime_cfg = overrides.get(regime_label)
    if not isinstance(regime_cfg, dict):
        return None
    alert_cfg = regime_cfg.get(alert_type)
    if not isinstance(alert_cfg, dict):
        return None
    min_abs_zscore = alert_cfg.get("min_abs_zscore")
    if min_abs_zscore is None:
        return None
    return float(min_abs_zscore)


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
    regime_hash_mismatch: bool,
    regime_override: dict,
    lifecycle: dict,
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
    regime_pass = regime_label != "Unknown" and not (
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
                    else (
                        "regime_missing"
                        if regime_label == "Unknown"
                        else "rr_extreme_blocked_in_stress"
                    )
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
            "worst_case_coherence": {
                "status": "PASS" if lifecycle.get("worst_case_coherent") else "FAIL",
                "reason_code": (
                    "worst_case_coherent"
                    if lifecycle.get("worst_case_coherent")
                    else "worst_case_incoherent"
                ),
            },
            "regime_hash": {
                "status": "FAIL" if regime_hash_mismatch else "PASS",
                "reason_code": (
                    "regime_hash_mismatch" if regime_hash_mismatch else "regime_hash_aligned_or_missing"
                ),
            },
            "regime_override": regime_override,
        },
        "score_method": {
            "mid": alert.get("score_method_mid"),
            "worst": alert.get("score_method_worst"),
        },
        "evidence_overlap": alert.get("evidence_overlap") or {
            "detected": False,
            "candidate_count": 1,
            "suppressed_alert_types": [],
            "strategy": "none",
        },
        "lifecycle": {
            "signal_state": lifecycle.get("signal_state"),
            "transition_reason_code": lifecycle.get("transition_reason_code"),
            "quality_blockers": lifecycle.get("quality_blockers", []),
            "execution_blockers": lifecycle.get("execution_blockers", []),
            "uncertainty_score": lifecycle.get("uncertainty_score"),
        },
    }


def compute_for_snapshot(
    snapshot_id: int,
    purge_existing: bool = True,
    config_path: Path | str | None = None,
) -> None:
    logger = logging.getLogger("compute")
    resolved_config_path = Path(config_path) if config_path is not None else None
    config = load_config(path=resolved_config_path)
    buckets = config["metrics"]["expiry_buckets_days"]
    window = config["metrics"]["zscore_window_days"]
    threshold = config["alerts"]["z_threshold"]
    persistence = config["alerts"]["persistence_snapshots"]
    pessimistic_gate = bool(config["alerts"].get("pessimistic_gate", True))
    history_scope = str(config["alerts"].get("history_scope", "global")).lower()
    metric_series_qc_only = bool(config["alerts"].get("metric_series_qc_only", True))
    emit_non_execution_states = bool(config["alerts"].get("emit_non_execution_states", False))
    lifecycle_cfg = config["alerts"].get("lifecycle", {})
    min_fit_confidence_validated = float(
        lifecycle_cfg.get("min_fit_confidence_validated", 0.55)
    )
    min_fit_confidence_execution = float(
        lifecycle_cfg.get("min_fit_confidence_execution", 0.70)
    )
    require_full_tier_for_execution = bool(
        lifecycle_cfg.get("require_full_tier_for_execution", False)
    )
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
        ts, spot, snapshot_run_id, snapshot_underlying = _load_snapshot(conn, snapshot_id)
        if purge_existing:
            _clear_snapshot_outputs(conn, snapshot_id)
        logger.info("snapshot_id=%s ts=%s spot=%s", snapshot_id, ts, spot)
        regime_label, persisted_regime_hash = _resolve_regime_for_snapshot(
            conn,
            snapshot_id=snapshot_id,
            ts=ts,
            run_id=snapshot_run_id,
        )
        if regime_label == "Unknown":
            logger.warning(
                "No scoped regime label available for snapshot_id=%s date=%s; defaulting to Unknown.",
                snapshot_id,
                ts.date(),
            )
        current_regime_hash = regime_threshold_hash(regime_params_from_config(config))
        regime_hash_mismatch = bool(
            persisted_regime_hash and persisted_regime_hash != current_regime_hash
        )
        if persisted_regime_hash and persisted_regime_hash != current_regime_hash:
            logger.warning(
                "Regime threshold hash mismatch for snapshot_id=%s; "
                "persisted_hash=%s current_hash=%s. "
                "Recompute regime_state with current config before relying on history.",
                snapshot_id,
                persisted_regime_hash,
                current_regime_hash,
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

        qc_clause = "AND m.qc_pass = TRUE" if metric_series_qc_only else ""
        if history_scope == "run" and snapshot_run_id is not None:
            metric_series = conn.execute(
                f"""
                SELECT s.ts, m.expiry_bucket, m.rr25_mid, m.fly25_mid, m.term_slope_mid,
                       m.rr25_worst, m.fly25_worst, m.term_slope_worst
                FROM surface_metrics m
                JOIN snapshots s ON s.snapshot_id = m.snapshot_id
                WHERE s.run_id = ?
                  AND s.ts <= ?
                  {qc_clause}
                """,
                (snapshot_run_id, ts),
            ).fetchdf()
        else:
            underlying_clause = "AND s.underlying = ?" if snapshot_underlying else ""
            params: tuple = (ts,)
            if snapshot_underlying:
                params = (ts, snapshot_underlying)
            metric_series = conn.execute(
                f"""
                SELECT s.ts, m.expiry_bucket, m.rr25_mid, m.fly25_mid, m.term_slope_mid,
                       m.rr25_worst, m.fly25_worst, m.term_slope_worst
                FROM surface_metrics m
                JOIN snapshots s ON s.snapshot_id = m.snapshot_id
                WHERE s.ts <= ?
                  {underlying_clause}
                  {qc_clause}
                """,
                params,
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
            alert_type = str(alert.get("alert_type") or "")
            zscore_mid = alert.get("zscore_mid")
            override_threshold = _resolve_regime_override_threshold(
                config,
                regime_label=regime_label,
                alert_type=alert_type,
            )
            effective_threshold = (
                float(override_threshold) if override_threshold is not None else float(threshold)
            )
            zscore_mid_abs = abs(float(zscore_mid)) if zscore_mid is not None else 0.0
            override_blocked = zscore_mid is None or zscore_mid_abs < effective_threshold
            regime_override_gate = {
                "status": "FAIL" if override_blocked else "PASS",
                "reason_code": (
                    "regime_override_threshold_not_met"
                    if override_blocked
                    else (
                        "regime_override_threshold_met"
                        if override_threshold is not None
                        else "regime_override_not_configured"
                    )
                ),
                "min_abs_zscore": effective_threshold,
                "zscore_mid_abs": zscore_mid_abs,
                "regime_label": regime_label,
                "alert_type": alert_type,
            }

            if override_blocked:
                if not emit_non_execution_states:
                    continue
                lifecycle = {
                    "signal_state": "Candidate",
                    "transition_reason_code": "regime_override_threshold_not_met",
                    "quality_blockers": ["regime_override_threshold_not_met"],
                    "execution_blockers": [],
                    "worst_case_coherent": _worst_case_coherent(
                        alert.get("zscore_mid"),
                        alert.get("zscore_worst"),
                        effective_threshold,
                    ),
                    "uncertainty_score": 0.35,
                }
                explain = _build_explain_payload(
                    alert=alert,
                    threshold=effective_threshold,
                    persistence_required=persistence,
                    tier=tier,
                    regime_label=regime_label,
                    tradability_score=tradability_score,
                    surface_qc_passed=surface_qc.passed,
                    surface_qc_reasons=list(surface_qc.reason_codes),
                    surface_quality_score=surface_qc.quality_score,
                    regime_hash_mismatch=regime_hash_mismatch,
                    regime_override=regime_override_gate,
                    lifecycle=lifecycle,
                )
                severity = float(alert.get("effective_severity") or zscore_mid_abs)
                conn.execute(
                    """
                    INSERT INTO alerts (
                        alert_id, snapshot_id, alert_type, expiry_bucket, severity,
                        zscore_mid, zscore_worst, tradability_score,
                        confidence_tier, persistence_count, regime_label,
                        signal_state, transition_reason_code, explain
                    ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot_id,
                        alert_type,
                        alert["expiry_bucket"],
                        severity,
                        alert.get("zscore_mid"),
                        alert.get("zscore_worst"),
                        tradability_score,
                        tier or "Unknown",
                        alert.get("persistence"),
                        regime_label,
                        lifecycle["signal_state"],
                        lifecycle["transition_reason_code"],
                        json.dumps(explain),
                    ),
                )
                continue

            lifecycle = _determine_signal_state(
                alert=alert,
                tier=tier,
                regime_label=regime_label,
                tradability_score=tradability_score,
                surface_qc_passed=surface_qc.passed,
                surface_quality_score=surface_qc.quality_score,
                threshold=effective_threshold,
                regime_hash_mismatch=regime_hash_mismatch,
                min_fit_confidence_validated=min_fit_confidence_validated,
                min_fit_confidence_execution=min_fit_confidence_execution,
                require_full_tier_for_execution=require_full_tier_for_execution,
            )
            signal_state = lifecycle["signal_state"]
            if signal_state != "ExecutionReady" and not emit_non_execution_states:
                continue
            explain = _build_explain_payload(
                alert=alert,
                threshold=effective_threshold,
                persistence_required=persistence,
                tier=tier,
                regime_label=regime_label,
                tradability_score=tradability_score,
                surface_qc_passed=surface_qc.passed,
                surface_qc_reasons=list(surface_qc.reason_codes),
                surface_quality_score=surface_qc.quality_score,
                regime_hash_mismatch=regime_hash_mismatch,
                regime_override=regime_override_gate,
                lifecycle=lifecycle,
            )
            severity = float(alert.get("effective_severity") or abs(alert["zscore_mid"]))
            conn.execute(
                """
                INSERT INTO alerts (
                    alert_id, snapshot_id, alert_type, expiry_bucket, severity,
                    zscore_mid, zscore_worst, tradability_score,
                    confidence_tier, persistence_count, regime_label,
                    signal_state, transition_reason_code, explain
                ) VALUES (DEFAULT, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    alert["alert_type"],
                    alert["expiry_bucket"],
                    severity,
                    alert["zscore_mid"],
                    alert["zscore_worst"],
                    tradability_score,
                    tier or "Unknown",
                    alert["persistence"],
                    regime_label,
                    signal_state,
                    lifecycle["transition_reason_code"],
                    json.dumps(explain),
                ),
            )

            if signal_state != "ExecutionReady":
                continue

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
                alert_severity=severity,
                alert_zscore_mid=alert["zscore_mid"],
                tradability_score=tradability_score,
            )
            _validate_structure_delta_support(context, logger, alert["expiry_bucket"])
            ideas = build_trade_ideas(alert["alert_type"], alert["expiry_bucket"], context)
            promote_eligible_idea_exists = False
            ranked_idea_seen = False
            blocked_reason_for_gate = None
            for idea in ideas:
                scenarios_obj = {}
                try:
                    scenarios_obj = json.loads(idea.get("scenarios") or "{}")
                except Exception:
                    scenarios_obj = {}
                ranking = scenarios_obj.get("ranking") if isinstance(scenarios_obj, dict) else None
                if isinstance(ranking, dict):
                    ranked_idea_seen = True
                    blocked_reason = ranking.get("blocked_reason")
                    if blocked_reason_for_gate is None and blocked_reason:
                        blocked_reason_for_gate = blocked_reason
                    if ranking.get("promote_eligible") is True:
                        promote_eligible_idea_exists = True

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

            if signal_state == "ExecutionReady" and ranked_idea_seen and not promote_eligible_idea_exists:
                if emit_non_execution_states:
                    conn.execute(
                        """
                        UPDATE alerts
                        SET signal_state = 'Validated',
                            transition_reason_code = ?
                        WHERE alert_id = ?
                        """,
                        (blocked_reason_for_gate or "non_positive_edge_after_cost", alert_id),
                    )
                else:
                    conn.execute("DELETE FROM trade_ideas WHERE alert_id = ?", (alert_id,))
                    conn.execute("DELETE FROM alerts WHERE alert_id = ?", (alert_id,))
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    compute_for_snapshot(int(sys.argv[1]))
