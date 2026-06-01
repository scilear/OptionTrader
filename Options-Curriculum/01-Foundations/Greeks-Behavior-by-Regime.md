---
title: Greeks Behavior by Market Regime
tags:
  - foundations
  - greeks
  - market-conditions
aliases:
  - Greeks in different regimes
  - Regime-dependent Greeks
status: draft
related:
  - "[[Gamma]]"
  - "[[Theta-Decay]]"
  - "[[Market-Condition-Classification]]"
---

# Greeks Behavior by Market Regime

Greeks don't behave consistently across all market conditions. Their sensitivity to moves, time, and vol changes *shifts* based on the regime.

## Calm (Low Vol, Low Trend)

| Greek | Behavior | Implication |
|---|---|---|
| **Theta** | Moderate, consistent decay | Steady income from short premium |
| **Gamma** | Low, predictable | Moves are gradual; hedges don't whipsaw |
| **Vega** | Low sensitivity | IV expansion unlikely; vol selling is safe |

## Transition (Rising Vol, Early Trend)

| Greek | Behavior | Implication |
|---|---|---|
| **Theta** | Accelerating decay but vega bleeds | Short premium struggles as vol rises |
| **Gamma** | Rising, becoming reactive | Hedges start to matter; delta drifts faster |
| **Vega** | Negative (losses) for short vol | Sellers face P&L pressure from rising IV |

## Stress (High Vol, Trending Down)

| Greek | Behavior | Implication |
|---|---|---|
| **Theta** | Exploding, but overwhelmed by vega | Time decay is useless; vol crush rules |
| **Gamma** | Extreme, non-linear | $1 moves create $10+ delta swings |
| **Vega** | Catastrophic for short vol | Negative vega positions hemorrhage |

## Rule of Thumb

**In calm:** Greeks are predictable. Sell premium.  
**In transition:** Greeks are volatile. Avoid selling.  
**In stress:** Greeks are explosive. Buy protection or go long.
