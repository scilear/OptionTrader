---
title: "PMCC Adjustments — Handling Adverse Moves"
tags:
  - options/strategy/pmcc
  - options/adjustment
  - options/leaps
  - options/covered-call
status: draft
aliases:
  - "Poor Man's Covered Call Adjustments"
  - "PMCC Defense"
related:
  - "[[PMCC]]"
  - "[[Rolling-Basics]]"
  - "[[Adjust-vs-Close]]"
  - "[[LEAPS]]"
---

# PMCC Adjustments — Handling Adverse Moves

The [[PMCC]] uses a deep ITM [[LEAPS]] in place of 100 shares. That structure makes adjustments more nuanced than a standard covered call — the long leg has its own delta, decay curve, and vega exposure, all of which can move against you independently.

> [!warning]
> If the short call moves deeper ITM than the LEAPS strike, the position loses its defined-risk character. Never allow that inversion. Adjust before it happens, not after.

---

## Scenario 1 — Short Call Goes Deep ITM (Stock Rallies Hard)

**Trigger:** Short call delta reaches 0.70–0.80, or the gap between the short strike and the LEAPS strike compresses to fewer than two strikes.

Roll the short call up and out to a higher strike in the next expiration cycle, collecting a net credit. If you cannot collect a credit, the position is likely at max gain — close it outright rather than rolling for a debit. See [[Rolling-Basics]] for mechanics.

**Hard rule:** The short call strike must always sit above the LEAPS strike. Roll before delta exceeds 0.80 — do not wait.

> [!tip]
> Roll 30–45 DTE forward. Rolling just one week out rarely generates enough credit to justify the extra transaction cost.

---

## Scenario 2 — LEAPS Decays or Loses Value (Stock Stagnant or Slowly Declining)

**Trigger:** LEAPS falls below 90 DTE, or its delta drops below 0.60 on a flat/down move.

Below 90 DTE, theta accelerates even on long-dated options. The LEAPS is no longer acting as an effective stock substitute.

**Decision:**
1. If the stock thesis is intact, roll the LEAPS out 6–12 months to a strike with delta 0.70–0.80 and at least 12 months of DTE. This costs a debit — budget for it.
2. If the thesis has weakened, close the entire position. Paying to extend a broken trade is rarely correct — see [[Adjust-vs-Close]].

> [!note]
> Rolling a LEAPS out 12 months typically costs 20–35% of the original premium (rule of thumb; varies by stock and IV level).

---

## Scenario 3 — Stock Drops 20% or More

**Trigger:** Underlying falls 20%+ from the LEAPS purchase price.

Stop selling short calls immediately. Selling any call below the LEAPS strike converts the position into a ratio spread with uncapped downside. If a short call is still open and now OTM, buy it back. Let the LEAPS ride if the thesis is intact; close it if the thesis is broken. Do not leg out piecemeal trying to recoup premium on an impaired position.

> [!danger]
> Selling short calls below the LEAPS strike is not appropriate for most traders. The resulting spread can produce losses exceeding the entire LEAPS value and requires active management to exit safely.

---

## Scenario 4 — IV Collapse on the LEAPS

**Trigger:** Implied volatility on the LEAPS collapses after entry — common when the LEAPS was bought during an elevated-IV event (earnings, macro spike).

A 10-point IV drop on a 12-month LEAPS can erase 15–25% of premium even if the stock is unchanged. Short call premium also reprices lower, making yield recovery slow.

**Rule of thumb:** If the short call you can sell covers less than 1% of LEAPS value per month, the PMCC is not generating adequate yield. Close the LEAPS and redeploy when IV normalizes.

> [!tip]
> Enter PMCC positions when IV is in the lower half of its 1-year range. Buying LEAPS in high-IV environments creates meaningful vega risk on the long leg even when the stock cooperates.

---

For the broader framework on when to manage through a loss versus take it and move on, see [[Adjust-vs-Close]].
