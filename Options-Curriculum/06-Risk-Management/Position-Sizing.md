---
title: Position Sizing
tags:
  - risk-management
  - position-sizing
  - iron-condor
  - cash-secured-put
  - portfolio-management
aliases:
  - sizing
  - trade-sizing
status: draft
related:
  - "[[Portfolio-Allocation]]"
  - "[[Max-Risk-Per-Trade]]"
  - "[[Drawdown-Management]]"
---

# Position Sizing

Position sizing is the single most important risk management skill for an options trader. Getting the strategy right but the size wrong will still blow up an account. A well-sized bad trade is survivable; an oversized good trade can still ruin you psychologically and financially when it briefly goes against you.

![[chart-position-sizing.png]]

## The Core Rule: 2–5% Max Loss Per Trade

> [!warning]
> The maximum loss on any single trade should not exceed 2–5% of total portfolio value. This is measured on a **max loss basis**, not on expected loss. Violating this rule consistently is the most common cause of account blow-ups among retail options traders.

For a $100K portfolio:
- 2% limit = $2,000 max loss per trade
- 5% limit = $5,000 max loss per trade

Use 2% when starting out or in elevated-risk environments. Graduate toward 5% only after 6–12 months of live trading with documented results.

## Calculating Position Size: Iron Condor Example

For the [[Standard-Iron-Condor]] (SPX 45DTE, $50-wide wings, $12.50 credit):

| Metric | Value |
|---|---|
| Wing width | $50 |
| Credit collected | $12.50 |
| Max loss per contract | ($50 − $12.50) × 100 = **$3,750** |
| 2% of $100K portfolio | $2,000 |
| Max contracts at 2% | 0 (one contract already exceeds limit) |
| Max contracts at 5% | 1 ($3,750 < $5,000) |

For a narrower IC collecting $15 on a $35-wide loss:

| Metric | Value |
|---|---|
| Max loss per contract | $35 × 100 = **$3,500** |
| 5% of $100K portfolio | $5,000 |
| Max contracts at 5% | 1 |
| Max contracts at 7% | 2 (aggressive — not recommended) |

> [!note]
> The canonical $50-wide SPX IC on a $100K account is a full-allocation trade at the 5% level. Many professional vol traders run 1–2% per leg. Beginners should treat one IC as their entire risk budget for that underlying.

## Cash-Secured Puts: Collateral Is the Position Size

For [[Cash-Secured-Puts]], the collateral requirement defines the maximum capital at risk (the stock going to zero is the true max loss). Apply the 5% rule to the **collateral posted**, not the premium collected.

- 5% of $100K = $5,000 max collateral per CSP
- A $50-strike CSP requires $5,000 collateral per contract — this is your entire 5% budget
- A $100-strike CSP requires $10,000 collateral — already 10%; requires explicit approval against a higher allocation rule

Link: [[Portfolio-Allocation]] tracks total capital deployed across all CSPs and defined-risk structures.

## Scaling Size by IV Environment

> [!tip]
> In high-IV environments (VIX > 25 or IV rank > 75), **reduce size by 25–50%**. Vol spikes create gamma risk that overwhelms normal sizing assumptions. High-IV entries are attractive for premium sellers, but the path to expiration is far more violent. Collect more premium per contract, run fewer contracts.

| VIX Level | Size Adjustment |
|---|---|
| < 15 (low IV) | 50–75% of normal size |
| 15–25 (normal) | 100% of normal size |
| 25–35 (elevated) | 50–75% of normal size |
| > 35 (stress) | 25–50% of normal size — or stand aside |

This is a rule of thumb derived from practitioner experience, not a backtested optimization. The directional effect (reduce size in high-vol regimes) is well-supported empirically; the exact percentages are guideposts.

## Correlation: The Hidden Concentration Risk

> [!danger]
> Correlation is the most underestimated position-sizing failure mode. Three SPX iron condors, one SPY strangle, and one QQQ put spread are **not** five independent positions — they are one large correlated bet on equity vol. Beginners routinely build what looks like a diversified book but is a single macro view dressed up as multiple trades.

Practical rule: count no more than **3–4 correlated positions as a single risk unit**. For equity-index vol traders this means:
- SPX, SPY, QQQ, and ES options all count toward the same bucket
- A second bucket might include GLD, TLT, or sector ETFs with lower equity correlation
- See [[Max-Risk-Per-Trade]] for how to aggregate correlated exposure

## The Sleep Test

Before entering any trade, ask: *If this position moved to max loss overnight, would I lose sleep?*

If yes — the position is too large. This is not a soft heuristic; it is a hard signal. A position that disrupts sleep impairs judgment, leads to early exits at the worst time, and breaks the systematic discipline that makes the strategy work. Reduce size until the answer is genuinely no.

## Summary Table: $100K Portfolio Limits

| Trade Type | Max Loss Basis | 2% Limit | 5% Limit |
|---|---|---|---|
| $50-wide IC, $12.50 credit | $3,750/contract | 0 contracts | 1 contract |
| $35-wide IC, $15 credit | $3,500/contract | 0 contracts | 1 contract |
| CSP, $50 strike | $5,000 collateral | 0 contracts | 1 contract |
| CSP, $25 strike | $2,500 collateral | 1 contract | 2 contracts |
| Vertical spread, $10-wide | $1,000/contract | 2 contracts | 5 contracts |

See [[Drawdown-Management]] for rules on when to stop trading and reduce overall portfolio exposure after a drawdown sequence.
