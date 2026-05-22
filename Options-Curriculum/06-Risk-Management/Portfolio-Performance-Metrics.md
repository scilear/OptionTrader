---
title: Portfolio Performance Metrics
tags: [risk-management, performance, metrics, tracking, income-strategies]
aliases: [Options Portfolio Metrics, Income Portfolio KPIs, Performance Tracking]
status: draft
related:
  - "[[Portfolio-Allocation]]"
  - "[[Drawdown-Management]]"
  - "[[Position-Sizing]]"
  - "[[Portfolio-Heat]]"
  - "[[Beta-Weighting]]"
---

# Portfolio Performance Metrics

Tracking the right numbers separates disciplined income trading from gambling. A profitable options income portfolio has a distinctive statistical fingerprint — high win rate, moderate average win, controlled drawdowns — and each metric below tells a different part of that story. Review them together; no single number is sufficient on its own.

> [!warning]
> All targets below are rules-of-thumb derived from practitioner experience with short-premium strategies (credit spreads, iron condors, cash-secured puts, covered calls). They are not guaranteed outcomes. Actual results depend on market regime, underlying selection, and execution quality.

---

## 1. Win Rate

**Target: > 65% for income strategies.**

Win rate is the percentage of closed trades that expire or are closed for a profit. Short-premium strategies are structurally designed for high win rates because you collect premium upfront and time decay works in your favor.

- A 65–70% win rate is typical for 30-delta short strangles managed at 50% of max profit.
- A win rate below 60% over 50+ trades warrants a strategy review — either strikes are too aggressive or management rules are inconsistent.

> [!tip]
> Win rate is only meaningful over a statistically significant sample. Require at least 30 closed trades before drawing conclusions. Fewer trades may reflect luck more than edge.

---

## 2. Average Win vs. Average Loss

**Target: Average win/loss ratio of 0.4–0.6 is acceptable when win rate compensates.**

Income strategies are asymmetric by design: small, frequent wins versus infrequent but larger losses. The math works as long as:

```
(Win Rate × Avg Win) > (Loss Rate × Avg Loss)
```

Example: 70% win rate, avg win $200, avg loss $400 → Expected value = (0.70 × $200) − (0.30 × $400) = $140 − $120 = **+$20 per trade**.

Track this ratio over rolling 20-trade windows. A sudden drop in avg win (e.g., exiting too early) or spike in avg loss (e.g., holding through breaches) signals a management problem.

---

## 3. Return on Capital (ROC)

**Target: 2–4% per month on deployed capital.**

ROC measures what the strategy actually earns on the capital it ties up, not on total account value. If a $5,000 iron condor returns $150 at close, that is 3% ROC for that trade.

Portfolio-level monthly ROC aggregates all closed trades. Annualized, 2–4%/month implies 24–48% annual return on deployed capital — consistent with what well-managed short-premium books produce in normal regimes, but not in every market environment.

---

## 4. Theta per Day

**Target: Track as an absolute dollar amount and as a % of portfolio NAV.**

[[Theta]] measures how much time value your portfolio decays per calendar day (not trading day). A healthy income portfolio should show positive net theta — you are a net seller of time value.

- Rule of thumb: theta/day of 0.05–0.10% of NAV is a reasonable range for a moderately active income book.
- Very high theta/day (> 0.20% NAV) usually means the portfolio is carrying excessive [[Portfolio-Heat]].

---

## 5. Max Drawdown

**Target: Rolling 6-month max drawdown < 15% of peak NAV.**

Track peak-to-trough drawdown on a rolling 6-month basis, not just inception-to-date. A 20% drawdown that happened three years ago is less actionable than one occurring now.

> [!danger]
> Drawdown thresholds are personal and capital-dependent. A 15% drawdown on a $10,000 account is $1,500; the same threshold on a $500,000 account is $75,000. Anchor drawdown rules to dollar amounts as well as percentages. See [[Drawdown-Management]] for escalating response tiers.

---

## 6. Sharpe Ratio

**Target: > 1.0 annualized.**

Sharpe = (Portfolio Return − Risk-Free Rate) / Annualized Volatility of Returns.

A Sharpe above 1.0 means you are earning more than one unit of return per unit of risk taken. Short-premium strategies often show attractive Sharpe ratios in calm regimes but suffer severe ratio compression during volatility spikes — which is precisely why drawdown tracking is a required companion metric.

---

## 7. Beta-Weighted Delta

**Target: Near zero, ± 0.10% of portfolio NAV per 1% SPX move.**

[[Beta-Weighting]] converts all your position deltas into SPX-equivalent exposure. A large positive beta-weighted delta means you are effectively long the market; large negative means short.

Income strategies are not directional bets. If your beta-weighted delta drifts meaningfully positive after a rally, you have accumulated hidden long-delta risk. Rebalance by trimming longs, adding puts, or opening delta-negative positions.

---

## 8. Premium Collected vs. Premium Returned

**Target: Keep > 50% of gross premium collected.**

For each closed trade: **(Premium collected − Cost to close) / Premium collected = Premium retention rate.**

Aggregate this across all closed trades for the period. Retention below 50% indicates either poor strike selection, premature exits, or inadequate management of losers.

> [!tip]
> tastytrade's built-in trade tracker reports this metric automatically. For manual tracking, a simple spreadsheet with columns for premium collected, premium paid to close, and net is sufficient.

---

## How to Track

- **Spreadsheet**: One row per trade. Columns: underlying, strategy, open date, close date, DTE at open, premium collected, premium paid, net P&L, ROC%, win/loss flag. Monthly tabs for aggregation.
- **tastytrade**: Built-in P&L dashboard with win/loss breakdown and premium retention. Does not compute Sharpe or beta-weighted delta natively.
- **Python/DuckDB**: See this project's `trade_ideas` and `alerts` tables for pipeline-generated metrics; the `surface_metrics` table tracks theta and Greeks over time.

---

## Monthly Review Checklist

- [ ] Win rate over last 20 closed trades > 65%?
- [ ] Average win/loss ratio producing positive expected value?
- [ ] Monthly ROC on deployed capital within 2–4% target band?
- [ ] Theta/day reasonable relative to NAV?
- [ ] Rolling 6-month max drawdown within limit per [[Drawdown-Management]]?
- [ ] Annualized Sharpe > 1.0 (requires at least 3 months of data)?
- [ ] Beta-weighted delta within ±0.10% of NAV per 1% SPX move?
- [ ] Premium retention > 50% for the month?
- [ ] [[Portfolio-Allocation]] buckets still in balance?
