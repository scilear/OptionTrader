from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from src.strategy_sim.dolt import run_dolt_query
from src.strategy_sim.types import SimulationConfig


REQUIRED_OPTION_COLUMNS = (
    "date",
    "act_symbol",
    "expiration",
    "strike",
    "call_put",
    "bid",
    "ask",
    "delta",
)


@dataclass
class MarketData:
    option_chain: pd.DataFrame
    underlying_prices: pd.DataFrame
    volatility_history: pd.DataFrame
    vix_daily: pd.DataFrame

    def __post_init__(self) -> None:
        self.option_chain = self.option_chain.copy()
        self.underlying_prices = self.underlying_prices.copy()
        self.volatility_history = self.volatility_history.copy()
        self.vix_daily = self.vix_daily.copy()

        for column in ("date", "expiration"):
            if column in self.option_chain.columns:
                self.option_chain[column] = pd.to_datetime(self.option_chain[column]).dt.date
        if "date" in self.underlying_prices.columns:
            self.underlying_prices["date"] = pd.to_datetime(self.underlying_prices["date"]).dt.date
        if "date" in self.volatility_history.columns:
            self.volatility_history["date"] = pd.to_datetime(self.volatility_history["date"]).dt.date
        if "date" in self.vix_daily.columns:
            self.vix_daily["date"] = pd.to_datetime(self.vix_daily["date"]).dt.date

        self.option_chain["call_put"] = self.option_chain["call_put"].astype(str).str.upper().str[:1]

        self.option_chain_groups = {
            (key[0], key[1]): frame.reset_index(drop=True)
            for key, frame in self.option_chain.groupby(["date", "act_symbol"])
        }
        self.spot_map = {
            (row["date"], row["act_symbol"]): float(row["close"])
            for _, row in self.underlying_prices.iterrows()
        }
        self.iv_hv_map = {
            (row["date"], row["act_symbol"]): (
                float(row["iv_current"]) if pd.notna(row["iv_current"]) else None,
                float(row["hv_current"]) if pd.notna(row["hv_current"]) else None,
            )
            for _, row in self.volatility_history.iterrows()
        }
        self.vix_map = {
            row["date"]: float(row["close"]) for _, row in self.vix_daily.iterrows() if pd.notna(row["close"])
        }

    @classmethod
    def from_dolt(cls, config: SimulationConfig) -> "MarketData":
        start = config.run.start_date.isoformat()
        end = config.run.end_date.isoformat()
        symbols_sql = ", ".join(f"'{s}'" for s in config.run.symbols)
        repo_path = config.run.data_repo_path

        option_chain = run_dolt_query(
            repo_path,
            f"""
            SELECT date, act_symbol, expiration, strike, call_put, bid, ask, delta
            FROM option_chain
            WHERE date >= '{start}'
              AND date <= '{end}'
              AND act_symbol IN ({symbols_sql})
              AND bid IS NOT NULL
              AND ask IS NOT NULL
              AND delta IS NOT NULL
            ORDER BY date, act_symbol, expiration, strike, call_put
            """,
        )
        underlying = run_dolt_query(
            repo_path,
            f"""
            SELECT date, act_symbol, close
            FROM underlying_prices_daily
            WHERE date >= '{start}'
              AND date <= '{end}'
              AND act_symbol IN ({symbols_sql})
            ORDER BY date, act_symbol
            """,
        )
        vol_hist = run_dolt_query(
            repo_path,
            f"""
            SELECT date, act_symbol, iv_current, hv_current
            FROM volatility_history
            WHERE date >= '{start}'
              AND date <= '{end}'
              AND act_symbol IN ({symbols_sql})
            ORDER BY date, act_symbol
            """,
        )
        vix = run_dolt_query(
            repo_path,
            f"""
            SELECT date, close
            FROM vix_daily
            WHERE date >= '{start}'
              AND date <= '{end}'
            ORDER BY date
            """,
        )

        missing_columns = [col for col in REQUIRED_OPTION_COLUMNS if col not in option_chain.columns]
        if missing_columns:
            raise ValueError(f"option_chain missing columns: {', '.join(missing_columns)}")
        if underlying.empty:
            raise ValueError("underlying_prices_daily query returned no rows")
        if vix.empty:
            raise ValueError("vix_daily query returned no rows")

        return cls(
            option_chain=option_chain,
            underlying_prices=underlying,
            volatility_history=vol_hist,
            vix_daily=vix,
        )

    def trading_dates(self) -> list[date]:
        from_dates = set(self.underlying_prices["date"].tolist())
        return sorted(from_dates)

    def get_option_chain(self, trade_date: date, symbol: str) -> pd.DataFrame:
        return self.option_chain_groups.get((trade_date, symbol), pd.DataFrame())

    def get_spot(self, trade_date: date, symbol: str) -> float | None:
        return self.spot_map.get((trade_date, symbol))

    def get_iv_hv(self, trade_date: date, symbol: str) -> tuple[float | None, float | None]:
        return self.iv_hv_map.get((trade_date, symbol), (None, None))

    def get_vix(self, trade_date: date) -> float | None:
        return self.vix_map.get(trade_date)
