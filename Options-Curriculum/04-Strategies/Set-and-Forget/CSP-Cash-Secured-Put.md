---
title: Cash-Secured Put (CSP)
tags:
  - strategy
  - set-and-forget
  - short-put
  - income
  - defined-risk
status: draft
aliases:
  - CSP
  - Cash Secured Put
  - Naked Put (cash-secured)
related:
  - "[[Covered-Call]]"
  - "[[Wheel-Strategy]]"
  - "[[Delta]]"
  - "[[IV-Rank]]"
  - "[[Rolling-Credit-Spreads]]"
---

# Cash-Secured Put (CSP)

## What It Is

A Cash-Secured Put is an income strategy where you sell one put option and simultaneously hold cash equal to the full obligation — `strike × 100` — in your account. If assigned, that cash is used to purchase the underlying shares at the strike price.

It is economically equivalent to a [[Covered-Call]] on the same strike, and forms the entry leg of the [[Wheel-Strategy]].

> [!note]
> "Cash-secured" means your broker holds collateral equal to `strike × 100`. A put sold without that collateral is a naked put — a different margin product with higher risk and different regulatory requirements.

---

## Structure

| Component | Detail |
|---|---|
| Legs | Short 1 put |
| Collateral | `strike × 100` in cash or T-bills |
| Directional bias | Bullish to neutral |
| Volatility bias | Short vol (benefits from IV contraction) |

---

## Best Conditions

- [[IV-Rank]] > 40 — elevated implied vol means richer premium (data-backed: premium harvesting studies consistently favor IVR > 40 as an entry filter)
- Bullish or neutral outlook on the underlying over the trade horizon
- Underlying at or near a technical support level (rule of thumb — not a guarantee)
- A stock or ETF you are genuinely willing to own at the strike price if assigned

> [!tip]
> Only sell CSPs on underlyings you would be happy to hold as a long stock position. Assignment is a real outcome, not a tail scenario — plan for it.

---

## Entry Rules

1. Select the expiry in the **21–45 DTE** window for the best theta-decay profile (rule of thumb, widely used in retail and institutional premium-selling desks).
2. Sell the put at **0.20–0.30 [[Delta]]** — this targets approximately a 70–80% probability of expiring worthless at entry.
3. Confirm the strike is at or below a meaningful support level on the chart.
4. Check [[IV-Rank]] > 40 before entering. Do not sell premium into a vol trough.

---

## Risk / Reward

| Metric | Formula | Note |
|---|---|---|
| Max profit | Premium received | Achieved if underlying closes above strike at expiry |
| Max loss | `Strike − Premium` | Realized if stock goes to zero |
| Breakeven at expiry | `Strike − Premium` | Below this, the position loses dollar-for-dollar |

![[pnl-csp.png]]

> [!warning]
> A CSP carries the **full downside of stock ownership** below the strike. If the stock drops 40%, your P&L is nearly identical to having bought the stock outright at the strike. Size accordingly — **never allocate more than 5% of your total portfolio to a single CSP position.**

---

## Trade Management

**Target exit: 50% of max profit.** Close the short put when you can buy it back for half the original credit received. This is data-backed: backtests across SPY and liquid single-stocks show that capturing 50% of the initial premium and redeploying produces higher annualized returns than holding to expiry, with meaningfully lower drawdowns (TastyTrade research, 2013–2023 SPY data).

**If the position is tested (underlying approaching or below strike):**

- With **≥21 DTE remaining**: consider rolling down and out — buy back the current put and sell a further-dated put at the same or lower strike for a net credit. See [[Rolling-Credit-Spreads]] for mechanics.
- With **<21 DTE remaining**: evaluate assignment. If you want the stock, let it assign. If not, close the position at a loss rather than rolling short-dated into a gamma-rich expiry.

---

## Exit Rules (Priority Order)

1. **50% profit** — close immediately, do not wait.
2. **21 DTE** — close regardless of P&L to avoid accelerated gamma risk in the final weeks.
3. **Stop-loss (optional)** — some traders close at 2× the initial credit received as a hard loss limit. This is a rule of thumb, not universally adopted.

---

## Ideal Underlyings

Choose underlyings you would own outright. Preference for:

- Large-cap quality stocks: AAPL, MSFT, JPM
- Broad market ETFs: SPY, QQQ
- Commodity ETFs with vol characteristics: GLD, SLV

Avoid highly speculative names, small-caps, or pre-earnings positions unless you fully understand the binary risk. The CSP on a speculative biotech is not the same trade as a CSP on SPY.

---

## Related Strategies

- [[Covered-Call]] — synthetic equivalent; the natural follow-on after CSP assignment
- [[Wheel-Strategy]] — CSP → assignment → covered call → repeat
- [[Rolling-Credit-Spreads]] — technique for managing a tested CSP without taking assignment
