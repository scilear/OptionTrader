from __future__ import annotations

import math
from typing import Iterable

import pandas as pd


def compute_zscore(series: pd.Series) -> float | None:
    score = _compute_robust_score(series)
    if score is None:
        return None
    zscore, _, _, _ = score
    return zscore


def _compute_robust_score(series: pd.Series) -> tuple[float, float, float, str] | None:
    if series is None:
        return None
    clean = pd.Series(series).dropna()
    if clean.empty or len(clean) < 3:
        return None

    center = float(clean.median())
    mad = float((clean - center).abs().median())
    if mad > 0 and not math.isnan(mad):
        scale = 1.4826 * mad
        return (float((clean.iloc[-1] - center) / scale), center, scale, "mad")

    q75 = float(clean.quantile(0.75))
    q25 = float(clean.quantile(0.25))
    iqr = q75 - q25
    if iqr > 0 and not math.isnan(iqr):
        scale = iqr / 1.349
        return (float((clean.iloc[-1] - center) / scale), center, scale, "iqr")

    std = float(clean.std(ddof=1))
    if std > 0 and not math.isnan(std):
        mean = float(clean.mean())
        return (float((clean.iloc[-1] - mean) / std), mean, std, "std")

    return None


def _persistence_count(values: pd.Series, center: float, scale: float, threshold: float) -> int:
    if scale == 0 or math.isnan(scale):
        return 0
    zscores = (values - center) / scale
    count = 0
    for z in reversed(zscores.tolist()):
        if abs(z) >= threshold:
            count += 1
        else:
            break
    return count


def _apply_overlap_guardrails(candidates: list[dict]) -> list[dict]:
    if len(candidates) <= 1:
        if candidates:
            candidates[0]["effective_severity"] = abs(float(candidates[0]["zscore_mid"]))
            candidates[0]["evidence_overlap"] = {
                "detected": False,
                "candidate_count": 1,
                "suppressed_alert_types": [],
                "strategy": "none",
            }
        return candidates

    signs = {
        1 if float(candidate["zscore_mid"]) >= 0 else -1
        for candidate in candidates
    }
    if len(signs) > 1:
        for candidate in candidates:
            candidate["effective_severity"] = abs(float(candidate["zscore_mid"]))
            candidate["evidence_overlap"] = {
                "detected": False,
                "candidate_count": 1,
                "suppressed_alert_types": [],
                "strategy": "none",
            }
        return candidates

    ordered = sorted(
        candidates,
        key=lambda item: (abs(float(item["zscore_mid"])), item["alert_type"]),
        reverse=True,
    )
    winner = ordered[0]
    suppressed = [item["alert_type"] for item in ordered[1:]]
    overlap_penalty = 1.0 / float(len(ordered))
    winner["effective_severity"] = abs(float(winner["zscore_mid"])) * overlap_penalty
    winner["evidence_overlap"] = {
        "detected": True,
        "candidate_count": len(ordered),
        "suppressed_alert_types": suppressed,
        "strategy": "dominant_only",
        "dominant_alert_type": winner["alert_type"],
        "overlap_penalty": overlap_penalty,
    }
    return [winner]


def compute_alerts(
    metrics_df: pd.DataFrame,
    window: int,
    threshold: float,
    persistence_required: int,
    pessimistic_gate: bool = True,
) -> list[dict]:
    alerts = []
    if metrics_df.empty:
        return alerts

    for bucket, df in metrics_df.groupby("expiry_bucket"):
        df = df.sort_values("ts")
        recent = df.tail(window)
        candidates: list[dict] = []
        for metric, metric_worst, alert_type in [
            ("rr25_mid", "rr25_worst", "RR_EXTREME"),
            ("fly25_mid", "fly25_worst", "FLY_EXTREME"),
            ("term_slope_mid", "term_slope_worst", "TERM_KINK"),
        ]:
            if metric not in recent.columns:
                continue
            series = recent[metric].dropna()
            score = _compute_robust_score(series)
            if score is None:
                continue
            z, center, scale, method_mid = score
            if abs(z) < threshold:
                continue

            persistence_window = max(int(persistence_required), 1)
            persistence = _persistence_count(
                series.tail(persistence_window),
                center,
                scale,
                threshold,
            )
            if persistence < persistence_required:
                continue

            z_worst = z
            method_worst = method_mid
            if metric_worst in recent.columns:
                worst_series = recent[metric_worst].dropna()
                worst_score = _compute_robust_score(worst_series)
                if worst_score is not None:
                    z_worst, _, _, method_worst = worst_score
            if pessimistic_gate and abs(z_worst) < threshold:
                continue

            candidates.append(
                {
                    "expiry_bucket": bucket,
                    "alert_type": alert_type,
                    "metric": metric,
                    "zscore_mid": z,
                    "zscore_worst": z_worst,
                    "persistence": persistence,
                    "score_method_mid": method_mid,
                    "score_method_worst": method_worst,
                }
            )

        alerts.extend(_apply_overlap_guardrails(candidates))

    return alerts
