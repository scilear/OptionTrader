from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.strategy_sim.artifacts import (
    DAILY_PNL_COLUMNS,
    ELIGIBILITY_COLUMNS,
    EVENT_COLUMNS,
    PLAN_COLUMNS,
    RISK_COLUMNS,
    SCREEN_COLUMNS,
    TRADES_COLUMNS,
    write_run_manifest,
    write_simulation_artifacts,
)


def test_write_simulation_artifacts_schema_columns(tmp_path: Path) -> None:
    output_dir = tmp_path / "sim"
    write_simulation_artifacts(
        output_dir=output_dir,
        daily_rows=[],
        trades_rows=[],
        event_rows=[],
        eligibility_rows=[],
        screen_rows=[],
        plan_rows=[],
        risk_rows=[],
    )

    daily = pd.read_csv(output_dir / "daily_pnl_timeseries.csv")
    trades = pd.read_csv(output_dir / "trades_timeseries.csv")
    events = pd.read_csv(output_dir / "trade_events_timeseries.csv")
    eligibility = pd.read_csv(output_dir / "eligibility_timeseries.csv")
    screen = pd.read_csv(output_dir / "screen_candidates.csv")
    plan = pd.read_csv(output_dir / "trade_plan.csv")
    risk = pd.read_csv(output_dir / "risk_report.csv")

    assert list(daily.columns) == DAILY_PNL_COLUMNS
    assert list(trades.columns) == TRADES_COLUMNS
    assert list(events.columns) == EVENT_COLUMNS
    assert list(eligibility.columns) == ELIGIBILITY_COLUMNS
    assert list(screen.columns) == SCREEN_COLUMNS
    assert list(plan.columns) == PLAN_COLUMNS
    assert list(risk.columns) == RISK_COLUMNS


def test_write_run_manifest(tmp_path: Path) -> None:
    output_dir = tmp_path / "sim"
    payload = {"run_id": "sim_test", "code_version": "sha"}
    write_run_manifest(output_dir, payload)
    content = json.loads((output_dir / "run_manifest.json").read_text())
    assert content == payload
