from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class IvResult:
    iv: float | None
    status: str


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _bs_price(
    spot: float,
    strike: float,
    rate: float,
    div: float,
    t_years: float,
    vol: float,
    right: str,
) -> float:
    if t_years <= 0 or vol <= 0:
        intrinsic = max(0.0, spot - strike) if right == "C" else max(0.0, strike - spot)
        return intrinsic

    fwd = spot * math.exp((rate - div) * t_years)
    vol_sqrt = vol * math.sqrt(t_years)
    d1 = (math.log(fwd / strike) + 0.5 * vol * vol * t_years) / vol_sqrt
    d2 = d1 - vol_sqrt
    disc = math.exp(-rate * t_years)

    if right == "C":
        return disc * (fwd * _norm_cdf(d1) - strike * _norm_cdf(d2))
    return disc * (strike * _norm_cdf(-d2) - fwd * _norm_cdf(-d1))


def bs_delta(
    spot: float,
    strike: float,
    rate: float,
    div: float,
    t_years: float,
    vol: float,
    right: str,
) -> float:
    if t_years <= 0 or vol <= 0:
        return 0.0

    fwd = spot * math.exp((rate - div) * t_years)
    vol_sqrt = vol * math.sqrt(t_years)
    d1 = (math.log(fwd / strike) + 0.5 * vol * vol * t_years) / vol_sqrt
    sign = 1.0 if right == "C" else -1.0
    if right == "C":
        return math.exp(-div * t_years) * _norm_cdf(d1)
    return math.exp(-div * t_years) * (_norm_cdf(d1) - 1.0)


def solve_iv(
    price: float,
    spot: float,
    strike: float,
    rate: float,
    div: float,
    t_years: float,
    right: str,
    vol_low: float = 1e-4,
    vol_high: float = 5.0,
    tol: float = 1e-6,
    max_iter: int = 100,
) -> IvResult:
    if price <= 0 or t_years <= 0 or spot <= 0 or strike <= 0:
        return IvResult(iv=None, status="invalid")

    intrinsic = max(0.0, spot - strike) if right == "C" else max(0.0, strike - spot)
    if price < intrinsic:
        return IvResult(iv=None, status="below_intrinsic")

    low_price = _bs_price(spot, strike, rate, div, t_years, vol_low, right)
    high_price = _bs_price(spot, strike, rate, div, t_years, vol_high, right)

    if price < low_price or price > high_price:
        return IvResult(iv=None, status="out_of_bounds")

    low = vol_low
    high = vol_high
    for _ in range(max_iter):
        mid = 0.5 * (low + high)
        mid_price = _bs_price(spot, strike, rate, div, t_years, mid, right)
        if abs(mid_price - price) < tol:
            return IvResult(iv=mid, status="ok")
        if mid_price > price:
            high = mid
        else:
            low = mid

    return IvResult(iv=0.5 * (low + high), status="max_iter")
