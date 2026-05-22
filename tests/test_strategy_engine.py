from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from src.strategy_sim.engine import run_simulation
from src.strategy_sim.types import (
    FilterSettings,
    PutSpreadSettings,
    RunSettings,
    SimulationConfig,
    StraddleSettings,
)


def _build_config(tmp_path: Path) -> SimulationConfig:
    return SimulationConfig(
        run=RunSettings(
            start_date=date(2026, 1, 2),
            end_date=date(2026, 1, 3),
            output_root=str(tmp_path / "artifacts"),
            symbols=("SPY",),
            data_repo_path="unused",
            contract_multiplier=100,
            initial_equity=100000.0,
            max_margin_utilization=0.5,
            transaction_fee_per_contract=1.0,
            slippage_bps=5.0,
            vix_gate_threshold=40.0,
            gate_short_straddle=False,
            gate_put_credit_spread=False,
        ),
        straddle=StraddleSettings(target_dte=30, dte_tolerance=5, close_dte=2),
        put_credit_spread=PutSpreadSettings(
            target_dte=30,
            dte_tolerance=5,
            short_delta_target=0.30,
            long_delta_target=0.10,
            early_profit_take=0.75,
            close_dte_itm=2,
        ),
        filters=FilterSettings(max_spread_pct=0.40),
    )


def _mock_market_data() -> object:
    class MockMarketData:
        def __init__(self) -> None:
            self.option_chain_groups = {}
            rows = [
                {
                    "date": date(2026, 1, 2),
                    "act_symbol": "SPY",
                    "expiration": date(2026, 2, 1),
                    "strike": 500.0,
                    "call_put": "C",
                    "bid": 10.0,
                    "ask": 10.2,
                    "delta": 0.5,
                },
                {
                    "date": date(2026, 1, 2),
                    "act_symbol": "SPY",
                    "expiration": date(2026, 2, 1),
                    "strike": 500.0,
                    "call_put": "P",
                    "bid": 9.8,
                    "ask": 10.0,
                    "delta": -0.5,
                },
                {
                    "date": date(2026, 1, 2),
                    "act_symbol": "SPY",
                    "expiration": date(2026, 2, 1),
                    "strike": 490.0,
                    "call_put": "P",
                    "bid": 5.0,
                    "ask": 5.2,
                    "delta": -0.1,
                },
                {
                    "date": date(2026, 1, 3),
                    "act_symbol": "SPY",
                    "expiration": date(2026, 2, 1),
                    "strike": 500.0,
                    "call_put": "C",
                    "bid": 9.0,
                    "ask": 9.2,
                    "delta": 0.48,
                },
                {
                    "date": date(2026, 1, 3),
                    "act_symbol": "SPY",
                    "expiration": date(2026, 2, 1),
                    "strike": 500.0,
                    "call_put": "P",
                    "bid": 8.8,
                    "ask": 9.0,
                    "delta": -0.48,
                },
                {
                    "date": date(2026, 1, 3),
                    "act_symbol": "SPY",
                    "expiration": date(2026, 2, 1),
                    "strike": 490.0,
                    "call_put": "P",
                    "bid": 4.6,
                    "ask": 4.8,
                    "delta": -0.09,
                },
            ]
            option_frame = pd.DataFrame(rows)
            self.option_chain_groups = {
                key: frame.reset_index(drop=True)
                for key, frame in option_frame.groupby(["date", "act_symbol"])
            }
            self.underlying_prices = pd.DataFrame(
                {
                    "date": [date(2026, 1, 2), date(2026, 1, 3)],
                    "act_symbol": ["SPY", "SPY"],
                    "close": [500.0, 502.0],
                }
            )
            self.spot_map = {
                (date(2026, 1, 2), "SPY"): 500.0,
                (date(2026, 1, 3), "SPY"): 502.0,
            }
            self.iv_hv_map = {
                (date(2026, 1, 2), "SPY"): (0.20, 0.15),
                (date(2026, 1, 3), "SPY"): (0.21, 0.16),
            }
            self.vix_map = {date(2026, 1, 2): 35.0, date(2026, 1, 3): 36.0}

        def trading_dates(self) -> list[date]:
            return [date(2026, 1, 2), date(2026, 1, 3)]

        def get_option_chain(self, trade_date: date, symbol: str):
            return self.option_chain_groups.get((trade_date, symbol), pd.DataFrame())

        def get_spot(self, trade_date: date, symbol: str):
            return self.spot_map.get((trade_date, symbol))

        def get_iv_hv(self, trade_date: date, symbol: str):
            return self.iv_hv_map.get((trade_date, symbol), (None, None))

        def get_vix(self, trade_date: date):
            return self.vix_map.get(trade_date)

    return MockMarketData()


def test_run_simulation_deterministic(monkeypatch, tmp_path: Path) -> None:
    config = _build_config(tmp_path)
    market = _mock_market_data()
    monkeypatch.setattr("src.strategy_sim.engine.MarketData.from_dolt", lambda _cfg: market)
    monkeypatch.setattr("src.strategy_sim.engine._resolve_code_version", lambda: "test-sha")

    raw = {"dummy": True}
    result_a = run_simulation(config=config, raw_config=raw, config_digest="abc123")
    result_b = run_simulation(config=config, raw_config=raw, config_digest="abc123")
    assert result_a.run_id == result_b.run_id

    daily_a = pd.read_csv(result_a.output_dir / "daily_pnl_timeseries.csv")
    daily_b = pd.read_csv(result_b.output_dir / "daily_pnl_timeseries.csv")
    assert daily_a.equals(daily_b)
    assert (result_a.output_dir / "run_manifest.json").exists()


def test_event_type_contract(monkeypatch, tmp_path: Path) -> None:
    config = _build_config(tmp_path)
    market = _mock_market_data()
    monkeypatch.setattr("src.strategy_sim.engine.MarketData.from_dolt", lambda _cfg: market)
    monkeypatch.setattr("src.strategy_sim.engine._resolve_code_version", lambda: "test-sha")

    result = run_simulation(config=config, raw_config={"dummy": True}, config_digest="abc123")
    events = pd.read_csv(result.output_dir / "trade_events_timeseries.csv")
    allowed = {"ENTRY", "HEDGE", "REBALANCE", "ROLL", "EXIT"}
    assert set(events["event_type"].astype(str).unique()).issubset(allowed)
