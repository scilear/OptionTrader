# QuantConnect SPX Validator

This validator is a historical test harness for the repo's SPX surface pipeline. It is designed to answer one question first:

- do RR/Fly/term alerts survive pessimistic SPX options execution assumptions?

## What it mirrors from the local pipeline

- 14-60 DTE SPX options universe
- 21D / 30D / 45D expiry buckets
- ATM / 25d / 10d IV point reconstruction from option quotes
- `RR_EXTREME`, `FLY_EXTREME`, and `TERM_KINK`
- pessimistic gate: buy at ask, sell at bid
- persistence filter
- simple tradability gate using spread percentage and open interest

The matching local references are:

- [metrics.py](/home/fabien/Documents/OptionTrader/src/core/metrics.py)
- [alerts.py](/home/fabien/Documents/OptionTrader/src/core/alerts.py)
- [trade_ideas.py](/home/fabien/Documents/OptionTrader/src/core/trade_ideas.py)
- [compute_snapshot.py](/home/fabien/Documents/OptionTrader/src/core/compute_snapshot.py)

## What it does not mirror exactly yet

- no external regime model; it infers a rough regime from current ATM IV
- no database-backed replay window; z-scores are rolling intraday observations inside the algo
- no real order routing; trades are tracked as virtual structures with pessimistic entry and exit marks
- `RR_EXTREME` follows the current repo mapping to a bounded put spread only
- `FLY_EXTREME` uses the current 1x2x1 mapping and should be treated as a validation scaffold, not final structure design

## File

- [spx_pipeline_validator.py](/home/fabien/Documents/OptionTrader/quantconnect/spx_pipeline_validator.py)

## Suggested validation workflow

1. Run the algorithm as signal-only for 2 years of SPX/SPXW data.
2. Confirm alert counts are sparse enough to avoid fatigue.
3. Check `worst_pass_rate` first. If this is weak, do not optimize structures yet.
4. Review skipped trades caused by spread and OI gates.
5. Only after signal credibility is acceptable, tighten exits and structure mapping.

## Research Modes

The validator now supports three modes through QC parameters:

- `research_mode=signal_scan`
  - computes signals only
  - no virtual trades
  - fastest mode for ranking candidate days
- `research_mode=trade_validation`
  - computes signals and marks tradability
  - still no virtual trades
  - use with `trade_validation_days=YYYY-MM-DD,...`
- `research_mode=full`
  - computes signals, marks tradability, and runs virtual trades

Useful parameters:

- `alert_filter=ALL|RR_EXTREME|FLY_EXTREME|TERM_KINK`
- `bucket_filter=ALL|21D|30D|45D`
- `eval_frequency_minutes=60|120|240`
- `max_candidate_days=10`
- `max_validation_snapshots=50`
- `trade_validation_days=2024-04-15,2024-04-17`

The summary log now separates:

- `signals_mid_passed`
- `signals_worst_passed`
- `signals_tradable`
- `worst_pass_rate`
- `tradable_rate`
- `conversion_rate`

## First metrics to trust

- `worst_pass_rate`
- number of alerts per month
- number of trades skipped by tradability gates
- PnL under pessimistic entry and exit
- win rate by alert type

## Suggested next repo step

If this validator produces usable signal density and fillability, the next step should be extracting the pure signal code into a shared module so the local pipeline and QC harness use the exact same formulas.
