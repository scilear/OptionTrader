---
title: Poor Man's Covered Call (PMCC)
tags:
  - strategy
  - options
  - leaps
  - income
  - diagonal-spread
  - intermediate
aliases:
  - PMCC
  - Poor Mans Covered Call
  - Synthetic Covered Call
status: draft
related:
  - "[[LEAPS]]"
  - "[[Diagonal-Spread]]"
  - "[[Covered-Call]]"
  - "[[PMCC-Adjustments]]"
  - "[[PMCC-Income]]"
---

# Poor Man's Covered Call (PMCC)

The Poor Man's Covered Call is a capital-efficient alternative to the traditional [[Covered-Call]]. Instead of purchasing 100 shares of stock (full notional exposure), you buy a deep in-the-money [[LEAPS]] call as a stock substitute, then sell short-dated OTM calls against it — the same mechanics as a covered call, but using ~20–30% of the capital required for share ownership.

Structurally, a PMCC is a [[Diagonal-Spread]]: two calls on the same underlying, different strikes, different expirations.

---

## Position Structure

| Leg | What to Buy/Sell | Target Delta | Expiration |
|-----|-----------------|-------------|------------|
| Long (back leg) | Buy ITM call (LEAPS) | 0.70–0.80 | 12–24 months out |
| Short (front leg) | Sell OTM call | 0.25–0.35 | 21–45 DTE |

![[pnl-pmcc.png]]

The LEAPS acts as synthetic long stock. Its high delta means it tracks the underlying closely, while its long expiration gives time for the short-call income to accumulate and offset (or recover) the LEAPS premium paid.

---

## Entry Rules

### 1. LEAPS Leg

- **Delta:** Buy at 0.70 delta or higher. Lower delta = less stock equivalence = more speculative.
- **Expiration:** At least 12 months remaining; 18–24 months is preferable for more time to collect income.
- **Extrinsic value check (rule of thumb):** Extrinsic value should be less than 10% of the stock price. If it is higher, you are overpaying for optionality relative to the intrinsic value the LEAPS provides. This is a rule of thumb, not a hard statistical threshold.
- **Strike selection:** Deep ITM strikes — choose a strike where the option has a delta in the 0.70–0.80 range on the day you enter.

### 2. Short Call Leg

- **Delta:** Sell at 0.25–0.35 delta (OTM). Higher delta short calls collect more premium but narrow your upside.
- **DTE:** 21–45 days to expiration. The 30–45 DTE zone captures the steepest portion of theta decay (data-backed: theta accelerates nonlinearly inside 45 DTE on most underlyings).
- **Credit vs. debit check (critical rule):** The net debit of the position (LEAPS cost minus short call credit) must be lower than the width between the two strikes. This ensures the spread has positive maximum value at expiration. If not satisfied, reduce the LEAPS cost or select a different short strike.

> [!danger]
> **Never sell the short call at a strike below your LEAPS strike.** If the short call strike is at or below the LEAPS strike, you have converted the PMCC into a simple debit spread with fully capped upside. Income potential disappears and max profit is fixed — the entire purpose of the strategy is lost.

---

## Capital Efficiency

Owning 100 shares of a $200 stock requires $20,000. A 0.75-delta LEAPS call on the same stock may cost $2,500–$4,500, depending on IV and time remaining — roughly 12–22% of the stock cost. This frees capital for other positions or leaves cash as a cushion.

> [!note]
> Capital efficiency comes with a trade-off: unlike a shareholder, the LEAPS holder receives no dividends and has a hard expiration. If the stock does nothing for 18 months and IV contracts, the LEAPS can lose value even though the stock is flat. This is the primary hidden cost of the structure.

---

## Management Rules

### Rolling the Short Call

- Roll when 21–30 DTE remains, or when the short call has captured 50–75% of its maximum profit — whichever comes first.
- Roll to the next 30–45 DTE expiration at the same or higher strike, collecting a net credit on the roll. If you cannot roll for a credit, evaluate whether the underlying thesis still holds.

### If the Stock Rallies Through the Short Call

- When the short call moves deep ITM (delta 0.70+), roll up and out immediately — extend expiration and raise the strike — for a net credit if possible.
- Do not wait for assignment risk to materialize. Early assignment on short calls is rare (American-style only), but possible near ex-dividend dates.

> [!warning]
> **If the short call goes deep ITM before you can roll, you may be forced to close the spread at a loss.** Monitor the delta of the short call continuously: when it reaches 0.70 or higher, roll immediately. A deeply ITM short call with little extrinsic left gives you no room — the spread collapses toward intrinsic value and your flexibility disappears.

### If the Stock Drops Significantly

- Stop selling new short calls once the short call premium available no longer justifies the risk of further capping upside on a weakened position.
- Let the LEAPS ride if your directional thesis is intact and enough time remains.
- If the underlying has broken down and you no longer hold a bullish view, close the LEAPS outright. Do not add more short calls to "recover" losses — this converts the position into a speculative short-vol bet.

> [!tip]
> Set a soft stop on the LEAPS: if it loses 50% of its value, reevaluate the entire position. At that point the delta may have fallen below 0.50, weakening the stock-substitute assumption that underpins the strategy.

---

## Income Accumulation Over Time

The goal is for the cumulative credits from short calls to fully offset the LEAPS debit over the life of the position. In practice (rule of thumb, not backtested guarantee):

- A 12-month LEAPS rolling 30-DTE short calls at 0.30 delta may generate 4–8 short call cycles.
- Each cycle's credit depends on realized IV and stock movement — expect variability.
- Break-even on the LEAPS cost is achievable in favorable trending or range-bound markets; in high-volatility, whipsaw environments it is harder.

For a deeper analysis of income modeling across cycles, see [[PMCC-Income]].

---

## Comparison: PMCC vs. Traditional Covered Call

| Factor | Covered Call | PMCC |
|--------|-------------|------|
| Capital required | ~100% of stock price | ~20–30% of stock price |
| Dividend exposure | Receives dividends | No dividends |
| Max loss | Stock goes to zero | LEAPS premium (defined) |
| Upside cap | Short call strike | Short call strike (same) |
| Complexity | Low | Intermediate |
| Margin treatment | Generally favorable | Varies by broker |

---

## Related Notes

- [[LEAPS]] — deep dive on LEAPS selection, delta decay, and vol crush risk
- [[Diagonal-Spread]] — the generalized structure underlying the PMCC
- [[Covered-Call]] — the capital-intensive version this strategy approximates
- [[PMCC-Adjustments]] — detailed rolling and repair playbook
- [[PMCC-Income]] — income modeling and annualized return expectations
