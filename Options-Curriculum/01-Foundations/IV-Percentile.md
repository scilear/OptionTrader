---
title: IV Percentile
tags:
  - volatility
  - iv
  - metrics
  - selling
aliases:
  - IVP
  - IV Percentile Rank
status: draft
related:
  - "[[IV-Rank]]"
  - "[[IV-vs-HV]]"
  - "[[Selling-Premium]]"
  - "[[Vol-Surface-Distortions]]"
---

## Definition

**IV Percentile (IVP)** is the percentage of days in a lookback window (typically 252 trading days / 1 year) where IV was lower than the current IV level.

$$\text{IVP} = \frac{\text{Days IV} < \text{Current IV}}{\text{Total Days}} \times 100$$

An IVP of 75 means current IV is higher than 75% of the past year's IV observations—a signal of elevated volatility relative to the stock's recent history.

## Formula vs. Calculation Method

IVP is *not* a simple formula like standard deviation. It's a **rank statistic**: sort the past 252 daily IV closes, find where today's IV sits, then compute its percentile rank. This makes IVP:
- Non-parametric (no assumptions about IV distribution)
- Robust to outliers by construction (a single spike does not change ranks of other days)
- Easy to interpret (0–100% scale)

## IVP vs. [[IV-Rank]]

Both measure "how high is IV relative to history," but they differ in robustness:

| Metric            | Calculation                                             | Distortion Risk                      | Best Use                                           |
| ----------------- | ------------------------------------------------------- | ------------------------------------ | -------------------------------------------------- |
| **IV Percentile** | Rank-based, position in 252-day sorted list             | Resistant to single spikes           | Stocks with post-earnings IV spikes, binary events |
| **IV Rank**       | (Current IV − 52-week low) / (52-week high − low) × 100 | Highly sensitive to max/min outliers | Steady-state regimes, index options (SPX)          |

**Practical difference**: A stock gaps up 15% on earnings, IV spikes to 200% realized move, then normalizes. That spike becomes the "high" in IV Rank for 252 days, depressing future IV Rank scores. IVP treats it as just one observation in a list—less distortion.

> [!note]
> OptionTrader's `iv_rank.py` tool computes both metrics. For SPX and liquid indices, IV Rank is stable. For single-name equities with event-driven spikes, prefer IVP.

## Practical Thresholds for Selling

These are **empirical rules**, not laws. Test on your own stock universe.

- **IVP > 50**: IV above median. Good environment for selling premium (covered calls, credit spreads, short strangles). Theta decay works in your favor, and you're selling at an elevated price.
- **IVP 30–50**: Neutral zone. Selling still viable, but less of an edge. Entry timing matters more.
- **IVP < 30**: IV is depressed relative to history. Avoid initiating short volatility positions unless you have a strong mean-reversion conviction. Risk/reward tilts against you—large moves become more likely relative to the option's price.

> [!warning]
> IVP < 30 signals historically low volatility, which often precedes *expansion*, not contraction. Selling puts or calls into depressed IV exposes you to re-pricing risk if realized volatility spikes. Backtest your structures in these regimes first.

## IVP ≠ Predictive

IVP tells you where IV is in the distribution, not where it is *going*. A stock at IVP 25 (low IV) may continue lower or may explode higher. IVP is useful for:
- **Valuation entry criteria** — sell premium when IVP is rich
- **Regime context** — understand if you're trading with or against IV history
- **Exclusion rules** — avoid selling in IVP < 20 unless thesis-driven

IVP does *not* predict direction.

## Combining IVP with [[IV-vs-HV]]

Compare IV (market's forecast of realized move) to HV (realized move over past 252 days):
- **IVP high + IV > HV**: Vol is elevated and expensive. Strong sell-premium environment.
- **IVP low + IV < HV**: Vol is depressed but realized moves are large. Dangerous for sellers.
- **IVP high + IV < HV**: Unusual; market may be hedging a low-probability tail event. Check earnings calendar, macro announcements.

## Implementation Note

OptionTrader's `iv_rank.py` computes IVP as the percentile of ATM IV across the past 252 trading days (or your specified `--lookback`). Cached for 1 day to avoid redundant yfinance calls.

```bash
./tools/iv_rank.sh --ticker GLD --lookback 252
```

## Summary

- **Use IVP when**: Trading single stocks or any underlying prone to event-driven IV spikes.
- **Prefer IV Rank when**: Trading SPX, liquid indices, or steady-state regimes.
- **Sell premium at**: IVP > 50 ideally; avoid IVP < 30 unless you're hedged or thesis-driven.
- **Remember**: IVP ranks, not predicts. Pair with [[IV-vs-HV]] for context.

> [!danger]
> Beginners often confuse "IV is at the 30th percentile" with "IV will revert to the 50th." Percentile rank is *data*, not a signal to trade counter-trend. Always pair entry rules with risk management and thesis.
