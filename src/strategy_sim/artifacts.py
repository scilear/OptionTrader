from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


DAILY_PNL_COLUMNS = [
    "run_id",
    "date",
    "strategy",
    "symbol",
    "trade_id",
    "option_pnl",
    "hedge_pnl",
    "total_pnl",
    "cum_pnl",
    "margin_used",
    "max_risk",
    "vix_close",
    "iv_current",
    "hv_current",
]

TRADES_COLUMNS = [
    "run_id",
    "trade_id",
    "strategy",
    "symbol",
    "entry_date",
    "exit_date",
    "entry_dte",
    "entry_expiration",
    "entry_credit",
    "max_risk",
    "exit_reason",
    "realized_pnl",
    "return_on_risk",
    "days_held",
]

EVENT_COLUMNS = [
    "run_id",
    "trade_id",
    "date",
    "event_type",
    "event_price",
    "event_qty",
    "fees",
    "slippage",
    "notes",
]

ELIGIBILITY_COLUMNS = [
    "run_id",
    "date",
    "strategy",
    "symbol",
    "expiration",
    "strike_short",
    "strike_long",
    "gate_vix_pass",
    "gate_liquidity_pass",
    "gate_data_pass",
    "gate_margin_pass",
    "fail_reason",
]

SCREEN_COLUMNS = [
    "run_id",
    "date",
    "strategy",
    "symbol",
    "expiration",
    "strike_short",
    "strike_long",
    "vix_close",
    "iv_current",
    "hv_current",
    "vrp",
    "candidate_score",
    "is_eligible",
    "fail_reason",
]

PLAN_COLUMNS = [
    "run_id",
    "date",
    "strategy",
    "symbol",
    "trade_id",
    "expiration",
    "strike_short",
    "strike_long",
    "entry_credit",
    "max_risk",
]

RISK_COLUMNS = [
    "run_id",
    "date",
    "strategy",
    "open_trades",
    "margin_used",
    "equity",
    "margin_utilization",
]


def _write_csv(rows: list[dict], columns: list[str], path: Path) -> None:
    frame = pd.DataFrame(rows)
    if frame.empty:
        frame = pd.DataFrame(columns=columns)
    else:
        for col in columns:
            if col not in frame.columns:
                frame[col] = None
        frame = frame[columns]
    frame.to_csv(path, index=False)


def write_simulation_artifacts(
    output_dir: Path,
    daily_rows: list[dict],
    trades_rows: list[dict],
    event_rows: list[dict],
    eligibility_rows: list[dict],
    screen_rows: list[dict],
    plan_rows: list[dict],
    risk_rows: list[dict],
) -> None:
    """Write simulation and screening artifacts to CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(daily_rows, DAILY_PNL_COLUMNS, output_dir / "daily_pnl_timeseries.csv")
    _write_csv(trades_rows, TRADES_COLUMNS, output_dir / "trades_timeseries.csv")
    _write_csv(event_rows, EVENT_COLUMNS, output_dir / "trade_events_timeseries.csv")
    _write_csv(eligibility_rows, ELIGIBILITY_COLUMNS, output_dir / "eligibility_timeseries.csv")
    _write_csv(screen_rows, SCREEN_COLUMNS, output_dir / "screen_candidates.csv")
    _write_csv(plan_rows, PLAN_COLUMNS, output_dir / "trade_plan.csv")
    _write_csv(risk_rows, RISK_COLUMNS, output_dir / "risk_report.csv")


def write_run_manifest(output_dir: Path, payload: dict) -> None:
    """Persist run manifest JSON alongside CSV artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run_manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True))
