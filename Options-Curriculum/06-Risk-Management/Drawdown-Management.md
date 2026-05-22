---
title: Drawdown Management
tags: [risk-management, drawdown, psychology, capital-preservation]
aliases: [Managing Drawdowns, DD Protocol, Drawdown Tiers]
status: draft
related:
  - "[[Position-Sizing]]"
  - "[[Stop-Loss-Strategies]]"
  - "[[Building-Discipline]]"
  - "[[Portfolio-Allocation]]"
---

# Drawdown Management

Drawdown is the peak-to-trough decline in account equity. For options income traders, drawdowns are not a question of *if* but *when*. The job of a risk framework is not to prevent them — it is to ensure that no single drawdown ends your career.

> [!note]
> A **drawdown** is measured from the highest equity high-water mark, not from the start of the year or month. It only ends when a new high is set.

## What to Expect

Even a well-run portfolio of [[Iron-Condor]] and [[Credit-Spread]] positions will experience **10–20% drawdowns** during volatile regimes (Feb 2018, March 2020, late 2022). This is a rule-of-thumb derived from practitioner experience and back-of-envelope simulation, not a tight statistical bound — actual figures depend on sizing, tenor, and delta exposure. See ![[chart-drawdown-sim.png]] for a representative simulated equity curve.

> [!warning]
> Income strategies have **negatively skewed return distributions**: many small wins, occasional large losses. Headline win rates of 80–90% can coexist with double-digit drawdowns. Do not size as if the smooth periods are the base case.

## The Recovery Math

The arithmetic of recovery is brutally asymmetric:

| Drawdown | Gain required to recover |
|---|---|
| 10% | 11.1% |
| 20% | 25.0% |
| 30% | 42.9% |
| 50% | 100.0% |

A 20% loss requires a **25% gain** just to break even. This single fact justifies prioritising capital preservation over opportunistic sizing-up. See [[Position-Sizing]] for the sizing side of this equation.

## Tiered Response Protocol

Define the action *before* the drawdown, not during it. The tiers below are a practical heuristic — calibrate the thresholds to your own volatility tolerance.

> [!tip]
> Print this table and tape it to your monitor. The whole point is that the decision is already made when emotion is highest.

**Tier 1 — 5% to 10% drawdown: Review**
- Audit every open position for thesis intactness
- Tighten entry criteria (raise minimum credit, lower delta, demand cleaner setups)
- No change in sizing yet — this is a yellow flag, not red

**Tier 2 — 10% to 15% drawdown: De-risk**
- Cut all new-position size by **50%**
- Take **no new trades for one week**; let the dust settle
- Review correlation (see below)

**Tier 3 — greater than 15% drawdown: Halt**
- Stop all new trades
- Close all **undefined-risk** positions (naked puts, short strangles, ratio spreads)
- Hold cash until objective conditions (VIX, realised vol, your own equity curve) normalise

> [!danger]
> "Trading out of a drawdown" by upsizing or adding undefined risk is the single most common way retail options accounts go to zero. If you feel the urge, that *is* the signal to step away.

## Correlation Diagnostic

During a drawdown, decompose the losses. Ask:
- Are losses concentrated in one **sector** (tech, energy, financials)?
- Are they driven by a single **factor** (market beta, vol-of-vol, rates)?
- Are spreads on different tickers behaving as **independent bets** or as the same bet wearing different costumes?

If the answer is "all one factor", the portfolio was never diversified — fix that in [[Portfolio-Allocation]] before resuming.

## Psychological Protocol

> [!warning]
> Drawdowns damage judgement before they damage capital. Most catastrophic blow-ups are post-drawdown decisions, not the drawdown itself.

Rules of thumb from experienced traders:

- **Journal daily** while in drawdown — entries, exits, emotional state, deviations from plan
- **Do not deviate from the written plan**, even if you "see" an obvious recovery trade
- **Reduce screen time**: monitor positions, but stop hunting new ones
- **Expect 30–90 days** to recover a 15% drawdown at normal income-strategy returns (roughly 1–2% monthly net); shorter recoveries usually mean you re-leveraged

Pair this with the routines in [[Building-Discipline]] and the mechanical exits in [[Stop-Loss-Strategies]]. Survival is the strategy.
