from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class SurfaceQcResult:
    passed: bool
    quality_score: float
    reason_codes: tuple[str, ...]


def _safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _check_vertical(metric: dict, epsilon: float) -> list[str]:
    reasons: list[str] = []
    rr25 = _safe_float(metric.get("rr25_mid"))
    rr10 = _safe_float(metric.get("rr10_mid"))
    fly25 = _safe_float(metric.get("fly25_mid"))
    fly10 = _safe_float(metric.get("fly10_mid"))

    if rr25 is not None and rr10 is not None and abs(rr10) + epsilon < abs(rr25):
        reasons.append("vertical_rr_magnitude_inversion")
    if fly25 is not None and fly25 < -epsilon:
        reasons.append("vertical_negative_fly25")
    if fly10 is not None and fly10 < -epsilon:
        reasons.append("vertical_negative_fly10")
    return reasons


def _check_calendar(metrics: list[dict], variance_epsilon: float) -> list[str]:
    reasons: list[str] = []
    sorted_metrics = sorted(
        metrics,
        key=lambda m: int(str(m.get("expiry_bucket", "0D")).replace("D", "") or 0),
    )
    for idx in range(len(sorted_metrics) - 1):
        near = sorted_metrics[idx]
        far = sorted_metrics[idx + 1]
        near_days = int(str(near.get("expiry_bucket", "0D")).replace("D", "") or 0)
        far_days = int(str(far.get("expiry_bucket", "0D")).replace("D", "") or 0)
        if near_days <= 0 or far_days <= 0 or far_days <= near_days:
            continue
        near_atm = _safe_float(near.get("atm_iv_mid"))
        far_atm = _safe_float(far.get("atm_iv_mid"))
        if near_atm is None or far_atm is None:
            continue
        near_total_var = (near_atm**2) * (near_days / 365.0)
        far_total_var = (far_atm**2) * (far_days / 365.0)
        if far_total_var + variance_epsilon < near_total_var:
            reasons.append(
                "calendar_total_variance_violation:"
                f"{near.get('expiry_bucket')}->{far.get('expiry_bucket')}"
            )
    return reasons


def evaluate_surface_qc(
    metrics: Iterable[dict],
    iv_points: Iterable,
    no_arb_epsilon: float | None = None,
    iv_epsilon: float | None = None,
    var_epsilon: float | None = None,
) -> SurfaceQcResult:
    base_epsilon = float(no_arb_epsilon or 0.0)
    iv_epsilon_value = base_epsilon if iv_epsilon is None else float(iv_epsilon)
    var_epsilon_value = base_epsilon if var_epsilon is None else float(var_epsilon)

    metrics_list = list(metrics)
    iv_points_list = list(iv_points)
    reason_codes: list[str] = []

    for metric in metrics_list:
        reason_codes.extend(_check_vertical(metric, iv_epsilon_value))

    reason_codes.extend(_check_calendar(metrics_list, var_epsilon_value))

    degraded_points = [p for p in iv_points_list if str(getattr(p, "solve_status", "")) == "degraded"]
    if degraded_points:
        reason_codes.append("degraded_surface_fit")

    unique_reasons = tuple(sorted(set(reason_codes)))
    if not metrics_list:
        return SurfaceQcResult(passed=False, quality_score=0.0, reason_codes=("empty_surface_metrics",))

    quality_values = [
        float(getattr(p, "fit_confidence", 0.0) or 0.0)
        for p in iv_points_list
        if getattr(p, "iv_mid", None) is not None
    ]
    quality_score = sum(quality_values) / len(quality_values) if quality_values else 0.0
    passed = len(unique_reasons) == 0
    return SurfaceQcResult(passed=passed, quality_score=quality_score, reason_codes=unique_reasons)
