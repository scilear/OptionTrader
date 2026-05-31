---
title: Delta
tags:
  - greeks
  - foundations
  - options-basics
  - directional-exposure
aliases:
  - Options Delta
  - Directional Exposure
status: draft
related:
  - "[[Greeks-Overview]]"
  - "[[CSP-Cash-Secured-Put]]"
  - "[[Bull-Put-Spread]]"
  - "[[Gamma]]"
  - "[[Probability-of-Profit]]"
---

# Delta

**Delta** measures the rate of change of an option's price relative to a $1 move in the underlying. It is the first derivative of the option price with respect to underlying price—the hedge ratio used by market makers to stay neutral.

## Definition and Mechanics

Delta ranges from 0 to 1 for calls and –1 to 0 for puts:

- A call with **delta = 0.30** gains approximately $0.30 when the underlying rises $1.
- A put with **delta = –0.30** gains approximately $0.30 when the underlying falls $1.

In practice, delta is the **partial derivative** of option price with respect to underlying price. For traders, this means delta quantifies your directional exposure per unit of position size.

> [!note]
> Delta is always positive for calls (both ITM and OTM) and always negative for puts. At-the-money options typically have delta close to ±0.50; deep ITM options approach ±1.00; deep OTM options approach 0.

## Delta as Probability

A widely used heuristic: **an option's delta approximates its risk-neutral probability of expiring in-the-money**.

- A call with delta = 0.30 has ~30% probability of finishing above strike at expiry.
- A put with delta = 0.30 has ~30% probability of finishing below strike at expiry.

This relationship is exact in the [[IV-vs-HV]] and holds empirically across liquid markets. It breaks down slightly for very short-dated or illiquid options, but remains a reliable trader's rule of thumb.

> [!warning]
> This is a probability *of expiry ITM*, not probability of profit. A 0.30-delta short put loses money if the underlying falls even slightly below strike, because you are short gamma and have capped upside. Always account for vega (volatility risk) and theta decay patterns before viewing delta as your sole P&L driver.

## Directional Exposure

Delta tells you your net Greeks position:

| Strategy | Delta | Directional Bias |
|----------|-------|------------------|
| Long call | +0.30 to +0.70 | Bullish |
| Short call | –0.30 to –0.70 | Bearish |
| Long put | –0.30 to –0.70 | Bearish |
| Short put | +0.30 to +0.70 | Bullish |
| Long stock | +1.00 | Bullish |
| Straddle | ~0.00 | Directionally neutral |

A portfolio delta of +0.00 is "delta neutral"—the P&L depends on gamma, vega, and theta rather than directional moves.

## Practical Delta Ranges by Strategy

### Cash-Secured Puts (CSP)

Preferred delta range: **0.20–0.30** (short leg).

- 0.20-delta: ~80% probability of expiring OTM; lower win rate but larger premium cushion.
- 0.30-delta: ~70% probability of expiring OTM; balanced risk/reward; standard for retail income trades.
- Avoid >0.40: skew risk, tighter risk management, tail risk of early assignment.

### Credit Spreads (Bull Put, Bear Call)

Preferred delta range: **0.25–0.35** (short leg).

- Short leg defines your margin risk and breakeven.
- Long leg (protective) should be 0.10–0.15 delta to cap losses.
- Tighter deltas (0.15–0.20) widen the spread; looser deltas (0.40+) concentrate risk.

### 0DTE (Zero Days to Expiration)

Preferred delta range: **0.10–0.20** (for directional bets) or **0.45–0.55** (for ATM gamma scalp).

- 0DTE gamma is extreme; delta changes rapidly with spot price.
- Sub-0.20 delta decays fastest; suitable for lottery-like risk.
- ATM (0.50-delta) gamma is highest; scalping profit from small moves.

> [!danger]
> 0DTE trades are unsuitable for beginners. Gamma crushing is violent. A 0.20-delta call can expire worthless in hours. Liquidity can evaporate; bid/ask spreads widen into the close. Position sizing must be tiny relative to account.

## Delta and Hedge Ratios

Institutions use delta as a hedge ratio. If you own 100 shares and want to hedge with puts:
- Buy puts with delta = –0.50 to reduce directional exposure to ~0.50.
- Buy puts with delta = –1.00 (ITM or synthetic) to eliminate all directional risk.

This relationship underlies [[Options-Basics]] and is why market makers delta-hedge continuously.

## Key Takeaways

- Delta is directional exposure and the hedge ratio.
- Delta ≈ probability of expiring ITM (under [[IV-vs-HV|Black-Scholes]] assumptions).
- Short delta = bearish; long delta = bullish; zero delta = neutral.
- Use delta ranges strategically: CSP 0.20–0.30, credit spreads 0.25–0.35, 0DTE 0.10–0.20.
- Delta is dynamic; as underlying moves, delta changes (that change is [[Gamma|gamma]]).
