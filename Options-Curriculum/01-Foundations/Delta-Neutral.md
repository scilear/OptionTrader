---
title: Delta-Neutral Positions
tags:
  - foundations
  - delta
  - hedging
  - structure-design
aliases:
  - Delta neutral
  - Hedged position
  - Vega position
status: draft
related:
  - "[[Delta]]"
  - "[[Gamma]]"
  - "[[Theta]]"
  - "[[Vega]]"
  - "[[Iron-Condor]]"
  - "[[Short-Straddle]]"
---

# Delta-Neutral Positions

A delta-neutral position is one where the combined [[Delta|delta]] of all legs equals zero. The position has no inherent directional bias — it does not profit or lose from upward or downward moves in the underlying, only from changes in *other* factors like volatility, time, or implied moves.

## What Does Delta-Neutral Mean?

**Delta:** The dollar amount an option price changes when the underlying moves $1.

**Delta-neutral:** The sum of deltas across all legs is zero (or close to zero).

### Example

- Long 1 SPX 5000 call: delta = +0.50
- Short 1 SPX 4950 put: delta = –0.50
- **Net delta = 0** → delta-neutral position

If SPX rallies from 5000 to 5050:
- Long call gains: +$25 (0.50 delta × 2% move)
- Short put loses: –$25 (–0.50 delta × 2% move)
- **Net P&L = $0** (ignoring gamma, vega, theta effects)

## Why Delta-Neutral Matters

Delta-neutral positions isolate specific risks or opportunities:

| If you're focused on... | Use delta-neutral structure |
|---|---|
| Volatility expansion | Long straddle (buy ATM call + ATM put) |
| Volatility compression | Short strangle (sell OTM call + OTM put) |
| Gamma P&L | Long ATM straddle or short iron condor |
| Theta decay | Short strangle or short iron condor |
| Skew reversion | Sell expensive puts, buy cheaper calls (put spread) |

All these structures attempt to isolate the desired edge (vol, gamma, theta, skew) by keeping delta near zero.

## Delta-Neutral in Practice

### Iron Condor

- Short call spread: delta = –0.10 to –0.20
- Short put spread: delta = +0.10 to +0.20
- **Net delta ≈ 0**

The position profits from time decay (theta) and volatility compression (vega), not directional moves.

### Short Strangle

- Short call: delta = –0.15
- Short put: delta = –0.15
- **Net delta ≈ –0.30** (slight downward bias)

To make truly delta-neutral:
- Sell 2 calls (delta –0.30)
- Sell 1 put (delta –0.15)
- **Net delta ≈ –0.45** — still not perfect

This is why most traders adjust delta by selling more OTM options.

## Maintenance: Delta Drifts

A position that is delta-neutral *today* will not be delta-neutral *tomorrow*.

**Why?**
- Underlying price changes → deltas change
- Time passes → delta of OTM options decreases
- Volatility changes → all deltas adjust

### Example

Sold a short strangle: long call at 5100 delta (–0.10), short put at 4900 delta (–0.10), net delta ≈ 0.

Next day, SPX rallies to 5050:
- 5100 call delta moves from –0.10 to –0.20 (further ITM)
- 4900 put delta moves from –0.10 to –0.02 (further OTM)
- **New net delta ≈ –0.22** (now short directional bias)

### Rehedging

To restore delta-neutral, you can:
1. **Buy stock / SPX call** to offset the new negative delta
2. **Close and re-sell** a new strangle with legs adjusted for new price
3. **Accept the drift** and manage it as a new position

Most traders do (3): accept the natural drift and either let it become a directional position or close and reopen.

## Delta-Neutral ≠ Risk-Free

> [!warning]
> A delta-neutral position is *not* risk-free. It has:
> - **Gamma risk:** If the underlying moves fast, you're short gamma (if short straddle/strangle)
> - **Vega risk:** If volatility spikes, you're short vega (if short vol structure)
> - **Gap risk:** If the underlying gaps overnight, your hedge breaks
> - **Liquidity risk:** Rebalancing to maintain delta-neutral can be expensive or impossible in a fast market

Delta-neutral positions are **vol plays**, not directional hedges.

## When to Use Delta-Neutral Structures

✓ **Use when:**
- You have a clear view on volatility (up or down), but not direction
- You want to isolate theta or vega edge from directional noise
- You're comfortable with gamma or vega risk in exchange for theta income

✗ **Avoid when:**
- An earnings announcement or macro event is imminent (gamma can explode)
- You're uncertain about volatility direction
- Bid/ask spreads are wide (rebalancing is expensive)
- You lack discipline to rebalance as the underlying moves

## Key Takeaway

Delta-neutral is a *framework* for designing positions that express specific edges. It's not a goal in itself. The goal is to profit from the edge you've identified (theta, vega, skew, gamma). Delta-neutral is the tool that removes directional noise so that edge can shine through.
