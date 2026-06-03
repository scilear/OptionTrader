---
title: Open Interest (OI)
tags:
  - foundations
  - options-mechanics
  - gex
aliases:
  - OI
  - Open interest
status: draft
related:
  - "[[Gamma-Regime-and-GEX]]"
  - "[[Gamma-Walls-Call-Put]]"
  - "[[Implied-Volatility]]"
---

# Open Interest (OI)

**Open Interest (OI)** is the **total number of outstanding option contracts that have not yet been closed or exercised.**

This is critical for understanding [[Gamma-Regime-and-GEX|GEX]] because OI is the "size" of the aggregate gamma risk that dealers must hedge.

## What OI Actually Represents

- **One contract in OI** = one buyer and one seller with an open position
- OI counts that contract **once**, not per side
- OI **increases** when new buyer-seller pairs create a fresh contract
- OI **decreases** when positions are closed (buyer sells to close, or seller buys to close) or exercised
- OI is a **snapshot at a point in time**, not a flow

## Common Misconceptions

| Misconception | Reality |
|---|---|
| OI = total contracts sold today | ❌ That's **volume**. OI tracks *standing* contracts, not daily trades. |
| OI = contracts available for sale | ❌ Options aren't like inventory. Any trader can sell to open whenever a buyer exists. |
| OI = contracts held by buyers only | ❌ Each contract has both a buyer and a seller; OI counts it once. |

## OI vs Volume: The Key Difference

- **Volume:** Contracts traded *today* (number of transactions)
- **Open Interest:** Contracts *still open* (cumulative standing exposure)

Example: 
- Monday: Buy 1000 calls → Volume = 1000, OI = 1000
- Tuesday: Sell 500 of those calls to close → Volume = 500, OI = 500
- Tuesday: Buy 200 new calls → Volume = 700, OI = 700

OI is more useful for GEX because it shows the *ongoing* gamma risk that requires dealer hedging. Volume tells you what traded; OI tells you what's still *live*.

## Why OI Matters for GEX

OI is the **foundation of the GEX formula:**

```
GEX = Gamma × Open Interest × Contract Multiplier × Spot Price²
```

- **Gamma** tells you *how fast* delta changes (sensitivity)
- **Open Interest** tells you the *size* of contracts exposed to that gamma
- **The product** reveals the total dollar hedging pressure at each strike

**Example:**
- 5100 call: gamma = 0.005, OI = 100,000 contracts, spot = 5000
- GEX contribution ≈ 0.005 × 100,000 × 100 × 5000² = $12.5 billion per 1% move

High OI at a strike + high gamma (near ATM) = **gamma wall** (wall of dealer hedging pressure).

## OI and Market Makers

Here's the crucial assumption in GEX modeling:

**Market makers are assumed to be the counterparty to all OI.**

When you buy or sell an option, a market maker (dealer) almost always takes the other side. So OI effectively represents **the total risk inventory that market makers are holding across all strikes and expirations.**

> [!note]
> This is an approximation. Not every OI contract has a dealer on one side; some are retail-to-retail or institutional-to-institutional. But dealers do provide the vast majority of liquidity, so this assumption works as a **practical proxy for aggregate dealer exposure.**

## 0DTE Effect: When OI Becomes Explosive

The impact of OI on GEX is **most dramatic with 0DTE (zero days to expiration) options.**

Why?
- 0DTE options have **extreme gamma** (maximum rate of delta change)
- Even a small OI in 0DTE contracts creates **massive gamma walls**
- Dealer hedging flows for 0DTE options can dominate intraday price action

Example: 100 0DTE contracts at ATM (gamma = 0.50) have the same gamma impact as 10,000 contracts at a far OTM strike (gamma = 0.005).

This is why 0DTE trading is **high-frequency and structurally important** — OI × gamma is explosive, creating fleeting hedging pressure that moves price in minutes.

## Key Takeaway

**Open Interest is the "size" of the bet; gamma is the "leverage" on that bet.**

OI alone doesn't create market impact. OI × gamma at each strike creates [[Gamma-Regime-and-GEX|GEX]], which drives dealer hedging behavior and, by extension, short-term price action. When OI is concentrated at a single strike *and* that strike is near ATM (high gamma), you have a [[Gamma-Walls-Call-Put|gamma wall]] — a level where mechanical hedging pressure is strongest.