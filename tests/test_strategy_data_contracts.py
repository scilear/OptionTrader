from __future__ import annotations

from datetime import date
from pathlib import Path

from src.strategy_sim.data_contracts import (
    build_data_quality_reports,
    validate_data_contracts,
)


def test_validate_data_contracts_fails_on_missing_table(tmp_path: Path) -> None:
    repo = tmp_path / "missing_repo"
    repo.mkdir(parents=True, exist_ok=True)
    import pandas as pd

    def fake_query(_repo_path: str | Path, _query: str) -> pd.DataFrame:
        return pd.DataFrame()

    import src.strategy_sim.data_contracts as contracts

    original = contracts.run_dolt_query
    contracts.run_dolt_query = fake_query
    try:
        try:
            validate_data_contracts(repo)
            assert False, "expected ValueError"
        except ValueError as exc:
            assert "Missing required Dolt tables" in str(exc)
    finally:
        contracts.run_dolt_query = original


def test_build_data_quality_reports_writes_csv(monkeypatch, tmp_path: Path) -> None:
    import pandas as pd

    def fake_query(_repo_path: str | Path, query: str) -> pd.DataFrame:
        if "FROM option_chain" in query and "GROUP BY act_symbol" in query and "option_rows" in query:
            return pd.DataFrame(
                {
                    "symbol": ["SPY"],
                    "option_rows": [100],
                    "option_date_min": ["2026-01-02"],
                    "option_date_max": ["2026-01-31"],
                }
            )
        if "FROM volatility_history" in query and "vol_rows" in query:
            return pd.DataFrame(
                {
                    "symbol": ["SPY"],
                    "vol_rows": [50],
                }
            )
        if "FROM underlying_prices_daily" in query and "underlying_rows" in query:
            return pd.DataFrame(
                {
                    "symbol": ["SPY"],
                    "underlying_rows": [20],
                }
            )
        if "FROM vix_daily" in query and "vix_rows" in query:
            return pd.DataFrame({"vix_rows": [20]})
        if "FROM option_chain" in query and "bid_null_count" in query:
            return pd.DataFrame(
                {
                    "symbol": ["SPY"],
                    "total_rows": [100],
                    "bid_null_count": [0],
                    "ask_null_count": [0],
                    "delta_null_count": [0],
                }
            )
        if "FROM volatility_history" in query and "iv_null_count" in query:
            return pd.DataFrame(
                {
                    "symbol": ["SPY"],
                    "total_rows": [50],
                    "iv_null_count": [1],
                    "hv_null_count": [0],
                }
            )
        if "expirations_near_target" in query:
            return pd.DataFrame(
                {
                    "date": ["2026-01-02"],
                    "symbol": ["SPY"],
                    "expirations_near_target": [2],
                }
            )
        return pd.DataFrame()

    monkeypatch.setattr("src.strategy_sim.data_contracts.run_dolt_query", fake_query)
    output = build_data_quality_reports(
        repo_path="unused",
        symbols=("SPY",),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        target_dte=30,
        dte_tolerance=5,
        output_dir=tmp_path,
    )
    assert output["coverage"].exists()
    assert output["null_diagnostics"].exists()
    assert output["dte_availability"].exists()
