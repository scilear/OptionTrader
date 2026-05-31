---
title: IV vs HV — Implied vs Historical Volatility
tags:
  - foundations
  - volatility
  - edge
  - premium-selling
aliases:
  - Implied vs Historical Volatility
  - Volatility Risk Premium
status: draft
related:
  - "[[IV-Rank]]"
  - "[[IV-Percentile]]"
  - "[[Vega]]"
  - "[[High-IV-Playbook]]"
---

# IV vs HV — Implied vs Historical Volatility

Understanding the difference between implied and historical volatility is the single most important conceptual foundation for any options seller. The spread between the two is where edge lives.

## Implied Volatility (IV)

[[Vega|Implied volatility]] is the volatility figure that, when plugged into the Black-Scholes model, produces the option's current market price. It is forward-looking: the market is pricing in its *collective forecast* of how much the underlying will move over the life of the option.

> [!note]
> IV is not a prediction by any single actor. It is the volatility figure *implied* by what buyers and sellers are willing to pay right now. It reflects uncertainty, demand for hedges, and supply of premium sellers all at once.

IV is quoted annualized (e.g., "30 vol") and can be decomposed into a per-day move: `daily move ≈ spot × IV / √252`. A 30 IV on a $500 stock implies roughly ±$9.5/day at one standard deviation.

## Historical Volatility (HV)

Historical volatility (also called realized volatility, or RV) measures the *actual* annualized standard deviation of log returns over a trailing window — most commonly 20, 30, or 60 days. Unlike IV, it is backward-looking and purely statistical.

Common windows and their uses:
- **HV20**: captures recent realized noise, most reactive
- **HV30**: matches the typical 30-DTE options cycle
- **HV60**: smooths over short-term spikes, useful for regime context

## The Volatility Risk Premium (VRP)

Across nearly every liquid underlier and timeframe studied, IV has historically *exceeded* realized HV on average. This gap is called the **volatility risk premium (VRP)**.

The intuition: buyers of options are willing to overpay for insurance. Sellers demand a premium for bearing vega risk, gap risk, and the cost of hedging. The VRP is the fundamental edge that options sellers harvest — not alpha from prediction, but compensation for providing liquidity and absorbing risk transfer.

Empirically (equity index options, multi-decade data), IV has exceeded 30-day realized HV roughly 75–80% of the time on SPX. This is the structural tailwind behind strategies in the [[High-IV-Playbook]].

> [!warning]
> The VRP is a long-run average, not a guarantee on any single trade. In stress regimes, HV can spike violently and *exceed* IV — turning the edge against sellers. See [[IV-Rank]] and [[IV-Percentile]] for tools to assess current conditions before selling.

## Using the IV-HV Spread to Confirm Edge

The practical question is: **is IV elevated enough above current HV to justify selling premium?**

A first-pass screen:

| Condition               | Base Signal                                            |
| ----------------------- | ------------------------------------------------------ |
| IV ≫ HV20 (≥10 vol pts) | Strong VRP signal → sellers have edge                  |
| IV > HV20 (5–9 vol pts) | Moderate edge → proceed with discipline                |
| IV ≈ HV20 (0–4 vol pts) | Compressed → avoid or reduce size                      |
| IV < HV20               | See exceptions below                                   |

### Exception: IV < HV20 But Trade Anyway

When IV < HV20, **check event calendar and RV trend before defaulting to "don't sell"**:

- **Post-event spike collapse:** Earnings / FOMC just resolved. HV20 is elevated from the *past* spike, but IV has already repriced down. Realized vol is *declining*. In this case, the past event's spike is baked into HV20 but the forward market has already calmed down. Selling premium into falling realized vol can have positive edge despite IV < HV20.
  
- **Pre-event anticipation:** Earnings / FOMC / econ data in 2–5 days. IV is spiking *ahead* of the event, creating wide spreads (favorable bid/ask). Current HV20 might be low because the event hasn't occurred yet, but IV has already jumped. Spread width > VRP gap. Selling with defined risk (credit spreads, not naked) captures the width.

- **Skew tells a story:** IV < HV20 overall, but *put skew is inverted* (puts IV > calls IV). The market is pricing tail risk selectively. Selling calls (which are relatively cheap) while buying protective puts is viable, even if aggregate IV < HV20.

### The Core Insight

**IV < HV20 is a warning flag, not a law.** It signals caution, but the final decision depends on:
1. **Event context** — what just happened, what's coming?
2. **RV direction** — is realized vol increasing or decreasing?
3. **Spread width** — is the actual bid/ask favorable, regardless of IV-HV gap?
4. **Skew direction** — what is the skew telling you about expectations?

> [!tip]
> Rule of thumb (data-backed for SPX, refinement needed for single stocks): **IV should be at least 5–10 vol points above 20-day HV before *reflexively* selling premium.** Below that threshold, condition sales on event calendar and realized volatility *trend*, not IV-HV alone. Always layer in [[IV-Rank]] and [[IV-Percentile]] for regime context, AND check what's on the economic calendar in the next 1–10 days.

## Limitations

- **IV can spike faster than HV rises.** A vol expansion event (earnings miss, macro shock) can double IV overnight while HV20 barely moves for days. By the time HV catches up, the short vega position has already lost.

- **HV is backward-looking.** A low HV20 during a calm period does not mean calm will persist. Selling into artificially low HV is how sellers get trapped before volatility events.

- **Event calendars override IV-HV metrics.** The IV-HV spread is a structural signal, but it blinds you to *timing*. An earnings announcement in 3 days will cause IV to spike even if IV < HV20 *today*. Always cross-reference with [[Earnings-Overview]] and macro calendar (FOMC, CPI, payroll). Treat imminent events as a "do not sell" flag regardless of IV-HV.

- **The VRP compresses in low-vol regimes.** When both IV and HV are depressed, the absolute spread shrinks even if the ratio looks acceptable. Use absolute spread (vol points), not just ratio.

> [!danger]
> A common beginner error: "IV < HV20, so I won't sell." But they forgot to check the calendar and missed that earnings is in 4 days, or didn't realize the recent HV20 spike was from a one-off event that is now over. Always ask: "What created the HV spike? Is that event still impacting the market?" before ruling out sales.

## Quick Reference

- IV = market's embedded forecast → shaped by [[Vega]] sensitivity
- HV = realized past movement → inputs to VRP calculation
- IV − HV spread = edge proxy → confirm with [[IV-Rank]] and [[IV-Percentile]]
- Playbook for elevated IV environments → [[High-IV-Playbook]]
