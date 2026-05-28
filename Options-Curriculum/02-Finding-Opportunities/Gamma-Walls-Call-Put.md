---
title: Gamma Walls — Call Wall and Put Wall
tags:
  - finding-opportunities
  - gamma
  - dealer-positioning
  - market-structure
  - setup-recognition
aliases:
  - Call Wall
  - Put Wall
  - Gamma Wall
  - GEX Levels
status: draft
related:
  - "[[Gamma-Regime-and-GEX]]"
  - "[[Setup-Recognition-Patterns]]"
  - "[[Iron-Condor]]"
  - "[[Bull-Put-Spread]]"
  - "[[Bear-Call-Spread]]"
  - "[[Entry-Confirmation-Signals]]"
  - "[[Market-Condition-Classification]]"
---

# Gamma Walls — Call Wall and Put Wall

A gamma wall is a strike price where aggregate **Net Gamma Exposure (GEX)** is heavily concentrated. At these strikes, market maker hedging activity is at its densest, which creates a measurable tendency for price to react — either reversing, stalling, or, if broken, accelerating through.

Gamma walls are **reaction zones, not trade signals.** The question is never "will price bounce here?" — it is "if price reaches this level, what does hedging flow imply about the probable next move, and what does price action confirm?"

> [!danger]
> The most common beginner error with gamma walls: treating the Put Wall as a guaranteed support level and buying calls when price touches it. The Put Wall is where dealer hedging *may* provide support in a positive gamma regime. In negative gamma — or if the wall breaks — dealers accelerate the move lower. Assuming a bounce without confirmation is a structural mistake.

---

## The Two Walls

### Call Wall (C1)

The strike with the highest concentration of **call gamma** above current price.

**Dealer behavior approaching C1 from below:**
Dealers who are net short calls must sell the underlying to hedge as price rises toward their strike. This selling pressure tends to cap rallies — the wall acts as resistance.

**If C1 breaks:**
Dealers must rapidly buy to cover their new exposure. A breakout above C1 can trigger a "gamma squeeze" — a fast, self-reinforcing move higher as dealer buying accelerates the rally.

**What to watch:**
- Stalling price action and decreasing momentum as C1 approaches
- Volume spike at C1 on the breakout attempt
- A slow, grindy approach to C1 with declining call volume is more likely to stall

### Put Wall (P1)

The strike with the highest concentration of **put gamma** below current price.

**Dealer behavior approaching P1 from above:**
Dealers net short puts must buy the underlying to hedge as price falls toward their strike. This buying tends to slow the decline — the wall acts as support.

**If P1 breaks:**
Dealers must sell aggressively to hedge the expanded put exposure. A break below P1 triggers the opposite of the call squeeze: dealer selling cascades the move lower.

**What to watch:**
- Slowing rate of decline and IV spike as P1 approaches (confirmation of dealer buying)
- A clean break of P1 on elevated put volume signals regime acceleration — do not fade it
- After a P1 break, wait for stabilization and a successful *retest* from below before considering long positions

---

## Confluence: When Walls Matter Most

A gamma wall becomes a high-probability reaction zone when multiple factors align at the same strike:

| Factor | Signal |
|---|---|
| High Net GEX at strike | Primary wall identification |
| High Open Interest (calls or puts) | Confirms large positioning at the level |
| High volume on the approach | Active positioning in real time |
| Proximity to a technical level | Price memory adds mechanical confirmation |

Confluence of 3+ factors at a single strike is the highest-quality setup. A wall with low open interest and low volume is a weak level — it may absorb dealer flow without a meaningful reaction.

---

## Strategic Application by Scenario

### Scenario A — Positive Gamma, Establishing a Range

**Context:** SPX is above the HVL ([[Gamma-Regime-and-GEX|positive gamma regime]]). C1 is at 5150, P1 is at 4850.

**Iron Condor setup:**
- Short call spread anchored near C1: sell 5150 / buy 5200
- Short put spread anchored near P1: sell 4850 / buy 4800
- Expected range: dealer dampening keeps SPX between the walls
- Take profit at 50% max credit; do not wait for expiry

**Why this works:** In positive gamma, dealer hedging mechanically reverts price away from the walls. The condor collects premium for a range-bound outcome that dealer flows are actively enforcing.

### Scenario B — Call Wall Breakout

**Context:** SPX is approaching C1 with momentum, volume is rising, not fading.

**Action:**
- Do not short the wall assuming rejection
- Wait for a confirmed stall (1–3 candles of range compression at the wall with declining volume)
- If price holds above C1 on a retest, consider a [[Bull-Put-Spread]] below the new support — the breakout shifts the probability range upward
- A false breakout (price tags C1, then reverses sharply on volume) is the rejection confirmation — *then* a short call spread makes sense

### Scenario C — Put Wall Break in Negative Gamma

**Context:** SPX breaks below P1 with acceleration. HVL has already been lost.

**Action:**
- Do not buy calls assuming a bounce — in negative gamma, the P1 break is a cascade signal
- Close or reduce net short delta exposure immediately
- If holding an iron condor, the put spread is threatened; roll the short put down or exit the position rather than waiting
- Consider protective puts (see [[Bear-Call-Spread]] for the inverse logic on using defined-risk in directional moves)

See [[Entry-Confirmation-Signals]] for the full confirmation framework before acting on any gamma level.

---

## The Four-Layer Read (Summary)

Use this checklist before any trade entry when markets are near a gamma wall:

1. **Regime check:** Above or below HVL? → Positive = dampening; Negative = amplifying
2. **Wall identification:** Where are C1 and P1 today?
3. **Confluence check:** Does C1/P1 have high OI and current volume?
4. **Momentum check:** Is price approaching with expanding or contracting volume?

Then decide: is this a reaction zone to structure a range trade around, or an acceleration zone to respect and step aside from?

> [!tip]
> Gamma walls are most reliable early in the week when open interest is at its peak for that expiry. As the week progresses and open interest rolls off into expiry, the mechanical hedging force behind the walls weakens. A C1 that held all week can become irrelevant by Thursday afternoon as dealers close positions.

---

## Cross-Reference

- [[Gamma-Regime-and-GEX]] — the HVL and positive/negative gamma regimes that determine wall behavior
- [[Setup-Recognition-Patterns]] — how gamma walls fit into the broader setup checklist
- [[Iron-Condor]] — the primary strategy for ranging positive-gamma environments
- [[Market-Condition-Classification]] — IV regime classification that pairs with GEX regime
