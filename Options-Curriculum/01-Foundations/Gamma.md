---
title: Gamma
tags:
  - foundations
  - greeks
  - risk-management
aliases:
  - gamma risk
  - convexity risk
status: draft
related:
  - "[[Greeks-Overview]]"
  - "[[0DTE-Overview]]"
  - "[[50pct-vs-Expiry]]"
  - "[[Gamma-Regime-and-GEX]]"
  - "[[Gamma-Walls-Call-Put]]"
---

# Gamma

Gamma is the rate of change of [[Greeks-Overview|delta]] with respect to a move in the underlying. If delta tells you how much an option's price moves for a $1 move in the stock, gamma tells you how fast that sensitivity is itself changing.

> [!note] Formal definition
> Gamma = ∂²V / ∂S² — the second derivative of option value with respect to spot price. It is always positive for long options and always negative for short options.

A long call with delta 0.40 and gamma 0.05 becomes a 0.45-delta call after a $1 rally. That same gamma works in reverse: the position accelerates against a short seller as the underlying moves away from their strike.

## Why Gamma Is the Core Risk for Options Sellers

Premium sellers (short straddles, short strangles, iron condors) earn [[Theta]] every day the market stays quiet. That income comes at a cost: negative gamma. Every point of theta collected is effectively renting out convexity to the buyer.

When the underlying moves sharply, negative gamma compounds the loss:
- Delta grows in the wrong direction automatically.
- The further the move, the faster the position deteriorates.
- A single large move can erase days or weeks of theta income.

This tradeoff — steady theta income vs. episodic gamma pain — is the central tension in volatility selling. It is not a free lunch. Rule of thumb (not data-backed): for every point of daily theta earned, assume you are accepting roughly one large-move day per month that can cost multiples of that theta.

## Gamma Explosion Near Expiration

Gamma is not constant. It spikes sharply as an option approaches expiration, especially for near-the-money strikes.

![[chart-gamma-vs-dte.png]]

With 30 DTE, a 1-point move in the underlying changes delta modestly. With 1 DTE, the same move can flip a near-ATM option from nearly worthless to deeply in-the-money. The delta can swing from 0.10 to 0.90 in a single session.

> [!warning]
> Gamma risk is highest for 0DTE and same-week trades — positions can move against you faster than you can react. A gap open or a fast intraday trend can produce losses that cannot be hedged in real time.

See [[0DTE-Overview]] for a full treatment of the structural risks specific to zero-days-to-expiration trading.

## The Gamma vs. Theta Tradeoff in Practice

| DTE | Theta decay (per day) | Gamma sensitivity |
|-----|----------------------|-------------------|
| 45 DTE | Moderate | Low — moves are manageable |
| 21 DTE | Increasing | Elevated — monitor closely |
| 7 DTE | High | High — consider closing |
| 0–1 DTE | Very high | Extreme — binary outcome risk |

Many systematic sellers target 30–45 DTE entries specifically to harvest theta before the gamma spike begins. Closing at 50% of max profit (see [[50pct-vs-Expiry]]) removes the position from the high-gamma zone entirely. This is a data-backed observation from TastyTrade research on short premium P&L distributions.

## Managing Gamma: Close Early, Size Small

> [!tip] The 50% rule as a gamma management tool
> Closing a short premium trade at 50% max profit is not just about locking in gains — it eliminates gamma exposure at the point where it begins to accelerate. The remaining potential profit rarely justifies the convexity risk of holding into expiration.

Practical guidelines (rule of thumb, not backtested here):
1. **Close short options positions before the final week** unless you have an explicit reason to hold.
2. **Reduce size going into events** — earnings, FOMC, CPI — that compress time to resolution and amplify gamma.
3. **Use defined-risk structures** (spreads, iron condors) when trading shorter DTE, so gamma cannot produce unlimited loss.
4. **Delta-hedge actively** only if you have infrastructure for it; most retail sellers manage gamma through position sizing and early exits rather than continuous hedging.

Gamma is not an enemy to be avoided — it is a cost to be priced. Sellers who understand and respect it outperform those who simply maximize theta collection.

## Aggregate Gamma: Market Structure Effects

The concepts above apply to individual positions. At the market level, the *aggregate* gamma exposure of all dealers across all options positions — called **GEX (Gamma Exposure)** — shapes intraday volatility in a measurable way. When dealers collectively hold positive GEX, their hedging dampens volatility. When they hold negative GEX, their hedging amplifies moves.

This aggregate effect is the basis for gamma walls, call walls, put walls, and the High Volatility Level (HVL) — practical tools for understanding whether the market is in a volatility-dampening or volatility-amplifying regime before selecting a strategy.

See [[Gamma-Regime-and-GEX]] for the market-structure application of GEX, and [[Gamma-Walls-Call-Put]] for how specific strike concentrations create reaction zones.
