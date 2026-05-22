from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import subprocess

import pandas as pd

from src.strategy_sim.artifacts import write_run_manifest, write_simulation_artifacts
from src.strategy_sim.market_data import MarketData
from src.strategy_sim.types import OpenTrade, PositionLeg, SimulationConfig


@dataclass(frozen=True)
class SimulationResult:
    run_id: str
    output_dir: Path
    trade_count: int
    daily_rows: int


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        cast = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(cast):
        return None
    return cast


def _spread_pct(row: pd.Series) -> float:
    bid = _safe_float(row.get("bid"))
    ask = _safe_float(row.get("ask"))
    if bid is None or ask is None:
        return float("inf")
    mid = (bid + ask) / 2.0
    if mid <= 0.0:
        return float("inf")
    return (ask - bid) / mid


def _mid(row: pd.Series) -> float | None:
    bid = _safe_float(row.get("bid"))
    ask = _safe_float(row.get("ask"))
    if bid is None or ask is None:
        return None
    return (bid + ask) / 2.0


def _slippage_cost(notional: float, slippage_bps: float) -> float:
    return abs(notional) * (slippage_bps / 10_000.0)


def _intrinsic(right: str, strike: float, spot: float) -> float:
    if right == "C":
        return max(0.0, spot - strike)
    return max(0.0, strike - spot)


def _quote_lookup(chain: pd.DataFrame) -> dict[tuple[date, float, str], pd.Series]:
    lookup: dict[tuple[date, float, str], pd.Series] = {}
    if chain.empty:
        return lookup
    for _, row in chain.iterrows():
        expiry = row["expiration"]
        strike = float(row["strike"])
        right = str(row["call_put"]).upper()
        key = (expiry, strike, right)
        lookup[key] = row
    return lookup


def _best_expiration(chain: pd.DataFrame, trade_date: date, target_dte: int, tolerance: int) -> date | None:
    if chain.empty:
        return None
    expiries = sorted(set(chain["expiration"].tolist()))
    candidates: list[tuple[int, int, date]] = []
    for expiry in expiries:
        dte = int((expiry - trade_date).days)
        if dte <= 0:
            continue
        distance = abs(dte - target_dte)
        if distance <= tolerance:
            candidates.append((distance, dte, expiry))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]


def _select_straddle_candidate(
    chain: pd.DataFrame,
    trade_date: date,
    spot: float,
    target_dte: int,
    tolerance: int,
) -> tuple[date | None, pd.Series | None, pd.Series | None]:
    expiry = _best_expiration(chain, trade_date, target_dte, tolerance)
    if expiry is None:
        return None, None, None
    slice_df = chain[chain["expiration"] == expiry]
    calls = slice_df[slice_df["call_put"] == "C"]
    puts = slice_df[slice_df["call_put"] == "P"]
    if calls.empty or puts.empty:
        return expiry, None, None

    call_by_strike = {float(row["strike"]): row for _, row in calls.iterrows()}
    put_by_strike = {float(row["strike"]): row for _, row in puts.iterrows()}
    common_strikes = sorted(set(call_by_strike.keys()) & set(put_by_strike.keys()))
    if not common_strikes:
        return expiry, None, None

    scored: list[tuple[float, float, float]] = []
    for strike in common_strikes:
        call_row = call_by_strike[strike]
        put_row = put_by_strike[strike]
        call_delta = abs(_safe_float(call_row.get("delta")) or 0.0)
        put_delta = abs(_safe_float(put_row.get("delta")) or 0.0)
        score = abs(strike - spot)
        tie = abs(call_delta - 0.5) + abs(put_delta - 0.5)
        scored.append((score, tie, strike))
    scored.sort()
    strike = scored[0][2]
    return expiry, call_by_strike[strike], put_by_strike[strike]


def _select_put_spread_candidate(
    chain: pd.DataFrame,
    trade_date: date,
    target_dte: int,
    tolerance: int,
    short_delta_target: float,
    long_delta_target: float,
) -> tuple[date | None, pd.Series | None, pd.Series | None]:
    expiry = _best_expiration(chain, trade_date, target_dte, tolerance)
    if expiry is None:
        return None, None, None
    puts = chain[(chain["expiration"] == expiry) & (chain["call_put"] == "P")]
    if puts.empty:
        return expiry, None, None

    target_short = -abs(short_delta_target)
    target_long = -abs(long_delta_target)
    short_row = min(
        [row for _, row in puts.iterrows()],
        key=lambda row: abs((_safe_float(row.get("delta")) or -1.0) - target_short),
    )
    short_strike = float(short_row["strike"])
    lower_puts = puts[puts["strike"] < short_strike]
    if lower_puts.empty:
        return expiry, short_row, None

    long_row = min(
        [row for _, row in lower_puts.iterrows()],
        key=lambda row: abs((_safe_float(row.get("delta")) or -1.0) - target_long),
    )
    return expiry, short_row, long_row


def _entry_credit_from_rows(strategy: str, rows: tuple[pd.Series, ...]) -> float:
    mids = [_mid(row) for row in rows]
    if any(mid is None for mid in mids):
        return 0.0
    if strategy == "short_straddle":
        return float(mids[0] + mids[1])
    return float(mids[0] - mids[1])


def _margin_requirement(
    strategy: str,
    spot: float,
    contract_multiplier: int,
    entry_credit: float,
    short_strike: float | None,
    long_strike: float | None,
) -> tuple[float, float]:
    if strategy == "short_straddle":
        gross = 0.20 * spot * contract_multiplier
        credit_value = max(0.0, entry_credit * contract_multiplier)
        margin = max(0.10 * spot * contract_multiplier, gross - credit_value)
        return margin, margin
    if short_strike is None or long_strike is None:
        return 0.0, 0.0
    width = max(0.0, short_strike - long_strike)
    max_loss = max(0.0, (width - entry_credit) * contract_multiplier)
    return max_loss, max_loss


def _mark_and_delta_for_leg(
    leg: PositionLeg,
    trade_date: date,
    spot: float,
    quote_map: dict[tuple[date, float, str], pd.Series],
) -> tuple[float, float]:
    key = (leg.expiration, leg.strike, leg.option_right)
    row = quote_map.get(key)
    if row is not None:
        mid = _mid(row)
        delta = _safe_float(row.get("delta"))
        if mid is not None and delta is not None:
            return mid, delta
    if trade_date >= leg.expiration:
        return _intrinsic(leg.option_right, leg.strike, spot), 0.0
    return leg.last_mark, leg.entry_delta


def _signed_leg_multiplier(side: str) -> int:
    return -1 if side == "SELL" else 1


def _compute_open_trade_state(
    trade: OpenTrade,
    trade_date: date,
    spot: float,
    quote_map: dict[tuple[date, float, str], pd.Series],
    contract_multiplier: int,
) -> tuple[float, float]:
    total_value = 0.0
    total_delta = 0.0
    for leg in trade.legs:
        mark, delta = _mark_and_delta_for_leg(leg, trade_date, spot, quote_map)
        leg.last_mark = mark
        sign = _signed_leg_multiplier(leg.side)
        total_value += sign * mark * leg.quantity * contract_multiplier
        total_delta += sign * delta * leg.quantity * contract_multiplier
    return total_value, total_delta


def _resolve_code_version() -> str:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return sha or "unknown"
    except Exception:
        return "unknown"


def _event_transition_allowed(previous: str | None, current: str) -> bool:
    if previous is None:
        return current == "ENTRY"
    if previous == "EXIT":
        return False
    allowed = {
        "ENTRY": {"HEDGE", "REBALANCE", "ROLL", "EXIT"},
        "HEDGE": {"HEDGE", "REBALANCE", "ROLL", "EXIT"},
        "REBALANCE": {"HEDGE", "REBALANCE", "ROLL", "EXIT"},
        "ROLL": {"ENTRY", "HEDGE", "REBALANCE", "EXIT"},
    }
    return current in allowed.get(previous, set())


def run_simulation(config: SimulationConfig, raw_config: dict, config_digest: str) -> SimulationResult:
    """Run the short straddle and put spread simulation and persist CSV artifacts."""
    market = MarketData.from_dolt(config)
    run_id = f"sim_{config.run.start_date}_{config.run.end_date}_{config_digest[:12]}"
    output_dir = Path(config.run.output_root) / run_id

    daily_rows: list[dict] = []
    trades_rows: list[dict] = []
    event_rows: list[dict] = []
    eligibility_rows: list[dict] = []
    screen_rows: list[dict] = []
    plan_rows: list[dict] = []
    risk_rows: list[dict] = []

    open_trades: dict[tuple[str, str], OpenTrade] = {}
    trade_sequence = 1
    event_state: dict[str, str] = {}
    cumulative_portfolio_pnl = 0.0
    current_equity = config.run.initial_equity

    dates = [
        trade_date
        for trade_date in market.trading_dates()
        if config.run.start_date <= trade_date <= config.run.end_date
    ]

    for trade_date in dates:
        date_strategy_margin: dict[str, float] = {"short_straddle": 0.0, "put_credit_spread": 0.0}
        for symbol in config.run.symbols:
            spot = market.get_spot(trade_date, symbol)
            chain = market.get_option_chain(trade_date, symbol)
            if spot is None:
                continue
            quote_map = _quote_lookup(chain)
            iv_current, hv_current = market.get_iv_hv(trade_date, symbol)
            vix_close = market.get_vix(trade_date)

            for strategy in ("short_straddle", "put_credit_spread"):
                key = (strategy, symbol)
                trade = open_trades.get(key)
                if trade is None:
                    continue

                option_value, option_delta = _compute_open_trade_state(
                    trade=trade,
                    trade_date=trade_date,
                    spot=spot,
                    quote_map=quote_map,
                    contract_multiplier=config.run.contract_multiplier,
                )
                option_pnl = option_value - trade.last_option_value
                trade.last_option_value = option_value

                hedge_pnl = 0.0
                if trade.last_spot is not None:
                    hedge_pnl += float(trade.hedge_shares) * (spot - trade.last_spot)
                trade.last_spot = spot

                dte = int((trade.expiration - trade_date).days)
                exit_reason = None
                if strategy == "short_straddle" and dte <= config.straddle.close_dte:
                    exit_reason = "PRE_EXPIRY_CLOSE"
                if strategy == "put_credit_spread":
                    short_put_strike = max(leg.strike for leg in trade.legs if leg.side == "SELL")
                    entry_credit_value = trade.entry_credit * config.run.contract_multiplier
                    profit_ratio = (
                        (entry_credit_value + option_value) / entry_credit_value
                        if entry_credit_value > 0
                        else 0.0
                    )
                    if profit_ratio >= config.put_credit_spread.early_profit_take:
                        exit_reason = "EARLY_PROFIT_TARGET"
                    elif dte <= config.put_credit_spread.close_dte_itm and spot < short_put_strike:
                        exit_reason = "ITM_NEAR_EXPIRY_ROLL"
                    elif dte <= 0:
                        exit_reason = "EXPIRED"

                if exit_reason is not None:
                    fees = config.run.transaction_fee_per_contract * len(trade.legs)
                    closing_notional = option_value
                    slip = _slippage_cost(closing_notional, config.run.slippage_bps)
                    option_pnl -= fees + slip

                    closing_event_type = "EXIT"
                    if strategy == "put_credit_spread" and exit_reason == "ITM_NEAR_EXPIRY_ROLL":
                        closing_event_type = "ROLL"

                    if strategy == "short_straddle" and trade.hedge_shares != 0:
                        hedge_notional = trade.hedge_shares * spot
                        hedge_slip = _slippage_cost(hedge_notional, config.run.slippage_bps)
                        hedge_pnl -= hedge_slip
                        trade.hedge_shares = 0
                        if not _event_transition_allowed(event_state.get(trade.trade_id), "EXIT"):
                            raise ValueError(f"Invalid event transition to EXIT for {trade.trade_id}")

                    if not _event_transition_allowed(event_state.get(trade.trade_id), closing_event_type):
                        raise ValueError(
                            f"Invalid event transition to {closing_event_type} for {trade.trade_id}"
                        )

                    event_rows.append(
                        {
                            "run_id": run_id,
                            "trade_id": trade.trade_id,
                            "date": trade_date.isoformat(),
                            "event_type": closing_event_type,
                            "event_price": round(abs(option_value) / config.run.contract_multiplier, 6),
                            "event_qty": len(trade.legs),
                            "fees": round(fees, 6),
                            "slippage": round(slip, 6),
                            "notes": exit_reason,
                        }
                    )
                    event_state[trade.trade_id] = closing_event_type
                    trade.last_option_value = 0.0
                else:
                    if strategy == "short_straddle":
                        target_shares = int(round(-option_delta))
                        share_delta = target_shares - trade.hedge_shares
                        if share_delta != 0:
                            event_type = "HEDGE" if trade.hedge_shares == 0 else "REBALANCE"
                            if not _event_transition_allowed(event_state.get(trade.trade_id), event_type):
                                raise ValueError(
                                    f"Invalid event transition to {event_type} for {trade.trade_id}"
                                )
                            hedge_notional = share_delta * spot
                            hedge_slip = _slippage_cost(hedge_notional, config.run.slippage_bps)
                            hedge_pnl -= hedge_slip
                            trade.hedge_shares = target_shares
                            event_rows.append(
                                {
                                    "run_id": run_id,
                                    "trade_id": trade.trade_id,
                                    "date": trade_date.isoformat(),
                                    "event_type": event_type,
                                    "event_price": round(spot, 6),
                                    "event_qty": share_delta,
                                    "fees": 0.0,
                                    "slippage": round(hedge_slip, 6),
                                    "notes": "delta_rebalance",
                                }
                            )
                            event_state[trade.trade_id] = event_type

                total_pnl = option_pnl + hedge_pnl
                trade.cumulative_option_pnl += option_pnl
                trade.cumulative_hedge_pnl += hedge_pnl
                cumulative_portfolio_pnl += total_pnl
                current_equity = config.run.initial_equity + cumulative_portfolio_pnl

                daily_rows.append(
                    {
                        "run_id": run_id,
                        "date": trade_date.isoformat(),
                        "strategy": strategy,
                        "symbol": symbol,
                        "trade_id": trade.trade_id,
                        "option_pnl": round(option_pnl, 6),
                        "hedge_pnl": round(hedge_pnl, 6),
                        "total_pnl": round(total_pnl, 6),
                        "cum_pnl": round(cumulative_portfolio_pnl, 6),
                        "margin_used": round(trade.margin_used, 6),
                        "max_risk": round(trade.max_risk, 6),
                        "vix_close": vix_close,
                        "iv_current": iv_current,
                        "hv_current": hv_current,
                    }
                )

                if exit_reason is not None:
                    realized = trade.cumulative_option_pnl + trade.cumulative_hedge_pnl
                    days_held = int((trade_date - trade.entry_date).days)
                    trades_rows.append(
                        {
                            "run_id": run_id,
                            "trade_id": trade.trade_id,
                            "strategy": strategy,
                            "symbol": symbol,
                            "entry_date": trade.entry_date.isoformat(),
                            "exit_date": trade_date.isoformat(),
                            "entry_dte": int((trade.expiration - trade.entry_date).days),
                            "entry_expiration": trade.expiration.isoformat(),
                            "entry_credit": round(trade.entry_credit, 6),
                            "max_risk": round(trade.max_risk, 6),
                            "exit_reason": exit_reason,
                            "realized_pnl": round(realized, 6),
                            "return_on_risk": round(realized / trade.max_risk, 6) if trade.max_risk > 0 else 0.0,
                            "days_held": days_held,
                        }
                    )
                    del open_trades[key]

                else:
                    date_strategy_margin[strategy] += trade.margin_used

            for strategy in ("short_straddle", "put_credit_spread"):
                key = (strategy, symbol)
                if key in open_trades:
                    continue

                if strategy == "short_straddle":
                    expiry, leg_short_call, leg_short_put = _select_straddle_candidate(
                        chain=chain,
                        trade_date=trade_date,
                        spot=spot,
                        target_dte=config.straddle.target_dte,
                        tolerance=config.straddle.dte_tolerance,
                    )
                    candidate_rows = [row for row in (leg_short_call, leg_short_put) if row is not None]
                    strike_short = float(leg_short_call["strike"]) if leg_short_call is not None else None
                    strike_long = None
                else:
                    expiry, leg_short_put, leg_long_put = _select_put_spread_candidate(
                        chain=chain,
                        trade_date=trade_date,
                        target_dte=config.put_credit_spread.target_dte,
                        tolerance=config.put_credit_spread.dte_tolerance,
                        short_delta_target=config.put_credit_spread.short_delta_target,
                        long_delta_target=config.put_credit_spread.long_delta_target,
                    )
                    candidate_rows = [row for row in (leg_short_put, leg_long_put) if row is not None]
                    strike_short = float(leg_short_put["strike"]) if leg_short_put is not None else None
                    strike_long = float(leg_long_put["strike"]) if leg_long_put is not None else None

                gate_data_pass = len(candidate_rows) == (2 if strategy == "short_straddle" else 2)
                gate_liquidity_pass = gate_data_pass and all(
                    _spread_pct(row) <= config.filters.max_spread_pct for row in candidate_rows
                )
                strategy_uses_vix_gate = (
                    config.run.gate_short_straddle
                    if strategy == "short_straddle"
                    else config.run.gate_put_credit_spread
                )
                gate_vix_pass = (not strategy_uses_vix_gate) or (
                    vix_close is not None and vix_close > config.run.vix_gate_threshold
                )

                entry_credit = 0.0
                if gate_data_pass:
                    rows_tuple = tuple(candidate_rows)
                    entry_credit = _entry_credit_from_rows(strategy, rows_tuple)

                candidate_margin, candidate_max_risk = _margin_requirement(
                    strategy=strategy,
                    spot=spot,
                    contract_multiplier=config.run.contract_multiplier,
                    entry_credit=entry_credit,
                    short_strike=strike_short,
                    long_strike=strike_long,
                )
                open_margin = sum(tr.margin_used for tr in open_trades.values())
                equity_cap = max(1.0, current_equity) * config.run.max_margin_utilization
                gate_margin_pass = (open_margin + candidate_margin) <= equity_cap if candidate_margin > 0 else False

                fail_reason = ""
                if not gate_data_pass:
                    fail_reason = "missing_candidate_legs"
                elif not gate_liquidity_pass:
                    fail_reason = "liquidity_gate_failed"
                elif not gate_vix_pass:
                    fail_reason = "vix_gate_failed"
                elif not gate_margin_pass:
                    fail_reason = "margin_gate_failed"

                eligibility_rows.append(
                    {
                        "run_id": run_id,
                        "date": trade_date.isoformat(),
                        "strategy": strategy,
                        "symbol": symbol,
                        "expiration": expiry.isoformat() if expiry is not None else None,
                        "strike_short": strike_short,
                        "strike_long": strike_long,
                        "gate_vix_pass": bool(gate_vix_pass),
                        "gate_liquidity_pass": bool(gate_liquidity_pass),
                        "gate_data_pass": bool(gate_data_pass),
                        "gate_margin_pass": bool(gate_margin_pass),
                        "fail_reason": fail_reason,
                    }
                )

                vrp = None
                if iv_current is not None and hv_current is not None:
                    vrp = iv_current - hv_current
                score = 0.0
                if gate_data_pass and gate_liquidity_pass:
                    avg_spread = sum(_spread_pct(row) for row in candidate_rows) / len(candidate_rows)
                    score = max(0.0, (vrp or 0.0)) + max(0.0, 1.0 - avg_spread)
                screen_rows.append(
                    {
                        "run_id": run_id,
                        "date": trade_date.isoformat(),
                        "strategy": strategy,
                        "symbol": symbol,
                        "expiration": expiry.isoformat() if expiry is not None else None,
                        "strike_short": strike_short,
                        "strike_long": strike_long,
                        "vix_close": vix_close,
                        "iv_current": iv_current,
                        "hv_current": hv_current,
                        "vrp": vrp,
                        "candidate_score": round(score, 6),
                        "is_eligible": bool(not fail_reason),
                        "fail_reason": fail_reason,
                    }
                )

                if fail_reason:
                    continue

                if expiry is None:
                    continue
                if strategy == "short_straddle":
                    assert leg_short_call is not None and leg_short_put is not None
                    legs = [
                        PositionLeg(
                            option_right="C",
                            strike=float(leg_short_call["strike"]),
                            expiration=expiry,
                            side="SELL",
                            quantity=1,
                            entry_price=float(_mid(leg_short_call) or 0.0),
                            entry_delta=float(_safe_float(leg_short_call.get("delta")) or 0.0),
                            last_mark=float(_mid(leg_short_call) or 0.0),
                        ),
                        PositionLeg(
                            option_right="P",
                            strike=float(leg_short_put["strike"]),
                            expiration=expiry,
                            side="SELL",
                            quantity=1,
                            entry_price=float(_mid(leg_short_put) or 0.0),
                            entry_delta=float(_safe_float(leg_short_put.get("delta")) or 0.0),
                            last_mark=float(_mid(leg_short_put) or 0.0),
                        ),
                    ]
                else:
                    assert leg_short_put is not None and leg_long_put is not None
                    legs = [
                        PositionLeg(
                            option_right="P",
                            strike=float(leg_short_put["strike"]),
                            expiration=expiry,
                            side="SELL",
                            quantity=1,
                            entry_price=float(_mid(leg_short_put) or 0.0),
                            entry_delta=float(_safe_float(leg_short_put.get("delta")) or 0.0),
                            last_mark=float(_mid(leg_short_put) or 0.0),
                        ),
                        PositionLeg(
                            option_right="P",
                            strike=float(leg_long_put["strike"]),
                            expiration=expiry,
                            side="BUY",
                            quantity=1,
                            entry_price=float(_mid(leg_long_put) or 0.0),
                            entry_delta=float(_safe_float(leg_long_put.get("delta")) or 0.0),
                            last_mark=float(_mid(leg_long_put) or 0.0),
                        ),
                    ]

                trade_id = f"{strategy}_{symbol}_{trade_sequence:06d}"
                trade_sequence += 1
                initial_option_value = sum(
                    _signed_leg_multiplier(leg.side)
                    * leg.entry_price
                    * leg.quantity
                    * config.run.contract_multiplier
                    for leg in legs
                )
                open_trades[key] = OpenTrade(
                    trade_id=trade_id,
                    strategy=strategy,
                    symbol=symbol,
                    entry_date=trade_date,
                    expiration=expiry,
                    entry_credit=entry_credit,
                    max_risk=candidate_max_risk,
                    margin_used=candidate_margin,
                    legs=legs,
                    last_option_value=initial_option_value,
                    hedge_shares=0,
                    last_spot=spot,
                )
                date_strategy_margin[strategy] += candidate_margin

                existing_keys = [trade.trade_id for trade in open_trades.values()]
                if len(existing_keys) != len(set(existing_keys)):
                    raise ValueError("Duplicate trade_id detected in open trades")

                if not _event_transition_allowed(event_state.get(trade_id), "ENTRY"):
                    raise ValueError(f"Invalid event transition to ENTRY for {trade_id}")
                fees = config.run.transaction_fee_per_contract * len(legs)
                slip = _slippage_cost(initial_option_value, config.run.slippage_bps)
                event_rows.append(
                    {
                        "run_id": run_id,
                        "trade_id": trade_id,
                        "date": trade_date.isoformat(),
                        "event_type": "ENTRY",
                        "event_price": round(abs(initial_option_value) / config.run.contract_multiplier, 6),
                        "event_qty": len(legs),
                        "fees": round(fees, 6),
                        "slippage": round(slip, 6),
                        "notes": "entry_open",
                    }
                )
                event_state[trade_id] = "ENTRY"

                cumulative_portfolio_pnl -= fees + slip
                current_equity = config.run.initial_equity + cumulative_portfolio_pnl
                daily_rows.append(
                    {
                        "run_id": run_id,
                        "date": trade_date.isoformat(),
                        "strategy": strategy,
                        "symbol": symbol,
                        "trade_id": trade_id,
                        "option_pnl": round(-(fees + slip), 6),
                        "hedge_pnl": 0.0,
                        "total_pnl": round(-(fees + slip), 6),
                        "cum_pnl": round(cumulative_portfolio_pnl, 6),
                        "margin_used": round(candidate_margin, 6),
                        "max_risk": round(candidate_max_risk, 6),
                        "vix_close": vix_close,
                        "iv_current": iv_current,
                        "hv_current": hv_current,
                    }
                )
                plan_rows.append(
                    {
                        "run_id": run_id,
                        "date": trade_date.isoformat(),
                        "strategy": strategy,
                        "symbol": symbol,
                        "trade_id": trade_id,
                        "expiration": expiry.isoformat(),
                        "strike_short": strike_short,
                        "strike_long": strike_long,
                        "entry_credit": round(entry_credit, 6),
                        "max_risk": round(candidate_max_risk, 6),
                    }
                )

        for strategy in ("short_straddle", "put_credit_spread"):
            strategy_open = [t for t in open_trades.values() if t.strategy == strategy]
            total_margin = sum(t.margin_used for t in strategy_open)
            risk_rows.append(
                {
                    "run_id": run_id,
                    "date": trade_date.isoformat(),
                    "strategy": strategy,
                    "open_trades": len(strategy_open),
                    "margin_used": round(total_margin, 6),
                    "equity": round(current_equity, 6),
                    "margin_utilization": round(
                        total_margin / max(1.0, current_equity),
                        6,
                    ),
                }
            )

    write_simulation_artifacts(
        output_dir=output_dir,
        daily_rows=daily_rows,
        trades_rows=trades_rows,
        event_rows=event_rows,
        eligibility_rows=eligibility_rows,
        screen_rows=screen_rows,
        plan_rows=plan_rows,
        risk_rows=risk_rows,
    )
    write_run_manifest(
        output_dir=output_dir,
        payload={
            "run_id": run_id,
            "start_date": config.run.start_date.isoformat(),
            "end_date": config.run.end_date.isoformat(),
            "symbols": list(config.run.symbols),
            "config_digest": config_digest,
            "code_version": _resolve_code_version(),
            "data_repo_path": config.run.data_repo_path,
            "row_counts": {
                "daily_pnl_timeseries": len(daily_rows),
                "trades_timeseries": len(trades_rows),
                "trade_events_timeseries": len(event_rows),
                "eligibility_timeseries": len(eligibility_rows),
            },
            "config": raw_config,
        },
    )
    return SimulationResult(
        run_id=run_id,
        output_dir=output_dir,
        trade_count=len(trades_rows),
        daily_rows=len(daily_rows),
    )
