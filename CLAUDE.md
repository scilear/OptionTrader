# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run full pipeline (ingest → regime → compute metrics/alerts/ideas)
python scripts/run_pipeline.py

# Run Streamlit UI
./scripts/run_streamlit.sh dev    # test DB
./scripts/run_streamlit.sh prod   # production DB

# Run all tests
pytest tests/

# Run a single test file
pytest tests/test_alerts_logic.py

# Run a single test by name
pytest tests/test_alerts_logic.py::test_pessimistic_gate_blocks

# Seed test database with synthetic data
python scripts/seed_test_db.py

# Override config path
OPTIONTRADER_CONFIG=config/config-test.yaml python scripts/run_pipeline.py

# Reset database schema
OPTIONTRADER_RESET_DB=1 python -c "from src.db.init_db import init_db; init_db()"

# Option chain tool (IB primary, yfinance fallback)
./tools/option_chain.sh --ticker GLD --dte 21
./tools/option_chain.sh --ticker SPX --expiry 2025-04-17 --delta-range 0.10 0.35
./tools/option_chain.sh --ticker AAPL --dte 30 --output csv > chain.csv
./tools/option_chain.sh --ticker GLD --dte 21 --no-ib   # yfinance only

# IV rank / term structure tool
./tools/iv_rank.sh --ticker GLD
./tools/iv_rank.sh --ticker SPX --lookback 252
./tools/iv_rank.sh --ticker AAPL --output json
./tools/iv_rank.sh --ticker GLD --no-cache   # bypass 1-day history cache
```

## Architecture

**OptionTrader** is a signal-first volatility surface analysis tool for SPX options. It detects relative-value dislocations in the vol surface and maps them to tradable structures, with execution realism (pessimistic bid/ask validation) as a first-class design principle.

### Data Pipeline

```
yfinance → snapshots + option_quotes → iv_points (delta grid) → surface_metrics → alerts → trade_ideas
```

Orchestrated by `scripts/run_pipeline.py`, which calls three stages:
1. `ingest/ingest_yfinance.py` — fetch SPX option chains, run quote QC
2. `core/regime.py` — classify daily regime (Calm/Transition/Stress)
3. `core/compute_snapshot.py` — solve IVs, compute metrics, generate alerts, build trade ideas

### Database

Single-file DuckDB at `data/optiontrader.duckdb` (or `data/test_optiontrader.duckdb` for tests). 7 tables: `snapshots`, `option_quotes`, `iv_points`, `surface_metrics`, `regime_state`, `alerts`, `trade_ideas`. Schema in `src/db/schema.sql`. Connection via `src/db/connection.py`.

### Core Modules (`src/core/`)

| Module | Role |
|--------|------|
| `iv_solve.py` | Black-Scholes IV solving, strike-from-delta, Greeks |
| `metrics.py` | Surface metrics per expiry bucket: RR25, Fly25, Term Slope, Event Premium |
| `alerts.py` | Z-score alerts (60-day rolling window), persistence filter (≥2 consecutive), pessimistic gate |
| `trade_ideas.py` | Maps alert types → structure templates (SkewFade, 1x2x1 Fly, ATM Calendar) with leg pricing |
| `regime.py` | Classifies regime from VIX%ile, RV20%ile, drawdown |
| `qc.py` | Quote validation: crossed quotes, zero-bid, wide spreads (15% gate) |
| `tradability.py` | Median spread % as tradability score |
| `compute_snapshot.py` | Main computation orchestrator |

### Alert Logic

- **Types**: `RR_EXTREME`, `FLY_EXTREME`, `TERM_KINK`
- **Gate 1**: Z-score ≥ 2.0 on 60-day rolling window
- **Gate 2**: Persistence — must fire on ≥2 consecutive snapshots
- **Gate 3**: Pessimistic — worst-case bid/ask z-score must also exceed threshold
- **Gate 4**: Regime filter — e.g., no skew-selling alerts in Stress regime

### IV Validity Tiers

- **Full**: All 5 delta points valid (0.10, 0.25, 0.50 per side), spread ≤15% → full alert suite
- **Core**: ATM + 25D valid → core alerts only
- **None**: Missing ATM or 25D → no alerts

### Configuration

YAML config at `config/config-v1.yaml` (prod) or `config/config-test.yaml` (dev). Loaded from `$OPTIONTRADER_CONFIG` env var or default path. Key sections: `data`, `storage`, `metrics`, `quality`, `alerts`, `regime`, `structures`.

### Standalone Tools (`tools/`)

| Tool | Wrapper | Role |
|------|---------|------|
| `option_chain.py` | `option_chain.sh` | Fetch full option chain for any ticker with BS Greeks (delta, gamma, vega, theta), IV solve, stale/wide-spread flags, IV rank. IB primary, yfinance fallback. Output: table / JSON / CSV. |
| `iv_rank.py` | `iv_rank.sh` | IV rank (0–100%), IV percentile, and ATM term structure (14/21/30/60/90 DTE) for any ticker. RV-proxy approach from 1-year yfinance history. 1-day cache in `data/cache/`. IB for live spot. Signals: elevated (>75) / depressed (<25). |

Both tools are DB-free (no DuckDB dependency) and safe to run independently of the pipeline.

### UI

Streamlit app (`src/app/streamlit_app.py`) with 6 pages: Alerts Dashboard, Metric Explorer, Alert Detail, Replay, Event Study, Health.

### Key Formulas

```
RR25(T)   = IV_call(+0.25Δ, T) - IV_put(-0.25Δ, T)
Fly25(T)  = 0.5*(IV_call(+0.25Δ,T) + IV_put(-0.25Δ,T)) - IV_ATM(T)
TermSlope = IV_ATM(front) - IV_ATM(back)
EventPrem = Var(T) - SMA(Var, window=3)  where Var(T) = IV_ATM(T)² * T
```
