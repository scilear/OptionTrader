---
title: Rho (Interest Rate Sensitivity)
tags:
  - foundations
  - greeks
aliases:
  - Rho
  - Interest rate Greek
status: draft
related:
  - "[[Greeks-Overview]]"
---

# Rho (Interest Rate Sensitivity)

Rho measures how much an option price changes when interest rates move 1%.

**Definition:** ∂Price / ∂Rate

**In practice for SPX options:** Rho is the *least important* Greek for most traders because:
- Current rates are in the 4–5% range
- A 1% rate move is rare
- Impact is $2–5 per option at most

**When rho matters:**
- Long-dated LEAPS (1–3 years) are sensitive to rate changes
- Portfolio hedging across equities + bonds (rate moves affect both)
- Never the primary decision for short-term options

For most traders: ignore rho and focus on [[Delta]], [[Gamma]], [[Theta-Decay]], [[Vega]].
