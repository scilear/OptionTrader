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
  - "[[Market-Condition-Classification]]"
  - "[[Gamma-Walls-Call-Put]]"
  - "[[Iron-Condor]]"
  - "[[High-IV-Playbook]]"
  - "[[0DTE-Iron-Condor]]"
---

# Gamma Regime and GEX

Market makers (dealers) hold large, continuously adjusted hedges across thousands of options positions. The aggregate direction of that hedging — whether dealers are buying or selling the underlying to stay delta-neutral — has a measurable effect on intraday volatility. **Gamma Exposure (GEX)** quantifies this aggregate, and its sign tells you whether dealer activity is dampening or amplifying the market's moves.

This is a distinct analytical layer from the [[Gamma|gamma Greek]] of individual positions. GEX is a market-structure input that informs which strategy family to deploy, not a signal about which direction to trade.

> [!note]
> GEX data is published by services like SpotGamma, SqueezeMetrics, and Market Chameleon. It is derived from public options open interest and model-implied dealer positioning. Treat it as a probability-weighted environment reading, not a precision forecast.

---

## The HVL: The Regime Pivot

The **High Volatility Level (HVL)** is the price level at which aggregate dealer GEX flips from positive to negative. It is calculated daily from the current open interest distribution across all strikes.

- **Price above HVL → Positive Gamma regime**
- **Price below HVL → Negative Gamma regime**

The HVL is not a support or resistance level in the technical sense. It is a behavioral pivot: crossing it changes *how* the market moves, not necessarily *where* it moves next.

---

## Positive Gamma Regime

**Condition:** SPX (or the relevant underlying) is trading above the HVL.

**Dealer behavior:** Dealers are net long gamma. To stay delta-neutral, they sell into rallies and buy into dips — hedging *against* the move.

**Market effect:**
- Intraday ranges compress
- Intraday trends stall and reverse at predictable levels
- Volatility is structurally dampened
- The market tends to oscillate within a range defined by the [[Gamma-Walls-Call-Put|Call Wall and Put Wall]]

**Strategy implications:**
- Ideal environment for [[Iron-Condor]] and credit spread strategies
- Short premium structures benefit from the mechanical reversion tendency
- Iron condors can be anchored near the Call Wall (upper) and Put Wall (lower) — the range tends to hold
- Avoid aggressive directional long premium; the dampening effect erodes value

> [!tip]
> Positive gamma does **not** mean bullish. A market can be in a Positive Gamma regime while trending slowly lower. The regime describes volatility *character*, not direction. Do not conflate the two.

---

## Negative Gamma Regime

**Condition:** SPX is trading below the HVL.

**Dealer behavior:** Dealers are net short gamma. To stay delta-neutral, they sell into dips and buy into rallies — hedging *with* the move.

**Market effect:**
- Moves accelerate rather than revert
- Intraday drops can cascade: dealer selling begets more selling
- VIX tends to spike; realized volatility overtakes implied volatility
- The market can gap through levels that would have acted as support in positive gamma

**Strategy implications:**
- Dangerous environment for short premium sellers — the mechanical reversion that profits iron condors is absent
- Undefined-risk short positions (strangles, naked puts) carry outsized gap risk
- Directional hedges (long puts, put spreads) are structurally appropriate
- Reduce overall position size; volatility per unit of time is elevated

> [!danger]
> A break below the HVL is not a dip to buy for premium sellers. Dealer hedging flows *accelerate* the move lower. The Put Wall (see [[Gamma-Walls-Call-Put]]) is no longer a support floor in negative gamma — it becomes a level where a break triggers additional dealer selling. Treat regime shifts with the same urgency as a stop-loss trigger.

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
