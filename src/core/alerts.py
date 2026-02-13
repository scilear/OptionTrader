from __future__ import annotations

import math
from typing import Iterable

import pandas as pd


def compute_zscore(series: pd.Series) -> float | None:
    if series is None or series.empty:
        return None
    mean = series.mean()
    std = series.std(ddof=1)
    if std == 0 or math.isnan(std):
        return None
    return (series.iloc[-1] - mean) / std


def _persistence_count(values: pd.Series, mean: float, std: float, threshold: float) -> int:
    if std == 0 or math.isnan(std):
        return 0
    zscores = (values - mean) / std
    count = 0
    for z in reversed(zscores.tolist()):
        if abs(z) >= threshold:
            count += 1
        else:
            break
    return count


def compute_alerts(
    metrics_df: pd.DataFrame,
    window: int,
    threshold: float,
    persistence_required: int,
) -> list[dict]:
    alerts = []
    if metrics_df.empty:
        return alerts

    for bucket, df in metrics_df.groupby("expiry_bucket"):
        df = df.sort_values("ts")
        recent = df.tail(window)
        for metric, metric_worst, alert_type in [
            ("rr25_mid", "rr25_worst", "RR_EXTREME"),
            ("fly25_mid", "fly25_worst", "FLY_EXTREME"),
            ("term_slope_mid", "term_slope_worst", "TERM_KINK"),
        ]:
            if metric not in recent.columns:
                continue
            series = recent[metric].dropna()
            if series.empty:
                continue
            mean = series.mean()
            std = series.std(ddof=1)
            if std == 0 or math.isnan(std):
                continue
            z = (series.iloc[-1] - mean) / std
            if abs(z) < threshold:
                continue

            persistence = _persistence_count(series.tail(persistence_required), mean, std, threshold)
            if persistence < persistence_required:
                continue

            z_worst = None
            if metric_worst in recent.columns:
                worst_series = recent[metric_worst].dropna()
                if not worst_series.empty:
                    z_worst = (worst_series.iloc[-1] - worst_series.mean()) / worst_series.std(ddof=1)
                    if z_worst is not None and abs(z_worst) < threshold:
                        continue

            alerts.append(
                {
                    "expiry_bucket": bucket,
                    "alert_type": alert_type,
                    "zscore_mid": z,
                    "zscore_worst": z_worst if z_worst is not None else z,
                    "persistence": persistence,
                }
            )

    return alerts
