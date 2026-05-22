---
title: Greeks Overview
tags:
  - foundations
  - greeks
  - risk-management
  - trade-management
aliases:
  - Options Greeks
  - Greek Sensitivities
status: draft
related:
  - "[[Delta]]"
  - "[[Gamma]]"
  - "[[Theta-Decay]]"
  - "[[Vega]]"
  - "[[IV-Rank]]"
  - "[[Position-Sizing]]"
  - "[[Trade-Management]]"
---

# Greeks Overview

Greeks are partial derivatives of an option's price with respect to different inputs. For active traders, they are not academic curiosities — they are a real-time dashboard telling you how your position behaves right now and how it will behave tomorrow.

![[chart-greeks-sensitivity.png]]

## Quick Reference Table

| Greek | What it measures | High = | Low = | Key decision |
|-------|-----------------|--------|-------|--------------|
| [[Delta]] | Directional exposure | Acts like more stock | Near-neutral directionally | Size and hedge the position |
| [[Gamma]] | Rate of delta change | Delta accelerates with moves | Delta stable near current price | Manage around earnings/events |
| [[Theta-Decay]] | Daily time decay | Earns more per day (seller) / Loses more per day (buyer) | Slow decay, cheaper carry | Entry timing, duration selection |
| [[Vega]] | Sensitivity to IV changes | Large IV bet, good or bad | Modest IV exposure | Enter before or after vol events |
| Rho | Sensitivity to interest rates | More affected by rate changes | Minimal rate sensitivity | Rarely actionable for short-dated options |

---

## Delta — Directional Exposure

**Definition:** How much the option's price moves for a $1 move in the underlying.

**Practical read:** A delta of 0.30 means the option gains (or loses) roughly $0.30 for every $1 the stock moves. Long 10 contracts at 0.30 delta = equivalent to being long 300 shares directionally.

**Decision use:**
- Use delta to understand your net directional bet across a multi-leg position.
- Delta-neutral trades ([[Iron Condor]], [[Short Straddle]]) need periodic re-hedging as the underlying drifts.
- High absolute delta (> 0.70) means you are mostly trading the stock, not vol — reconsider the structure.

> [!tip] For defined-risk spreads, target the short strike at 0.20–0.30 delta. This keeps premium meaningful while giving the underlying room to move.

---

## Gamma — Delta Acceleration

**Definition:** How much delta changes for a $1 move in the underlying.

**Practical read:** High gamma means your delta is unstable. A position with gamma of 0.05 gains 0.05 additional delta for every $1 up move — your exposure accelerates quickly.

**Decision use:**
- Long gamma (long options) benefits from large, fast moves. Short gamma is hurt by them.
- Gamma risk spikes near expiration and near the money. A short option with 2 DTE can move from 0.40 delta to near 1.0 on a single-day move.
- Reduce position size when gamma exposure is large and you are short options. See [[Position-Sizing]].

> [!warning] Short gamma positions near expiration can suffer outsized losses from a single gap move. This is not a theoretical risk — it has wiped accounts. Always define max loss or set a hard stop before expiration week.

---

## Theta — Time Decay

**Definition:** How much the option loses in value per calendar day, all else equal.

**Practical read:** A theta of -0.05 means the option loses $5 per day per contract (100 shares) purely from time passing.

**Decision use:**
- Option sellers collect theta. [[Short Premium]] strategies (short straddle, iron condor, short strangle) are positive-theta trades.
- Theta accelerates in the final 30–45 DTE — this is why many traders target entry at 30–45 DTE and close at 50% profit.
- Buying options for direction? You are fighting theta every day you are right but not right enough.

> [!note] Theta is not linear. The decay curve is convex — it accelerates as expiration approaches, not a flat daily drip.

---

## Vega — Volatility Exposure

**Definition:** How much the option's price changes for a 1-point (1%) change in implied volatility.

**Practical read:** A vega of 0.15 means the option gains or loses $15 per contract for every 1-vol-point move in IV.

**Decision use:**
- Selling options when [[IV-Rank]] is high captures elevated vega premium. If IV reverts, you profit even if the underlying is flat.
- Long vega positions (long options, long straddles) profit from IV expansion — useful around events.
- A trade can be "right" on direction and still lose money if IV collapses after entry (vega crush).

> [!danger] Selling vega into a vol spike without defined risk (naked options) can produce losses that dwarf the premium collected. Vega scales with position size — even modest notional can carry extreme dollar sensitivity to a vol surge.

---

## Rho — Interest Rate Sensitivity

Rho measures sensitivity to changes in the risk-free rate. For options with less than 6 months to expiration, rho is small enough to ignore in most trade decisions. It becomes meaningful for long-dated LEAPS or in rate-volatile environments. Track it, but rarely act on it.

---

## Putting It Together

No Greek lives in isolation. A short iron condor is short delta/gamma, long theta, and short vega simultaneously. Managing the position means watching all four dials together, not one at a time. See [[Trade-Management]] for position-level Greek monitoring workflows.
