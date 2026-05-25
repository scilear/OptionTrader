---
title: Diagonal Spread
tags:
  - strategy
  - income
  - defined-risk
  - theta
  - diagonal
  - leaps
  - pmcc
aliases:
  - Poor Man's Covered Call
  - PMCC
  - call diagonal
  - put diagonal
status: draft
related:
  - "[[Calendar-Spread]]"
  - "[[PMCC]]"
  - "[[LEAPS]]"
  - "[[Iron-Condor]]"
  - "[[Vertical-Spread]]"
---

# Diagonal Spread

A **diagonal spread** is a two-leg position that combines elements of a [[Calendar-Spread]] and a [[Vertical-Spread]]: you buy one option at a further expiration and sell another option at a nearer expiration, but the two legs are at *different strikes*. The strike mismatch is what separates a diagonal from a pure calendar and is what introduces a **directional bias**.

> [!note]
> A calendar spread uses the same strike on both legs; a diagonal shifts one strike to create delta exposure. All [[PMCC]] structures are call diagonals by definition.

## Structure (Call Diagonal — Income Setup)

| Leg | Position | Strike | Expiry | Typical Delta |
|-----|----------|--------|--------|---------------|
| Long call | Buy | Lower (deeper ITM) | Far-dated (LEAPS, 12–24 months) | 70–80 Δ |
| Short call | Sell | Higher (OTM) | Near-term (30–45 DTE) | ~0.30 Δ |

The long LEAPS call acts as a leveraged proxy for 100 shares of the underlying — this is the [[PMCC]] framing. Each monthly short call collected reduces the cost basis of the long leg.

![[pnl-diagonal-spread.png]]

## Why This Structure Works

- **Theta advantage**: the short near-term call decays faster (convex theta curve) than the long LEAPS leg loses value. Rule of thumb: the short call should collect at least one-third of its strike width in premium each cycle to justify the position.
- **Delta exposure**: unlike a calendar, the ITM long leg carries meaningful positive delta (~0.70–0.80). The position profits from slow, moderate upward moves — not just from vol staying flat.
- **Vega**: net long vega overall (the long LEAPS dominates). A vol expansion helps the position; a vol crush hurts. This is the opposite of a short strangle. Data-backed: [[LEAPS]] vega is roughly proportional to √T, so a 365-DTE call has ~4× the vega of a 21-DTE call at the same strike.

> [!tip]
> When entering, verify that the net debit paid for the diagonal is less than the maximum spread width (difference between strikes). If debit ≥ width, you have no upside profit potential at the near-term expiry.

## Entry Checklist

1. Select underlying with liquid options (tight bid/ask on LEAPS).
2. Buy the LEAPS call with **delta 70–80**. This typically corresponds to a strike 1–2 strikes in the money.
3. Sell the front-month call at **~0.30 delta** (roughly 1–2 strikes OTM).
4. Confirm net debit < (long strike − short strike).
5. Implied volatility rank (IVR) > 30 preferred — helps the short leg collect more premium.

## Management Rules

These are rule-of-thumb guidelines derived from practitioner consensus, not a formal backtest:

- **Roll the short call** at 21 DTE or when it reaches 50% profit, whichever comes first. Roll out to the next monthly cycle at the same or higher strike.
- **Adjust strike on roll** if the stock has moved significantly. Do not let the short call strike fall below the long call strike (that converts the diagonal into a short vertical — unlimited risk profile).
- **Close the position** if delta of the long leg drops below **60 Δ**. A long leg with delta below 60 no longer behaves like a stock proxy; continued short-call sales against it carry increasing risk.
- **Roll the long leg out** when the LEAPS has less than **90 DTE remaining**. At that point, theta decay on the long leg accelerates and the core advantage of the structure erodes. Roll to a new LEAPS 12–18 months out, accepting additional debit.

## Comparison to Calendar Spread

| Feature | [[Calendar-Spread]] | Diagonal Spread |
|---------|---------------------|-----------------|
| Strike alignment | Same strike both legs | Different strikes |
| Delta exposure | Near-neutral (slight) | Moderate positive (call diag.) |
| Directional bias | Minimal | Yes — bullish (call) or bearish (put) |
| Max profit location | At short strike at expiry | Above short strike (call diag.) |
| Cost vs. calendar | Lower (OTM long leg) | Higher (ITM long leg for PMCC) |

## Put Diagonal (Bearish Income)

The structure works in reverse: buy a far-dated ITM put (70–80 Δ), sell a near-term OTM put (~0.30 Δ). This is a bearish income trade. The same management rules apply — close if long leg delta falls below 60, roll when under 90 DTE.

> [!warning]
> A diagonal spread carries **undefined downside risk relative to a covered call** if the long leg loses value faster than expected (e.g., a volatility crush on the LEAPS after a spike). The position can also suffer if the stock gaps sharply above the short strike, creating a short vertical risk that exceeds the collected premium. Always size this position so that a total loss of the net debit is within your single-trade risk tolerance.

## Related Notes

- [[Calendar-Spread]] — same-strike version; lower delta, pure theta/vega play
- [[PMCC]] — specific call-diagonal implementation with LEAPS as stock substitute
- [[LEAPS]] — characteristics of long-dated options used as the long leg
- [[Vertical-Spread]] — what a diagonal becomes if the long leg expires before rolling
