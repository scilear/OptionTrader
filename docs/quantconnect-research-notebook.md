# SPX Surface Signal Lab in QuantConnect Research

This file is structured so each section maps to one notebook cell you can copy/paste directly into a QuantConnect Python research notebook.

The workflow is intentionally hybrid:

1. use daily `OptionUniverse` history for fast signal discovery
2. use minute `OptionHistory` only on candidate dates for quote-level validation

That is materially faster than a full backtest and more precise than relying only on daily precomputed fields.

## Cell 1 - Imports and Notebook Setup

```python
from datetime import datetime, timedelta, time
from collections import defaultdict, deque
from dataclasses import dataclass
import math
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

qb = QuantBook()
pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 220)
```

## Cell 2 - Research Parameters

```python
UNDERLYING = "SPX"
OPTION_TICKER = "SPXW"

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

DTE_MIN = 14
DTE_MAX = 60
EXPIRY_BUCKETS = [21, 30, 45]

Z_THRESHOLD = 2.0
PERSISTENCE_REQUIRED = 2
SPREAD_GATE_PCT = 0.15
MIN_OPEN_INTEREST = 100

TARGET_SNAPSHOT_TIMES = [
    time(10, 0),
    time(13, 0),
    time(15, 30),
]

VALIDATION_WINDOW_MINUTES = 1
DAILY_CHUNK_MONTHS = 1
MAX_CANDIDATE_DAYS = 5
ALERT_FILTER = "ALL"   # ALL, RR_EXTREME, FLY_EXTREME, TERM_KINK
BUCKET_FILTER = "ALL"  # ALL, 21D, 30D, 45D
```

## Cell 3 - Add SPX and SPXW Subscriptions

```python
index_symbol = qb.add_index(UNDERLYING, Resolution.MINUTE).symbol
option = qb.add_index_option(index_symbol, OPTION_TICKER)
option.set_filter(-120, 120, DTE_MIN, DTE_MAX)

print(index_symbol)
print(option.symbol)
```

## Cell 4 - Helper Functions

```python
@dataclass
class IvPoint:
    expiry: datetime.date
    delta_bucket: str
    iv_mid: float | None
    iv_bid: float | None
    iv_ask: float | None
    quality_score: float


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_price(spot, strike, rate, div, t_years, vol, right):
    if t_years <= 0 or vol <= 0:
        intrinsic = max(0.0, spot - strike) if right == "C" else max(0.0, strike - spot)
        return intrinsic
    fwd = spot * math.exp((rate - div) * t_years)
    vol_sqrt = vol * math.sqrt(t_years)
    d1 = (math.log(fwd / strike) + 0.5 * vol * vol * t_years) / vol_sqrt
    d2 = d1 - vol_sqrt
    disc = math.exp(-rate * t_years)
    if right == "C":
        return disc * (fwd * norm_cdf(d1) - strike * norm_cdf(d2))
    return disc * (strike * norm_cdf(-d2) - fwd * norm_cdf(-d1))


def bs_delta(spot, strike, rate, div, t_years, vol, right):
    if t_years <= 0 or vol <= 0:
        return 0.0
    fwd = spot * math.exp((rate - div) * t_years)
    vol_sqrt = vol * math.sqrt(t_years)
    d1 = (math.log(fwd / strike) + 0.5 * vol * vol * t_years) / vol_sqrt
    if right == "C":
        return math.exp(-div * t_years) * norm_cdf(d1)
    return math.exp(-div * t_years) * (norm_cdf(d1) - 1.0)


def solve_iv(price, spot, strike, rate, div, t_years, right, vol_low=1e-4, vol_high=5.0, tol=1e-6, max_iter=100):
    if price <= 0 or t_years <= 0 or spot <= 0 or strike <= 0:
        return None
    intrinsic = max(0.0, spot - strike) if right == "C" else max(0.0, strike - spot)
    if price < intrinsic:
        return None
    low_price = bs_price(spot, strike, rate, div, t_years, vol_low, right)
    high_price = bs_price(spot, strike, rate, div, t_years, vol_high, right)
    if price < low_price or price > high_price:
        return None
    low = vol_low
    high = vol_high
    for _ in range(max_iter):
        mid = 0.5 * (low + high)
        mid_price = bs_price(spot, strike, rate, div, t_years, mid, right)
        if abs(mid_price - price) < tol:
            return mid
        if mid_price > price:
            high = mid
        else:
            low = mid
    return 0.5 * (low + high)


def forward_price(spot, rate, div, t_years):
    return spot * math.exp((rate - div) * t_years)


def bucket_days(dte, buckets):
    return min(buckets, key=lambda b: abs(dte - b))


def safe_underlying_price(value):
    if hasattr(value, "price"):
        return float(value.price)
    if isinstance(value, (int, float, np.floating)):
        return float(value)
    return np.nan


def days_to_expiry(expiry_value, ts_value):
    expiry_ts = pd.Timestamp(expiry_value)
    ts_ts = pd.Timestamp(ts_value)
    if pd.isna(expiry_ts) or pd.isna(ts_ts):
        return np.nan
    return (expiry_ts.date() - ts_ts.date()).days


def month_chunks(start_dt, end_dt, months=1):
    chunks = []
    cursor = pd.Timestamp(start_dt).normalize()
    end_ts = pd.Timestamp(end_dt).normalize()
    while cursor <= end_ts:
        chunk_end = min(cursor + pd.DateOffset(months=months) - pd.Timedelta(days=1), end_ts)
        chunks.append((cursor.to_pydatetime(), chunk_end.to_pydatetime()))
        cursor = chunk_end + pd.Timedelta(days=1)
    return chunks


def compute_persistence(series, threshold):
    if len(series) < PERSISTENCE_REQUIRED:
        return 0
    mean = series.mean()
    std = series.std(ddof=1)
    if pd.isna(std) or std == 0:
        return 0
    z = (series - mean) / std
    count = 0
    for value in reversed(z.tail(PERSISTENCE_REQUIRED).tolist()):
        if abs(value) >= threshold:
            count += 1
        else:
            break
    return count


def compute_zscore(series):
    if len(series) < 20:
        return np.nan
    mean = series.iloc[:-1].mean()
    std = series.iloc[:-1].std(ddof=1)
    if pd.isna(std) or std == 0:
        return np.nan
    return (series.iloc[-1] - mean) / std


def coarse_regime_label(atm_iv):
    if pd.isna(atm_iv):
        return "Unknown"
    if atm_iv >= 0.30:
        return "Stress"
    if atm_iv <= 0.18:
        return "Calm"
    return "Transition"


def pick_column(df, candidates, required=False):
    existing = {str(c).lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in existing:
            return existing[candidate.lower()]
    if required:
        raise KeyError(f"Missing required column. Tried: {candidates}")
    return None


def normalize_daily_history(history_df):
    df = history_df.copy()

    rows = []
    for idx, row in df.iterrows():
        ts = None
        symbol_obj = idx

        if isinstance(idx, tuple) and len(idx) >= 2:
            ts = pd.Timestamp(idx[0])
            symbol_obj = idx[-1]
        elif isinstance(df.index, pd.MultiIndex) and len(df.index.names) >= 2:
            ts = pd.Timestamp(idx[0])
            symbol_obj = idx[-1]

        sid = getattr(symbol_obj, "id", None)
        if sid is None:
            continue
        expiry = sid.date
        right_obj = sid.option_right
        strike = float(sid.strike_price)
        right = "C" if str(right_obj).upper().endswith("CALL") else "P"

        if ts is None:
            ts_value = row.get("time", row.get("endtime", None))
            if ts_value is None:
                continue
            ts = pd.Timestamp(ts_value)

        rows.append(
            {
                "ts": ts,
                "symbol": symbol_obj,
                "expiry": pd.Timestamp(expiry),
                "strike": strike,
                "right": right,
                "open_interest": float(row.get("openinterest", np.nan)),
                "iv": float(row.get("impliedvolatility", np.nan)),
                "delta": float(row.get("delta", np.nan)),
                "price": float(row.get("price", np.nan)),
                "underlying": safe_underlying_price(row.get("underlying", np.nan)),
            }
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    out["ts"] = pd.to_datetime(out["ts"], errors="coerce")
    out["expiry"] = pd.to_datetime(out["expiry"], errors="coerce")
    out = out.dropna(subset=["ts", "expiry"]).copy()

    if out.empty:
        raise ValueError(
            "Daily history normalization produced no valid rows after datetime coercion. "
            "Inspect `daily_history_raw.head()` and `daily_history_raw.index.names`."
        )

    out["dte"] = out.apply(lambda row: days_to_expiry(row["expiry"], row["ts"]), axis=1)
    out = out.dropna(subset=["dte"]).copy()
    out["dte"] = out["dte"].astype(int)
    out = out[(out["dte"] >= DTE_MIN) & (out["dte"] <= DTE_MAX)].copy()
    return out


def compute_surface_from_iv(df):
    if df.empty:
        return pd.DataFrame()

    records = []
    for ts, snap in df.groupby("ts"):
        spot = snap["underlying"].dropna().iloc[0] if snap["underlying"].notna().any() else np.nan
        if pd.isna(spot) or spot <= 0:
            continue

        candidates = {}
        for expiry, exp_df in snap.groupby("expiry"):
            dte = int((expiry.date() - ts.date()).days)
            if dte <= 0:
                continue

            atm = exp_df.iloc[(exp_df["strike"] - spot).abs().argsort()[:1]]
            if atm.empty:
                continue
            atm_iv = atm["iv"].iloc[0]

            call25 = exp_df[exp_df["right"] == "C"].copy()
            put25 = exp_df[exp_df["right"] == "P"].copy()
            if call25.empty or put25.empty:
                continue

            call25 = call25.iloc[(call25["delta"] - 0.25).abs().argsort()[:1]]
            put25 = put25.iloc[(put25["delta"] + 0.25).abs().argsort()[:1]]

            if call25.empty or put25.empty or pd.isna(atm_iv):
                continue

            c25_iv = call25["iv"].iloc[0]
            p25_iv = put25["iv"].iloc[0]
            bucket = bucket_days(dte, EXPIRY_BUCKETS)

            record = {
                "ts": ts,
                "expiry": expiry,
                "expiry_bucket": f"{bucket}D",
                "dte": dte,
                "atm_iv_mid": atm_iv,
                "rr25_mid": c25_iv - p25_iv,
                "fly25_mid": 0.5 * (c25_iv + p25_iv) - atm_iv,
                "open_interest_min": min(call25["open_interest"].iloc[0], put25["open_interest"].iloc[0]),
            }

            key = f"{bucket}D"
            dist = abs(dte - bucket)
            if key not in candidates or dist < candidates[key][0]:
                candidates[key] = (dist, record)

        bucket_rows = [record for _, record in candidates.values()]
        bucket_rows = sorted(bucket_rows, key=lambda x: int(x["expiry_bucket"].replace("D", "")))
        for i, row in enumerate(bucket_rows):
            next_row = bucket_rows[i + 1] if i + 1 < len(bucket_rows) else None
            row["term_slope_mid"] = row["atm_iv_mid"] - next_row["atm_iv_mid"] if next_row else np.nan
            row["regime_label"] = coarse_regime_label(row["atm_iv_mid"])
            records.append(row)

    return pd.DataFrame(records)


def compute_daily_alerts(surface_df):
    if surface_df.empty:
        return pd.DataFrame()

    surface_df = surface_df.sort_values(["expiry_bucket", "ts"]).copy()
    alerts = []
    for bucket, bucket_df in surface_df.groupby("expiry_bucket"):
        bucket_df = bucket_df.sort_values("ts").copy()
        for metric, alert_type in [
            ("rr25_mid", "RR_EXTREME"),
            ("fly25_mid", "FLY_EXTREME"),
            ("term_slope_mid", "TERM_KINK"),
        ]:
            bucket_df[f"{metric}_z"] = (
                bucket_df[metric]
                .rolling(61, min_periods=20)
                .apply(lambda s: compute_zscore(pd.Series(s)), raw=False)
            )

        for i in range(len(bucket_df)):
            row = bucket_df.iloc[i]
            for metric, alert_type in [
                ("rr25_mid", "RR_EXTREME"),
                ("fly25_mid", "FLY_EXTREME"),
                ("term_slope_mid", "TERM_KINK"),
            ]:
                if ALERT_FILTER != "ALL" and alert_type != ALERT_FILTER:
                    continue
                if BUCKET_FILTER != "ALL" and bucket != BUCKET_FILTER:
                    continue
                z_col = f"{metric}_z"
                history = bucket_df.loc[: bucket_df.index[i], metric].dropna()
                z_value = row[z_col]
                if pd.isna(z_value) or abs(z_value) < Z_THRESHOLD:
                    continue
                if compute_persistence(history, Z_THRESHOLD) < PERSISTENCE_REQUIRED:
                    continue
                if alert_type == "RR_EXTREME" and row["regime_label"] == "Stress":
                    continue

                alerts.append(
                    {
                        "ts": row["ts"],
                        "expiry_bucket": bucket,
                        "alert_type": alert_type,
                        "zscore_mid": z_value,
                        "atm_iv_mid": row["atm_iv_mid"],
                        "open_interest_min": row["open_interest_min"],
                        "regime_label": row["regime_label"],
                    }
                )
    return pd.DataFrame(alerts).sort_values("ts")


def normalize_minute_option_history(raw_df):
    df = raw_df.copy().reset_index()
    df.columns = [str(c).lower() for c in df.columns]

    time_col = pick_column(df, ["time", "endtime", "timestamp"], required=True)
    expiry_col = pick_column(df, ["expiry", "expiration"], required=False)
    strike_col = pick_column(df, ["strike", "strikeprice"], required=False)
    right_col = pick_column(df, ["right", "optionright"], required=False)
    bid_close_col = pick_column(df, ["bidclose", "bid_close", "closebid", "bidprice"])
    ask_close_col = pick_column(df, ["askclose", "ask_close", "closeask", "askprice"])
    oi_col = pick_column(df, ["openinterest", "open_interest"])
    underlying_col = pick_column(df, ["underlying"])

    if expiry_col is None or strike_col is None or right_col is None:
        raise KeyError(
            "Could not infer expiry/strike/right columns from OptionHistory. "
            f"Available columns: {list(df.columns)}"
        )

    out = pd.DataFrame(
        {
            "ts": pd.to_datetime(df[time_col]),
            "expiry": pd.to_datetime(df[expiry_col]),
            "strike": pd.to_numeric(df[strike_col], errors="coerce"),
            "right": df[right_col].astype(str).str.upper().str[0],
            "bid": pd.to_numeric(df[bid_close_col], errors="coerce") if bid_close_col else np.nan,
            "ask": pd.to_numeric(df[ask_close_col], errors="coerce") if ask_close_col else np.nan,
            "open_interest": pd.to_numeric(df[oi_col], errors="coerce") if oi_col else np.nan,
            "underlying": df[underlying_col].apply(safe_underlying_price) if underlying_col else np.nan,
        }
    )

    out = out.dropna(subset=["ts", "expiry", "strike"]).copy()
    out["dte"] = out.apply(lambda row: days_to_expiry(row["expiry"], row["ts"]), axis=1)
    out = out.dropna(subset=["dte"]).copy()
    out["dte"] = out["dte"].astype(int)
    out = out[(out["dte"] >= DTE_MIN) & (out["dte"] <= DTE_MAX)].copy()
    return out


def compute_intraday_snapshot_metrics(minute_df):
    if minute_df.empty:
        return pd.DataFrame()

    rate = 0.0
    div = 0.0
    rows = []

    for ts, snap in minute_df.groupby("ts"):
        spot_series = snap["underlying"].dropna()
        if spot_series.empty:
            continue
        spot = float(spot_series.iloc[0])
        if spot <= 0:
            continue

        by_expiry = defaultdict(list)
        for _, row in snap.iterrows():
            bid = row["bid"]
            ask = row["ask"]
            if pd.isna(bid) or pd.isna(ask) or bid < 0 or ask < 0 or bid > ask:
                continue
            if bid == 0 and ask == 0:
                continue
            by_expiry[row["expiry"].date()].append(row)

        candidates = {}
        for expiry, exp_rows in by_expiry.items():
            t_years = max((expiry - ts.date()).days, 0) / 365.0
            if t_years <= 0:
                continue

            enriched = []
            for row in exp_rows:
                mid = 0.5 * (row["bid"] + row["ask"]) if row["bid"] + row["ask"] > 0 else 0.0
                iv_mid = solve_iv(mid, spot, row["strike"], rate, div, t_years, row["right"]) if mid > 0 else None
                iv_bid = solve_iv(row["bid"], spot, row["strike"], rate, div, t_years, row["right"]) if row["bid"] > 0 else None
                iv_ask = solve_iv(row["ask"], spot, row["strike"], rate, div, t_years, row["right"]) if row["ask"] > 0 else None
                if iv_mid is None:
                    continue
                delta = bs_delta(spot, row["strike"], rate, div, t_years, iv_mid, row["right"])
                spread_pct = (row["ask"] - row["bid"]) / mid if mid > 0 else np.nan
                quality = 0.0 if pd.notna(spread_pct) and spread_pct > SPREAD_GATE_PCT else 1.0
                enriched.append(
                    {
                        "strike": row["strike"],
                        "right": row["right"],
                        "open_interest": row["open_interest"],
                        "iv_mid": iv_mid,
                        "iv_bid": iv_bid,
                        "iv_ask": iv_ask,
                        "delta": delta,
                        "quality": quality,
                    }
                )

            if not enriched:
                continue

            exp_df = pd.DataFrame(enriched)
            dte = int((expiry - ts.date()).days)
            bucket = bucket_days(dte, EXPIRY_BUCKETS)
            fwd = forward_price(spot, rate, div, t_years)

            atm = exp_df.iloc[(exp_df["strike"] - fwd).abs().argsort()[:1]]
            calls = exp_df[exp_df["right"] == "C"].copy()
            puts = exp_df[exp_df["right"] == "P"].copy()
            if atm.empty or calls.empty or puts.empty:
                continue

            c25 = calls.iloc[(calls["delta"] - 0.25).abs().argsort()[:1]]
            p25 = puts.iloc[(puts["delta"] + 0.25).abs().argsort()[:1]]
            c10 = calls.iloc[(calls["delta"] - 0.10).abs().argsort()[:1]]
            p10 = puts.iloc[(puts["delta"] + 0.10).abs().argsort()[:1]]

            if c25.empty or p25.empty:
                continue

            quality_atm = atm["quality"].iloc[0]
            quality_c25 = c25["quality"].iloc[0]
            quality_p25 = p25["quality"].iloc[0]
            quality_c10 = c10["quality"].iloc[0] if not c10.empty else 0.0
            quality_p10 = p10["quality"].iloc[0] if not p10.empty else 0.0

            tier = None
            if quality_atm >= 1 and quality_c25 >= 1 and quality_p25 >= 1:
                tier = "Core"
            if tier == "Core" and quality_c10 >= 1 and quality_p10 >= 1:
                tier = "Full"
            if tier is None:
                continue

            record = {
                "ts": ts,
                "expiry": pd.Timestamp(expiry),
                "expiry_bucket": f"{bucket}D",
                "dte": dte,
                "tier": tier,
                "atm_iv_mid": atm["iv_mid"].iloc[0],
                "atm_iv_worst": atm["iv_bid"].iloc[0],
                "rr25_mid": c25["iv_mid"].iloc[0] - p25["iv_mid"].iloc[0],
                "rr25_worst": c25["iv_ask"].iloc[0] - p25["iv_bid"].iloc[0],
                "fly25_mid": 0.5 * (c25["iv_mid"].iloc[0] + p25["iv_mid"].iloc[0]) - atm["iv_mid"].iloc[0],
                "fly25_worst": 0.5 * (c25["iv_ask"].iloc[0] + p25["iv_bid"].iloc[0]) - atm["iv_bid"].iloc[0],
                "open_interest_min": min(c25["open_interest"].iloc[0], p25["open_interest"].iloc[0]),
            }

            key = f"{bucket}D"
            dist = abs(dte - bucket)
            if key not in candidates or dist < candidates[key][0]:
                candidates[key] = (dist, record)

        bucket_rows = [record for _, record in candidates.values()]
        bucket_rows = sorted(bucket_rows, key=lambda x: int(x["expiry_bucket"].replace("D", "")))
        for i, row in enumerate(bucket_rows):
            next_row = bucket_rows[i + 1] if i + 1 < len(bucket_rows) else None
            row["term_slope_mid"] = row["atm_iv_mid"] - next_row["atm_iv_mid"] if next_row else np.nan
            row["term_slope_worst"] = row["atm_iv_worst"] - next_row["atm_iv_worst"] if next_row else np.nan
            rows.append(row)

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    out["tradability_pass"] = (
        (out["open_interest_min"] >= MIN_OPEN_INTEREST) &
        out["tier"].isin(["Core", "Full"])
    )
    return out


def pull_daily_history_chunked(option_symbol, start_dt, end_dt, months=1):
    frames = []
    for chunk_start, chunk_end in month_chunks(start_dt, end_dt, months):
        frame = qb.history(option_symbol, chunk_start, chunk_end, flatten=True)
        if len(frame) == 0:
            print("Daily chunk empty:", chunk_start.date(), "->", chunk_end.date())
            continue
        print("Daily chunk:", chunk_start.date(), "->", chunk_end.date(), "rows:", len(frame))
        frames.append(frame)
    return pd.concat(frames) if frames else pd.DataFrame()


def pull_minute_history_for_days(index_symbol, selected_days):
    frames = []
    for day in selected_days:
        start = datetime.combine(day, time(9, 30))
        end = datetime.combine(day, time(16, 0))
        option_history = qb.option_history(
            index_symbol,
            start,
            end,
            Resolution.MINUTE,
            fill_forward=False,
            extended_market_hours=False
        )
        frame = option_history.data_frame
        if len(frame) == 0:
            print("Minute day empty:", day)
            continue
        print("Minute day:", day, "rows:", len(frame))
        frames.append(frame)
    return pd.concat(frames) if frames else pd.DataFrame()
```

## Cell 5 - Pull Fast Daily Universe History in Monthly Chunks

```python
daily_history_raw = pull_daily_history_chunked(
    option.symbol,
    START_DATE,
    END_DATE,
    months=DAILY_CHUNK_MONTHS,
)

print("Daily rows:", len(daily_history_raw))
display(daily_history_raw.head())
display(daily_history_raw.tail())
```

## Cell 6 - Build the Fast Daily Signal Panel

```python
daily_chain = normalize_daily_history(daily_history_raw)
daily_surface = compute_surface_from_iv(daily_chain)
daily_alerts = compute_daily_alerts(daily_surface)

print("Daily chain rows:", len(daily_chain))
print("Daily surface rows:", len(daily_surface))
print("Daily alerts:", len(daily_alerts))

display(daily_surface.head())
display(daily_alerts.tail(20))
```

## Cell 7 - Inspect Daily Signal Density

```python
if daily_alerts.empty:
    print("No alerts found in the coarse daily scan.")
else:
    summary = (
        daily_alerts
        .assign(month=lambda x: x["ts"].dt.to_period("M").astype(str))
        .groupby(["month", "alert_type"])
        .size()
        .unstack(fill_value=0)
    )
    display(summary.tail(24))

    bucket_summary = (
        daily_alerts
        .groupby(["expiry_bucket", "alert_type"])
        .size()
        .rename("count")
        .reset_index()
        .sort_values(["alert_type", "expiry_bucket"])
    )
    display(bucket_summary)

    fig, ax = plt.subplots(figsize=(14, 5))
    daily_surface.pivot(index="ts", columns="expiry_bucket", values="rr25_mid").plot(ax=ax, title="Daily RR25 Mid by Bucket")
    ax.axhline(0, color="black", linewidth=1)
    plt.show()
```

## Cell 8 - Pick Candidate Dates for Quote-Level Validation

```python
candidate_days = (
    daily_alerts
    .assign(day=lambda x: x["ts"].dt.date)
    .groupby(["day", "alert_type"])
    .agg(
        alert_count=("alert_type", "size"),
        max_abs_z=("zscore_mid", lambda s: float(np.max(np.abs(s)))),
    )
    .reset_index()
    .sort_values(["max_abs_z", "alert_count"], ascending=[False, False])
)

display(candidate_days.head(20))

SELECTED_DAYS = candidate_days["day"].head(MAX_CANDIDATE_DAYS).tolist()
print("Selected validation days:", SELECTED_DAYS)
```

## Cell 9 - Pull Minute Option History Only for Selected Days

```python
minute_raw = pull_minute_history_for_days(index_symbol, SELECTED_DAYS)
print("Total minute rows:", len(minute_raw))
display(minute_raw.head())
```

## Cell 10 - Inspect the Minute Schema Before Normalization

```python
print("Index names:", minute_raw.index.names if not minute_raw.empty else [])
print("Columns:", list(minute_raw.columns)[:100] if not minute_raw.empty else [])
display(minute_raw.head(3))
```

## Cell 11 - Normalize Minute Quotes and Keep Only Target Snapshot Times

```python
minute_quotes = normalize_minute_option_history(minute_raw)

minute_quotes["clock"] = minute_quotes["ts"].dt.time
minute_quotes["minute_of_day"] = minute_quotes["ts"].dt.hour * 60 + minute_quotes["ts"].dt.minute

target_minutes = [t.hour * 60 + t.minute for t in TARGET_SNAPSHOT_TIMES]

def nearest_target_minute(x):
    return min(target_minutes, key=lambda m: abs(x - m))

minute_quotes["target_minute"] = minute_quotes["minute_of_day"].apply(nearest_target_minute)
minute_quotes["distance_to_target"] = (minute_quotes["minute_of_day"] - minute_quotes["target_minute"]).abs()
minute_quotes = minute_quotes[minute_quotes["distance_to_target"] <= VALIDATION_WINDOW_MINUTES].copy()

print("Normalized minute quote rows:", len(minute_quotes))
display(minute_quotes.head())
```

## Cell 12 - Recompute Quote-Level Intraday Surface Metrics

```python
intraday_surface = compute_intraday_snapshot_metrics(minute_quotes)

print("Intraday surface rows:", len(intraday_surface))
display(intraday_surface.head(20))

if not intraday_surface.empty:
    intraday_summary = (
        intraday_surface
        .assign(day=lambda x: x["ts"].dt.date)
        .groupby(["day", "expiry_bucket"])
        .agg(
            snapshots=("ts", "size"),
            tradability_pass_rate=("tradability_pass", "mean"),
            avg_rr25_mid=("rr25_mid", "mean"),
            avg_rr25_worst=("rr25_worst", "mean"),
            avg_fly25_mid=("fly25_mid", "mean"),
            avg_fly25_worst=("fly25_worst", "mean"),
        )
        .reset_index()
    )
    display(intraday_summary)
```

## Cell 13 - Quote-Level Alert Validation

```python
if intraday_surface.empty:
    print("No intraday surface rows to validate.")
else:
    validated_alerts = []

    for bucket, bucket_df in intraday_surface.groupby("expiry_bucket"):
        bucket_df = bucket_df.sort_values("ts").copy()
        for metric_mid, metric_worst, alert_type in [
            ("rr25_mid", "rr25_worst", "RR_EXTREME"),
            ("fly25_mid", "fly25_worst", "FLY_EXTREME"),
            ("term_slope_mid", "term_slope_worst", "TERM_KINK"),
        ]:
            bucket_df[f"{metric_mid}_z"] = (
                bucket_df[metric_mid]
                .rolling(30, min_periods=10)
                .apply(lambda s: compute_zscore(pd.Series(s)), raw=False)
            )
            bucket_df[f"{metric_worst}_z"] = (
                bucket_df[metric_worst]
                .rolling(30, min_periods=10)
                .apply(lambda s: compute_zscore(pd.Series(s)), raw=False)
            )

        for i in range(len(bucket_df)):
            row = bucket_df.iloc[i]
            for metric_mid, metric_worst, alert_type in [
                ("rr25_mid", "rr25_worst", "RR_EXTREME"),
                ("fly25_mid", "fly25_worst", "FLY_EXTREME"),
                ("term_slope_mid", "term_slope_worst", "TERM_KINK"),
            ]:
                z_mid = row[f"{metric_mid}_z"]
                z_worst = row[f"{metric_worst}_z"]
                if pd.isna(z_mid) or pd.isna(z_worst):
                    continue
                if abs(z_mid) < Z_THRESHOLD or abs(z_worst) < Z_THRESHOLD:
                    continue
                if not row["tradability_pass"]:
                    continue

                validated_alerts.append(
                    {
                        "ts": row["ts"],
                        "expiry_bucket": row["expiry_bucket"],
                        "alert_type": alert_type,
                        "zscore_mid": z_mid,
                        "zscore_worst": z_worst,
                        "tradability_pass": row["tradability_pass"],
                        "tier": row["tier"],
                        "open_interest_min": row["open_interest_min"],
                    }
                )

    validated_alerts = pd.DataFrame(validated_alerts).sort_values("ts")
    print("Validated quote-level alerts:", len(validated_alerts))
    display(validated_alerts.head(30))
```

## Cell 14 - Compare Coarse Daily Scan vs Quote-Level Validation

```python
if daily_alerts.empty:
    print("No daily alerts to compare.")
else:
    daily_alert_days = set(daily_alerts["ts"].dt.date.tolist())
    validated_days = set(validated_alerts["ts"].dt.date.tolist()) if "validated_alerts" in globals() and not validated_alerts.empty else set()

    comparison = pd.DataFrame(
        {
            "metric": [
                "daily_alert_count",
                "daily_unique_days",
                "validated_alert_count",
                "validated_unique_days",
                "day_overlap_ratio",
            ],
            "value": [
                len(daily_alerts),
                len(daily_alert_days),
                len(validated_alerts) if "validated_alerts" in globals() and not validated_alerts.empty else 0,
                len(validated_days),
                (len(daily_alert_days & validated_days) / len(daily_alert_days)) if daily_alert_days else 0.0,
            ],
        }
    )
    display(comparison)
```

## Cell 15 - Inspect One Validation Day in Detail

```python
INSPECT_DAY = SELECTED_DAYS[0] if SELECTED_DAYS else None
INSPECT_BUCKET = "30D"

if INSPECT_DAY is None or intraday_surface.empty:
    print("Nothing to inspect.")
else:
    detail = intraday_surface[
        (intraday_surface["ts"].dt.date == INSPECT_DAY) &
        (intraday_surface["expiry_bucket"] == INSPECT_BUCKET)
    ].copy()

    if detail.empty:
        print("No detail rows for", INSPECT_DAY, INSPECT_BUCKET)
    else:
        display(detail)

        fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
        detail.plot(x="ts", y=["rr25_mid", "rr25_worst"], ax=axes[0], title=f"{INSPECT_DAY} {INSPECT_BUCKET} RR25")
        detail.plot(x="ts", y=["fly25_mid", "fly25_worst"], ax=axes[1], title=f"{INSPECT_DAY} {INSPECT_BUCKET} Fly25")
        detail.plot(x="ts", y=["term_slope_mid", "term_slope_worst"], ax=axes[2], title=f"{INSPECT_DAY} {INSPECT_BUCKET} Term Slope")
        plt.tight_layout()
        plt.show()
```

## Cell 16 - Export Research Artifacts

```python
exports = {
    "daily_surface_rows": len(daily_surface),
    "daily_alert_rows": len(daily_alerts),
    "selected_days": [str(x) for x in SELECTED_DAYS],
}

if "validated_alerts" in globals() and not validated_alerts.empty:
    exports["validated_alert_rows"] = len(validated_alerts)

print(json.dumps(exports, indent=2))

daily_surface.to_csv("daily_surface.csv", index=False)
daily_alerts.to_csv("daily_alerts.csv", index=False)

if "intraday_surface" in globals() and not intraday_surface.empty:
    intraday_surface.to_csv("intraday_surface.csv", index=False)

if "validated_alerts" in globals() and not validated_alerts.empty:
    validated_alerts.to_csv("validated_alerts.csv", index=False)

print("Wrote CSV exports to the notebook working directory.")
```

## Notes

- The daily scan is for speed, not final execution validation.
- The minute validation stage is where bid/ask realism enters.
- If `normalize_minute_option_history` fails because QC changed `OptionHistory.data_frame` column names, inspect Cell 10 and update the candidate column lists in the helper.
- For your pipeline, the main research decision variable should be:
  - how many daily alerts survive quote-level worst-case validation?
