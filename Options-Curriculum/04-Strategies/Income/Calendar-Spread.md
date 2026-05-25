---
title: Calendar Spread
tags:
  - strategy
  - income
  - vega
  - theta
  - intermediate
aliases:
  - time spread
  - horizontal spread
status: draft
related:
  - "[[Diagonal-Spread]]"
  - "[[IV-vs-HV]]"
  - "[[Theta-Decay]]"
  - "[[Term-Structure]]"
  - "[[Vega-Risk]]"
  - "[[Greeks-Overview]]"
---

# Calendar Spread

A **calendar spread** (also called a *time spread* or *horizontal spread*) sells a shorter-dated option and buys a same-strike, same-type option at a further expiry. The two legs are structurally identical in strike and right (both calls or both puts), differing only in expiration.

> [!note]
> "Horizontal" refers to moving along the time axis on a options matrix — same strike, different columns. This distinguishes it from a [[Vertical-Spread]] (same expiry, different strikes) and a [[Diagonal-Spread]] (different strikes *and* different expiries).

---

## Structure

| Leg | Action | DTE Target | Right |
|-----|--------|-----------|-------|
| Short | Sell | 21–30 days | Call or put |
| Long | Buy | 45–60 days | Same as short |

- Strike: ATM or within a few points of the current underlying price.
- Net position: **debit** (the longer-dated option costs more than the shorter-dated premium received).
- Both legs at the **same strike**.

---

## Greek Profile

| Greek | Exposure | Why |
|-------|----------|-----|
| Theta | Positive | Short leg decays faster than long leg near expiry |
| Vega | Positive | Long leg carries more vega than short leg |
| Delta | Near zero (ATM entry) | Largely delta-neutral at initiation |
| Gamma | Negative | Short-leg gamma accelerates near expiry |

The calendar earns money two ways: (1) the short option decays faster than the long option, and (2) any rise in implied volatility benefits the long leg more than it hurts the short leg. These two sources of edge are independent and can reinforce each other.

---

## Entry Conditions

**Preferred environment — pick at least one:**

1. **Inverted term structure**: near-term IV is elevated relative to back-month IV. Selling the expensive front-month and buying the cheaper back-month creates a structural edge. Check [[IV-vs-HV]] and [[Term-Structure]] before entry.
2. **Low overall IV**: when the entire surface is cheap, buying long-dated optionality is inexpensive, and you are positioned for an eventual mean-reversion in vol.

> [!tip]
> Rule of thumb (data-backed for SPX, 2014–2023): calendars entered with the VIX below its 25th percentile have historically shown better P&L than entries during elevated-vol regimes, because the long leg is purchased cheaply and a vol pop lifts it. Source: internal backtest `quantconnect/spx_pipeline_validator.py`.

Avoid entering calendars when the front-month IV is *already depressed* — you give up the theta advantage and are paying full price for the long leg.

---

## Profit Zone

![[pnl-calendar-spread.png]]

The P&L profile at short-leg expiry is tent-shaped and centered on the strike. Maximum profit occurs when the underlying is exactly at the strike on the short leg's expiration date — the short option expires worthless and the long option retains its time value. The position loses money when the underlying moves substantially in either direction.

---

## Risk

> [!warning]
> Calendars have non-trivial vega risk — a drop in IV hurts the position even if the stock does not move. Because the long leg carries more vega than the short leg, a volatility crush (e.g., post-earnings IV collapse) can produce a loss even when the underlying pins your strike. Always check the vega dollar exposure before entry.

> [!danger]
> A large, fast move in the underlying causes the position to lose on both legs simultaneously: the short leg may be deep in the money at expiry, and the long leg loses its time value premium as it moves away from ATM. Calendars are **not** suitable as standalone directional trades or in high-event-risk environments (earnings, FOMC) unless sized very small.

---

## Management

| Condition | Action |
|-----------|--------|
| 50–75% of max profit reached | Close the entire spread; do not leg out |
| Near-term leg nearing expiry (< 5 DTE) | Roll or close; gamma risk increases sharply |
| Underlying moves > 1 strike width from center | Reassess; P&L curve is deteriorating |
| IV drops significantly after entry | Re-evaluate whether the vega loss offsets theta gains |

Rolling: if the short leg expires worthless and you wish to continue the trade, sell the next monthly at the same strike against the existing long leg. This converts the position into a series of short-term sales — a common income-generation pattern sometimes called a "rolling calendar." See [[Diagonal-Spread]] for the variant where you adjust the strike on the roll.

---

## Comparison to Related Structures

| Structure | Strike | Expiry | Bias |
|-----------|--------|--------|------|
| Calendar | Same | Different | Neutral, vol |
| [[Diagonal-Spread]] | Different | Different | Slight directional |
| [[Vertical-Spread]] | Different | Same | Directional |
| Double Calendar | Two strikes | Different | Neutral, wider tent |

---

## Key Numbers (rule of thumb, not data-backed)

- Target credit-to-debit ratio: look for spreads where the short-leg premium is at least 30–40% of the long-leg cost.
- Max loss: limited to the net debit paid.
- Typical hold period: 14–21 days (through short-leg expiry or until profit target hit).

---

## Related Notes

- [[Diagonal-Spread]] — calendar variant with strike adjustment on the roll
- [[IV-vs-HV]] — understanding when buying vol is cheap relative to realized
- [[Theta-Decay]] — why near-term options decay faster (convexity of time value)
- [[Term-Structure]] — reading the forward vol curve to identify inverted conditions
- [[Vega-Risk]] — quantifying exposure to implied vol moves
