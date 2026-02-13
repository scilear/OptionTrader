# Stories (v1)

## EPIC-01 Ingestion & Data Quality

### ST-01 Ingest snapshot and quotes
AC:
- Inserts snapshot record with ts/spot/source/session_tag
- Inserts option_quotes with bid/ask/last/oi/volume
- Uses config symbol and DTE window

### ST-02 QC flags on ingest
AC:
- Crossed quotes excluded (AT-01)
- Zero-bid excluded unless allow_zero_bid (AT-02)
- Wide spread flagged (AT-03)

## EPIC-02 IV Solve & Metrics

### ST-10 IV solver interface
AC:
- iv_points table populated with solve_status
- Supports mid/bid/ask pricing

### ST-11 Delta grid extraction
AC:
- Delta buckets: ATM, ±25D, ±10D
- AT-21 satisfied

### ST-12 Metrics computation
AC:
- RR/Fly/Term metrics computed per expiry bucket
- Z-scores computed with rolling window

## EPIC-03 Alert Engine

### ST-20 Tiered IV validity
AC:
- Full/Core/None tiers enforced (AT-10/11/12)

### ST-21 Pessimistic pricing gate
AC:
- Alerts suppressed when z_worst fails (AT-31)

### ST-22 Persistence and regime filter
AC:
- Persistence >= 2 snapshots
- Stress regime suppresses skew selling (AT-32)

### ST-23 Explainability payload
AC:
- Every alert includes why/persistence/regime/tier (AT-50/51)

## EPIC-04 Trade Idea Generator

### ST-30 Map alerts to structures
AC:
- RR -> skew fade, Fly -> fly/BWF, Term -> calendar
- Pricing includes mid and worst case

### ST-31 Risk labels and greeks
AC:
- Risk flags (short gamma, tail, liquidity) attached

## EPIC-05 Streamlit UI

### ST-40 Alerts dashboard
AC:
- Shows alert list with tier + pessimistic flag

### ST-41 Metric explorer
AC:
- RR/Fly/Term series render by bucket

### ST-42 Alert detail
AC:
- Explainability card + trade ideas

## EPIC-06 Replay/Backtest

### ST-50 Replay determinism
AC:
- Same snapshots => same metrics/alerts (AT-40/41)

### ST-51 Feature event study
AC:
- Reversion time, MAE/MFE by regime

## EPIC-07 Acceptance & Regression

### ST-60 Acceptance test suite
AC:
- All AT-* tests implemented and passing
