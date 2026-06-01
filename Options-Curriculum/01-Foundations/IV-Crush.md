---
title: IV Crush
tags:
  - earnings
  - volatility
  - iv-mechanics
aliases:
  - IV crush
  - Volatility crush
status: draft
related:
  - "[[IV-Crush-Mechanics]]"
  - "[[Implied-Volatility]]"
---

# IV Crush

**IV crush** is the rapid collapse in implied volatility immediately after an earnings announcement or major event.

## Mechanics

**Pre-event:** IV is elevated (e.g., 35 vol for SPX during earnings season)  
**At announcement:** IV *can rise further* if the move is large  
**Post-event:** IV collapses 30–60% as uncertainty is resolved (e.g., 35 vol → 15 vol)

## Why It Happens

Uncertainty is priced into IV. Once the event occurs and the outcome is known, that uncertainty *dissolves*. Option prices collapse even if the stock doesn't move much.

## For Sellers (Good)

Sold a strangle before earnings. Post-announcement, IV crush helps your position:
- All short premium decays faster
- Both sides become more profitable

## For Buyers (Bad)

Bought a straddle before earnings expecting a large move. The stock does move 5%, but IV crush overwhelms the directional gain:
- Straddle loses money despite the move
- Delta profit < vega loss

## Key Takeaway

IV crush is a *vega effect*, not a delta effect. It favors sellers and hurts buyers, regardless of directional accuracy. See [[IV-Crush-Mechanics]] for detailed treatment.
