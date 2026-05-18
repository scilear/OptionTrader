from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import statistics
import sys
from typing import Any

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.core.bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from scripts.evaluate_alert_outcomes import evaluate_alert_outcomes
from scripts.generate_regime_ablation_artifact import _fetch_precision_metrics
from src.core.config import load_config
from src.core.regime import (
    first_regime_ready_date,
    regime_params_from_config,
    regime_threshold_hash,
)
from src.core.replay import replay_walk_forward
from src.db.connection import connect
from src.db.init_db import init_db


DEFAULT_CONTRACT_ID = "S7-CONTRACT-v1"
DEFAULT_START_TS = "2010-01-01T00:00:00Z"
DEFAULT_END_TS = "2023-12-31T23:59:59Z"
DEFAULT_UNDERLYING = "SPX"
DEFAULT_BASELINE_LINEAGE = "3b024c9"
DEFAULT_CANDIDATE_LINEAGE = "5128e8e"
DEFAULT_CONFIG_PATH = "config/config-eod-truth.yaml"
DEFAULT_OUTPUT_PATH = "docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Report.md"
DEFAULT_JSON_OUTPUT_PATH = "docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Payload.json"
DEFAULT_BASELINE_CAPTURE_PATH = "docs/roadmap/OptionTrader_Sprint_7_Baseline_Capture_v1.json"


def _parse_utc_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)


def _format_utc_ts(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_effective_start_ts(
    *,
    requested_start_ts: str,
    end_ts: str,
    baseline_meta: dict[str, Any],
    candidate_meta: dict[str, Any],
    config_path: str,
) -> dict[str, Any]:
    del end_ts
    requested_start_dt = _parse_utc_ts(requested_start_ts)
    cfg = load_config(path=Path(config_path))
    params = regime_params_from_config(cfg)

    ready_dates: dict[str, str | None] = {"baseline": None, "candidate": None}
    candidate_dates = [requested_start_dt.date()]

    baseline_run_id = baseline_meta.get("run_id")
    if isinstance(baseline_run_id, int):
        baseline_ready = first_regime_ready_date(baseline_run_id, params=params)
        if baseline_ready is not None:
            ready_dates["baseline"] = baseline_ready.isoformat()
            candidate_dates.append(baseline_ready)

    candidate_run_id = candidate_meta.get("run_id")
    if isinstance(candidate_run_id, int):
        candidate_ready = first_regime_ready_date(candidate_run_id, params=params)
        if candidate_ready is not None:
            ready_dates["candidate"] = candidate_ready.isoformat()
            candidate_dates.append(candidate_ready)

    effective_start_date = max(candidate_dates)
    effective_start_dt = datetime.combine(
        effective_start_date,
        datetime.min.time(),
        tzinfo=timezone.utc,
    )
    warmup_excluded_days = max((effective_start_date - requested_start_dt.date()).days, 0)
    return {
        "requested_start_ts": requested_start_ts,
        "effective_start_ts": _format_utc_ts(effective_start_dt),
        "warmup_excluded_days": warmup_excluded_days,
        "warmup_exclusion_applied": warmup_excluded_days > 0,
        "regime_ready_dates": ready_dates,
    }


def _lineage_meta(underlying: str, start_ts: str, end_ts: str, lineage_prefix: str) -> dict[str, Any]:
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
    code_version_value = str(code_version) if code_version is not None else None
    if code_version_value and marker in code_version_value:
        profile_id = code_version_value.split(marker, 1)[1]
    return {
        "run_id": int(run_id),
        "code_version": code_version_value,
        "config_hash": str(config_hash) if config_hash is not None else None,
        "profile_id": profile_id,
    }


def _walk_forward_gate(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    candidate_lineage: str,
    train_size: int,
    test_size: int,
    step_size: int,
) -> dict[str, Any]:
    splits = replay_walk_forward(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        train_size=train_size,
        test_size=test_size,
        step_size=step_size,
        lineage_prefix=candidate_lineage,
        purge_existing=False,
        execute_test_replay=False,
    )
    test_lengths = [len(split.test_snapshot_ids) for split in splits]
    deterministic = len(set(test_lengths)) <= 1 if test_lengths else False
    return {
        "split_count": len(splits),
        "train_size": train_size,
        "test_size": test_size,
        "step_size": step_size,
        "test_window_lengths": test_lengths,
        "deterministic_schedule": deterministic,
        "pass": len(splits) > 0 and deterministic,
    }


def _adversarial_gate() -> dict[str, Any]:
    scenario_selectors = {
        "sparse_wings": "tests/test_surface_adversarial.py::test_sparse_wings_emit_degraded_status",
        "stale_books": "tests/test_surface_adversarial.py::test_stale_books_emit_no_alert",
        "missing_tenors": "tests/test_surface_adversarial.py::test_missing_tenors_term_slope_remains_null",
        "discontinuous_chain_snapshots": (
            "tests/test_surface_adversarial.py::test_discontinuous_chain_snapshots_emit_no_false_alert"
        ),
    }

    scenarios: dict[str, bool] = {}
    details: dict[str, dict[str, Any]] = {}
    for scenario, selector in scenario_selectors.items():
        cmd = [sys.executable, "-m", "pytest", selector, "-q"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        passed = result.returncode == 0
        scenarios[scenario] = passed
        details[scenario] = {
            "selector": selector,
            "returncode": int(result.returncode),
            "stdout": result.stdout.strip().splitlines()[-1:] if result.stdout else [],
            "stderr": result.stderr.strip().splitlines()[-1:] if result.stderr else [],
        }
    return {
        "scenarios": scenarios,
        "details": details,
        "pass": all(scenarios.values()),
    }


def _regime_stratified_summary(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    lineage_prefix: str,
    horizon_days: int,
) -> dict[str, dict[str, float | int | None]]:
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT
              CASE
                WHEN a.regime_label IS NULL OR a.regime_label = 'Neutral' THEN
                  COALESCE(rsl.regime_label, COALESCE(rs.regime_label, 'Unknown'))
                ELSE a.regime_label
              END AS regime_label,
              COUNT(*) AS alerts,
              SUM(CASE WHEN ao.outcome_label = 'tp' THEN 1 ELSE 0 END) AS tp,
              SUM(CASE WHEN ao.outcome_label = 'fp' THEN 1 ELSE 0 END) AS fp
            FROM alerts a
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            LEFT JOIN regime_snapshot_labels rsl ON rsl.snapshot_id = s.snapshot_id
            LEFT JOIN regime_state rs ON rs.regime_date = CAST(s.ts AS DATE)
            LEFT JOIN alert_outcomes ao
              ON ao.alert_id = a.alert_id AND ao.horizon_days = ?
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND pr.code_version LIKE ?
            GROUP BY 1
            ORDER BY 1
            """,
            (horizon_days, underlying, start_ts, end_ts, f"{lineage_prefix}%"),
        ).fetchall()
    finally:
        conn.close()

    out: dict[str, dict[str, float | int | None]] = {}
    for regime_label, alerts, tp, fp in rows:
        tp_count = int(tp or 0)
        fp_count = int(fp or 0)
        precision = (tp_count / (tp_count + fp_count)) if (tp_count + fp_count) > 0 else None
        out[str(regime_label)] = {
            "alerts": int(alerts),
            "tp": tp_count,
            "fp": fp_count,
            "precision": precision,
        }
    return out


def _regime_gate(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    baseline_lineage: str,
    candidate_lineage: str,
    horizon_days: int,
) -> dict[str, Any]:
    baseline = _fetch_precision_metrics(
        underlying,
        start_ts,
        end_ts,
        baseline_lineage,
        horizon_days,
    )
    candidate = _fetch_precision_metrics(
        underlying,
        start_ts,
        end_ts,
        candidate_lineage,
        horizon_days,
    )
    baseline_precision = baseline.get("precision")
    candidate_precision = candidate.get("precision")
    precision_non_regression = (
        baseline_precision is not None
        and candidate_precision is not None
        and float(candidate_precision) >= float(baseline_precision)
    )
    transition_blocked_reason = None
    transition_ok = False
    if (
        baseline.get("transition_fp_density") is not None
        and candidate.get("transition_fp_density") is not None
    ):
        transition_ok = float(candidate["transition_fp_density"]) <= float(baseline["transition_fp_density"])
    else:
        transition_blocked_reason = "missing_transition_alerts"

    baseline_by_regime = _regime_stratified_summary(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        lineage_prefix=baseline_lineage,
        horizon_days=horizon_days,
    )
    candidate_by_regime = _regime_stratified_summary(
        underlying=underlying,
        start_ts=start_ts,
        end_ts=end_ts,
        lineage_prefix=candidate_lineage,
        horizon_days=horizon_days,
    )
    required_regimes = ["Calm", "Transition", "Stress"]
    observed_regimes = sorted(candidate_by_regime.keys())
    missing_regimes = [name for name in required_regimes if name not in candidate_by_regime]
    regime_coverage_pass = len(missing_regimes) == 0
    unknown_regime_count = int(candidate_by_regime.get("Unknown", {}).get("alerts", 0))
    candidate_alert_count = int(sum(item.get("alerts", 0) for item in candidate_by_regime.values()))
    unknown_regime_share = (
        (unknown_regime_count / candidate_alert_count) if candidate_alert_count > 0 else None
    )
    unknown_regime_pass = unknown_regime_count == 0

    min_required_outcomes = 5
    per_regime_outcome_counts: dict[str, int] = {}
    per_regime_validity: dict[str, bool] = {}
    for regime_name in required_regimes:
        row = candidate_by_regime.get(regime_name, {})
        tp_count = int(row.get("tp", 0))
        fp_count = int(row.get("fp", 0))
        outcomes = tp_count + fp_count
        per_regime_outcome_counts[regime_name] = outcomes
        per_regime_validity[regime_name] = outcomes >= min_required_outcomes
    outcome_validity_pass = all(per_regime_validity.values())

    transition_metric_available = (
        baseline.get("transition_fp_density") is not None
        and candidate.get("transition_fp_density") is not None
    )
    evidence_valid = (
        regime_coverage_pass
        and unknown_regime_pass
        and outcome_validity_pass
        and transition_metric_available
        and candidate_alert_count > 0
    )

    incremental_edge_confirmed = bool(
        evidence_valid and precision_non_regression and candidate_precision is not None and baseline_precision is not None
        and float(candidate_precision) > float(baseline_precision)
        and transition_ok
    )
    no_incremental_edge_observed = bool(
        evidence_valid and not incremental_edge_confirmed
    )

    if not evidence_valid:
        verdict = "invalid_evidence"
    elif incremental_edge_confirmed:
        verdict = "incremental_edge_confirmed"
    else:
        verdict = "no_incremental_edge_observed"

    pass_value = verdict == "incremental_edge_confirmed"

    blocked_reasons: list[str] = []
    if not regime_coverage_pass:
        blocked_reasons.append("missing_required_regimes")
    if not precision_non_regression:
        blocked_reasons.append("precision_regression_or_missing")
    if not transition_ok:
        blocked_reasons.append(transition_blocked_reason or "transition_fp_density_worsened")
    if not unknown_regime_pass:
        blocked_reasons.append("unknown_regime_labels_present")
    if not outcome_validity_pass:
        blocked_reasons.append("insufficient_per_regime_outcomes")

    if not transition_metric_available:
        blocked_reasons.append("missing_transition_fp_density")

    if candidate_alert_count == 0:
        blocked_reasons.append("no_candidate_alerts")

    return {
        "horizon_days": horizon_days,
        "baseline": baseline,
        "candidate": candidate,
        "baseline_by_regime": baseline_by_regime,
        "candidate_by_regime": candidate_by_regime,
        "required_regimes": required_regimes,
        "observed_regimes": observed_regimes,
        "missing_regimes": missing_regimes,
        "regime_coverage_pass": regime_coverage_pass,
        "unknown_regime_count": unknown_regime_count,
        "unknown_regime_share": unknown_regime_share,
        "candidate_alert_count": candidate_alert_count,
        "unknown_regime_pass": unknown_regime_pass,
        "min_required_outcomes_per_regime": min_required_outcomes,
        "per_regime_outcome_counts": per_regime_outcome_counts,
        "per_regime_outcome_validity": per_regime_validity,
        "outcome_validity_pass": outcome_validity_pass,
        "precision_non_regression": precision_non_regression,
        "transition_fp_density_non_worsening": transition_ok,
        "transition_fp_density_blocked_reason": transition_blocked_reason,
        "transition_metric_available": transition_metric_available,
        "evidence_valid": evidence_valid,
        "taxonomy_verdict": verdict,
        "blocked_reasons": blocked_reasons,
        "pass": pass_value,
    }


def _threshold_freeze_gate(
    *,
    expected_config_path: str,
    baseline_meta: dict[str, Any],
    candidate_meta: dict[str, Any],
) -> dict[str, Any]:
    cfg = load_config(path=Path(expected_config_path))
    current_hash = regime_threshold_hash(regime_params_from_config(cfg))
    baseline_hash = baseline_meta.get("config_hash")
    candidate_hash = candidate_meta.get("config_hash")
    baseline_aligned = bool(baseline_hash)
    candidate_aligned = bool(candidate_hash)
    frozen = baseline_aligned and candidate_aligned and baseline_hash != candidate_hash
    blocked_reasons: list[str] = []
    if not baseline_aligned:
        blocked_reasons.append("baseline_config_hash_missing")
    if not candidate_aligned:
        blocked_reasons.append("candidate_config_hash_missing")
    if baseline_hash and candidate_hash and baseline_hash == candidate_hash:
        blocked_reasons.append("baseline_candidate_config_hash_identical")

    return {
        "current_config_hash": current_hash,
        "baseline_config_hash": baseline_hash,
        "candidate_config_hash": candidate_hash,
        "threshold_freeze_pass": frozen,
        "blocked_reasons": blocked_reasons,
    }


def _independence_diagnostics(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    lineage_prefix: str,
) -> dict[str, Any]:
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT rs.decomposition
            FROM regime_snapshot_labels rsl
            JOIN snapshots s ON s.snapshot_id = rsl.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            LEFT JOIN regime_state rs ON rs.regime_date = rsl.regime_date
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND pr.code_version LIKE ?
            """,
            (underlying, start_ts, end_ts, f"{lineage_prefix}%"),
        ).fetchall()
    finally:
        conn.close()

    contributions_sum: dict[str, float] = {
        "vix": 0.0,
        "rv20": 0.0,
        "drawdown": 0.0,
        "event": 0.0,
        "stress_proxy": 0.0,
    }
    vix_values: list[float] = []
    rv20_values: list[float] = []
    stress_proxy_values: list[float] = []

    for (decomposition_json,) in rows:
        if not decomposition_json:
            continue
        try:
            payload = json.loads(decomposition_json)
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        contrib = payload.get("contributions") if isinstance(payload.get("contributions"), dict) else {}
        for key in contributions_sum:
            value = contrib.get(key)
            if isinstance(value, (int, float)):
                contributions_sum[key] += abs(float(value))

        features = payload.get("features") if isinstance(payload.get("features"), dict) else {}
        vix_pct = features.get("vix_percentile")
        rv20_pct = features.get("rv20_percentile")
        stress_pct = features.get("stress_proxy_percentile")
        if isinstance(vix_pct, (int, float)) and isinstance(rv20_pct, (int, float)) and isinstance(stress_pct, (int, float)):
            vix_values.append(float(vix_pct))
            rv20_values.append(float(rv20_pct))
            stress_proxy_values.append(float(stress_pct))

    total_contrib = sum(contributions_sum.values())
    contribution_shares = {
        key: (value / total_contrib if total_contrib > 0 else 0.0)
        for key, value in contributions_sum.items()
    }

    def _corr(xs: list[float], ys: list[float]) -> float | None:
        if len(xs) < 3 or len(ys) < 3:
            return None
        x_mean = sum(xs) / len(xs)
        y_mean = sum(ys) / len(ys)
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        den_x = sum((x - x_mean) ** 2 for x in xs)
        den_y = sum((y - y_mean) ** 2 for y in ys)
        denom = (den_x * den_y) ** 0.5
        if denom == 0.0:
            return None
        return num / denom

    corr_stress_vix = _corr(stress_proxy_values, vix_values)
    corr_stress_rv20 = _corr(stress_proxy_values, rv20_values)
    independence_warning = bool(
        (corr_stress_vix is not None and abs(corr_stress_vix) >= 0.95)
        or (corr_stress_rv20 is not None and abs(corr_stress_rv20) >= 0.95)
    )

    return {
        "samples": len(vix_values),
        "contribution_shares": contribution_shares,
        "correlation_stress_vs_vix": corr_stress_vix,
        "correlation_stress_vs_rv20": corr_stress_rv20,
        "near_redundant_feature_warning": independence_warning,
    }


def _event_governance_gate(config_path: str) -> dict[str, Any]:
    cfg = load_config(path=Path(config_path))
    regime_cfg = cfg.get("regime", {}) if isinstance(cfg, dict) else {}
    event_path = str(regime_cfg.get("event_path", "config/regime_events_v1.yaml"))
    event_file = Path(event_path)
    blocked_reasons: list[str] = []
    if not event_file.exists():
        blocked_reasons.append("event_calendar_missing")
        return {
            "event_path": event_path,
            "event_calendar_exists": False,
            "effective_date_immutability_pass": False,
            "blocked_reasons": blocked_reasons,
        }
    try:
        payload = json.loads(json.dumps(load_config(path=Path(config_path))))
        _ = payload
        text = event_file.read_text(encoding="utf-8")
        governance_pass = "date:" in text and "severity:" in text
        if not governance_pass:
            blocked_reasons.append("event_calendar_missing_required_fields")
    except Exception:
        governance_pass = False
        blocked_reasons.append("event_calendar_unreadable")
    return {
        "event_path": event_path,
        "event_calendar_exists": True,
        "effective_date_immutability_pass": governance_pass,
        "blocked_reasons": blocked_reasons,
    }


def _ablation_gate(
    *,
    underlying: str,
    start_ts: str,
    end_ts: str,
    candidate_lineage: str,
    config_path: str,
) -> dict[str, Any]:
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT ti.scenarios
            FROM trade_ideas ti
            JOIN alerts a ON a.alert_id = ti.alert_id
            JOIN snapshots s ON s.snapshot_id = a.snapshot_id
            JOIN pipeline_runs pr ON pr.run_id = s.run_id
            WHERE s.underlying = ?
              AND s.ts >= ?
              AND s.ts <= ?
              AND pr.code_version LIKE ?
            """,
            (underlying, start_ts, end_ts, f"{candidate_lineage}%"),
        ).fetchall()
    finally:
        conn.close()

    edge_values: list[float] = []
    cost_values: list[float] = []
    for (scenarios_json,) in rows:
        if not scenarios_json:
            continue
        try:
            payload = json.loads(scenarios_json)
        except Exception:
            continue
        ranking = payload.get("ranking") if isinstance(payload, dict) else None
        if not isinstance(ranking, dict):
            continue
        edge = ranking.get("edge_after_cost")
        cost = ranking.get("total_friction_cost")
        if isinstance(edge, (int, float)):
            edge_values.append(float(edge))
        if isinstance(cost, (int, float)):
            cost_values.append(float(cost))

    mean_edge = statistics.mean(edge_values) if edge_values else None
    mean_cost = statistics.mean(cost_values) if cost_values else None

    cfg = load_config(path=Path(config_path))
    regime_weights = cfg.get("regime", {}).get("weights", {}) if isinstance(cfg, dict) else {}
    components = []
    for component_name in ["vix", "rv20", "drawdown", "event", "stress_proxy"]:
        weight = float(regime_weights.get(component_name, 0.0))
        components.append(
            {
                "component": component_name,
                "weight": weight,
                "status": "retained" if weight > 0.0 else "ablated",
            }
        )

    return {
        "ideas_with_ranking": len(edge_values),
        "mean_edge_after_cost": mean_edge,
        "mean_total_friction_cost": mean_cost,
        "component_ledger": components,
        "pass": len(edge_values) > 0,
    }


def _build_payload(
    *,
    contract_id: str,
    config_path: str,
    underlying: str,
    start_ts: str,
    end_ts: str,
    baseline_lineage: str,
    candidate_lineage: str,
    train_size: int,
    test_size: int,
    step_size: int,
    horizon_days: int,
) -> dict[str, Any]:
    lineage_metadata = {
        "baseline": _lineage_meta(underlying, start_ts, end_ts, baseline_lineage),
        "candidate": _lineage_meta(underlying, start_ts, end_ts, candidate_lineage),
    }
    warmup_window = _resolve_effective_start_ts(
        requested_start_ts=start_ts,
        end_ts=end_ts,
        baseline_meta=lineage_metadata["baseline"],
        candidate_meta=lineage_metadata["candidate"],
        config_path=config_path,
    )
    effective_start_ts = str(warmup_window["effective_start_ts"])

    walk_forward = _walk_forward_gate(
        underlying=underlying,
        start_ts=effective_start_ts,
        end_ts=end_ts,
        candidate_lineage=candidate_lineage,
        train_size=train_size,
        test_size=test_size,
        step_size=step_size,
    )
    adversarial = _adversarial_gate()
    regime = _regime_gate(
        underlying=underlying,
        start_ts=effective_start_ts,
        end_ts=end_ts,
        baseline_lineage=baseline_lineage,
        candidate_lineage=candidate_lineage,
        horizon_days=horizon_days,
    )
    ablation = _ablation_gate(
        underlying=underlying,
        start_ts=effective_start_ts,
        end_ts=end_ts,
        candidate_lineage=candidate_lineage,
        config_path=config_path,
    )
    freeze = _threshold_freeze_gate(
        expected_config_path=config_path,
        baseline_meta=lineage_metadata["baseline"],
        candidate_meta=lineage_metadata["candidate"],
    )
    independence = {
        "baseline": _independence_diagnostics(
            underlying=underlying,
            start_ts=effective_start_ts,
            end_ts=end_ts,
            lineage_prefix=baseline_lineage,
        ),
        "candidate": _independence_diagnostics(
            underlying=underlying,
            start_ts=effective_start_ts,
            end_ts=end_ts,
            lineage_prefix=candidate_lineage,
        ),
    }
    event_governance = _event_governance_gate(config_path)

    gates = {
        "walk_forward_pass": walk_forward["pass"],
        "adversarial_resilience_pass": adversarial["pass"],
        "regime_falsification_pass": regime["pass"],
        "ablation_ledger_pass": ablation["pass"],
        "threshold_freeze_pass": freeze["threshold_freeze_pass"],
        "event_governance_pass": event_governance["effective_date_immutability_pass"],
    }
    overall_pass = all(gates.values())
    gates["overall_pass"] = overall_pass

    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "contract": {
            "id": contract_id,
            "config_path": config_path,
            "underlying": underlying,
            "start_ts": start_ts,
            "effective_start_ts": effective_start_ts,
            "end_ts": end_ts,
            "baseline_lineage": baseline_lineage,
            "candidate_lineage": candidate_lineage,
            "walk_forward": {
                "train_size": train_size,
                "test_size": test_size,
                "step_size": step_size,
            },
            "horizon_days": horizon_days,
        },
        "window": {
            "underlying": underlying,
            "requested_start_ts": start_ts,
            "effective_start_ts": effective_start_ts,
            "end_ts": end_ts,
            "warmup_excluded_days": warmup_window["warmup_excluded_days"],
            "warmup_exclusion_applied": warmup_window["warmup_exclusion_applied"],
            "regime_ready_dates": warmup_window["regime_ready_dates"],
        },
        "lineage_metadata": lineage_metadata,
        "walk_forward": walk_forward,
        "adversarial": adversarial,
        "regime_falsification": regime,
        "ablation_ledger": ablation,
        "threshold_freeze": freeze,
        "independence_diagnostics": independence,
        "event_governance": event_governance,
        "taxonomy_verdict": regime.get("taxonomy_verdict", "invalid_evidence"),
        "gates": gates,
        "recommendation": "promotable" if overall_pass else "not_promotable",
    }


def _is_missing_lineage(payload: dict[str, Any]) -> bool:
    baseline_run = payload["lineage_metadata"]["baseline"].get("run_id")
    candidate_run = payload["lineage_metadata"]["candidate"].get("run_id")
    return baseline_run is None or candidate_run is None


def _render_markdown(payload: dict[str, Any], command: str) -> str:
    gates = payload["gates"]
    lines = [
        "# OptionTrader Sprint 7 Release Validation Report",
        "",
        f"Generated at: {payload['generated_at']}",
        "Source script: `scripts/validate_release.py`",
        "",
        "## Contract",
        "",
        f"- Contract ID: `{payload['contract']['id']}`",
        f"- Config path: `{payload['contract']['config_path']}`",
        f"- Underlying: `{payload['contract']['underlying']}`",
        f"- Start: `{payload['contract']['start_ts']}`",
        f"- Effective start (post warm-up): `{payload['contract']['effective_start_ts']}`",
        f"- End: `{payload['contract']['end_ts']}`",
        f"- Baseline lineage: `{payload['contract']['baseline_lineage']}`",
        f"- Candidate lineage: `{payload['contract']['candidate_lineage']}`",
        "",
        "## Gate Evaluation",
        "",
        f"- Walk-forward deterministic gate: {'PASS' if gates['walk_forward_pass'] else 'FAIL'}",
        (
            "- Adversarial resilience gate: "
            f"{'PASS' if gates['adversarial_resilience_pass'] else 'FAIL'}"
        ),
        (
            "- Regime falsification gate: "
            f"{'PASS' if gates['regime_falsification_pass'] else 'FAIL'}"
        ),
        f"- Ablation ledger gate: {'PASS' if gates['ablation_ledger_pass'] else 'FAIL'}",
        f"- Overall release gate: {'PASS' if gates['overall_pass'] else 'FAIL'}",
        "",
        "## Warm-up Exclusion",
        "",
        f"- Warm-up exclusion applied: `{payload['window']['warmup_exclusion_applied']}`",
        f"- Warm-up excluded days: `{payload['window']['warmup_excluded_days']}`",
        f"- Requested start: `{payload['window']['requested_start_ts']}`",
        f"- Effective start: `{payload['window']['effective_start_ts']}`",
        "",
        "## Recommendation",
        "",
        f"- Final recommendation: `{payload['recommendation']}`",
        f"- Taxonomy verdict: `{payload.get('taxonomy_verdict', 'invalid_evidence')}`",
        "",
        "## Summary Payload",
        "",
        "```json",
        json.dumps(payload, indent=2, sort_keys=True),
        "```",
        "",
        "## Reproducibility",
        "",
        "```bash",
        "source .venv/bin/activate",
        command,
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Sprint 7 release gates")
    parser.add_argument("--contract-id", default=DEFAULT_CONTRACT_ID)
    parser.add_argument("--config-path", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--start-ts", default=DEFAULT_START_TS)
    parser.add_argument("--end-ts", default=DEFAULT_END_TS)
    parser.add_argument("--underlying", default=DEFAULT_UNDERLYING)
    parser.add_argument("--baseline-lineage", default=DEFAULT_BASELINE_LINEAGE)
    parser.add_argument("--candidate-lineage", default=DEFAULT_CANDIDATE_LINEAGE)
    parser.add_argument("--train-size", type=int, default=252)
    parser.add_argument("--test-size", type=int, default=63)
    parser.add_argument("--step-size", type=int, default=63)
    parser.add_argument("--horizon-days", type=int, default=5)
    parser.add_argument("--report-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--payload-path", default=DEFAULT_JSON_OUTPUT_PATH)
    parser.add_argument("--baseline-capture-path", default=DEFAULT_BASELINE_CAPTURE_PATH)
    parser.add_argument("--skip-outcome-refresh", action="store_true")
    args = parser.parse_args()

    os.environ["OPTIONTRADER_CONFIG"] = args.config_path
    init_db()
    if not args.skip_outcome_refresh:
        evaluate_alert_outcomes(horizon_days=args.horizon_days, overwrite=False)

    payload = _build_payload(
        contract_id=args.contract_id,
        config_path=args.config_path,
        underlying=args.underlying,
        start_ts=args.start_ts,
        end_ts=args.end_ts,
        baseline_lineage=args.baseline_lineage,
        candidate_lineage=args.candidate_lineage,
        train_size=args.train_size,
        test_size=args.test_size,
        step_size=args.step_size,
        horizon_days=args.horizon_days,
    )
    command = (
        f"python scripts/validate_release.py --config-path {args.config_path} "
        f"--start-ts {args.start_ts} --end-ts {args.end_ts} "
        f"--underlying {args.underlying} --baseline-lineage {args.baseline_lineage} "
        f"--candidate-lineage {args.candidate_lineage} --train-size {args.train_size} "
        f"--test-size {args.test_size} --step-size {args.step_size} "
        f"--horizon-days {args.horizon_days}"
    )
    report_text = _render_markdown(payload, command)

    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text + "\n", encoding="utf-8")

    payload_path = Path(args.payload_path)
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    baseline_capture = {
        "captured_at": payload["generated_at"],
        "contract": payload["contract"],
        "lineage_metadata": {
            "baseline": payload["lineage_metadata"]["baseline"],
        },
        "walk_forward": payload["walk_forward"],
        "regime_falsification": {
            "baseline": payload["regime_falsification"]["baseline"],
            "baseline_by_regime": payload["regime_falsification"].get("baseline_by_regime", {}),
        },
    }
    baseline_capture_path = Path(args.baseline_capture_path)
    baseline_capture_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_capture_path.write_text(
        json.dumps(baseline_capture, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(payload, indent=2, sort_keys=True))
    print(f"report_written={report_path}")
    print(f"payload_written={payload_path}")
    print(f"baseline_capture_written={baseline_capture_path}")
    if _is_missing_lineage(payload):
        raise SystemExit(3)
    if payload["gates"]["overall_pass"]:
        raise SystemExit(0)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
