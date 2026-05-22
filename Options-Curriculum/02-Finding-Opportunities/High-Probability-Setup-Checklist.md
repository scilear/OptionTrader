---
title: High-Probability Setup Checklist
tags:
  - finding-opportunities
  - checklist
  - risk-management
  - volatility
  - liquidity
aliases:
  - Setup Checklist
  - Pre-Trade Checklist
status: draft
related:
  - "[[Ticker-Selection-System]]"
  - "[[Position-Sizing]]"
  - "[[Market-Condition-Classification]]"
---

# High-Probability Setup Checklist

Before placing any options trade, run through this checklist in full. Every item is binary — pass or fail. The scoring system at the bottom determines whether to trade, size down, or walk away.

> [!note]
> This checklist applies to defined-risk and undefined-risk premium strategies alike. Items in the **Strategy Fit** section will shift depending on whether you are buying or selling volatility — read each item carefully. For ticker selection upstream of this checklist, see [[Ticker-Selection-System]].

---

## Volatility — 3 items

- [ ] **IV Rank (IVR) is appropriate for the strategy.** For premium selling: IVR > 40. For premium buying: IVR < 25. IVR is calculated as (current IV − 52-week low IV) / (52-week high IV − 52-week low IV). *Data-backed threshold from backtests on SPX/ETF underlyings; rule-of-thumb on single names.*
- [ ] **IV Percentile (IVP) confirms the IVR reading.** IVP > 50 for selling, IVP < 35 for buying. IVP and IVR can diverge when the IV distribution is skewed; both checks together reduce false signals. See [[Market-Condition-Classification]] for regime context.
- [ ] **No pending vol event is inflating the number.** An earnings date, Fed announcement, or CPI print inside your DTE window will distort IVR and make a "high IV" reading misleading. Verify the economic calendar before treating IV as elevated for the right reasons.

---

## Liquidity — 3 items

- [ ] **Open interest at the target strike exceeds 500 contracts.** Low OI leads to wide markets and difficulty closing. *Rule of thumb; 1,000+ preferred for undefined-risk positions.*
- [ ] **Bid-ask spread at the target strike is less than 10% of the mid price.** Wide spreads destroy edge at entry and exit. Calculate: (ask − bid) / mid. Reject if > 0.10.
- [ ] **The underlying itself trades average daily volume > 500,000 shares (or equivalent for ETFs).** Thin underlyings correlate with thin options markets even when OI looks adequate.

---

## Technical — 2 items

- [ ] **The trade is not inside an earnings window.** Define "inside" as fewer than 5 calendar days before the announcement date. Earnings create binary gap risk that invalidates most vol-surface assumptions.
- [ ] **A key technical level or trend is identified and the trade is structured around it.** This is not a requirement to be a technical analyst — it is a requirement to know where the underlying is likely to find support or resistance so that your short strike placement is deliberate, not arbitrary.

---

## Strategy Fit — 2 items

- [ ] **The chosen strategy matches the current [[Market-Condition-Classification]].** Example: selling naked puts in a Stress regime is misaligned. Selling iron condors in a Calm/low-IV regime destroys edge. The regime filter should have eliminated bad matches before you reach this checklist.
- [ ] **DTE is within the optimal range for the structure.** For premium selling: 21–45 DTE at entry. For calendars and diagonals: front leg < 21 DTE. For debit spreads targeting a move: 30–60 DTE to allow time for the thesis to develop.

---

## Risk Check — 2 items

- [ ] **Position size is within your allocation limit.** Maximum notional risk per trade as defined in [[Position-Sizing]]. Never exceed this limit even for a "high-conviction" trade.
- [ ] **The max loss scenario is explicitly calculated and acceptable.** Write the number down. If an undefined-risk trade has no hard max loss, the worst-case scenario must still be sized to a level you can withstand without materially impairing the account.

---

## Scoring

| Score | Action |
|-------|--------|
| 12 / 12 | Trade at full target size |
| 10 – 11 | Trade at 50–75% of target size |
| < 10 | Pass — do not enter |

> [!tip]
> When in doubt, pass. There will always be another setup. The cost of missing a good trade is far lower than the cost of entering a bad one. Discipline on this checklist compounds over time exactly as edge does.

> [!warning]
> Scoring 12/12 on this checklist does not guarantee a profitable trade. Options selling strategies carry assignment risk, gap risk, and tail risk that no checklist can eliminate. Size every position as if it can be a full loss.

---

## Related Notes

- [[Ticker-Selection-System]] — upstream filter for which underlyings to scan
- [[Position-Sizing]] — how to calculate allocation limits referenced in Risk Check
- [[Market-Condition-Classification]] — regime definitions used in Strategy Fit
