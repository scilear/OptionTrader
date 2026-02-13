# Acceptance Tests & TDD Plan (v1)

## Data Quality
- AT-01: crossed quotes (bid > ask) are excluded and flagged
- AT-02: zero-bid quotes excluded unless allow_zero_bid = true
- AT-03: wide spread points downgrade confidence tier (spread > 15%)

## IV Solve & Tiering
- AT-10: Tier Full requires all 5 delta points valid with spread gate
- AT-11: Tier Core requires ATM + both 25D points valid
- AT-12: Tier None => no alerts for that expiry

## Forward & Delta Consistency
- AT-20: forward derived near ATM is stable within tolerance
- AT-21: delta extraction selects nearest strike to target delta

## Alerts
- AT-30: alert requires persistence >= 2 snapshots/days
- AT-31: pessimistic pricing gate suppresses alert if z_worst fails
- AT-32: regime filter blocks skew selling in Stress

## Replay Determinism
- AT-40: recompute on same snapshot yields identical metrics
- AT-41: alert list deterministic for given snapshot series

## Explainability
- AT-50: every alert includes why/thresholds/persistence/regime
- AT-51: confidence tier displayed for each alert
