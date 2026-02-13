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
