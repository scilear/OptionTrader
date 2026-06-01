---
title: Implied Move vs Actual Move
tags:
  - earnings
  - volatility
  - event-risk
aliases:
  - Expected move
  - Implied move
status: draft
related:
  - "[[Implied-Volatility]]"
  - "[[Earnings-Overview]]"
---

# Implied Move vs Actual Move

The **implied move** is how much the market expects the underlying to move by a specific date (usually earnings). The **actual move** is what *really* happens. The difference is where edge lives.

## Implied Move Calculation

```
Implied Move = Spot × IV × √(days to event / 365)
```

**Example:** SPX 5000, IV 20, 7 days to earnings
- Implied Move = 5000 × 0.20 × √(7/365) = ±189 points

The market expects SPX to move ±189 points (3.8%) by earnings.

## The Mismatch

Historically, actual moves *exceed* implied moves 40–50% of the time. This creates an edge:

- **If actual > implied:** Long premium structures (straddles, long spreads) profit
- **If actual < implied:** Short premium structures (condors, strangles) profit

## Trading the Gap

**Setup:** Earnings coming. Implied move = ±3%, but company is in transition (new CEO, product launch)
- **Trade:** Buy straddle. If actual move is ±5%, profit
- **Risk:** If actual move is ±1%, lose to time decay

The edge is asymmetric: traders who correctly forecast volatility outperformers and underperformers accumulate alpha over many events.
