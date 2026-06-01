---
title: Volatility Smile and Skew
tags:
  - foundations
  - volatility
  - iv-surface
  - skew
aliases:
  - Volatility smile
  - Volatility skew
  - IV skew
status: draft
related:
  - "[[Implied-Volatility]]"
  - "[[Greeks-Behavior-by-Regime]]"
---

# Volatility Smile and Skew

IV is not constant across all strikes. The pattern of IV across the strike ladder is called the **skew** (if asymmetrical) or **smile** (if U-shaped). Understanding and trading this pattern is a key edge.

## What is Skew?

In equity index options (SPX), put IV is typically *higher* than call IV for the same delta distance from ATM. This is **put skew** or **reverse skew**.

**Example (SPX):**
- 4900 puts (25-delta OTM): IV = 28
- 5000 ATM: IV = 20
- 5100 calls (25-delta OTM): IV = 18

The skew *steepens* (becomes more pronounced) before events. Post-event, it *flattens* (compresses).

## Why Skew Exists

**Tail risk premium:** The market prices downside protection (puts) more expensively than upside calls because:
- Panic buying of puts during crashes drives demand
- Sellers demand premium for tail risk exposure
- Institutional portfolio insurance creates consistent put demand

## Trading Skew Changes

### Pre-Event Skew Steepening

**Setup:** Earnings or macro event 3–5 days out
- Put IV rises faster than call IV
- Skew steepens
- **Trade:** Sell puts (expensive), buy calls (cheap) → put spread or strangle

### Post-Event Skew Compression

**Setup:** Event resolved, tail risk passes
- Put IV crashes faster than call IV
- Skew flattens toward call IV
- **Trade:** Sell puts (fall from high IV), let decay take calls

## Key Insight

Skew is a **mean-reverting** signal. Extreme skew (puts trading at +10 vol premium) is unsustainable. When skew is steep, fade it: sell expensive puts, buy cheap calls. When skew is flat, avoid put-heavy strategies.
