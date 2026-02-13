# UX Spec v1 (Streamlit)

## User Flow
Alerts Dashboard -> Metric Explorer -> Alert Detail

## Screen 1: Alerts Dashboard
Purpose: surface the best signals and make a quick decision.

Components:
- Alerts table with columns:
  - Signal (RR/Fly/Term)
  - Bucket (e.g., 21D/30D/45D)
  - Severity (z-score)
  - Tradability score
  - Regime label (Calm/Transition/Stress)
  - Confidence tier (Full/Core)
  - Survives pessimistic pricing (Yes/No)
  - Why (short explanation)

Actions:
- Filter by signal, bucket, regime, confidence tier
- Toggle optimistic vs pessimistic views
- Open alert detail

Data required:
- Alert list with z-scores (mid/worst), tradability score, regime, tier, persistence

## Screen 2: Metric Explorer
Purpose: validate that the signal is real and understand context.

Components:
- Time-series charts for RR25, Fly25, ATM term slope
- Z-score overlays
- Regime bands (Calm/Transition/Stress)
- Event markers (FOMC/CPI)

Actions:
- Select metric
- Select bucket
- Adjust date range
- Compare mid vs pessimistic

Data required:
- Metric time series (mid/worst)
- Regime series
- Event calendar tags

## Screen 3: Alert Detail
Purpose: explain the signal and show 2–3 candidate structures.

Components:
- Explainability card:
  - Why it fired
  - Persistence
  - Regime fit
  - Confidence tier
  - Pessimistic survivability
- Structure menu:
  - 2–3 trade ideas
  - Leg list, price (mid/worst), greeks, max loss
- Risk labels:
  - short gamma, tail risk, event gap, liquidity
- Scenario snapshot:
  - simple spot x vol shift grid

Actions:
- Compare structures
- View scenario grid
- Export trade idea (json)

## UX Guardrails
- No 3D surface in v1
- Always show mid vs pessimistic side-by-side
- Every alert must teach: "Why it matters" + "Main risk"
- Confidence tier must be visible at all times
