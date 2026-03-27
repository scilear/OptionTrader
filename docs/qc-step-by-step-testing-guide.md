# QuantConnect Step-by-Step Testing Guide

## Current Constraint

QuantConnect rejected the current full validator file with:

`File main.py not saved. It exceeds the maximum size of 32000 characters`

Current local file size:

- [spx_pipeline_validator.py](/home/fabien/Documents/OptionTrader/quantconnect/spx_pipeline_validator.py)

This means the current full validator is too large to paste directly into QC `main.py` as-is.

For now, use this guide as the runbook for the workflow and treat the current QC code as the reference implementation. If needed, the next step is to produce a compact QC-uploadable version focused on one mode at a time.

## Goal

Run QuantConnect in three passes:

1. fast signal scan
2. focused quote validation
3. full virtual-trade validation

Primary files:

- [spx_pipeline_validator.py](/home/fabien/Documents/OptionTrader/quantconnect/spx_pipeline_validator.py)
- [quantconnect-research-notebook.md](/home/fabien/Documents/OptionTrader/docs/quantconnect-research-notebook.md)
- [quantconnect-validator.md](/home/fabien/Documents/OptionTrader/docs/quantconnect-validator.md)

## Recommended Order

1. `RR_EXTREME`, `30D`, `2024`, signal scan
2. research notebook on the top 3 candidate days from that run
3. `RR_EXTREME`, `30D`, trade validation on those exact days
4. `RR_EXTREME`, `30D`, full virtual-trade validation
5. repeat for `45D`
6. repeat for `TERM_KINK`, `30D`
7. leave `FLY_EXTREME` for last

## Phase 1: Fast Signal Scan

Purpose:

- measure signal density
- measure worst-case survival
- identify candidate days worth deeper inspection

### Backtest Parameters

Use these QC parameters:

```text
research_mode=signal_scan
start_year=2024
start_month=1
start_day=1
end_year=2024
end_month=12
end_day=31
alert_filter=RR_EXTREME
bucket_filter=30D
eval_frequency_minutes=120
use_weeklys=true
z_threshold=2.0
persistence_required=2
spread_gate_pct=0.15
min_open_interest=100
max_candidate_days=10
max_validation_snapshots=50
```

### What To Read In Logs

Look for:

- `SUMMARY`
- `CANDIDATE_DAYS`

Important fields:

- `signals_mid_passed`
- `signals_worst_passed`
- `signals_tradable`
- `worst_pass_rate`
- `tradable_rate`
- `conversion_rate`

### How To Interpret

- low `signals_mid_passed`: signal too rare or filters too tight
- low `worst_pass_rate`: spread/worst-case pricing kills the edge
- low `tradable_rate`: structure mapping or OI/spread gates are too strict
- `CANDIDATE_DAYS`: use these in notebook validation and trade-validation runs

### Recommended Phase 1 Runs

Run each separately:

1. `RR_EXTREME`, `30D`, `2024`
2. `RR_EXTREME`, `45D`, `2024`
3. `TERM_KINK`, `30D`, `2024`
4. `FLY_EXTREME`, `30D`, `2024`

## Phase 2: Focused Quote Validation In Research

Purpose:

- validate only the strongest candidate dates
- inspect quote-level spread and IV reconstruction
- avoid full-year minute-history pulls

### Notebook File

Use:

- [quantconnect-research-notebook.md](/home/fabien/Documents/OptionTrader/docs/quantconnect-research-notebook.md)

### Cell 2 Parameters For First Pass

Set:

```python
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

ALERT_FILTER = "RR_EXTREME"
BUCKET_FILTER = "30D"

DAILY_CHUNK_MONTHS = 1
MAX_CANDIDATE_DAYS = 3
```

### Notebook Execution Order

1. Run Cells 1-8 only.
2. Review:
   - `daily_alerts`
   - monthly signal counts
   - `SELECTED_DAYS`
3. If the selected days look sane, run Cells 9-16.

### Stability Rules

- do not start with 2023-2024 together
- start with 2024 only
- use one alert type only
- use one bucket only
- keep `MAX_CANDIDATE_DAYS <= 3`
- keep `DAILY_CHUNK_MONTHS = 1`

If still heavy:

1. reduce to 6 months
2. reduce `MAX_CANDIDATE_DAYS` to `2`

### What To Check

- how many daily alerts survive quote-level validation?
- do `rr25_worst`, `fly25_worst`, `term_slope_worst` still confirm the setup?
- are OI and spread conditions acceptable?
- do the same few dates remain strong after quote-level validation?

## Phase 3: Trade Validation Mode

Purpose:

- validate signal-to-tradability on selected dates
- avoid running a full year of virtual trades

### Backtest Parameters

Replace the candidate days with the dates from Phase 1 or the notebook:

```text
research_mode=trade_validation
start_year=2024
start_month=1
start_day=1
end_year=2024
end_month=12
end_day=31
alert_filter=RR_EXTREME
bucket_filter=30D
eval_frequency_minutes=120
trade_validation_days=2024-04-15,2024-04-17,2024-07-18
max_validation_snapshots=20
use_weeklys=true
z_threshold=2.0
persistence_required=2
spread_gate_pct=0.15
min_open_interest=100
```

### What To Check

Read:

- `signals_mid_passed`
- `signals_worst_passed`
- `signals_tradable`
- `worst_pass_rate`
- `tradable_rate`

This is the cleanest bridge between signal quality and execution realism.

## Phase 4: Full Virtual-Trade Validation

Purpose:

- test holding-period behavior
- test path dependence and overlapping exposure
- test virtual trade outcomes after the signal is already credible

### Backtest Parameters

```text
research_mode=full
start_year=2024
start_month=1
start_day=1
end_year=2024
end_month=12
end_day=31
alert_filter=RR_EXTREME
bucket_filter=30D
eval_frequency_minutes=120
use_weeklys=true
z_threshold=2.0
persistence_required=2
spread_gate_pct=0.15
min_open_interest=100
max_open_trades=2
max_hold_days=10
```

### Rules

- only one alert type at a time
- only one bucket at a time
- only one year at a time
- do not mix all signals yet

## What To Record For Every Run

Capture:

- parameter set
- `signals_mid_passed`
- `signals_worst_passed`
- `signals_tradable`
- `worst_pass_rate`
- `tradable_rate`
- `conversion_rate`
- `trades_opened`
- `closed_trades`
- `win_rate`
- `avg_pnl`
- `CANDIDATE_DAYS`

A spreadsheet is enough.

## Decision Rules

Promote a setup only if:

- `worst_pass_rate` is acceptable
- `tradable_rate` is acceptable
- notebook quote validation confirms the same dates
- full-mode virtual PnL is not just spread illusion

Reject or rework if:

- signals vanish under worst-case pricing
- tradability is too low
- results depend on a few isolated outlier days

## Strong First Benchmark

Start with:

1. `RR_EXTREME`
2. `30D`
3. `2024`
4. `signal_scan`

That is the cleanest first benchmark.

## Practical Note

Because the full QC validator file currently exceeds the QC `main.py` save limit, the most practical next implementation step is:

1. create a compact QC upload file for `signal_scan`
2. create a second compact QC upload file for `trade_validation` / `full`

That keeps each QC file under the platform size limit and matches the phased workflow above.
