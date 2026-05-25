---
title: Rolling Credit Spreads — Bull Put and Bear Call Playbook
tags:
  - options/adjustments
  - options/rolling
  - options/credit-spreads
  - options/bull-put
  - options/bear-call
  - options/management
aliases:
  - Roll a Credit Spread
  - Credit Spread Adjustment
  - Rolling Bull Put
  - Rolling Bear Call
status: draft
related:
  - "[[Rolling-Basics]]"
  - "[[Bull-Put-Spread]]"
  - "[[Bear-Call-Spread]]"
  - "[[Adjust-vs-Close]]"
  - "[[Adjustment-Decision-Tree]]"
  - "[[Rolling-for-Credit]]"
  - "[[Losing-Trade-Mindset]]"
---

# Rolling Credit Spreads — Bull Put and Bear Call Playbook

A credit spread defines your maximum loss at entry, which is its biggest advantage over a naked short option. But a defined-risk position can still be adjusted rather than simply closed — if the market will give you additional credit to do so. This note covers the three roll types for [[Bull-Put-Spread]] and [[Bear-Call-Spread]] positions, when each is appropriate, and the one rule you must never break.

## When to Consider Rolling a Bull Put Spread

All three of these conditions should be present before you reach for the adjustment toolbox. Act on one alone and you risk rolling too early (burning strike room you did not yet need) or too late (strike already deep ITM, no credit available).

| Trigger | Threshold | Notes |
|---|---|---|
| Short put delta | > 0.40 | Delta above 0.40 means the market assigns >40% probability of expiring ITM. Rule of thumb — not a backtested trigger. |
| Unrealized loss | > 1.5× credit received | If you collected $0.80, start evaluating once the spread is worth ~$1.20. Data-backed: tastytrade research shows closing at 2× credit collected limits drawdowns; rolling should be evaluated before that point. |
| DTE remaining | ≥ 21 | Inside 21 DTE, gamma accelerates and the move-per-dollar worsens. See [[Rolling-Basics]] for the 21-DTE rationale. |

For a [[Bear-Call-Spread]], mirror these triggers: short call delta > 0.40, loss > 1.5× credit, ≥ 21 DTE.

> [!note]
> These thresholds work together as a checklist, not a formula. You need both the delta evidence (the market is moving against you) and enough time remaining to make the roll mechanically useful.

## The Three Roll Types

### 1. Roll Down (Bull Put Only)

Move both strikes lower — short put to a lower strike, long put the same width below it — within the **same expiry**. The underlying has fallen and you want more distance from the current price.

- Mechanically: buy back the original spread, sell a new spread with both strikes shifted down by 5–10 points (or one strike width).
- Goal: collect a net credit while creating distance from the stock.
- Limitation: staying in the same expiry means theta is not reset. Only useful when you have comfortable DTE remaining (35+ days).

### 2. Roll Out (Same Strikes, Next Expiry)

Keep both strikes identical and push to the next monthly expiry. You still like the strikes but need more time.

- Mechanically: buy back the near-term spread, sell the identical spread one expiry further out.
- Goal: collect the additional time premium in the new expiry as net credit.
- Use when: the stock is testing your spread but has not broken through, and you believe the thesis holds.

### 3. Roll Down and Out (New Strikes, Next Expiry)

The most powerful adjustment — you gain both additional distance from the stock and a full theta reset. Change both the strikes (lower) and the expiry (next month) simultaneously.

- Mechanically: one combined four-leg order — buy back the original spread, sell the new lower-strike spread in the next expiry.
- Goal: net credit, usually achievable because the new expiry carries substantially more time value.
- Use when: the stock is deeply threatening your position and you need both time and distance to recover.

> [!tip]
> Always execute the roll as a single combined order — not two separate orders. A single order eliminates leg-out risk (closing the short leg first, then getting an adverse fill on the new leg). Most platforms label this a "spread roll" order type.

## Worked Example: Bull Put $190/$185 Tested

**Setup:** You sold the $190/$185 bull put spread for $0.80 credit (30 DTE). The stock falls from $196 to $192. The spread is now worth ~$1.60; short put delta has moved to 0.44.

**Decision:** All three triggers are satisfied (delta > 0.40, loss at 2× credit, 28 DTE remaining). Rolling is worth evaluating.

**Roll down and out:**
- Buy back the $190/$185 spread (debit ~$1.60 mid)
- Sell the $185/$180 spread, next monthly expiry (credit ~$1.75 mid)
- **Net credit: $0.15**

**Result:** The new short put is $185, 7 points below the current stock price of $192. You collected an additional $0.15. The new trade is the $185/$180 bull put spread with ~58 DTE and a total credit of $0.95 ($0.80 + $0.15).

> [!warning]
> Never roll a spread for a debit — this compounds your maximum loss. If the market will not offer a net credit at any reasonable combination of lower strikes and/or next expiry, close the position outright. See [[Adjust-vs-Close]] for the close-vs-roll decision framework.

## Decision Table: Scenario → Action

| Scenario | Action |
|---|---|
| Stock near short strike, 35+ DTE, credit available | Roll down (same expiry, lower strikes) |
| Stock near short strike, 21–35 DTE, credit available | Roll down and out (lower strikes, next expiry) |
| Stock not yet at short strike, 21–35 DTE, time decay stalling | Roll out (same strikes, next expiry) |
| Stock has blown through short strike, inside 21 DTE | Evaluate closing; roll credit likely unavailable |
| Already rolled twice | Close — do not roll a third time |
| No net credit available at any combination | Close — see [[Adjust-vs-Close]] |
| Catalyst (earnings, event) now inside new expiry window | Close — do not roll into an unplanned event |

## Bear Call Spread: Mirror Logic

All three roll types apply symmetrically to a [[Bear-Call-Spread]] with directions reversed:

- **Roll up:** move both strikes higher (away from a rising stock).
- **Roll out:** same strikes, next expiry.
- **Roll up and out:** most powerful — higher strikes plus next expiry.

The trigger logic is identical: short call delta > 0.40, loss > 1.5× credit, ≥ 21 DTE.

## Limits

- **Maximum two rolls.** After two adjustments, the original thesis has failed. Take the defined loss and redeploy capital. This is a rule of thumb among experienced premium sellers, not a statistical law.
- **Width discipline.** Do not narrow the spread width on a roll to generate a larger credit — this reduces your max-loss buffer on the new position. Keep the original width or widen it.
- **Capital commitment.** Rolling extends how long margin is tied up in a challenged position. Weigh the opportunity cost against starting a fresh, uncorrelated trade. See [[Losing-Trade-Mindset]] for the psychology of holding vs. closing.
