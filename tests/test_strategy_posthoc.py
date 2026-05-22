from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.strategy_sim.posthoc import compute_kept_trade_ids, reaggregate_daily_pnl


def test_compute_kept_trade_ids(tmp_path: Path) -> None:
    eligibility = pd.DataFrame(
        [
            {
                "date": "2026-01-02",
                "strategy": "short_straddle",
                "symbol": "SPY",
                "gate_vix_pass": True,
                "gate_liquidity_pass": True,
                "gate_data_pass": True,
                "gate_margin_pass": True,
            },
            {
                "date": "2026-01-03",
                "strategy": "short_straddle",
                "symbol": "SPY",
                "gate_vix_pass": False,
                "gate_liquidity_pass": True,
                "gate_data_pass": True,
                "gate_margin_pass": True,
            },
        ]
    )
    trades = pd.DataFrame(
        [
            {
                "trade_id": "short_straddle_SPY_000001",
                "strategy": "short_straddle",
                "symbol": "SPY",
                "entry_date": "2026-01-02",
            },
            {
                "trade_id": "short_straddle_SPY_000002",
                "strategy": "short_straddle",
                "symbol": "SPY",
                "entry_date": "2026-01-03",
            },
        ]
    )
    eligibility_csv = tmp_path / "eligibility.csv"
    trades_csv = tmp_path / "trades.csv"
    eligibility.to_csv(eligibility_csv, index=False)
    trades.to_csv(trades_csv, index=False)

    kept = compute_kept_trade_ids(eligibility_csv=eligibility_csv, trades_csv=trades_csv)
    assert kept == {"short_straddle_SPY_000001"}


def test_reaggregate_daily_pnl(tmp_path: Path) -> None:
    daily = pd.DataFrame(
        [
            {
                "date": "2026-01-02",
                "strategy": "short_straddle",
                "symbol": "SPY",
                "trade_id": "short_straddle_SPY_000001",
                "option_pnl": 10.0,
                "hedge_pnl": 2.0,
                "total_pnl": 12.0,
            },
            {
                "date": "2026-01-03",
                "strategy": "short_straddle",
                "symbol": "SPY",
                "trade_id": "short_straddle_SPY_000002",
                "option_pnl": -3.0,
                "hedge_pnl": 0.0,
                "total_pnl": -3.0,
            },
        ]
    )
    path = tmp_path / "daily.csv"
    daily.to_csv(path, index=False)
    out = reaggregate_daily_pnl(path, {"short_straddle_SPY_000001"})
    assert len(out) == 1
    assert float(out.iloc[0]["total_pnl"]) == 12.0
