---
title: Best Days of Week for Options Trading
tags:
  - entry-exit
  - timing
  - microstructure
  - theta
  - weekly-options
  - credit-spreads
aliases:
  - Weekly Trading Calendar
  - Day-of-Week Timing
status: draft
related:
  - "[[Intraday-Timing-Open]]"
  - "[[0DTE-Overview]]"
  - "[[Building-Discipline]]"
---

# Best Days of Week for Options Trading

Market microstructure creates repeatable intraday and intraweek patterns that experienced options traders exploit for timing entries and exits. Day-of-week effects arise from how institutional flows, option expiration mechanics, and volatility mean-reversion interact across the weekly cycle.

> [!note]
> These patterns are **rule-of-thumb**, not statistically guaranteed edges. They reflect commonly observed tendencies in SPX and equity index options. Individual weeks — especially around FOMC, CPI, or earnings clusters — can invert these patterns completely.

---

## Day-by-Day Breakdown

| Day | Open New Positions? | Strategy Types | Notes |
|-----|--------------------|--------------------|-------|
| Monday | Avoid or size small | None preferred | Weekend gap risk not yet absorbed; commitment flows thin |
| Tuesday | Yes — primary entry day | Credit spreads, Iron Condors, 21–45 DTE income trades | Vol typically normalizes; 3–4 days of theta decay ahead |
| Wednesday | Yes — secondary entry | 0DTE (Wed expiry on SPX), new weeklies if missed Tuesday | SPX has Wed/Fri/Mon expirations; 0DTE flow is high |
| Thursday | Selective only | Rolls, adjustments, closing losers | Last practical entry for Friday-expiring weeklies; gamma rising |
| Friday | Close and manage only | 0DTE (Fri expiry), no new weekly positions | Highest gamma risk of the week; liquidity thins into close |

---

## Monday — Weekend Gap Risk Still Settling

Monday opens with unresolved uncertainty: geopolitical weekend news, Sunday futures moves, and institutional rebalancing all compress into the first hours. Bid/ask spreads on options are frequently wider than Tuesday levels, and the VIX term structure often shows elevated near-term vol that fades by mid-morning.

Entering a credit spread before that gap risk settles means you may be selling vol that is about to collapse — pricing you out of a fair premium. See [[Intraday-Timing-Open]] for how the first 30–45 minutes amplify this problem.

> [!warning]
> A gap open that moves against an undisciplined Monday entry can cost you the entire week's expected theta before Tuesday arrives. Waiting one day costs almost no theta on a 21–45 DTE position.

---

## Tuesday — Primary Entry Day for Income Strategies

Tuesday is the consensus best entry day for weekly and monthly income trades. By Tuesday, weekend noise has cleared, institutional commitment flows are visible, and there are still 3–4 trading days of theta capture ahead for Friday-expiring positions.

**Core rule:** Enter 21–45 DTE income trades on Tuesday–Wednesday for best theta capture relative to the time you carry overnight risk.

Strategies that benefit most: [[Iron-Condor]], [[Credit-Spread]], [[Short-Strangle]].

---

## Wednesday — 0DTE and Secondary Entry

SPX offers Wednesday expirations (in addition to Friday and Monday), making Wednesday the primary 0DTE session mid-week. If you trade [[0DTE-Overview]], Wednesday is a structural opportunity; the market has usually established a directional tone by then.

For non-0DTE traders, Wednesday is an acceptable secondary entry if Tuesday was skipped — you still have 2 days of theta before Friday expiry.

> [!tip]
> On 0DTE Wednesday trades, wait until after the first 30 minutes for the opening range to set. Entering a 0DTE condor at 9:35 ET often pays worse premium than entering at 10:00 ET once the range is clearer.

---

## Thursday — Roll and Adjust, Not Enter

By Thursday, Friday-expiring weekly options have elevated gamma. New entries on short premium in these strikes carry asymmetric risk: a 1% move on Thursday afternoon can erase the entire credit. The appropriate action on Thursday is:

- Roll positions that are near the tested strike
- Close losers at a pre-defined max-loss level
- Leave winners alone unless they have reached 50% of max profit

---

## Friday — Manage and Close Only

Friday is a [[0DTE-Overview]] day for SPX (Friday expiry), but it is simultaneously the most dangerous day to open new non-0DTE positions. Gamma is at its maximum for expiring strikes; liquidity thins into the 3 PM–4 PM window.

> [!danger]
> Opening a new 1-week credit spread on a Friday afternoon is a beginner mistake. You pay wide spreads, carry overnight gap risk immediately, and have only 4 days of theta — minus the worst-liquidity close. This pattern is a consistent wealth transfer from retail to market makers.

Discipline on Fridays separates consistent traders from impulsive ones. See [[Building-Discipline]] for the full decision framework around trade entry rules.

---

## Summary Rule

**Tuesday is the anchor.** If you miss Tuesday, Wednesday is acceptable for income trades. Thursday and Friday are for management, not initiation. Monday is for observation.
