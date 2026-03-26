# Implementation Milestones (Streamlit v1)

## M0: Project Skeleton
- Repo layout
- Config file and environment setup

## Gate 1: Data Quality + Forward Consistency
- Quote QC rules implemented
- Forward estimation validated near ATM

## M1: IV Solve + Metrics Pipeline
- IV solving (mid/bid/ask)
- Delta extraction
- RR/Fly/ATM term metrics

## Gate 2: IV Solve Coverage
- Valid delta points meet tier rules
- Minimum coverage threshold met in 14–60 DTE

## M2: Alert Engine
- Z-scores, persistence filter
- Pessimistic pricing gate
- Regime model integration

## Gate 3: False-Alert Suppression
- Alerts suppressed when pessimistic pricing fails
- Confidence tier attached to each alert

## M3: Trade Idea Generator
- Phase 1 structures (skew fade, fly, calendar)
- Greeks and max loss
- Scenario snapshot

## M4: Streamlit UI
- Alerts dashboard
- Metric explorer
- Alert detail

## M5: Replay/Backtest Harness
- Recompute alerts for historical snapshots
- Feature-level event study

## M6: Acceptance Tests + Tuning
- AT-01 to AT-05
- Threshold tuning (spreads, z-scores, persistence)

---

## Standalone Tools

### T1-01: Option Chain Tool — **Done** (2026-03-26)
- `tools/option_chain.py` + `tools/option_chain.sh`
- Any ticker; `--dte` or `--expiry`; optional `--delta-range`
- Full BS Greeks (delta, gamma, vega, theta via BS formula)
- IV solved from mid price; stale/wide-spread flags
- IV rank (RV proxy from 1-year yfinance history)
- IB Gateway primary, yfinance fallback; `--no-ib` flag
- Output: table / JSON / CSV

### T1-02: IV Rank / Vol Surface Tool — **Done** (2026-03-26)
- `tools/iv_rank.py` + `tools/iv_rank.sh`
- 30D ATM IV, IV rank (0–100%), IV percentile
- ATM term structure across 14/21/30/60/90 DTE buckets
- RV-proxy from 1-year rolling 21D realized vol
- 1-day cache in `data/cache/iv_rank_{ticker}.json`
- Signals: elevated (rank > 75), depressed (rank < 25)
- IB for live spot; yfinance for option chains
