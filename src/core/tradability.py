from __future__ import annotations

from dataclasses import dataclass
from math import pow

import pandas as pd


def compute_tradability_score(quotes: pd.DataFrame, spread_gate_pct: float) -> float:
    if quotes.empty:
        return 0.0

    bids = quotes["bid"].astype(float)
    asks = quotes["ask"].astype(float)
    mids = (bids + asks) / 2
    valid = (bids > 0) & (asks > 0) & (mids > 0)
    if not valid.any():
        return 0.0

    spreads = (asks[valid] - bids[valid]) / mids[valid]
    median_spread = float(spreads.median()) if not spreads.empty else 1.0
    score = 1.0 - min(1.0, median_spread / spread_gate_pct) if spread_gate_pct > 0 else 0.0
    return max(0.0, score)


@dataclass(frozen=True)
class CostBreakdown:
    edge_before_cost: float
    transaction_cost: float
    size_impact_cost: float
    hedge_path_cost: float

    @property
    def total_friction_cost(self) -> float:
        return self.transaction_cost + self.size_impact_cost + self.hedge_path_cost

    @property
    def edge_after_cost(self) -> float:
        return self.edge_before_cost - self.total_friction_cost


def compute_friction_costs(
    *,
    edge_before_cost: float,
    gross_premium_notional: float,
    net_gamma: float,
    spot: float,
    size: float,
    transaction_cost_bps: float,
    impact_cost_bps: float,
    impact_exponent: float,
    hedge_turnover_bps: float,
    include_hedge_path: bool,
) -> CostBreakdown:
    safe_size = max(float(size), 0.0)
    base_notional = max(float(gross_premium_notional), 0.0)
    transaction_cost = base_notional * max(transaction_cost_bps, 0.0) / 10000.0
    size_impact_multiplier = 0.0 if safe_size <= 0.0 else pow(safe_size, max(impact_exponent, 1.0))
    size_impact_cost = base_notional * max(impact_cost_bps, 0.0) / 10000.0 * size_impact_multiplier
    if include_hedge_path:
        hedge_path_cost = (
            abs(float(net_gamma))
            * max(float(spot), 0.0)
            * max(float(hedge_turnover_bps), 0.0)
            / 10000.0
            * max(1.0, pow(safe_size, 0.5))
        )
    else:
        hedge_path_cost = 0.0
    return CostBreakdown(
        edge_before_cost=max(float(edge_before_cost), 0.0),
        transaction_cost=transaction_cost,
        size_impact_cost=size_impact_cost,
        hedge_path_cost=hedge_path_cost,
    )


def build_size_sensitivity(
    *,
    edge_before_cost: float,
    gross_premium_notional: float,
    net_gamma: float,
    spot: float,
    transaction_cost_bps: float,
    impact_cost_bps: float,
    impact_exponent: float,
    hedge_turnover_bps: float,
    include_hedge_path: bool,
    size_tiers: list[float],
) -> list[dict]:
    out: list[dict] = []
    for size in size_tiers:
        costs = compute_friction_costs(
            edge_before_cost=edge_before_cost,
            gross_premium_notional=gross_premium_notional,
            net_gamma=net_gamma,
            spot=spot,
            size=size,
            transaction_cost_bps=transaction_cost_bps,
            impact_cost_bps=impact_cost_bps,
            impact_exponent=impact_exponent,
            hedge_turnover_bps=hedge_turnover_bps,
            include_hedge_path=include_hedge_path,
        )
        out.append(
            {
                "size": float(size),
                "total_friction_cost": costs.total_friction_cost,
                "edge_after_cost": costs.edge_after_cost,
            }
        )
    return out
