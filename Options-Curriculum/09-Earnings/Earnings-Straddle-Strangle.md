---
title: "Earnings Straddle & Strangle — Buying the Move"
tags:
  - options/earnings
  - options/long-volatility
  - options/straddle
  - options/strangle
  - options/debit-spread
aliases:
  - earnings straddle
  - earnings strangle
  - long earnings vol
status: draft
related:
  - "[[IV-Crush-Mechanics]]"
  - "[[Earnings-IC-Playbook]]"
  - "[[Earnings-Overview]]"
  - "[[Expected-Move-Formula]]"
  - "[[Earnings-Ticker-Selection]]"
---

# Earnings Straddle & Strangle — Buying the Move

Most earnings options strategies are about *selling* implied volatility before IV crush. This note covers the opposite position: buying a straddle or strangle when you expect the actual move to exceed what the market has priced in.

> [!danger]
> Long earnings vol is a high-cost, time-sensitive trade with multiple ways to lose simultaneously (IV crush, insufficient move, time decay). It is not suitable for beginners who have not yet mastered [[IV-Crush-Mechanics]] and [[Expected-Move-Formula]] mechanics.

---

## The Straddle

A **long straddle** buys an ATM call and an ATM put at the same strike and expiration.

- AAPL spot = 200, buy the 200 call + 200 put expiring just after earnings
- If the combined premium costs $8, you need AAPL to move more than $8 in either direction to profit at expiration
- **Breakeven**: 200 − 8 = 192 on the downside, 200 + 8 = 208 on the upside
- Max loss = $8 per share if AAPL closes exactly at 200

> [!note]
> The straddle premium *is* the market's implied move. It closely tracks the [[Expected-Move-Formula]] derived from front-month IV. If AAPL's ATM straddle costs $8 on a $200 stock, the market is pricing a ±4% one-standard-deviation move.

---

## The Strangle

A **long strangle** buys an OTM call and an OTM put — for example, the 210 call and 190 put on AAPL at spot 200.

- Cheaper than the straddle because both legs are out-of-the-money
- Requires a larger move to reach breakeven (strike of the call + total premium paid, or strike of the put − total premium paid)
- The lower upfront cost comes with lower probability of profit — the stock must clear both strikes before you gain intrinsic value

> [!tip]
> Rule of thumb: use a straddle when you want the lower breakeven. Use a strangle when you want lower dollar risk but can accept a higher breakeven threshold. Neither is universally superior — the choice depends on your breakeven tolerance vs. cost sensitivity.

---

## When to Buy (Not Sell) Earnings Vol

The core edge case for buying is when a specific stock has a *documented history* of moving more than the implied move at earnings. This is an empirical question, not a rule.

**Recommended workflow (data-backed):**
1. Pull the stock's earnings history on [Market Chameleon](https://marketchameleon.com) — look at "Earnings Move vs Implied Move" for the last 8–12 quarters
2. Count how many times the actual move exceeded the implied move
3. If the actual move exceeded implied 6+ out of 8 times (75%+), that is a meaningful signal — not a guarantee
4. Cross-check with [[Earnings-Ticker-Selection]] criteria: high short interest, binary catalysts, concentrated analyst divergence

> [!warning]
> Historical earnings move ratios are backward-looking. A stock with a strong track record of beating implied moves can IV-crush you just as hard as any other if the actual move comes in short. Past earnings behavior does not guarantee future volatility.

---

## Entry Timing: 5–7 Days Before Earnings

IV rises into earnings — buying earlier means less inflated premium. Entering 5–7 days before the event captures a period where IV has started to rise but has not reached peak.

- On the day before earnings, front-month IV is typically near its event-cycle high
- Entering 5–7 days out gives the position time to profit from continued IV expansion *and* the move itself
- This is an experienced-trader rule of thumb, not a fixed formula — some names inflate IV earlier than others

---

## The IV Crush Risk

Even if the stock moves, [[IV-Crush-Mechanics]] will deflate the option value significantly the morning after earnings. For a long straddle to profit through earnings, the actual move must exceed the full implied move priced into the straddle — not just be "large."

A $6 move on AAPL with a $8 straddle is a loss, even though $6 sounds large in absolute terms.

---

## Alternative: Directional Debit Spread

If you have a conviction on direction (e.g., expecting a large upside beat), a **call debit spread** reduces vega exposure while retaining directional leverage:

- Buy the 200 call, sell the 210 call
- The short call offsets much of the vega you are long — IV crush hurts less
- Max gain is capped at the spread width minus the net debit
- Use when you want directional exposure more than pure vol exposure

> [!tip]
> A debit spread is the pragmatic middle ground between selling premium (as in [[Earnings-IC-Playbook]]) and buying a naked straddle. It works well when you have directional conviction but want to limit IV crush damage.

---

## Exit Rules

- **Before earnings**: exit 1 day before if IV has inflated enough to show a profit — this captures the "vol expansion" trade without taking event risk
- **Immediately after earnings**: if holding through, close within the first 30 minutes after the announcement; IV crush accelerates through the morning session
- **Do not hold** a long straddle or strangle into regular trading hours the day after earnings hoping for a secondary move — IV will have collapsed and theta will compound the damage

> [!warning]
> Holding a long straddle through earnings and into the next trading day without a plan is one of the most common and costly beginner mistakes in earnings trading. Set a firm exit rule before you enter the trade.
