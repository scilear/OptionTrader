from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class RunSettings:
    start_date: date
    end_date: date
    output_root: str
    symbols: tuple[str, ...]
    data_repo_path: str
    contract_multiplier: int
    initial_equity: float
    max_margin_utilization: float
    transaction_fee_per_contract: float
    slippage_bps: float
    vix_gate_threshold: float
    gate_short_straddle: bool
    gate_put_credit_spread: bool


@dataclass(frozen=True)
class StraddleSettings:
    target_dte: int
    dte_tolerance: int
    close_dte: int


@dataclass(frozen=True)
class PutSpreadSettings:
    target_dte: int
    dte_tolerance: int
    short_delta_target: float
    long_delta_target: float
    early_profit_take: float
    close_dte_itm: int


@dataclass(frozen=True)
class FilterSettings:
    max_spread_pct: float


@dataclass(frozen=True)
class SimulationConfig:
    run: RunSettings
    straddle: StraddleSettings
    put_credit_spread: PutSpreadSettings
    filters: FilterSettings


@dataclass
class PositionLeg:
    option_right: str
    strike: float
    expiration: date
    side: str
    quantity: int
    entry_price: float
    entry_delta: float
    last_mark: float


@dataclass
class OpenTrade:
    trade_id: str
    strategy: str
    symbol: str
    entry_date: date
    expiration: date
    entry_credit: float
    max_risk: float
    margin_used: float
    legs: list[PositionLeg]
    last_option_value: float
    hedge_shares: int = 0
    last_spot: float | None = None
    cumulative_option_pnl: float = 0.0
    cumulative_hedge_pnl: float = 0.0
