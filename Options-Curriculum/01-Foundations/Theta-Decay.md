---
title: Theta Decay
tags:
  - foundations
  - greeks
  - options-selling
  - income-strategies
aliases:
  - Time Decay
  - Theta
status: draft
related:
  - "[[Greeks-Overview]]"
  - "[[50pct-vs-Expiry]]"
  - "[[IV-Rank]]"
---

# Theta Decay

Theta measures how much an option's price erodes with the passage of one calendar day, all else equal. It is expressed as a negative number for long positions: a theta of −0.05 means the option loses $5 per contract per day from time value alone. For sellers who are net short options, theta appears as a positive cash flow — time works in their favor.

> [!note]
> Theta captures only the time-value component of an option's price. Intrinsic value (the in-the-money amount) does not decay. A deep ITM option therefore has very little theta relative to its total price.

## The Acceleration Curve

Theta is non-linear. At 90 DTE, decay is slow and nearly linear. As expiration approaches, decay accelerates — particularly inside the final 21–30 days. This is the "gamma risk zone": theta is at its fastest, but gamma (sensitivity of delta to price moves) is also peaking. A large overnight gap can wipe out weeks of collected premium.

![[chart-theta-decay-curve.png]]

The curve shape is roughly proportional to the square root of time remaining: an option with 25 DTE decays roughly twice as fast as one with 100 DTE, not four times (rule of thumb, not exact).

## Why Sellers Benefit

An option seller collects the full premium upfront. Each day that passes without a large adverse move, the option's theoretical value declines. The seller can buy it back at a lower price, realizing a profit. This is the core mechanics of [[Greeks-Overview#Theta|theta harvesting]].

The profitability of a theta strategy depends on whether realized volatility (actual price movement) stays below implied volatility (the vol priced into the option). See [[IV-Rank]] for how to assess whether implied vol is rich or cheap before selling.

## The Sweet Spot: 21–45 DTE

Most income-strategy practitioners (covered calls, cash-secured puts, iron condors, strangles) target the 21–45 DTE window.

- **Too far out (> 60 DTE):** Theta is slow; premium collected per day is low relative to vega exposure. A vol expansion punishes the position hard before time decay compensates.
- **Too close (< 21 DTE):** Theta is fastest, but gamma is extreme. A single large move can exceed the entire premium collected. Bid/ask spreads also widen relative to premium.
- **21–45 DTE:** Decay is accelerating, gamma is manageable, and there is still enough premium to justify the trade.

> [!tip]
> The 45 DTE entry is widely used by systematic sellers (data-backed by TastyTrade research across SPX and ETF underlyings) because it balances theta capture with manageable gamma and enough time to adjust before expiration.

## Theta vs. Vega Tradeoff

Selecting strike distance involves a tradeoff between theta income and vega exposure:

- **ATM options** have the highest theta (dollar terms) but also the highest vega. A vol spike hits hard.
- **Further OTM options** have lower theta (less premium) but also lower vega — a vol expansion hurts less in absolute dollar terms.

For sellers in high-IV environments ([[IV-Rank]] > 50), wider strikes (lower delta) are common because elevated vol means more premium is available further OTM while vega risk per dollar collected is lower.

## The 50% Profit Rule

A well-established (and empirically supported) management rule: **close the position when you have captured 50% of the maximum possible profit** — i.e., when the option or spread has lost half its original value.

This matters because theta decay is asymptotic. The last half of the premium requires holding through the highest-gamma, highest-risk period near expiration for a diminishing return. Exiting at 50% realizes most of the edge while shedding the tail risk. See [[50pct-vs-Expiry]] for a detailed comparison of P&L outcomes.

> [!warning]
> Holding short options to expiration to "collect the last few cents" significantly increases the probability of a catastrophic loss from a late-term gap move. Gamma near expiration means delta can swing from near-zero to near-one overnight. The expected value of that final 50% of premium does not compensate for the tail risk in most underlyings.

> [!danger]
> Naked short options with no hedge have theoretically unlimited loss potential. Theta strategies should be implemented with defined risk (spreads) or with substantial capital reserves and active position monitoring. Not suitable for beginners.
