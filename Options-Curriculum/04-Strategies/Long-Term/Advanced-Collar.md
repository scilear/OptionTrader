---
title: Advanced Collar
tags:
  - strategy
  - collar
  - hedging
  - long-term
  - tax-efficient
  - stock-protection
  - multi-leg
  - call-spread
aliases:
  - Collar with Call Spread
  - Upside-Enhanced Collar
status: draft
related:
  - "[[Zero-Risk-Collar]]"
  - "[[Covered-Call]]"
  - "[[Portfolio-Margin]]"
  - "[[LEAPS-Investing]]"
  - "[[Rolling-Options]]"
  - "[[Delta]]"
---

# Advanced Collar

The Advanced Collar is a refinement of the [[Zero-Risk-Collar]] for stock holders who want downside protection without completely surrendering upside. The key change: replace the single short call with a call spread — sell a lower strike, buy a higher one — creating a capped but real participation zone above the sold strike.

> [!warning]
> This is a multi-leg strategy on an existing stock position. Errors in execution — wrong strikes, wrong expiries, mismatched quantities — can leave you with unintended naked exposure. Always verify all legs before submitting. A net debit trade requires a cash outlay that is at risk if all options expire worthless.

---

## The Problem with a Standard Collar

A [[Zero-Risk-Collar]] solves downside protection but creates a hard cap on upside. Sell a $110 call to finance your $90 put and you forfeit every dollar of a rally above $110. For a concentrated low-basis position in a taxable account, that cap is a significant hidden cost — you surrender optionality in exchange for premium that merely pays for protection you already wanted.

---

## Structure: Call Spread Instead of a Single Short Call

Sell a lower strike call, buy a higher strike call. The net premium collected is less than selling the lower call alone, so the put may not be fully financed — the result is typically a **small net debit**.

**Example — stock at $100, 90 DTE:**

| Leg | Strike | Action | Premium |
|-----|--------|--------|---------|
| Long put | $90 | Buy | −$3.50 |
| Short call | $110 | Sell | +$2.80 |
| Long call | $120 | Buy | −$0.90 |
| **Net** | | | **−$1.60 debit** |

**P&L zones at expiry:** put protects below $90 (loss capped ~$11.60); free range $90–$110 with only the debit as drag; dollar-for-dollar participation $110–$120; capped above $120 (max option gain ~$8.40/share).

![[pnl-advanced-collar.png]]

> [!note]
> You earn 1:1 within the spread width rather than being permanently capped at the sold strike. Actual breakevens depend on strikes chosen, premium received, and dividends.

---

## Variation: Ratio Put Backspread for Enhanced Downside Protection

If the call spread generates surplus premium, that excess can fund a **ratio put backspread** (sell one near-ATM put, buy two further OTM puts), adding convexity if the stock falls sharply. The trade-off: a loss zone opens between the two put strikes.

> [!danger]
> The ratio put backspread variation is not suitable for beginners. It produces a multi-zone payoff with a region of maximum loss that requires active monitoring and rolling. Only use this with [[Portfolio-Margin]] and direct experience managing backspread risk.

---

## When to Use

Best suited to concentrated long stock positions with a low cost basis (selling triggers a capital gain), where you are moderately bullish but cannot absorb a 20–30% drawdown. Requires liquid options with tight bid/ask spreads across at least three strikes — wide spreads erode the call spread's efficiency.

> [!tip]
> Long-run backtests (CBOE CLL — S&P 500 95-110 Collar index) show collared positions underperform in strong bull markets but outperform risk-adjusted across full cycles. The Advanced Collar narrows that bull-market gap at the cost of a small annual debit. Treat this as directional context, not a precise return guarantee.

---

## Risk and Complexity

- **Net debit drag**: If the stock drifts sideways and no protection is triggered, you paid for nothing — and this compounds across multiple annual rolls.
- **Execution slippage**: Three legs require disciplined limit-order management. Legging in carelessly widens the effective debit.
- **Vega asymmetry**: The long upper call is long vega. A post-entry volatility collapse erodes it faster than the short call, increasing the net cost invisibly.

---

## Management: Annual Rolling Discipline

Unlike a [[Covered-Call]] written monthly, Advanced Collars are structured with 90–180 DTE (or LEAPS length) and rolled once per year. Before rolling: confirm whether the call spread activated and whether the put protected you, then restrike both legs to the current stock price. In taxable accounts, coordinate roll timing with a tax advisor to manage wash-sale risk.

> [!tip]
> Rule of thumb: if the annual net debit exceeds 2% of stock value and the call spread rarely activates, simplify back to a [[Zero-Risk-Collar]] or accept unhedged risk. Complexity must justify its cost over a 3–5 year horizon, not just in theory.
