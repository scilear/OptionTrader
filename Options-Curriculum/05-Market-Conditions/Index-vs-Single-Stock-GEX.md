---
title: Index vs Single-Stock GEX and Correlation
tags:
  - market-conditions
  - gex
  - correlation
  - index-mechanics
aliases:
  - Index GEX
  - Single-stock GEX
  - Market correlation
status: draft
related:
  - "[[Gamma-Regime-and-GEX]]"
  - "[[Market-Condition-Classification]]"
---

# Index vs Single-Stock GEX and Correlation

Index-level GEX and single-stock GEX are **deeply interconnected in a bidirectional relationship** governed by **market correlation**. Understanding which dominates at any moment is critical for predicting price action.

## The Two-Way Street

### Index → Single Stocks: The Gravity of the Broad Market

Index-level GEX (SPX, NDX) has become the primary "transmission hub" for mechanical hedging flows. When dealers hedge index options, those flows cascade into individual stocks through two channels:

**1. ETF Hedging Effect**
- Dealers hedging SPX or NDX options trade SPY, QQQ, and related ETFs
- This creates broad pressure across all index components
- If SPX has positive gamma suppressing volatility, individual stocks experience less erratic moves — **regardless of their own GEX**

**2. Composition Effect**
- Mega-cap stocks (NVDA, MSFT, AAPL, TSLA) dominate index weighting
- Their individual options activity directly moves the index
- In high-correlation regimes, index GEX overwhelms stock-level GEX

**Implication:** In **high-correlation** environments, **index GEX is destiny**. A positive gamma environment at the SPX level suppresses individual stock moves, even if that stock has negative GEX.

### Single Stocks → Index: The Mega-Cap Tail Wagging the Dog

This is the increasingly powerful influence.

**The NVDIA Case Study (2025-2026)**

NVIDIA exemplifies this dynamic:
- NVDA has become the single largest contributor to S&P 500 earnings growth
- A handful of mega-caps (including NVDA) account for ~69% of SPX gains since March 2026
- NVDA's extreme GEX levels have surged, driven by massive options volume in AI mega-caps
- **This creates a self-reinforcing gamma loop**: A NVDA rally forces dealers to hedge NVDA options → which flows into the index via futures/hedging → which lifts the entire SPX → which flows back into NVDA due to its weight

**Result:** "As Nvidia goes, so goes Wall Street." A sharp move in NVDA triggers hedging flows that influence not just NVDA's price, but the entire index.

**Implication:** When a mega-cap with extreme GEX moves, **watch the index**. Its gamma exposure is large enough to move the whole market.

---

## The Master Switch: Market Correlation

The question of **which direction dominates** has a clear answer: **it depends on the market correlation regime.**

| Correlation Regime | Dominant Influence | Dynamic | Strategy |
|---|---|---|---|
| **Low Correlation** | Single-stock GEX | Stocks move independently. Index GEX matters less. Each stock's gamma walls are locally important. | Trade individual gamma walls; use stock-specific setups. |
| **High Correlation** | Index GEX | Macro flows override individual stock dynamics. All stocks move together regardless of individual gamma. The "tide lifts (or sinks) all boats." | Follow index GEX; individual stock GEX is noise. |

### Low-Correlation Environment

**When:** Market rotation happens (tech underperforms, value rallies), sector divergence is high, individual catalysts drive stocks.

**What happens:**
- Single stocks can rally while the SPX falls (or vice versa)
- NVDA positive GEX doesn't guarantee SPX positive GEX
- Individual [[Gamma-Walls-Call-Put|gamma walls]] are locally important
- Strategy concentration per stock matters

**Strategy implication:** Trade individual stock gamma walls and setups. Index GEX is a secondary filter.

### High-Correlation Environment

**When:** Macro shock (rate hike, Fed announcement), euphoria/panic, massive earnings miss/beat.

**What happens:**
- All mega-caps move together
- Individual stock gamma is overwhelmed by index GEX flows
- A break of the SPX gamma wall cascades through all index components
- Diversification provides no protection; sector rotation doesn't work

**Strategy implication:** Follow index GEX first. Individual stock GEX is a noise filter. A positive gamma SPX environment suppresses *all* individual stock volatility.

---

## Practical Application: The Correlation Check

Before entering a trade on an individual stock, ask:

1. **What's the current correlation level?** (1-month correlation high or low?)
   - Check: Is the market moving as one, or as individual components?
   
2. **What's the index GEX regime?** (Positive or negative?)
   - If negative GEX at SPX level, even a bullish single-stock setup is risky
   - If positive GEX at SPX level, individual stock gamma walls are reinforced
   
3. **What's the single-stock GEX?** (Positive or negative?)
   - If correlation is low, stock GEX is decisive
   - If correlation is high, stock GEX is secondary to index GEX

4. **Is this a mega-cap?** (NVDA, MSFT, AAPL, TSLA, GOOG?)
   - If YES and correlation is high, its GEX directly influences the index
   - If NO and correlation is high, it's swept along by index flows

---

## Key Insight: The Feedback Loop

In **high-correlation regimes with extreme single-stock GEX on a mega-cap**, you can get **self-reinforcing gamma spirals:**

**The NVDA Rally Loop:**
1. NVDA rallies → dealers hedge short calls by selling NVDA
2. NVDA selling slows the rally → dealers adjust
3. But NVDA has 7% weight in SPX → this hedging affects the index
4. Index rise → flows back into NVDA via index hedging
5. NVDA continues higher → cycle repeats

This is **mechanical amplification**. The stock's gamma exposure is so large that it moves the index, and the index's weight in that stock creates feedback.

**Implication:** In high-correlation panics, mega-cap GEX can be **more important than the fundamental catalyst**. The gamma mechanics overwhelm technicals.

---

## Summary

- **Yes, index and single-stock GEX influence each other bidirectionally.**
- **Mega-caps like NVDA wield outsized influence**, creating two-way feedback loops.
- **Correlation is the master switch:**
  - Low correlation: stock GEX dominates
  - High correlation: index GEX overrides everything
- **In high-correlation stress**, even a bullish single-stock setup fails if index GEX is negative. The tide overwhelms the tide pool.

Always check **both index and single-stock GEX**, and **adjust your conviction based on the correlation regime**.