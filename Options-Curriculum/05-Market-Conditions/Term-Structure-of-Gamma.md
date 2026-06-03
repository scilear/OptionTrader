---
title: Term Structure of Gamma (Across Maturities)
tags:
  - market-conditions
  - gex
  - term-structure
  - time-decay
aliases:
  - Gamma term structure
  - Multi-maturity GEX
  - Temporal layering
status: draft
related:
  - "[[Gamma-Regime-and-GEX]]"
  - "[[Open-Interest]]"
  - "[[0DTE-Overview]]"
  - "[[Gamma-Tsunami]]"
---

# Term Structure of Gamma (Across Maturities)

Gamma exposure across maturities follows a **structured dominance hierarchy**: **near-term options rule the day, unless far-term options are deeply in-the-money (ITM).**

When calculating aggregate GEX, market participants sum gamma across *all* strikes and *all* expirations. But they are not equal. Time to expiration and moneyness determine each maturity's contribution to the market's mechanical behavior.

## The Core Principle

**Gamma decreases dramatically as time to expiration increases.** The term structure of gamma forms an inverse pyramid: 0DTE at the top (explosive), monthlies in the middle (moderate), and far-dated options at the base (nearly dormant) — unless those far-dated options are deep ITM.

---

## The 0DTE Dominance: Short-Term Earthquake

0DTE options have completely reshaped intraday market dynamics. They now drive close to **half of all SPX volume**, and their gamma is uniquely explosive.

### Why 0DTE Gamma is Extreme

- **Exponential Growth**: Unlike longer-dated options, gamma in 0DTE contracts doesn't increase linearly—it grows **exponentially** as expiration approaches
- **Massive Delta Swings**: A ~1% market move can shift delta from 0.50 to 0.95 (or 0.05) within hours
- **Continuous Rebalancing**: Dealers must hedge in real time; static hedging is impossible
- **Volume Integration**: Correlation between 0DTE volumes and spot price movements increased from 0.25–0.30 (pre-2021) to 0.59 (2023), indicating deep market integration

### Result

On any given trading day, the gamma exposure of 0DTE options **massively overwhelms** the contribution of longer-dated contracts. The first step in reading GEX is to "identify the expirations that matter today (often 0DTE and the nearest weekly)."

---

## The Term Structure Table (ATM Options)

| Maturity | Gamma per Option | Hedging Speed | Dominant Influence |
|---|---|---|---|
| **0DTE / Weekly** | Extremely High | Milliseconds (real-time) | Intraday to a few days |
| **Monthly** | Moderate | Minutes to hours | Weeks |
| **Quarterly / LEAPS** | Very Low | Hours to days | Long-term structural anchors |

This explains why aggregate GEX is essentially a **short-dated gamma number**. Far-dated, ATM options contribute negligibly.

---

## The Far-Dated Exception: Deep ITM Options

There is one crucial exception to the term structure rule: **Deep In-The-Money options.**

### Deep OTM Options
- Have gamma near zero regardless of time to expiration
- Contribute nothing to dealer hedging flows
- Example: A quarterly call 10% OTM is practically worthless; its delta ≈ 0, gamma ≈ 0

### Deep ITM Options
- Behave almost like stock (delta ≈ 1)
- Have low instantaneous gamma
- **But: Create powerful structural floors/ceilings**

**Example:** A quarterly deep ITM put with significant OI can act as a **long-term anchor** that provides structural support for weeks or months, even if its moment-to-moment gamma contribution is lower than a 0DTE option.

> [!note]
> A trader must watch **both** immediate 0DTE levels (intraday mechanics) **and** significant far-dated OI concentrations (long-term structure). They are complementary, not competing views.

---

## Convergence and Divergence: When Maturities Align or Conflict

### Convergence: The "Gamma Tsunami" Setup

When multiple expirations have significant gamma concentrated at the **same strike price**, the effect is **multiplicative**.

- 0DTE gamma + weekly gamma + monthly gamma = **extremely powerful gamma wall**
- Most common around major monthly or quarterly expirations
- Price can "pin" to the strike with remarkable precision
- Example: An SPX level that is a major psychological number (e.g., 5000) often has gamma converged across multiple expirations, making it an unusually sticky level

> [!tip]
> Look for **gamma convergence** when analyzing "pinning" trades (e.g., butterflies targeting a high-gamma strike). Multiple expirations converging create stronger mechanical support.

### Divergence: The "Gamma Seesaw"

When maturities have **conflicting** gamma exposure:
- 0DTE may be negative (amplifying moves), destabilizing the market
- But longer-dated options may be positive (stabilizing)
- Example: Market dips, triggering negative 0DTE hedging (dealer selling)
- But if the dip reaches a zone where **quarterly puts have high positive gamma**, longer-dated dealers step in and **buy aggressively**, creating a floor
- Result: The longer-dated, positive gamma **overwhelms the short-term dynamics**, reversing the sell-off

> [!warning]
> This is why [[Gamma-Tsunami|gamma tsunamis]] sometimes fail. Always check if a deep decline will hit a zone where far-dated, deep ITM put gamma becomes extremely positive. That gamma seesaw can turn a potential disaster into a reversal.

---

## The Gamma Flip: The Unified Perspective

While contributions from different maturities vary, the market treats them as one aggregated force at the critical level: **the Gamma Flip**. This is the single price point where the sum total of gamma across *all* maturities crosses from positive (stabilizing) to negative (amplifying).

| Spot Relative to Flip | Aggregate Gamma | Market Behavior |
|---|---|---|
| **Well Above** | Positive (Long Gamma) | Volatility suppressed; mean reversion; premium-selling edge |
| **Near Flip** | Neutral | Regime uncertain; vol can spike if breached |
| **Below Flip** | Negative (Short Gamma) | Volatility amplified; trending; long-vol opportunities |

The gamma flip is the **single most important short-term vol regime signal** from options market positioning, regardless of which maturity mix created it.

### Case Study: August 5, 2024 Yen Carry Unwind

SPX was in positive gamma. The yen carry unwound, pushing SPX down through its gamma flip. Dealers flipped to negative gamma. Forced selling accelerated. **VIX spiked from ~17 to 38 within hours** — a +120% explosion driven entirely by mechanical gamma amplification, not fundamental selling.

---

## Practical Application

### When Analyzing GEX Levels:

1. **Start with 0DTE and nearest weekly** — they drive intraday behavior
2. **Check for monthly convergence** — is there a major technical level with multiple expirations' gamma concentrated there?
3. **Scan for far-dated, deep ITM concentrations** — are there structural support/resistance zones from quarterly or LEAPS options?
4. **Identify the gamma flip** — is price above or below the aggregate regime pivot?
5. **Watch for the seesaw** — if a decline is happening in negative 0DTE gamma, will it eventually hit a zone of strong far-dated positive gamma that could reverse it?

### Position Sizing:

- In positive gamma regimes with **no far-dated ITM gamma backstop**, size short premium modestly — the immediate stabilization could break at any moment
- In positive gamma regimes where **far-dated ITM gamma is extremely strong**, you can be more aggressive in short premium — the long-term floor is robust
- Below the gamma flip, **reduce size dramatically** — you are in destabilizing territory where small moves can cascade

---

## Key Insight

The art of using GEX effectively is to recognize which **maturity layer is currently driving the market** and to **anticipate how the longer-term structure might reinforce or ultimately reverse** that short-term flow. A 0DTE gamma wall might only matter for a day. A quarterly gamma wall can matter for weeks. And the gamma flip — the aggregate of all maturities — tells you the regime's character on any given day.