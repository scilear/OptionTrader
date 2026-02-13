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


def compute_event_study_by_regime(
    series: pd.DataFrame,
    metric: str,
    threshold: float,
    regime_df: pd.DataFrame,
    max_days: int = 10,
) -> pd.DataFrame:
    if series.empty or metric not in series.columns:
        return pd.DataFrame()

    df = series.sort_values("ts").dropna(subset=[metric]).reset_index(drop=True)
    if df.empty:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["ts"]).dt.date
    if not regime_df.empty:
        regime_df = regime_df.copy()
        regime_df["date"] = pd.to_datetime(regime_df["regime_date"]).dt.date
        df = df.merge(regime_df[["date", "regime_label"]], on="date", how="left")
    else:
        df["regime_label"] = "Unknown"

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
        return pd.DataFrame()

    stats = {}
    for idx in events:
        start_z = z.iloc[idx]
        if pd.isna(start_z):
            continue
        regime = df.loc[idx, "regime_label"] or "Unknown"
        end_idx = min(idx + max_days, len(df) - 1)
        window = z.iloc[idx + 1 : end_idx + 1]

        if start_z > 0:
            adverse = (window.max() - start_z) if not window.empty else 0.0
            favorable = (start_z - window.min()) if not window.empty else 0.0
        else:
            adverse = (start_z - window.min()) if not window.empty else 0.0
            favorable = (window.max() - start_z) if not window.empty else 0.0

        reverted_days = None
        for j in range(idx + 1, end_idx + 1):
            if (start_z > 0 and z.iloc[j] <= 1.0) or (start_z < 0 and z.iloc[j] >= -1.0):
                reverted_days = j - idx
                break

        stats.setdefault(regime, {"events": 0, "hits": 0, "days": [], "mae": [], "mfe": []})
        stats[regime]["events"] += 1
        stats[regime]["mae"].append(adverse)
        stats[regime]["mfe"].append(favorable)
        if reverted_days is not None:
            stats[regime]["hits"] += 1
            stats[regime]["days"].append(reverted_days)

    rows = []
    for regime, values in stats.items():
        events_count = values["events"]
        hit_rate = values["hits"] / events_count if events_count else 0.0
        median_days = float(pd.Series(values["days"]).median()) if values["days"] else None
        median_mae = float(pd.Series(values["mae"]).median()) if values["mae"] else None
        median_mfe = float(pd.Series(values["mfe"]).median()) if values["mfe"] else None
        rows.append(
            {
                "regime_label": regime,
                "events": events_count,
                "hit_rate": hit_rate,
                "median_reversion_days": median_days,
                "median_mae": median_mae,
                "median_mfe": median_mfe,
            }
        )

    return pd.DataFrame(rows)
