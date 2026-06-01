---
title: IV Rank and IV Percentile
tags:
  - foundations
  - volatility
  - screening
  - regime-classification
aliases:
  - IV Rank
  - IV Percentile
  - Volatility ranking
status: draft
related:
  - "[[Implied-Volatility]]"
  - "[[IV-vs-HV]]"
  - "[[IV-Rank]]"
  - "[[IV-Percentile]]"
---

# IV Rank and IV Percentile

Both IV Rank and IV Percentile answer the same question: **Is current IV cheap or expensive relative to the past?** They are closely related but calculate the answer differently.

## IV Rank

**Definition:** The percentile rank of current IV within the past year's (252-day) range.

**Formula:**
```
IV Rank = (Current IV - 52-week low IV) / (52-week high IV - 52-week low IV) × 100%
```

**Example:** SPX last year: IV low = 10, IV high = 40. Today: IV = 25
- IV Rank = (25 - 10) / (40 - 10) × 100 = 50%

**Interpretation:**
- IV Rank 0–25%: Cheap IV (low end of range)
- IV Rank 25–75%: Neutral
- IV Rank 75–100%: Expensive IV (high end of range)

## IV Percentile

**Definition:** The percentage of days in the past year where IV was *lower* than today's IV.

**Example:** If IV was below today's level on 180 days of the past 252 days:
- IV Percentile = 180/252 = 71%

**Interpretation:**
- IV Percentile 0–25%: IV is very low (cheapest levels of the year)
- IV Percentile 25–75%: IV is in middle of range
- IV Percentile 75–100%: IV is very high (most expensive levels of the year)

## The Key Difference

| | IV Rank | IV Percentile |
|---|---|---|
| Measures | Position in range | Frequency |
| Focus | Are we at highs or lows? | Are we in the bulk of the distribution? |
| Timing | Fast on new highs/lows | Smoothed, lagged |

**Scenario:** IV spikes from 20 to 40, a new 52-week high.
- IV Rank = 100% (at the top of the year's range)
- IV Percentile = 100% (IV was lower on all past 252 days)

Both say "expensive," but from different angles.

## Trading Application

**For premium sellers:**
- Entry bias: IV Rank > 60% or IV Percentile > 75% → favorable for selling
- Avoid: IV Rank < 30% or IV Percentile < 25% → edge is thin

**For premium buyers:**
- Entry bias: IV Rank < 30% or IV Percentile < 25% → favorable for buying
- Avoid: IV Rank > 70% or IV Percentile > 75% → paying peak prices

**But context overrides percentiles.** An IV Rank of 40% (neutral) one day before earnings is still "cheap" relative to post-announcement expectations. Always cross-check with the [[Earnings-Overview|earnings calendar]].

## Limitations

1. **Rank is sensitive to outliers.** One spike to 60 vol a year ago sets the high. Any vol < 60 will look "cheap" on rank.
2. **Percentile lags spikes.** In an up spike, percentile gets dragged down (more days are now below the new high).
3. **Single number, multiple regimes.** IV Rank doesn't distinguish between "calm + elevated" and "vol expansion just starting."

Use [[IV-vs-HV|IV vs HV spread]] as a complementary measure for edge confirmation.
