---
title: Put-Call Parity
tags:
  - foundations
  - options-basics
  - pricing
aliases:
  - Put-call parity
  - Parity relationship
status: draft
related:
  - "[[Options-Basics]]"
  - "[[Implied-Volatility]]"
---

# Put-Call Parity

Put-call parity is a fundamental relationship between call prices, put prices, strike, and spot price. It holds in liquid, no-arbitrage markets.

## The Equation

```
Call Price - Put Price = Spot - Strike (discounted by risk-free rate)
```

**Example:** SPX at 5000, risk-free rate ≈ 0% (ignore discounting)
- 5100 call: $50
- 5100 put: $100
- **Parity check:** $50 - $100 = -$50 ✓ (Spot - Strike = 5000 - 5100 = -$100, so parity holds with no rounding)

## Trading Application

If a call and put at the same strike deviate from parity, an **arbitrage opportunity** exists:
- **Overpriced call:** Sell call, buy put, buy stock → lock in profit
- **Overpriced put:** Buy call, sell put, sell stock short → lock in profit

In practice, arbitrage opportunities vanish in liquid markets due to fast traders. Parity holds.

## Key Insight

Parity shows that calls and puts are *linked*. You cannot price one without considering the other. A cheap call at a strike implies an expensive put at that same strike, and vice versa.
