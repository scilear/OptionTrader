---
title: "50% Profit Target vs. Holding to Expiry"
tags:
  - profit-taking
  - risk-management
  - theta
  - backtesting
  - tastytrade
aliases:
  - "50 percent rule"
  - "half profit close"
  - "profit target exits"
status: draft
related:
  - "[[Iron-Condor]]"
  - "[[CSP-Cash-Secured-Put]]"
  - "[[Theta-Decay]]"
  - "[[Scaling-Out-of-Winners]]"
---

# 50% Profit Target vs. Holding to Expiry

The question of when to exit a winning options trade is one of the most consequential decisions a premium seller makes. Tastytrade's research across 10,000+ backtested trades provides one of the clearest data-backed answers available to retail traders.

## The Research Case for 50%

Tastytrade's large-scale backtests consistently showed that closing short premium positions at 50% of max profit produces **the same or better win rate** as holding to expiry, while meaningfully reducing risk. The core finding: the last half of a trade's profit potential requires disproportionate time and carries disproportionate risk.

![[chart-theta-decay-curve.png]]

> [!note]
> "Max profit" for a defined-risk trade like an [[Iron-Condor]] equals the net credit received. Closing at 50% means buying back the spread for half the original credit.

## The Theta Math

A 45-DTE iron condor closed at approximately 15–20 DTE captures **roughly 85% of the total theta** the trade will ever earn. This happens because [[Theta-Decay]] is not linear — it accelerates as expiration approaches. The final two to three weeks are where theta is highest, but so is gamma.

Capturing 85% of theta while eliminating 100% of the remaining gamma exposure is a favorable trade. The final 15% of potential theta comes at the cost of holding through a period where a single adverse move can erase the entire premium collected.

> [!warning]
> In the final 15–21 DTE window, gamma risk rises sharply. A 2–3 sigma move against a short iron condor that was safely out-of-the-money can become a max-loss candidate within days. Holding for the last fraction of profit exposes the full position to this compressed risk.

## Profit Targets by Strategy

These guidelines reflect data-backed tastytrade thresholds and experienced practitioner rules of thumb:

| Strategy | Recommended Target | Rationale |
|---|---|---|
| [[Iron-Condor]] | 50% of credit | Balanced gamma/theta tradeoff at mid-life |
| [[CSP-Cash-Secured-Put]] | 50% of credit | Frees collateral for next cycle |
| 0DTE structures | 25–30% of credit | Timeframe compressed; gamma dominates from open |
| Calendars / Diagonals | 75% of credit | Longer structure; vega exposure requires more time to resolve |

> [!tip]
> For 0DTE trades, the compressed timeframe means gamma is dominant from the moment the trade opens. A 25–30% profit target is the practitioner consensus precisely because the trade has no "safe" middle period to coast through.

## The Counter-Argument: Hold to Expiry

Holding to expiry maximizes per-trade profit — on winning trades. The problem is selection bias in how traders remember those trades. The full picture from backtesting shows that holding longer:

- Increases variance of outcomes
- Increases maximum drawdown per trade
- Does not proportionally increase total annual return, because fewer trades fit into the same calendar year

## The Opportunity Cost Argument

A [[CSP-Cash-Secured-Put]] or [[Iron-Condor]] opened at 45 DTE that closes at 50% profit in 20–25 DTE frees capital immediately. That capital can be redeployed into a fresh 45-DTE trade. Over a 12-month period, this recycling of capital into new premium-selling cycles typically generates more total return than extracting the final dollars from each individual trade.

[[Scaling-Out-of-Winners]] captures a related technique: closing half the position at 50% while letting the remainder run, which balances both perspectives.

> [!danger]
> Blindly holding to expiry without a defined exit rule is a beginner pattern that leads to accounts suffering unnecessary max-loss events on trades that were profitable weeks earlier. Mechanical profit targets remove the psychological temptation to "let it ride."

## Practical Implementation

- Set a GTC limit order to close at 50% of credit at the time of entry
- Do not adjust the target upward mid-trade simply because the position is still safe
- Review realized P&L on a per-year, not per-trade, basis to assess whether the approach is working
