from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import math
from typing import Iterable

import pandas as pd


@dataclass
class FitOutput:
    expiry: date
    delta_bucket: str
    iv_mid: float | None
    iv_bid: float | None
    iv_ask: float | None
    solve_status: str
    quality_score: float
    fit_model_id: str
    fit_residual: float | None
    fit_support: int
    fit_confidence: float
    reason_codes: tuple[str, ...]


def _forward(spot: float, rate: float, div: float, t_years: float) -> float:
    return spot * math.exp((rate - div) * t_years)


def _interp_linear(x0: float, y0: float, x1: float, y1: float, x: float) -> float:
    if x1 == x0:
        return y0
    w = (x - x0) / (x1 - x0)
    return y0 + w * (y1 - y0)


def _interp_column(lower: pd.Series, upper: pd.Series, target: float, column: str) -> float | None:
    y0 = lower[column]
    y1 = upper[column]
    if pd.isna(y0) or pd.isna(y1):
        return None
    return float(_interp_linear(float(lower["delta"]), float(y0), float(upper["delta"]), float(y1), target))


def _fit_signed_delta_bucket(
    rows: pd.DataFrame,
    target: float,
    bucket: str,
    right: str,
) -> FitOutput | None:
    sub = rows.loc[rows["right"] == right].copy()
    if sub.empty:
        return None

    sub = sub.sort_values("delta")
    support = int(len(sub))
    reason_codes: list[str] = []

    exact = sub.loc[(sub["delta"] - target).abs() < 1e-9]
    if not exact.empty:
        row = exact.iloc[0]
        return FitOutput(
            expiry=row["expiry"],
            delta_bucket=bucket,
            iv_mid=float(row["iv_mid"]) if pd.notna(row["iv_mid"]) else None,
            iv_bid=float(row["iv_bid"]) if pd.notna(row["iv_bid"]) else None,
            iv_ask=float(row["iv_ask"]) if pd.notna(row["iv_ask"]) else None,
            solve_status="ok",
            quality_score=float(row["quality"]),
            fit_model_id="exact_delta_v1",
            fit_residual=0.0,
            fit_support=support,
            fit_confidence=max(0.0, min(1.0, float(row["quality"]))),
            reason_codes=(),
        )

    lower = sub.loc[sub["delta"] <= target].tail(1)
    upper = sub.loc[sub["delta"] >= target].head(1)
    have_bracket = not lower.empty and not upper.empty

    if have_bracket and int(lower.index[0]) != int(upper.index[0]) and support >= 2:
        lower_row = lower.iloc[0]
        upper_row = upper.iloc[0]
        iv_mid = _interp_column(lower_row, upper_row, target, "iv_mid")
        iv_bid = _interp_column(lower_row, upper_row, target, "iv_bid")
        iv_ask = _interp_column(lower_row, upper_row, target, "iv_ask")
        residual = abs(float(upper_row["iv_mid"]) - float(lower_row["iv_mid"]))
        quality = min(float(lower_row["quality"]), float(upper_row["quality"]))
        return FitOutput(
            expiry=lower_row["expiry"],
            delta_bucket=bucket,
            iv_mid=iv_mid,
            iv_bid=iv_bid,
            iv_ask=iv_ask,
            solve_status="ok",
            quality_score=quality,
            fit_model_id="linear_delta_v1",
            fit_residual=residual,
            fit_support=support,
            fit_confidence=max(0.0, min(1.0, quality)),
            reason_codes=tuple(reason_codes),
        )

    nearest_idx = (sub["delta"] - target).abs().idxmin()
    nearest = sub.loc[nearest_idx]
    if support < 2:
        reason_codes.append("insufficient_support")
    else:
        reason_codes.append("delta_out_of_range")

    return FitOutput(
        expiry=nearest["expiry"],
        delta_bucket=bucket,
        iv_mid=float(nearest["iv_mid"]) if pd.notna(nearest["iv_mid"]) else None,
        iv_bid=float(nearest["iv_bid"]) if pd.notna(nearest["iv_bid"]) else None,
        iv_ask=float(nearest["iv_ask"]) if pd.notna(nearest["iv_ask"]) else None,
        solve_status="degraded",
        quality_score=float(nearest["quality"]),
        fit_model_id="nearest_fallback_v1",
        fit_residual=None,
        fit_support=support,
        fit_confidence=0.25 * max(0.0, min(1.0, float(nearest["quality"]))),
        reason_codes=tuple(reason_codes),
    )


def fit_surface_for_expiry(
    rows: pd.DataFrame,
    expiry: date,
    spot: float,
    rate: float,
    div: float,
    t_years: float,
    delta_points: Iterable[float],
) -> list[FitOutput]:
    out: list[FitOutput] = []
    if rows.empty:
        return out

    fwd = _forward(spot, rate, div, t_years)
    rows = rows.copy()
    rows["fwd_dist"] = (rows["strike"] - fwd).abs()
    atm_row = rows.loc[rows["fwd_dist"].idxmin()]
    out.append(
        FitOutput(
            expiry=expiry,
            delta_bucket="ATM",
            iv_mid=float(atm_row["iv_mid"]) if pd.notna(atm_row["iv_mid"]) else None,
            iv_bid=float(atm_row["iv_bid"]) if pd.notna(atm_row["iv_bid"]) else None,
            iv_ask=float(atm_row["iv_ask"]) if pd.notna(atm_row["iv_ask"]) else None,
            solve_status="ok",
            quality_score=float(atm_row["quality"]),
            fit_model_id="forward_anchor_v1",
            fit_residual=None,
            fit_support=int(len(rows)),
            fit_confidence=max(0.0, min(1.0, float(atm_row["quality"]))),
            reason_codes=(),
        )
    )

    for point in sorted({float(p) for p in delta_points}, reverse=True):
        if point <= 0.0 or point > 0.5:
            continue
        call_result = _fit_signed_delta_bucket(rows, point, f"+{point:.2f}C", "C")
        put_result = _fit_signed_delta_bucket(rows, -point, f"-{point:.2f}P", "P")
        if call_result is not None:
            call_result.expiry = expiry
            out.append(call_result)
        if put_result is not None:
            put_result.expiry = expiry
            out.append(put_result)

    return out
