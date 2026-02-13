from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class EventStats:
    events: int
    hit_rate: float
    median_reversion_days: float | None


def compute_event_study(
    series: pd.DataFrame,
    metric: str,
    threshold: float,
    max_days: int = 10,
) -> EventStats:
    if series.empty or metric not in series.columns:
        return EventStats(events=0, hit_rate=0.0, median_reversion_days=None)

    df = series.sort_values("ts").dropna(subset=[metric]).reset_index(drop=True)
    if df.empty:
        return EventStats(events=0, hit_rate=0.0, median_reversion_days=None)

    mean = df[metric].rolling(window=60, min_periods=20).mean()
    std = df[metric].rolling(window=60, min_periods=20).std(ddof=1)
    z = (df[metric] - mean) / std

    events = []
    for idx, zval in z.items():
        if pd.isna(zval):
            continue
        if abs(zval) >= threshold:
            events.append(idx)

    if not events:
        return EventStats(events=0, hit_rate=0.0, median_reversion_days=None)

    reversion_days = []
    hits = 0
    for idx in events:
        start_z = z.iloc[idx]
        if pd.isna(start_z):
            continue
        target = 1.0 if start_z > 0 else -1.0
        end_idx = min(idx + max_days, len(df) - 1)
        reverted = False
        for j in range(idx + 1, end_idx + 1):
            if (start_z > 0 and z.iloc[j] <= target) or (start_z < 0 and z.iloc[j] >= target):
                reversion_days.append(j - idx)
                reverted = True
                break
        if reverted:
            hits += 1

    hit_rate = hits / len(events) if events else 0.0
    median_days = float(pd.Series(reversion_days).median()) if reversion_days else None
    return EventStats(events=len(events), hit_rate=hit_rate, median_reversion_days=median_days)
