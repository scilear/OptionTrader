---
title: Range-Bound Strategies
tags: [options, strategy, market-conditions, range-bound, neutral]
aliases: [Rangebound Market Playbook, Range-Bound Market Strategies, Neutral Market Strategies]
status: draft
related:
  - "[[Iron-Condor]]"
  - "[[Iron-Fly]]"
  - "[[Market-Condition-Classification]]"
  - "[[Adjust-vs-Close]]"
---

# Range-Bound Strategies

A range-bound market is one where price oscillates between defined support and resistance without making sustained directional progress. This is the ideal environment for premium sellers running market-neutral structures.

## Identifying a Range

Do not assume a range exists — confirm it before trading into it:

- **Bollinger Bands contracting** — bandwidth declining over 10+ days signals decreasing realized volatility and range compression
- **ATR declining** — the 14-day Average True Range is shrinking, confirming smaller daily moves
- **At least three touches** — price has bounced off the same support level and reversed at the same resistance level at least three times each
- **No trend structure** — no sequence of higher highs / higher lows or lower highs / lower lows

> [!note]
> Ranges can persist for weeks or months, particularly on major indices during low-macro-volatility periods. They can also break violently on news events. Identification is a prerequisite, not a guarantee.

## Best Strategies for Range-Bound Markets

### Iron Condor

The [[Iron-Condor]] is the canonical range-bound trade. Short strikes at or just inside the range boundaries; long strikes further out for protection.

- **Short strikes**: place at or just inside the range extremes (tested support and resistance)
- **Long strikes**: 1–2 strikes further out for defined risk
- **Target credit**: ≥ 1/3 of the width of the spread (rule of thumb)
- **DTE**: 21–35 days — gives the range time to persist without requiring you to hold through expiration

### Iron Fly

The [[Iron-Fly]] is appropriate when the range is very tight and price clusters near a central midpoint. The short straddle at the center collects maximum premium but has a narrow breakeven.

- Best when the stock has been pinned near a single price level for multiple sessions
- Requires more active management than an IC due to the tighter profit zone
- Not recommended for beginners given the limited margin for error

> [!danger]
> The Iron Fly is unsuitable for beginners. The narrow profit zone and high theta/gamma sensitivity means a moderate move against you can erase the entire credit before you can react. Use the IC until you have experience managing short straddle risk.

### Butterfly

The long butterfly (e.g., buy 1 put, sell 2 puts at midpoint, buy 1 put lower) profits when price expires at the midpoint of the range. It is a cheaper structure than the IC but requires price to stay pinned near the center strike.

- Useful as a low-cost, defined-risk neutral trade when you have high confidence in a specific price magnet
- Maximum profit only realized at expiration — partial profits can be taken early if price converges on the middle strike

## Entry Rules

> [!tip]
> Sell at range extremes only. Entering an IC in the middle of a range gives you no edge — you are selling strikes near current price, and the first move in either direction will immediately test your short strike. Wait for price to reach resistance before entering the call side, or wait for a touch of support before entering the put side.

Staged entry can improve the trade:
1. Price touches resistance → sell the call spread
2. Price pulls back to support → sell the put spread to complete the IC

This means you may be legging into the IC rather than entering it as a single order.

## Failure Mode: Breakout

Ranges break. This is the primary risk. Define your response before entering:

- **Stop at the range boundary** — if price closes beyond the support or resistance level on a daily basis, the range is in question
- **Close the IC** — do not hold an IC through a range breakout; the position that was market-neutral is now deeply directional against you
- **See [[Adjust-vs-Close]]** for the decision framework on whether to roll or exit

> [!warning]
> A range breakout on an IC will quickly move the breached side from 0.20 delta to 0.40–0.50 delta. At that point, the short strike is no longer "far OTM." If you do not have a predefined exit, you are hoping for a reversal — hope is not a risk management strategy.

## DTE and Monitoring

- **21–35 DTE on entry** gives you a theta curve that is not too steep but still meaningful
- Avoid entries with more than 45 DTE in ranges — you are exposed to too many potential breakout events over a longer window
- Check the position daily against the range boundaries; no need for intraday monitoring unless price is near a boundary

## Quick Reference

| Range Width | Best Structure | Notes |
|---|---|---|
| Wide (> 10% of stock price) | Iron Condor | Standard; wide strikes, 21–35 DTE |
| Tight (< 5% of stock price) | Iron Fly | High risk; advanced only |
| Price near midpoint consistently | Butterfly | Defined-risk, low cost |

See also: [[Market-Condition-Classification]] for identifying when a range regime transitions to a trend.
