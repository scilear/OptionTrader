---
title: High IV Playbook
tags: [options, volatility, strategy, market-conditions, playbook]
aliases: [High Volatility Playbook, Elevated IV Trading]
status: draft
related:
  - "[[Iron-Condor]]"
  - "[[Bull-Put-Spread]]"
  - "[[IV-Rank]]"
  - "[[Market-Condition-Classification]]"
---

# High IV Playbook

**Threshold**: [[IV-Rank]] > 50, VIX > 20. When implied volatility is elevated, the market is pricing in large future moves. For options sellers, this is the primary opportunity window — but it demands discipline on sizing and structure.

## Why High IV Favors Sellers

When IV rank is above 50, the premium embedded in options is rich relative to historical norms. Two structural forces work in the seller's favor:

1. **Mean reversion tendency** — IV is a mean-reverting quantity. When it spikes, it tends to eventually contract. Sellers who collect elevated premium benefit as vega decays and IV normalizes. This is empirically observed across equity indices, though timing is unpredictable.
2. **Elevated theta** — Higher IV inflates the absolute value of time decay. A 45 DTE position in a high-IV environment collects more premium per day than the same structure in low IV.

> [!note]
> "High IV" does not guarantee favorable outcomes — it means the market is paying you more to take on the same structural risk. The risk itself is also higher.

## Strategies to Deploy

### Index Iron Condors (SPY, QQQ, SPX)

The [[Iron-Condor]] on broad indices is the natural trade in elevated IV. The wide expected move gives you room to set strikes further OTM while still collecting meaningful credit.

- Target 0.15–0.20 delta on both the put and call sides
- Use 30–45 DTE for a balanced theta/gamma profile
- Look for credit ≥ 1/3 of the width of the spread (rule of thumb, not a guaranteed edge)

### Cash-Secured Puts on Quality Stocks

The [[Bull-Put-Spread]] or outright CSP on names you genuinely want to own at the strike price. High IV inflates the put premium, improving your effective entry price if assigned.

- Only use on stocks with strong fundamentals you are comfortable owning
- Confirm the strike is at a level you consider fair value or better

### Bull Put Spreads

Defined-risk alternative to naked CSPs. Spreads cap your loss if the stock collapses, which matters most in high-IV/high-stress environments.

## Strike Selection in High IV

When IV is elevated, the market's expected move is wider. Adjust accordingly:

- **Widen condor wings** — with larger expected moves, tighter strikes will be breached more often
- **Go further OTM** — target 1.0–1.5 standard deviation strikes rather than the tighter 1 sigma, to account for the fat-tailed distribution that high IV implies
- Do not squeeze for premium by moving strikes closer. This is a common mistake that backfires in volatile regimes.

## Size Down: This Is Critical

High IV means the market is pricing in large moves. Your positions need room to breathe, and your emotional bandwidth is finite.

**Rule of thumb (not statistically derived):** Reduce position size 25–50% compared to your normal sizing in low-volatility environments. A standard-sized IC that goes wrong in a 30 VIX environment can move against you far faster than you can manage.

> [!warning]
> High IV environments correlate with volatile markets — your IC can still lose even at wide strikes. A gap open of 3–5% is not unusual when VIX is above 25. Wide strikes do not eliminate gap risk.

## When to Enter

Timing matters. Do not enter on the day of a volatility spike — IV may spike further, and you are not selling at the peak.

**Better entry signal**: IV rank is elevated (> 50) but has **plateaued or begun to pull back** from its recent high. You are selling into stability, not into panic.

> [!tip]
> Wait for the VIX to close below its 5-day high before initiating new short-premium positions. Entering on the day of maximum fear often means selling into a vol trend that has further to run.

## What to Avoid

- **Undefined risk positions** (naked calls, naked puts) — in volatile markets, tail events occur more frequently than models predict
- **Calendars and diagonals** — these are long-vega structures; if IV drops sharply after your entry, both legs lose value and the trade deteriorates even if price stays flat
- **New LEAPS purchases** — long-dated options are expensive in high IV; you are paying peak premium for time value that may erode rapidly as IV normalizes

## Quick Reference

| Condition | Action |
|---|---|
| IV rank > 50, VIX plateauing | Enter IC on SPY/QQQ, CSP on quality stocks |
| IV rank > 70, market panicking | Wait — do not enter during the spike; if entering, size at 25% of normal |
| IV rank dropping from > 50 | Ideal window; vega tailwind begins working in your favor |
| Trend breaking down sharply | Shift IC to put spreads only; close call side |

See also: [[Market-Condition-Classification]] for how regime context interacts with IV level.
