# PRD v1 (Streamlit, Single User)

## Problem
Surface signals (skew/term/curvature) are visible but hard to translate into tradable, realistic structures. Traders often rely on mid prices and ignore execution realism, leading to false edges and poor drawdown control.

## Goal
Deliver a signal-first volatility surface tool for SPX (14–60 DTE) that detects relative-value dislocations, validates them under pessimistic pricing, and maps each signal to 2–3 structures with clear risk labels and scenario context. The system must be stable and deterministic to allow autonomous iteration without constant user oversight.

## Non-Goals
- Automated trading or routing
- 0–7 DTE strategies or intraday scalping
- American/assignment logic (SPY later)
- Arbitrage promises
- Full 3D surface visualization

## Primary Users
- Single user (Fabien) working locally
- Ultimately expand to multi-user platform for retail options traders
- Intermediate options knowledge, learning-focused

## Success Metrics
- >= 70% of alerts survive pessimistic bid/ask test
- >= 60% of suggested structures selected for review
- Alerts computed within 2 minutes of snapshot
- User can explain why an alert fired and key risks

## Scope v1
- SPX only
- 14–60 DTE
- Signals: RR25/RR10, Fly25/Fly10, ATM term slope, event premium
- Regime filter (VIX/RV20/drawdown)
- Alerts with explainability and confidence tier
- Replay/backtest (feature-level) for learning

## User Workflow
1) Open alerts dashboard and scan ranked signals
2) Inspect time-series context in metrics explorer
3) Open alert detail for structures + risk flags
4) Replay similar historical signals for learning

## Functional Requirements
- Ingest option chains into snapshots with QC flags
- Compute IV points on delta grid (mid/bid/ask)
- Compute RR/Fly/Term metrics with z-scores
- Enforce tiered IV validity + pessimistic pricing gates
- Generate alerts with explainability and confidence tier
- Provide 2–3 structure suggestions per alert
- Provide replay and deterministic recompute

## Non-Functional Requirements
- Deterministic recompute for same snapshot series
- Alert generation within 2 minutes of snapshot
- No alerts when data quality fails tier rules
- Local single-user operation without external services

## Risks
- Data quality and stale quotes driving false signals
- Overfitting z-scores without regime conditioning
- Spread drag overwhelming theoretical edge

## Dependencies
- Reliable data source (yfinance first)
- DuckDB/SQLite storage
- Ingestion job + Streamlit UI

## Assumptions
- Single user, local execution
- EOD + optional intraday snapshots are sufficient
- Execution realism (bid/ask) is mandatory

## Out of Scope (Explicit)
- Live execution or broker integration
- Multi-user access and hosted deployment
- Real-time 3D visualization
