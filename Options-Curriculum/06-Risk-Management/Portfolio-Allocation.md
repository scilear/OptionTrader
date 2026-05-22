---
title: Portfolio Allocation
tags: [risk-management, portfolio, allocation, diversification]
aliases: [Capital Allocation, Bucket Allocation, Portfolio Construction]
status: draft
related:
  - "[[Position-Sizing]]"
  - "[[Max-Risk-Per-Trade]]"
  - "[[Drawdown-Management]]"
  - "[[Portfolio-Heat]]"
  - "[[Beta-Weighting]]"
---

# Portfolio Allocation

Portfolio-level allocation is the layer above [[Position-Sizing]]. Even perfectly sized trades can blow up a portfolio if they are all in the same bucket, sector, or beta exposure. The framework below splits capital by *strategy role*, then constrains exposure by sector, beta, and cash buffer.

## The Three Buckets

> [!note] Bucket allocation separates capital by *return profile and risk role*, not by ticker. A single underlying can appear in multiple buckets (e.g., AAPL CSP in Core, AAPL LEAPS in Growth).

**(a) Core Income — 50-60% of capital**
Defined-risk and cash-secured premium strategies: [[Iron-Condor]], [[Cash-Secured-Put]], [[Covered-Call]], [[The-Wheel-Strategy]]. Steady theta, modest variance. This is the chassis of the portfolio.

**(b) Long-Term Growth — 20-30% of capital**
[[LEAPS]] and [[PMCC]] (Poor Man's Covered Call). Capital-efficient long delta with managed decay. Slower P&L cadence; intended to capture trend, not premium.

**(c) Speculative / 0DTE — max 10-15% of capital**
[[0DTE-Strategies]], earnings plays, lottery tickets, directional debit spreads. Hard ceiling — this bucket is *expected* to have high variance and frequent losses.

> [!danger] The speculative bucket is unsuitable for beginners until at least 12 months of consistent Core-bucket performance. 0DTE has a "win often, lose huge" payoff that disguises bleed.

## Sample Allocation — $200K Portfolio

| Bucket | Target % | $ Allocated | Typical Vehicles |
|---|---|---|---|
| Core Income | 55% | $110,000 | IC, CSP, CC, Wheel |
| Long-Term Growth | 20% | $40,000 | LEAPS, PMCC |
| Speculative / 0DTE | 10% | $20,000 | 0DTE spreads, earnings |
| Cash Buffer | 15% | $30,000 | Cash / T-bills |
| **Total** | **100%** | **$200,000** | |

Allocations are *capital-at-risk* targets, not notional. For defined-risk trades use max loss; for CSPs use the cash secured; for LEAPS use premium paid.

## Sector Diversification

No more than **25% of deployed capital** in any single GICS sector. Tech mega-caps in particular tend to dominate retail option portfolios — AAPL, MSFT, NVDA, GOOGL, META all sit in Information Technology / Communication Services and move together on rate news.

> [!tip] Rule of thumb: if you can name your top three tickers from memory and they sum to >40% of capital, you are concentrated. Rotate before the next earnings cycle.

## Beta Weighting and Hidden Correlation

Ticker diversification is *not* risk diversification. A book of CSPs on AAPL, MSFT, GOOGL, and SPY has a beta-weighted delta that is essentially long SPX. See [[Beta-Weighting]] for the calculation.

> [!warning] Options portfolios can appear diversified by ticker but be fully correlated by beta — check your total delta exposure.

Mitigation: hedge concentrated SPX-correlated exposure with index trades (SPX/ES put debit spreads, VIX call spreads) sized to neutralize a meaningful fraction of beta-weighted delta. This is a hedge, not a profit center.

## Cash Buffer

Keep **20-30% in cash** (the table above uses 15% buffer + ~10% unused margin capacity in Core). Cash serves three roles:

1. **Margin cushion** — assignment, IV expansion, and SPAN moves all consume buying power suddenly.
2. **Opportunity capital** — vol spikes are when premium is richest; you cannot harvest them while fully deployed.
3. **Drawdown reserve** — see [[Drawdown-Management]] for the rule that paused buckets release capital back to cash.

## Monthly Review Process

On the first trading day of each month:

1. Mark each bucket to market (capital-at-risk basis).
2. Compute drift: `actual % - target %`.
3. **Rebalance when any bucket drifts > 10 percentage points** from target (e.g., Core at 68% vs 55% target → trim).
4. Recheck sector concentration and beta-weighted delta.
5. Log the snapshot — drift trends matter more than any single reading.

> [!tip] Rebalancing is usually achieved by *not opening new trades* in the over-allocated bucket and letting expirations bleed it down, rather than forced closes that pay slippage.

See also [[Max-Risk-Per-Trade]] for the per-trade ceiling that feeds these bucket totals.
