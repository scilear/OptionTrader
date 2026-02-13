from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import math
from typing import Iterable

import pandas as pd

from src.core.iv_solve import bs_delta, solve_iv


@dataclass
class IvPoint:
    expiry: date
    delta_bucket: str
    iv_mid: float | None
    iv_bid: float | None
    iv_ask: float | None
    solve_status: str
    quality_score: float


def _t_years(snapshot_ts: datetime, expiry: date) -> float:
    days = (expiry - snapshot_ts.date()).days
    return max(days, 0) / 365.0


def _forward(spot: float, rate: float, div: float, t_years: float) -> float:
    return spot * math.exp((rate - div) * t_years)


def _bucket_days(dte: int, buckets: Iterable[int]) -> int:
    return min(buckets, key=lambda b: abs(dte - b))


def compute_iv_points(
    quotes: pd.DataFrame,
    snapshot_ts: datetime,
    spot: float,
    spread_gate_pct: float,
) -> list[IvPoint]:
    points: list[IvPoint] = []
    if quotes.empty:
        return points

    rate = 0.0
    div = 0.0

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
            rows.append((strike, right, bid, ask, mid, iv_mid, iv_bid, iv_ask, delta, quality_score))

        if not rows:
            continue

        df = pd.DataFrame(
            rows,
            columns=[
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

        fwd = _forward(spot, rate, div, t_years)
        df["fwd_dist"] = (df["strike"] - fwd).abs()

        atm_row = df.loc[df["fwd_dist"].idxmin()]
        points.append(
            IvPoint(
                expiry=expiry,
                delta_bucket="ATM",
                iv_mid=float(atm_row["iv_mid"]),
                iv_bid=float(atm_row["iv_bid"]) if pd.notna(atm_row["iv_bid"]) else None,
                iv_ask=float(atm_row["iv_ask"]) if pd.notna(atm_row["iv_ask"]) else None,
                solve_status="ok",
                quality_score=float(atm_row["quality"]),
            )
        )

        def select_delta(target: float, right: str) -> pd.Series | None:
            sub = df[df["right"] == right]
            if sub.empty:
                return None
            sub = sub.copy()
            sub["delta_dist"] = (sub["delta"] - target).abs()
            return sub.loc[sub["delta_dist"].idxmin()]

        for target, bucket, right in [
            (0.25, "+0.25C", "C"),
            (-0.25, "-0.25P", "P"),
            (0.10, "+0.10C", "C"),
            (-0.10, "-0.10P", "P"),
        ]:
            row = select_delta(target, right)
            if row is None:
                continue
            points.append(
                IvPoint(
                    expiry=expiry,
                    delta_bucket=bucket,
                    iv_mid=float(row["iv_mid"]),
                    iv_bid=float(row["iv_bid"]) if pd.notna(row["iv_bid"]) else None,
                    iv_ask=float(row["iv_ask"]) if pd.notna(row["iv_ask"]) else None,
                    solve_status="ok",
                    quality_score=float(row["quality"]),
                )
            )

    return points


def compute_surface_metrics(
    iv_points: list[IvPoint],
    snapshot_ts: datetime,
    buckets: Iterable[int],
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
        atm = exp_df.loc[exp_df["bucket"] == "ATM", "iv_mid"].squeeze()
        c25 = exp_df.loc[exp_df["bucket"] == "+0.25C", "iv_mid"].squeeze()
        p25 = exp_df.loc[exp_df["bucket"] == "-0.25P", "iv_mid"].squeeze()
        c10 = exp_df.loc[exp_df["bucket"] == "+0.10C", "iv_mid"].squeeze()
        p10 = exp_df.loc[exp_df["bucket"] == "-0.10P", "iv_mid"].squeeze()

        atm_bid = exp_df.loc[exp_df["bucket"] == "ATM", "iv_bid"].squeeze()
        c25_ask = exp_df.loc[exp_df["bucket"] == "+0.25C", "iv_ask"].squeeze()
        p25_bid = exp_df.loc[exp_df["bucket"] == "-0.25P", "iv_bid"].squeeze()
        c10_ask = exp_df.loc[exp_df["bucket"] == "+0.10C", "iv_ask"].squeeze()
        p10_bid = exp_df.loc[exp_df["bucket"] == "-0.10P", "iv_bid"].squeeze()

        def q(bucket: str) -> float:
            return float(exp_df.loc[exp_df["bucket"] == bucket, "quality"].squeeze())

        quality_atm = q("ATM") if "ATM" in exp_df["bucket"].values else 0.0
        quality_c25 = q("+0.25C") if "+0.25C" in exp_df["bucket"].values else 0.0
        quality_p25 = q("-0.25P") if "-0.25P" in exp_df["bucket"].values else 0.0
        quality_c10 = q("+0.10C") if "+0.10C" in exp_df["bucket"].values else 0.0
        quality_p10 = q("-0.10P") if "-0.10P" in exp_df["bucket"].values else 0.0

        tier = None
        if quality_atm >= 1 and quality_c25 >= 1 and quality_p25 >= 1:
            tier = "Core"
        if tier == "Core" and quality_c10 >= 1 and quality_p10 >= 1:
            tier = "Full"

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
