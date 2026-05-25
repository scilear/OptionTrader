---
title: 0DTE Iron Condor
tags:
  - 0dte
  - iron-condor
  - spx
  - premium-selling
  - defined-risk
status: draft
aliases:
  - 0DTE IC
  - Same-Day Iron Condor
related:
  - "[[0DTE-Overview]]"
  - "[[0DTE-Entry-Timing]]"
  - "[[0DTE-Adjustments]]"
  - "[[Iron-Condor]]"
---

# 0DTE Iron Condor

A same-day iron condor on SPX sells a [[Put Spread]] and a [[Call Spread]] that expire at the close, targeting the range the market is expected to stay within for the session. Because time value collapses to zero by 4:00 PM, premium erodes rapidly — but so does the margin for error.

> [!warning]
> SPX 0DTE options can move against you faster than you can react. A single catalyst (Fed speak, geopolitical headline, flash crash) can take a position from full profit to maximum loss within minutes. Size this strategy as if every trade could go to max loss, because some will.

---

## Setup

Sell an [[Iron-Condor]] with all four legs expiring the same day:

- **Put spread**: sell a put at 0.10–0.15 delta, buy a put $25–$50 lower.
- **Call spread**: sell a call at 0.10–0.15 delta, buy a call $25–$50 higher.
- Both spreads should be symmetric in width when starting out.

The structure profits if SPX stays between the two short strikes through expiry. Total risk is defined: maximum loss equals wing width minus credit received.

![[pnl-0dte-ic.png]]

---

## When to Use

This setup is suited to a specific market environment — using it on the wrong day is the most common source of outsized losses.

**Favorable conditions (all three should be present):**

1. VIX below 20, ideally below 17. Elevated VIX widens the [[Expected Move]] and prices the short strikes closer to the money, shrinking the probability of profit.
2. A clear intraday range established by 10:00 AM — price has consolidated, not trending. Check whether SPX is inside the prior day's range.
3. No major scheduled afternoon catalysts: FOMC statements, economic releases after noon, or earnings from index-heavy names.

> [!tip]
> Check the economic calendar before entry. A 2:00 PM ISM print or Fed speaker can invalidate the low-volatility thesis in minutes, even when VIX is calm at open.

---

## Strike Selection

1. Pull the 0DTE option chain at or after 10:00 AM (see [[0DTE-Entry-Timing]] for timing rationale).
2. Identify the short put strike where delta is closest to −0.12 and the short call strike where delta is closest to +0.12.
3. Buy protection $25 or $50 out from each short strike. $25-wide wings are standard for a $8–$12 credit target; $50-wide wings are used when structure credit is insufficient on $25 wings but they require larger notional risk.

> [!note]
> Delta of 0.10–0.15 corresponds roughly to the 1-standard-deviation move for the session. At VIX 15 with SPX at 5000, the expected daily move is approximately ±$25 (1 SD), so a 0.12-delta short strike will be near $5040 on the call side and $4960 on the put side.

---

## Credit Target

Collect **15–25% of the total wing width** in combined credit. For $25-wide wings, that means $3.75–$6.25 per spread, or $7.50–$12.50 for the full iron condor. For $50-wide wings, the target is $7.50–$12.50 per spread.

If the combined credit falls below 15% of wing width, the risk/reward does not support the trade — skip it or wait for a better moment. This is a rule of thumb based on experienced practitioner guidelines, not a statistically derived threshold.

---

## Practical Example

SPX = 5000, VIX = 15, session expected move = $25.

| Leg | Strike | Action | Premium |
|-----|--------|--------|---------|
| Short put | 4960 | Sell | +$5.00 |
| Long put | 4935 | Buy | −$1.50 |
| Short call | 5040 | Sell | +$5.00 |
| Long call | 5065 | Buy | −$1.50 |
| **Net credit** | | | **+$7.00** |

Wing width = $25. Credit = $7.00 = 28% of width (above target, acceptable). Max loss = $25.00 − $7.00 = $18.00 per share, or $1,800 per contract.

---

## Trade Management

**Profit target:** Close the entire iron condor at **50% of credit received**. On a $7.00 credit, place a GTC limit order to buy back at $3.50 immediately after entry. This is a data-backed guideline consistent with the 45-DTE premium-selling research from tastytrade (applied here to intraday time compression).

**Side tested:** If either short strike is breached and its delta rises above 0.30, **close the entire iron condor immediately**. Do not attempt to leg out or roll individual spreads on 0DTE — execution slippage and rapid gamma make legging a losing strategy at this time frame. See [[0DTE-Adjustments]] for detail.

> [!danger]
> Legging out of a 0DTE iron condor — closing only the losing side while holding the winning side — is a beginner mistake that frequently converts a defined-loss trade into a much larger realized loss. Close both spreads together.

**Hard stops (both apply, whichever triggers first):**

1. **200% credit loss**: if the position is down 2× the credit received, close immediately. On a $7.00 credit, close when the buyback cost reaches $21.00.
2. **3:45 PM closing rule**: close the entire position no later than 3:45 PM regardless of P&L. Gamma risk in the final 15 minutes is extreme and not compensated by the remaining time premium.

---

## Related Notes

- [[0DTE-Overview]] — framework and prerequisite reading
- [[0DTE-Entry-Timing]] — when and how to enter during the session
- [[0DTE-Adjustments]] — what to do when a side is tested
- [[Iron-Condor]] — multi-day version with different management rules
