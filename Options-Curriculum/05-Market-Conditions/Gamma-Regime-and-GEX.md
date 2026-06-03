---
title: Gamma Regime and GEX
tags:
  - options/market-conditions
  - options/gamma
  - options/dealer-positioning
  - options/strategy-selection
  - options/volatility-regime
aliases:
  - GEX
  - Gamma Exposure
  - Positive Gamma
  - Negative Gamma
  - HVL
status: draft
related:
  - "[[Gamma]]"
  - "[[Open-Interest]]"
  - "[[Gamma-Walls-Call-Put]]"
  - "[[Index-vs-Single-Stock-GEX]]"
  - "[[Market-Condition-Classification]]"
  - "[[Iron-Condor]]"
  - "[[High-IV-Playbook]]"
  - "[[0DTE-Iron-Condor]]"
---

# Gamma Regime and GEX (Gamma Exposure)

**Gamma Exposure (GEX)** is a measure of the total net gamma from all options across all strikes and expirations. It quantifies the aggregate hedging flows that market makers are compelled to execute as price moves.

When a market maker sells an option, they must hedge the directional risk to stay [[Delta|delta-neutral]]. As the underlying price moves, the option's delta changes, forcing the dealer to continuously adjust their hedge—buying or selling shares to remain neutral. This constant rebalancing, driven by gamma, creates measurable hedging flows that influence intraday price action.

**GEX is a market-structure input that tells you *how* the market will behave, not *where* it will go.** It's distinct from the [[Gamma|gamma Greek]] of individual options—GEX reveals the aggregate mechanical force across all dealer positioning.

## The Core Mechanism: Dealer Hedging Flows

### Example: A Market Maker Sells a Call
- Sells 1 SPX 5100 call (delta = +0.50)
- Buys 50 shares (δ hedge) to stay delta-neutral
- Price rallies to 5050 → call delta increases to +0.60
- Market maker must sell 10 more shares to rebalance
- This forced selling can slow the rally

This rebalancing, aggregated across all dealers and all contracts, creates GEX flows that influence short-term price momentum.

> [!note]
> GEX data is published by SpotGamma, Barchart, InsiderFinance, TradingView, and others. It is derived from public open interest and model-implied dealer positioning. Treat it as a real-time map of mechanical pressure, not a price forecast.

---

## GEX Calculation and Dollar Impact

GEX is calculated as:

```
GEX = Gamma × Open Interest × Contract Multiplier × Spot Price²
```

The result is expressed as a **dollar value**. 

**Example:** SPX with +$5 billion GEX means:
- For every 1% move in SPX, dealers need to adjust their hedges by ~$5 billion in stock
- This creates mechanical pressure that tends to slow or reverse the move
- Larger GEX = more powerful mechanical effect

> [!warning]
> GEX is NOT precise, but it's the best available proxy for hidden dealer flows. It assumes market makers are the counterparty to all open interest, which is a necessary approximation.

## The HVL: The Gamma Flip

The **High Volatility Level (HVL)** is the price level where aggregate dealer GEX **flips from positive to negative** (or vice versa). It is the critical regime pivot calculated daily from open interest distribution.

- **Price above HVL → Positive Gamma regime** (dealers net long gamma)
- **Price below HVL → Negative Gamma regime** (dealers net short gamma)

Crossing the HVL is a **behavioral regime shift**, not a technical support/resistance. It changes *how* the market moves mechanically.

---

## Positive Gamma Regime (Long Gamma)

**Condition:** SPX is trading **above the HVL**. Dealers hold **net long gamma** exposure.

**Dealer behavior:** As price rises, dealers must **sell** to hedge (delta increases, they reduce). As price falls, dealers must **buy** to hedge (delta decreases, they add). They are **hedging against the move**.

**Market effect: Stabilizing & Range-Bound**
- Intraday rallies stall as dealers sell into strength
- Intraday dips get support as dealers buy weakness
- Volatility is **structurally dampened** — moves are slower and revert toward center
- Price action tends to oscillate within a **bounded range** defined by [[Gamma-Walls-Call-Put|gamma walls]]
- Mean reversion is mechanical, not just statistical

**Why:** Dealers' hedging flows **push against the move**. A 100-point rally triggers dealer selling, which naturally caps further rally. A 100-point drop triggers dealer buying, which creates a floor.

**Strategy implications:**
- ✅ **Iron Condors** — the suppressed volatility and range-bound action favor defined-risk spreads
- ✅ **Credit spreads** — theta decay works while gamma stays bounded
- ✅ **Short strangles** — mechanical support and resistance prevent catastrophic loss
- ❌ Avoid **long premium** — the dampening effect erodes time value faster than theta compensates
- ❌ Avoid **aggressive directional moves** — the market is actively suppressed

> [!tip]
> Positive gamma does **not** mean bullish. A market can be in a Positive Gamma regime while grinding lower. The regime describes volatility *character* (suppressed, range-bound), not direction. Size short premium accordingly — the regime limits max loss but not max profit.

---

## Negative Gamma Regime (Short Gamma)

**Condition:** SPX is trading **below the HVL**. Dealers hold **net short gamma** exposure.

**Dealer behavior:** As price rises, dealers must **buy** to hedge (delta increases, they add). As price falls, dealers must **sell** to hedge (delta decreases, they reduce). They are **hedging with the move**, amplifying it.

**Market effect: Destabilizing & Accelerating**
- A 50-point rally can trigger $1B+ in dealer buying, pushing it to 100 points
- A 50-point drop can trigger $1B+ in dealer selling, pushing it to 100 points  
- Moves **accelerate and cascade** rather than revert
- [[Gamma-Walls-Call-Put|Gamma walls]] that provided support/resistance become **trigger points for acceleration**
- Volatility is **structurally amplified** — realized vol exceeds implied, gaps widen intraday

**Why:** Dealers' hedging flows **push with the move**. A 100-point rally triggers dealer buying, which fuels further buying. A 100-point drop triggers dealer selling, which accelerates the drop. **It's a feedback loop, not a stabilizer.**

**Strategy implications:**
- ❌ **Iron Condors** — walls break through; max loss becomes a floor, not a ceiling
- ❌ **Credit spreads** — undefined risk becomes **very defined and painful**
- ❌ **Short strangles** — both sides can gap-down or gap-up simultaneously
- ✅ **Long premium strategies** — long straddles, long calls/puts, protective hedges
- ✅ **Directional momentum plays** — trends accelerate; directional bets have positive carry
- ✅ **Reduced overall size** — the amplifying effect can turn small losses into catastrophes

> [!danger]
> Below the HVL, the Put Wall is **not a floor — it's an accelerator.** When price breaks below the Put Wall in negative gamma, dealer selling cascades, creating a potential freefall. This is **the most dangerous regime for naked short premium.** Treat a break below HVL with the same urgency as a stop-loss hit. If you're short premium, close positions or reduce size immediately. The mechanical force is against you.

---

## The Four-Layer Environment Check

Before selecting a strategy, evaluate the market through four layers in sequence:

| Layer | Question | Informs |
|---|---|---|
| 1. Volatility regime | Above or below HVL? | Positive vs. negative gamma character |
| 2. Key gamma levels | Where are C1/P1 walls? | Strike-level range bounds |
| 3. Open interest distribution | Concentration of calls vs. puts across strikes | Confirmation of wall strength |
| 4. Volume / flow | Net call or put volume today? | Current sentiment and real-time positioning |

This four-layer read provides the environmental context before applying [[Market-Condition-Classification|the IV-and-trend classification matrix]]. GEX regime and IV level are complementary — a high-IV environment in positive gamma is very different from high-IV in negative gamma.

---

## Regime × IV Matrix

| | **Positive Gamma** | **Negative Gamma** |
|---|---|---|
| **High IV** | Sell premium with moderate wings; dealer dampening helps condors | Hedge, reduce size; cascading vol makes selling dangerous |
| **Low IV** | Calendars, tight flies; dampened vol compresses well | Avoid most strategies; moves are episodic and uncontrollable |

---

## Practical Checklist

1. Check HVL daily before market open (available from GEX data services)
2. Is SPX above or below HVL? → Classify regime
3. Identify C1 (Call Wall) and P1 (Put Wall) strikes → See [[Gamma-Walls-Call-Put]]
4. Cross-check with VIX level → Apply [[Market-Condition-Classification]]
5. Select strategy family appropriate to the combined regime
6. If SPX breaks below HVL intraday, treat it as a regime-shift signal — tighten stops or reduce short premium exposure

The regime does not guarantee outcomes. It shifts the probability distribution of intraday behavior in a way that is systematically exploitable when paired with defined-risk structures and disciplined exits.
