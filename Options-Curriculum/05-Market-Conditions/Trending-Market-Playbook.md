---
title: Trending Market Strategies
tags: [options, strategy, market-conditions, trend, directional]
aliases: [Trending Market Playbook, Directional Options Strategies]
status: draft
related:
  - "[[Bull-Put-Spread]]"
  - "[[Bear-Call-Spread]]"
  - "[[Market-Condition-Classification]]"
  - "[[Range-Bound-Strategies]]"
---

# Trending Market Strategies

A trending market is one where the underlying is making consistent higher highs and higher lows (uptrend) or lower highs and lower lows (downtrend). The [[Iron-Condor]] — the default strategy for many premium sellers — is a liability in trending conditions. One side will be tested with high probability, and the structure will work against you.

## Trend Identification

Before choosing a directional strategy, confirm the trend is real:

- **20-day SMA slope** — if the SMA is rising and price is above it, the uptrend is in force. If the SMA is declining and price is below it, downtrend.
- **Consecutive higher highs / lower lows** — at least three swing points in the same direction
- **Price structure** — pullbacks hold above prior lows (uptrend) or rallies fail below prior highs (downtrend)

> [!note]
> These are discretionary filters, not mechanical signals. They are useful for eliminating trades in adverse conditions, not for generating precise entries.

## Uptrend Strategies

### Sell Put Credit Spreads at Pullback Support

The [[Bull-Put-Spread]] is the natural trade in an uptrend. You sell a put spread below current support levels, collecting credit while the trend does the work. Pullbacks toward the 20-day SMA are the preferred entry timing.

- Strike selection: short put 1–2 standard deviations below current price, at or below visible support
- DTE: 21–35 days
- Exit at 50% of max profit or before the short leg reaches 0.30 delta

### Buy Call Debit Spreads for Defined-Risk Participation

For directional participation with capped risk, a call debit spread limits your loss to the premium paid while capturing upside movement.

- Target debit ≤ 50% of the width of the spread
- Choose strikes around the near-term target price
- Useful when IV is low enough that credit spreads don't offer sufficient premium

### What to Avoid in an Uptrend

- **Iron Condors** — the call side will likely be tested as price moves higher
- **Naked put selling** — unnecessary risk; a spread achieves the same directional exposure with defined loss
- **Selling calls against a rising stock** — this caps your upside and goes against the trend

> [!tip]
> Rule: In a strong uptrend, only sell puts — never sell calls against a rising stock or index. The trend is evidence that buyers are in control. Do not fight it by capping upside.

## Downtrend Strategies

### Sell Call Credit Spreads at Resistance

The [[Bear-Call-Spread]] mirrors the bull put spread logic. Sell a call spread above resistance in a confirmed downtrend, collecting credit as price continues lower or consolidates.

- Strike selection: short call 1–2 standard deviations above current price, at or above visible resistance
- Rallies to the 20-day SMA are the preferred entry timing

### Buy Put Debit Spreads

Defined-risk participation in a downtrend. Buy a put spread below current price when you expect continued decline.

- Useful in high-IV environments where the debit is partially offset by rich premium
- Exits: take profit at 50–75% of maximum gain; do not hold to expiration in fast-moving downtrends

### What to Avoid in a Downtrend

- **Iron Condors** — the put side will likely be tested
- **Selling puts on falling stocks** — even for names you want to own, catching a falling knife is a capital destruction risk

> [!warning]
> In a downtrend, selling puts on declining stocks ("I'll buy it cheaper here") is a common trap. If the stock continues lower, your spread becomes worthless and assignment at the short strike means buying into further losses. Wait for the downtrend to stabilize.

## Position Sizing in Trending Markets

Do not use full IC sizing for directional structures. Since you are expressing a one-sided view, you are taking on more directional risk than a market-neutral IC. Recommended adjustment:

- Size directional positions at 50–75% of your normal IC notional
- On the offset, you can run more concurrent positions since each is one-sided

## When the Trend Ends

Trends fail. Define your exit before entering:

- **Exit trigger**: price closes above the prior swing high (downtrend) or below the prior swing low (uptrend) on a daily close
- **SMA cross**: price crosses the 20-day SMA on a closing basis — exit directional positions promptly
- Do not average into a losing directional spread. Close it and reassess.

When the trend ends and price enters a range, transition to [[Range-Bound-Strategies]].

See also: [[Market-Condition-Classification]] for how trend regime interacts with IV level.
