---
title: LEAPS — Long-term Equity Anticipation Securities
tags:
  - options
  - leaps
  - stock-replacement
  - set-and-forget
  - long-term
  - pmcc
  - vega
  - theta
status: draft
aliases:
  - LEAPS
  - Long-term Options
  - Stock Replacement Options
related:
  - "[[PMCC]]"
  - "[[Diagonal-Spread]]"
  - "[[LEAPS-Investing]]"
  - "[[Delta]]"
  - "[[Theta-Decay]]"
  - "[[Vega]]"
  - "[[Covered-Call]]"
---

# LEAPS — Long-term Equity Anticipation Securities

## What Are LEAPS?

LEAPS are standard listed options with an expiration date **more than one year away** — typically 12 to 30 months out. They behave exactly like ordinary calls and puts under Black-Scholes, but their extended time horizon gives them a distinct risk profile that makes them useful in strategies that shorter-dated options cannot replicate cleanly.

> [!note]
> The LEAPS designation is purely administrative. Once an option rolls inside 12 months to expiration, it loses the "LEAPS" label but is otherwise identical. No mechanical change occurs at the 12-month boundary.

## Why Traders Use LEAPS

### 1. Stock Replacement (Defined-Risk Equity Exposure)

A deep in-the-money LEAPS call with a [[Delta]] of 0.70–0.80 moves almost dollar-for-dollar with 100 shares of stock — but costs roughly **20–30% of the notional** required to own those shares outright. This frees capital, limits downside to the premium paid, and eliminates margin requirements.

Example (rule of thumb, not a live quote): if a stock trades at $150, 100 shares costs $15,000. A 70-delta LEAPS call with 18 months to expiry might cost $3,000–$4,500 — capturing most of the upside while capping the downside at the premium.

> [!warning]
> The defined-risk advantage of LEAPS is real, but the premium represents a hard loss if the stock stagnates or declines. Unlike owning shares, a buyer who holds to expiration with no price movement loses the entire time-value component. There is no recovery from a permanently sideways stock unless the position is actively managed.

### 2. Foundation for the [[PMCC]]

The Poor Man's Covered Call uses a LEAPS call in place of 100 shares. You sell short-dated calls against the LEAPS to collect premium and progressively reduce cost basis. This is a [[Diagonal-Spread]] structure by construction: same underlying, different strikes, different expirations.

### 3. Long-term Directional Exposure Without Margin

Investors who want bullish (or bearish) exposure over a multi-year thesis — earnings recovery, product cycle, macro re-rating — can express that view through LEAPS without the overnight margin risk of futures or leveraged ETFs.

## How LEAPS Behave Differently from Short-dated Options

![[chart-leaps-vs-stock.png]]

**[[Theta-Decay]] is slower and back-loaded.** Theta on a 24-month option is a fraction of theta on a 30-day option with the same strike. The decay curve is relatively flat early in a LEAPS position and steepens as expiration approaches. This is data-backed: theta scales approximately with 1/√T, so doubling time to expiration roughly halves daily decay.

**[[Vega]] sensitivity is high.** LEAPS prices move substantially with implied volatility changes. A 5-point IV drop on a 24-month position can cost more in P&L than several months of favorable delta movement. This cuts both ways: buying LEAPS after a volatility spike is expensive; buying after a vol compression is more favorable.

> [!tip]
> Buying LEAPS when [[IV-Rank]] is below 30 reduces the vega drag. You take on less risk of IV mean-reversion working against you on entry.

**Less responsive to short-term news.** A one-day earnings move, a Fed statement, or a sector rotation creates less percentage impact on a 70-delta LEAPS call than on a 30-day near-the-money option. The long time horizon smooths event-driven shocks — which is a feature for long-term thesis plays and a limitation if you need tactical event exposure.

## Entry Parameters

| Parameter | Guideline |
|---|---|
| Delta | 0.70–0.80 (deep ITM) |
| Expiration | 12–24 months out (18 months is a common starting point) |
| Strike selection | Choose the strike that produces target delta; avoid going above 0.85 delta as liquidity thins |
| Bid-ask spread | Prefer underlyings where the LEAPS spread is under 2% of mid — wide spreads erode edge immediately |

> [!danger]
> Buying low-delta (0.20–0.40) LEAPS as "lottery tickets" on a long-term thesis is a common beginner mistake. The probability of achieving profitability is low, theta still accumulates, and any IV contraction compounds the loss. Stick to high-delta LEAPS if the goal is stock replacement or PMCC foundation.

## Assignment Risk

As the buyer of a LEAPS call or put, **assignment risk is zero** — you hold the long side of the contract. You may choose to exercise early (almost never optimal for calls), but you cannot be assigned.

## Rolling and Exit

- Roll out to maintain the LEAPS designation if you want to stay in the position: when the LEAPS falls inside 6–8 months, consider rolling to a new 15–18 month expiry.
- Close (sell to close) if the thesis is invalidated or if the position has captured the bulk of its potential gain.
- In a [[PMCC]] structure, coordinate LEAPS rolls with the short call management cycle.

## Related Notes

- [[PMCC]] — full strategy using LEAPS as the long leg
- [[Diagonal-Spread]] — the structural category PMCC belongs to
- [[LEAPS-Investing]] — using LEAPS in a long-term portfolio context (buy-and-hold framing)
- [[Covered-Call]] — comparison: same income mechanics, different capital requirements
