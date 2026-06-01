---
title: IV Expansion Risk (Vega Risk)
tags:
  - foundations
  - risk-management
  - volatility-risk
aliases:
  - Vega risk
  - IV expansion risk
status: draft
related:
  - "[[Vega]]"
  - "[[Implied-Volatility]]"
  - "[[Gamma-Regime-and-GEX]]"
---

# IV Expansion Risk (Vega Risk)

**IV expansion risk** is the risk that implied volatility rises *against* your position. It is the primary enemy of short premium strategies.

## Example

**Setup:** Sell an iron condor with IV Rank = 70%
- **Expected:** IV compresses back to 50%
- **Actual:** Earnings/FOMC announced, IV spikes to 85%

**P&L impact:** All short premium positions lose money as all option prices rise. This happens *regardless of whether price moves against you*.

## Protection

1. **Size down** when IV is already high
2. **Check the calendar** before entering (is an event imminent?)
3. **Use defined-risk spreads** (defined vega loss is bounded)
4. **Exit when IV rises faster than expected** (don't wait for price mean reversion)

IV expansion is *more dangerous* than directional moves because it affects all legs equally and accelerates in stress regimes.
