from __future__ import annotations

from pathlib import Path

import pandas as pd


def compute_kept_trade_ids(
    eligibility_csv: str | Path,
    trades_csv: str | Path,
    *,
    require_vix_pass: bool = True,
    require_liquidity_pass: bool = True,
    require_data_pass: bool = True,
    require_margin_pass: bool = True,
) -> set[str]:
    """Return kept trade IDs by applying gate requirements to eligibility rows."""
    frame = pd.read_csv(eligibility_csv)
    required = {
        "date",
        "strategy",
        "symbol",
        "gate_vix_pass",
        "gate_liquidity_pass",
        "gate_data_pass",
        "gate_margin_pass",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"eligibility csv missing columns: {', '.join(sorted(missing))}")

    mask = pd.Series([True] * len(frame))
    if require_vix_pass:
        mask &= frame["gate_vix_pass"].astype(bool)
    if require_liquidity_pass:
        mask &= frame["gate_liquidity_pass"].astype(bool)
    if require_data_pass:
        mask &= frame["gate_data_pass"].astype(bool)
    if require_margin_pass:
        mask &= frame["gate_margin_pass"].astype(bool)

    kept_candidates = frame.loc[mask, ["date", "strategy", "symbol"]].drop_duplicates()

    trades = pd.read_csv(trades_csv)
    required_trade_columns = {"trade_id", "strategy", "symbol", "entry_date"}
    trade_missing = required_trade_columns - set(trades.columns)
    if trade_missing:
        raise ValueError(f"trades csv missing columns: {', '.join(sorted(trade_missing))}")

    joined = kept_candidates.merge(
        trades,
        how="inner",
        left_on=["date", "strategy", "symbol"],
        right_on=["entry_date", "strategy", "symbol"],
    )
    return set(joined["trade_id"].astype(str).tolist())


def reaggregate_daily_pnl(
    daily_pnl_csv: str | Path,
    kept_trade_ids: set[str],
) -> pd.DataFrame:
    """Reaggregate kept-trade daily PnL without rerunning simulation."""
    frame = pd.read_csv(daily_pnl_csv)
    required = {
        "date",
        "strategy",
        "symbol",
        "trade_id",
        "option_pnl",
        "hedge_pnl",
        "total_pnl",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"daily pnl csv missing columns: {', '.join(sorted(missing))}")

    kept = frame[frame["trade_id"].isin(kept_trade_ids)].copy()
    if kept.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "strategy",
                "total_option_pnl",
                "total_hedge_pnl",
                "total_pnl",
                "trade_count",
                "cum_pnl",
            ]
        )

    grouped = (
        kept.groupby(["date", "strategy"], as_index=False)
        .agg(
            total_option_pnl=("option_pnl", "sum"),
            total_hedge_pnl=("hedge_pnl", "sum"),
            total_pnl=("total_pnl", "sum"),
            trade_count=("trade_id", "nunique"),
        )
        .sort_values(["date", "strategy"]) 
    )
    grouped["cum_pnl"] = grouped["total_pnl"].cumsum()
    return grouped
