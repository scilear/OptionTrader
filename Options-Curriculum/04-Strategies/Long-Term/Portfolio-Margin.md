---
title: Portfolio Margin for Advanced Options Traders
tags:
  - margin
  - risk-management
  - capital-efficiency
  - advanced
  - options
status: draft
aliases:
  - PM Account
  - Risk-Based Margin
related:
  - "[[Advanced-Collar]]"
  - "[[Zero-Risk-Collar]]"
  - "[[Portfolio-Allocation]]"
  - "[[PMCC-Income]]"
  - "[[LEAPS-Investing]]"
---

# Portfolio Margin for Advanced Options Traders

Portfolio margin (PM) is a risk-based margin methodology that evaluates the net exposure of your entire portfolio, rather than applying fixed per-position rules as [[Portfolio-Margin]] does. Under PM, the broker stress-tests your holdings across a range of price and volatility scenarios — typically ±15% in the underlying and ±30% in implied volatility — and charges margin only for the worst projected loss.

> [!note]
> Reg-T margin is rule-based: each position has a fixed requirement regardless of hedges held elsewhere. Portfolio margin is model-based: a long put that offsets a short call lowers your net requirement to reflect the real economic exposure.

## How Portfolio Margin Is Calculated

The OCC's Theoretical Intermarket Margin System (TIMS) drives most PM calculations. It shifts the underlying through ten stress scenarios and nets the resulting P&L across all correlated positions in the same underlying or index group. The margin requirement equals the largest projected loss across all scenarios.

Key inputs the model considers:

- **Net delta** — hedged portfolios (e.g., stock + protective put) show near-zero delta, and the model rewards that.
- **Net vega** — long and short vega positions offset each other.
- **Correlation** — a position in SPY and a short SPX put are treated as correlated; both legs count toward one stress test.

![[chart-drawdown-recovery.png]]

## Eligibility Requirements

These figures are consistent across major US brokers, though not legally standardized (rule of thumb based on industry practice, not a regulatory mandate):

- **Minimum account equity:** $100,000–$125,000 (Interactive Brokers requires $110,000; tastytrade $125,000).
- **Options trading experience:** 2+ years, typically documented at the application stage.
- **Options approval level:** Must already hold the highest tier (spreads, uncovered index options).

To apply, request PM access through your broker's account management portal. Most brokers require a short knowledge assessment. Interactive Brokers also runs a daily real-time check — if your equity falls below the minimum, you revert to Reg-T rules automatically.

## Capital Efficiency in Practice

A hedged portfolio can carry 50–70% less margin under PM than Reg-T. This is data-backed from IB's published margin examples (rule-of-thumb percentages vary by position and scenario):

| Position | Reg-T Requirement | PM Requirement |
|---|---|---|
| 100 shares SPY + long put | ~50% of notional | ~10–20% of notional |
| [[Advanced-Collar]] (stock + put + short call) | ~30–40% of notional | ~5–15% of notional |
| [[Zero-Risk-Collar]] | ~30% of notional | Near zero (fully hedged delta) |

For the [[PMCC-Income]] strategy specifically, a PMCC with a deeply hedged net delta can require only marginal PM, freeing capital for additional positions or a cash buffer.

> [!warning]
> Portfolio margin is a tool, not a license to increase leverage. The extra buying power should be used for hedging, not speculation. A trader who fills the freed-up buying power with additional naked short options is now carrying more gross risk than before — the model only measures net risk at the moment of calculation.

## Risk Management Under Portfolio Margin

The reduced margin requirement can create a false sense of security. The stress tests used by TIMS are calibrated for normal market conditions; tail events routinely exceed the model's scenarios.

Practical rules for PM accounts:

1. **Run your own stress test.** Calculate your portfolio P&L if the market drops 20% overnight and VIX doubles. Brokers will run a margin call — calculate yours before they do.
2. **Maintain a cash buffer.** Keep 15–25% of account equity in cash or short-term T-bills. This absorbs margin calls without forced liquidation at worst-case prices.
3. **Monitor delta daily.** PM rewards delta-neutral portfolios. If a position drifts significantly, re-hedge before the stress test exposure grows.
4. **Understand margin calls under PM.** Unlike Reg-T, PM margin calls can be very large and must be met same-day (IB's policy). Forced liquidation at the open after a gap down is a significant risk.

> [!danger]
> Portfolio margin is unsuitable for traders who have not actively managed multi-leg options books for at least two years. The leverage available through freed buying power can produce losses that exceed the initial account equity in a single adverse session. This is not a beginner account type.

## Brokers Offering Portfolio Margin

| Broker | PM Minimum | Notes |
|---|---|---|
| Interactive Brokers | $110,000 | Most capital-efficient PM implementation; real-time margining |
| tastytrade | $125,000 | Straightforward application; good for defined-risk strategies |
| TD Ameritrade (now Schwab) | $125,000 | Available on thinkorswim platform |

Interactive Brokers is the preferred broker for PM accounts among professional retail traders because its real-time margin calculations are the most granular, and its rates on margin loans are competitive when you do need to use buying power.

> [!tip]
> Apply for PM before you need it. The application and knowledge check can take 1–5 business days. Having PM enabled in advance means you can deploy a [[Advanced-Collar]] or add a hedge leg quickly without waiting for account changes to process during a volatile period.

## Summary

Portfolio margin replaces fixed per-position rules with a net-portfolio stress test, reducing margin requirements by 50–70% for genuinely hedged books. It is most useful for strategies like [[Advanced-Collar]], [[Zero-Risk-Collar]], and PMCC structures where delta and vega are actively managed. The core discipline: treat the freed buying power as a buffer, not as an invitation to scale up gross exposure. See [[Portfolio-Allocation]] for how to size individual strategies within a PM account.
