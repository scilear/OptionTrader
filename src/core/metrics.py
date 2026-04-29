from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

import pandas as pd

from src.core.iv_solve import bs_delta, solve_iv
from src.core.surface_fit import fit_surface_for_expiry


@dataclass
class IvPoint:
    expiry: date
    delta_bucket: str
    iv_mid: float | None
    iv_bid: float | None
    iv_ask: float | None
    solve_status: str
    quality_score: float
    fit_model_id: str = ""
    fit_residual: float | None = None
    fit_support: int = 0
    fit_confidence: float = 0.0
    fit_reason_codes: tuple[str, ...] = ()


def _t_years(snapshot_ts: datetime, expiry: date) -> float:
    days = (expiry - snapshot_ts.date()).days
    return max(days, 0) / 365.0


def filter_quotes_by_dte(
    quotes: pd.DataFrame,
    snapshot_ts: datetime,
    dte_min: int,
    dte_max: int,
) -> pd.DataFrame:
    if quotes.empty:
        return quotes
    expiry_dates = pd.to_datetime(quotes["expiry"]).dt.date
    dte = expiry_dates.apply(lambda d: (d - snapshot_ts.date()).days)
    mask = (dte >= dte_min) & (dte <= dte_max)
    return quotes.loc[mask].copy()


def event_premium_series(series: pd.DataFrame) -> pd.Series:
    if series.empty or "atm_iv_mid" not in series.columns or "ts" not in series.columns:
        return pd.Series(dtype=float)

    df = series.sort_values("ts").copy()
    df["t_years"] = 1 / 12
    df["var"] = (df["atm_iv_mid"] ** 2) * df["t_years"]
    df["var_smooth"] = df["var"].rolling(3, min_periods=1).mean()
    df["event_premium"] = df["var"] - df["var_smooth"]
    return df["event_premium"]


def _bucket_days(dte: int, buckets: Iterable[int]) -> int:
    return min(buckets, key=lambda b: abs(dte - b))


def _quality_for_bucket(exp_df: pd.DataFrame, bucket: str) -> float:
    values = exp_df.loc[exp_df["bucket"] == bucket, "quality"]
    if values.empty:
        return 0.0
    return float(values.iloc[0])


def _value_for_bucket(exp_df: pd.DataFrame, bucket: str, column: str) -> float | None:
    values = exp_df.loc[exp_df["bucket"] == bucket, column]
    if values.empty:
        return None
    value = values.iloc[0]
    return float(value) if pd.notna(value) else None


def _resolve_tier(
    exp_df: pd.DataFrame,
    min_valid_points_core: int,
    min_valid_points_full: int,
) -> str | None:
    core_required = ["ATM", "+0.25C", "-0.25P"]
    full_required = core_required + ["+0.10C", "-0.10P"]

    core_membership_ok = all(_quality_for_bucket(exp_df, b) >= 1.0 for b in core_required)
    full_membership_ok = all(_quality_for_bucket(exp_df, b) >= 1.0 for b in full_required)
    valid_count = int((exp_df["quality"] >= 1.0).sum())

    if full_membership_ok and valid_count >= int(min_valid_points_full):
        return "Full"
    if core_membership_ok and valid_count >= int(min_valid_points_core):
        return "Core"
    return None


def compute_iv_points(
    quotes: pd.DataFrame,
    snapshot_ts: datetime,
    spot: float,
    spread_gate_pct: float,
    delta_points: Iterable[float] | None = None,
    rate: float = 0.0,
    div: float = 0.0,
) -> list[IvPoint]:
    points: list[IvPoint] = []
    if quotes.empty:
        return points

    for expiry_value, exp_df in quotes.groupby("expiry"):
        expiry = pd.to_datetime(expiry_value).date()
        t_years = _t_years(snapshot_ts, expiry)
        if t_years <= 0:
            continue

        rows = []
        for _, row in exp_df.iterrows():
            bid = float(row["bid"]) if row["bid"] is not None else 0.0
            ask = float(row["ask"]) if row["ask"] is not None else 0.0
            mid = (bid + ask) / 2 if bid + ask > 0 else 0.0
            right = row["option_right"]
            strike = float(row["strike"])

            iv_mid = solve_iv(mid, spot, strike, rate, div, t_years, right).iv if mid > 0 else None
            iv_bid = solve_iv(bid, spot, strike, rate, div, t_years, right).iv if bid > 0 else None
            iv_ask = solve_iv(ask, spot, strike, rate, div, t_years, right).iv if ask > 0 else None
            if iv_mid is None:
                continue
            delta = bs_delta(spot, strike, rate, div, t_years, iv_mid, right)
            quality_score = 1.0
            if mid > 0:
                spread = (ask - bid) / mid
                if spread > spread_gate_pct:
                    quality_score = 0.0
            rows.append((expiry, strike, right, bid, ask, mid, iv_mid, iv_bid, iv_ask, delta, quality_score))

        if not rows:
            continue

        df = pd.DataFrame(
            rows,
            columns=[
                "expiry",
                "strike",
                "right",
                "bid",
                "ask",
                "mid",
                "iv_mid",
                "iv_bid",
                "iv_ask",
                "delta",
                "quality",
            ],
        )

        fit_points = fit_surface_for_expiry(
            rows=df,
            expiry=expiry,
            spot=spot,
            rate=rate,
            div=div,
            t_years=t_years,
            delta_points=delta_points or [0.10, 0.25],
        )
        for fit_point in fit_points:
            points.append(
                IvPoint(
                    expiry=fit_point.expiry,
                    delta_bucket=fit_point.delta_bucket,
                    iv_mid=fit_point.iv_mid,
                    iv_bid=fit_point.iv_bid,
                    iv_ask=fit_point.iv_ask,
                    solve_status=fit_point.solve_status,
                    quality_score=fit_point.quality_score,
                    fit_model_id=fit_point.fit_model_id,
                    fit_residual=fit_point.fit_residual,
                    fit_support=fit_point.fit_support,
                    fit_confidence=fit_point.fit_confidence,
                    fit_reason_codes=fit_point.reason_codes,
                )
            )

    return points


def compute_surface_metrics(
    iv_points: list[IvPoint],
    snapshot_ts: datetime,
    buckets: Iterable[int],
    min_valid_points_core: int = 3,
    min_valid_points_full: int = 5,
) -> list[dict]:
    if not iv_points:
        return []

    df = pd.DataFrame(
        [
            {
                "expiry": p.expiry,
                "bucket": p.delta_bucket,
                "iv_mid": p.iv_mid,
                "iv_bid": p.iv_bid,
                "iv_ask": p.iv_ask,
                "quality": p.quality_score,
            }
            for p in iv_points
        ]
    )

    out = []
    candidates: dict[str, tuple[int, dict]] = {}
    for expiry, exp_df in df.groupby("expiry"):
        dte = (expiry - snapshot_ts.date()).days
        if dte <= 0:
            continue
        bucket_days = _bucket_days(dte, buckets)
        atm = _value_for_bucket(exp_df, "ATM", "iv_mid")
        c25 = _value_for_bucket(exp_df, "+0.25C", "iv_mid")
        p25 = _value_for_bucket(exp_df, "-0.25P", "iv_mid")
        c10 = _value_for_bucket(exp_df, "+0.10C", "iv_mid")
        p10 = _value_for_bucket(exp_df, "-0.10P", "iv_mid")

        atm_bid = _value_for_bucket(exp_df, "ATM", "iv_bid")
        c25_ask = _value_for_bucket(exp_df, "+0.25C", "iv_ask")
        p25_bid = _value_for_bucket(exp_df, "-0.25P", "iv_bid")
        c10_ask = _value_for_bucket(exp_df, "+0.10C", "iv_ask")
        p10_bid = _value_for_bucket(exp_df, "-0.10P", "iv_bid")

        tier = _resolve_tier(
            exp_df,
            min_valid_points_core=min_valid_points_core,
            min_valid_points_full=min_valid_points_full,
        )

        rr25 = (c25 - p25) if pd.notna(c25) and pd.notna(p25) else None
        rr10 = (c10 - p10) if pd.notna(c10) and pd.notna(p10) else None
        fly25 = ((c25 + p25) / 2 - atm) if pd.notna(c25) and pd.notna(p25) and pd.notna(atm) else None
        fly10 = ((c10 + p10) / 2 - atm) if pd.notna(c10) and pd.notna(p10) and pd.notna(atm) else None

        rr25_worst = (c25_ask - p25_bid) if pd.notna(c25_ask) and pd.notna(p25_bid) else None
        rr10_worst = (c10_ask - p10_bid) if pd.notna(c10_ask) and pd.notna(p10_bid) else None
        fly25_worst = (
            ((c25_ask + p25_bid) / 2 - atm_bid)
            if pd.notna(c25_ask) and pd.notna(p25_bid) and pd.notna(atm_bid)
            else None
        )
        fly10_worst = (
            ((c10_ask + p10_bid) / 2 - atm_bid)
            if pd.notna(c10_ask) and pd.notna(p10_bid) and pd.notna(atm_bid)
            else None
        )

        entry = {
            "expiry_bucket": f"{bucket_days}D",
            "atm_iv_mid": atm,
            "rr25_mid": rr25,
            "rr10_mid": rr10,
            "fly25_mid": fly25,
            "fly10_mid": fly10,
            "atm_iv_worst": atm_bid,
            "rr25_worst": rr25_worst,
            "rr10_worst": rr10_worst,
            "fly25_worst": fly25_worst,
            "fly10_worst": fly10_worst,
            "dte": dte,
            "tier": tier,
        }

        dist = abs(dte - bucket_days)
        key = f"{bucket_days}D"
        if key not in candidates or dist < candidates[key][0]:
            candidates[key] = (dist, entry)

    for _, entry in candidates.values():
        out.append(entry)

    bucket_order = sorted(out, key=lambda x: int(x["expiry_bucket"].replace("D", "")))
    for idx, entry in enumerate(bucket_order):
        next_entry = bucket_order[idx + 1] if idx + 1 < len(bucket_order) else None
        if next_entry and entry.get("atm_iv_mid") is not None and next_entry.get("atm_iv_mid") is not None:
            entry["term_slope_mid"] = entry["atm_iv_mid"] - next_entry["atm_iv_mid"]
        else:
            entry["term_slope_mid"] = None
        if next_entry and entry.get("atm_iv_worst") is not None and next_entry.get("atm_iv_worst") is not None:
            entry["term_slope_worst"] = entry["atm_iv_worst"] - next_entry["atm_iv_worst"]
        else:
            entry["term_slope_worst"] = None

    return out
