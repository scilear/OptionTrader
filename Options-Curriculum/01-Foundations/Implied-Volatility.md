---
title: Implied Volatility (IV)
tags:
  - foundations
  - volatility
  - options-pricing
aliases:
  - IV
  - Implied Vol
status: draft
related:
  - "[[IV-vs-HV]]"
  - "[[IV-Rank]]"
  - "[[IV-Percentile]]"
  - "[[Vega]]"
  - "[[Options-Basics]]"
---

# Implied Volatility (IV)

Implied volatility is the volatility figure that, when plugged into the Black-Scholes model, produces the option's current market price. It is **forward-looking** — the market's collective forecast of how much the underlying will move over the life of the option.

## Definition

IV is not a prediction by any single person or algorithm. It is the volatility figure *implied* by what buyers and sellers are willing to pay *right now*. It reflects:
- Uncertainty about the future
- Demand for hedges (VIX calls, long puts)
- Supply of premium sellers (strangles, condors)
- Event risk (earnings, macro data, geopolitical)

All compressed into a single number quoted annualized (e.g., "30 vol").

## How IV is Used in Practice

### Daily Move Estimation

IV is annualized. To convert to daily move, use:

```
Daily move ≈ Spot × IV ÷ √252
```

Example: SPX at 5000, IV at 20
- Daily move ≈ 5000 × 0.20 ÷ √252 ≈ ±63 points (1 std dev)

This is the expected daily range on a typical day *before* factoring in specific events.

### Option Pricing

Higher IV → higher option prices (both calls and puts). This is [[Vega|vega]] in action:

- IV = 15: SPX 5050 call priced at $10
- IV = 25: SPX 5050 call priced at $16 (same strike, same DTE, higher IV)

Premium sellers harvest the difference when IV compresses.

## IV vs HV (Implied vs Historical)

- **IV** = forward-looking, market consensus, embedded in option prices
- **HV** = backward-looking, realized actual moves over past 20/30/60 days

The gap between them is the [[IV-vs-HV|Volatility Risk Premium (VRP)]] — the structural edge that options sellers exploit.

Empirically, IV exceeds HV roughly 75–80% of the time on SPX over long periods. But on any given trade, context matters: check [[IV-Rank]] and [[IV-Percentile]] for regime context.

## IV Across Strikes: Skew

IV is not constant across all strikes. A phenomenon called **skew** or **smile** causes:
- OTM puts to have higher IV than ATM
- OTM calls to have lower IV than ATM (or vice versa in certain markets)

This reflects risk asymmetry: the market prices tail-risk protection (put demand) at a premium.

Example (SPX skew):
- 4900 puts (OTM): IV = 28
- 5000 ATM calls: IV = 20
- 5100 calls (OTM): IV = 18

Skew steepens (increases) before events. A trader can sell expensive puts and buy cheaper calls to capture the skew compression post-event.

## IV During Events

- **Pre-event:** IV rises as the market prices uncertainty. A 3-day earnings announcement typically pushes IV up 5–10 vol points.
- **At announcement:** IV can double intraday if the move is large or unexpected.
- **Post-event:** IV crush — IV collapses 30–60% as uncertainty is resolved. This is where short vega positions make or lose large amounts.

## When IV is "Cheap" vs "Expensive"

Use [[IV-Rank]] or [[IV-Percentile]] to contextualize:
- **IV Rank < 30%:** Cheap relative to the past year. Premium sellers may find thin edges.
- **IV Rank 30–70%:** Neutral zone. Check [[IV-vs-HV]] spread.
- **IV Rank > 70%:** Expensive relative to the past year. Favorable for premium sellers.

But context overrides percentiles: an IV Rank of 60% one day before earnings is still "cheap" relative to post-announcement expectations.

> [!warning]
> Many traders confuse IV rank with IV level. A stock with IV Rank 75% (expensive relative to its own history) can still have an absolute IV of 15 vol (cheap compared to SPX). Always ask: "Cheap relative to *what*?" Context is everything.

## Key Takeaway

IV is the single most important variable in options trading. It moves faster than price, and understanding it separates profitable traders from losers. A seller who ignores IV spike risk has no edge. A buyer who buys into high IV close to major events is paying peak prices.
