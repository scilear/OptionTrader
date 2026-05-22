---
title: Low IV Playbook
tags: [options, volatility, strategy, market-conditions, playbook]
aliases: [Low Volatility Playbook, Depressed IV Trading]
status: draft
related:
  - "[[High-IV-Playbook]]"
  - "[[Calendar-Spread]]"
  - "[[LEAPS]]"
  - "[[Earnings-Overview]]"
  - "[[Market-Condition-Classification]]"
---

# Low IV Playbook

**Threshold**: [[IV-Rank]] < 25, VIX < 15. When implied volatility is depressed, premium is thin. The market is pricing in small moves. This is a hostile environment for premium sellers and a favorable one for buyers — if you understand how to use it.

## Why Low IV Is Bad for Sellers

When IV rank is below 25, the credit you collect for short options positions is too small to justify the structural risk you are taking. Two problems compound:

1. **Thin premium margin** — A 0.25 delta put spread might collect only 0.3–0.5% of the stock price. If the stock moves against you even modestly, you lose multiples of what you collected.
2. **Asymmetric vega risk** — If you sell options in a low-IV environment and IV subsequently expands (which it tends to do from depressed levels), your short options increase in value against you even if price barely moves.

> [!warning]
> Selling premium in a low-IV environment means accepting full downside risk for a fraction of the normal reward. The risk/reward is structurally poor. If the [[IV-Rank]] is below 20, the default position is cash.

## Strategies to Deploy

### LEAPS Purchases

[[LEAPS]] (options with 12+ months to expiration) become attractive when IV is low. You are buying long-term optionality cheaply. The vega exposure works in your favor: if IV expands from depressed levels, your LEAPS increase in value independent of price movement.

- Target deep ITM or ATM strikes for high delta participation
- Use on high-conviction names where you want leveraged long exposure
- 12–24 month expirations give sufficient time for the thesis to play out

### Calendars and Diagonals

[[Calendar-Spread|Calendars]] and diagonals are long-vega structures — they profit from IV expansion. In a low-IV environment, you are buying cheap near-term options and selling slightly less cheap far-term options, with the expectation that IV will eventually rise.

- Enter with 30–60 DTE on the short leg
- Best on underlyings where you expect IV to expand (earnings, macro events approaching)
- The breakeven range is narrow; calendars require active management

### Debit Spreads

Vertical debit spreads (bull call spreads, bear put spreads) have better risk/reward in low-IV environments than credit spreads. You are buying the spread at a discount and your maximum loss is the debit paid.

- Look for debit ≤ 50% of the width of the spread for acceptable risk/reward
- Choose direction based on [[Market-Condition-Classification|market regime]] — do not use debit spreads against the trend

## What to Avoid

- **Naked premium selling** — the worst possible use of a low-IV environment
- **Iron Condors** — the credit is insufficient to justify the capped upside; you are taking full gap risk for minimal reward
- **Cash-Secured Puts on expensive stocks** — same problem; thin credit, full downside if the stock breaks

> [!danger]
> Running an IC or selling a CSP when IV rank is below 20 is a beginner mistake with consistent negative expectancy. The credit does not compensate for the tail risk you are accepting.

## The Patience Rule

> [!tip]
> If the [[IV-Rank]] is below 20, the default action is to hold cash and wait. Low-IV environments do not last indefinitely. VIX historically reverts from sub-15 levels within weeks to months. Patience here is a position.

**Practical threshold (rule of thumb, not data-backed):** If the credit on a 0.25 delta CSP is less than 1% of the stock price, skip the trade entirely. The premium is not worth the capital commitment and monitoring overhead.

## Earnings Plays in Low IV

[[Earnings-Overview|Earnings plays]] become more interesting in low-IV environments. Pre-earnings, IV on the near-term options rises as uncertainty increases. Buying options (or calendars with a long near-term leg through earnings) lets you capture the IV expansion before the event.

- Buy straddles or strangles 5–10 days before earnings when IV is still depressed
- Sell or close before the announcement to avoid the post-earnings IV crush
- This is a speculative timing trade — size accordingly

## Quick Reference

| IV Rank | Default Action |
|---|---|
| < 20 | Hold cash; only LEAPS or calendars if high conviction |
| 20–35 | Selective debit spreads; begin watching for rising IV |
| 35–50 | Transition zone; begin small credit positions if IV is rising |
| > 50 | See [[High-IV-Playbook]] |

See also: [[Market-Condition-Classification]] for the full regime framework.
