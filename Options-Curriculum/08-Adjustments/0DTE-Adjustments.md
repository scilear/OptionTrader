---
title: "0DTE Adjustments — Managing Positions When They Move Against You"
tags:
  - options/0dte
  - options/adjustments
  - options/risk-management
  - options/iron-condor
  - options/discipline
aliases:
  - "0DTE Position Management"
  - "0DTE Under Pressure"
  - "Same-Day Expiry Adjustments"
status: draft
related:
  - "[[0DTE-Overview]]"
  - "[[0DTE-Credit-Spread]]"
  - "[[0DTE-Iron-Condor]]"
  - "[[Adjust-vs-Close]]"
  - "[[Rolling-Basics]]"
  - "[[Losing-Trade-Mindset]]"
---

# 0DTE Adjustments — Managing Positions When They Move Against You

> [!warning]
> 0DTE gamma can move positions from safe to max loss in minutes. There is no "wait and see" — have a plan before entering. Every decision point described below must already be written down before you put the trade on.

0DTE positions collapse the entire adjustment timeline to hours. Standard rules about "giving the trade room to breathe" or "rolling with time remaining" do not apply. When a same-day position moves against you, you are making decisions under extreme time pressure with rapidly accelerating gamma. The playbook below is structured around **pre-committed decision rules**, not real-time judgment calls.

## Pre-Entry: Write Down Your Stop Level

Before entering any 0DTE trade, record three numbers in your trade log:

1. **The stop price** — the underlying price at which you will close, no discretion.
2. **The short-strike delta threshold** — typically 0.40. If either short strike reaches this delta, you act.
3. **The hard time stop** — 3:45 PM ET, unconditionally (see below).

This is not a suggestion. 0DTE gamma accelerates so quickly that "deciding in the moment" consistently leads to holding through max loss. The decision must be pre-committed because the psychological pressure at the moment of testing is the worst possible time to reason clearly.

> [!tip]
> Write the stop level on a sticky note or in a pinned trade journal entry before order entry is even confirmed. Traders who skip this step disproportionately report "I couldn't pull the trigger" on closes that were obvious in retrospect.

## Scenario 1: One-Sided Test on an Iron Condor

When the underlying moves to one wing of a [[0DTE-Iron-Condor]], the short strike on the tested side begins accumulating delta rapidly. **The rule is binary:**

- **Short strike delta < 0.40**: monitor; no action required yet.
- **Short strike delta ≥ 0.40**: close the entire IC immediately.

Do not close only the losing side and hold the winning side. The winning side's premium has mostly decayed and is not worth the ongoing risk. Closing the full IC at this point typically recovers a portion of the max loss; hoping for a reversal when delta is already at 0.40 in a 0DTE context is statistically unfavorable. This threshold is rule-of-thumb from practitioner experience, not from a published dataset — your own log data should confirm or refine it over time.

> [!note]
> Delta of 0.40 on a short strike means the option is behaving roughly like owning 40 shares of stock per contract, and that sensitivity is increasing every minute as expiry approaches. The position is no longer in "safe" territory by any conventional metric.

## Scenario 2: Converting the Tested Side to a Tighter Hedge

If you want to attempt a partial salvage rather than a full close, there is one structured alternative — but it requires acting early, before the tested-side short strike reaches 0.40.

1. Close the **winning** (untested) side of the IC for a small debit. This frees up margin and locks in whatever residual credit remains on that side.
2. Use that freed credit to **widen the long strike** on the losing side — buy a closer-to-the-money long to reduce your max loss on the tested wing.

The result is a single credit spread on the losing side with a narrower maximum loss than the original IC. This is a defensive conversion, not an improvement. You have reduced the ceiling on your loss, but you have not changed the directional exposure. See [[Adjust-vs-Close]] for the general framework governing when conversion is preferable to outright closing.

> [!danger]
> This conversion requires two fast, precise orders in a fast-moving market. Legging risk is real — if the first leg fills and the second does not, your position is more exposed, not less. Practice this sequence in paper trading before attempting it live.

## Scenario 3: Hard Time Stop at 3:45 PM

This rule has no exceptions for 0DTE losers:

**Never hold a losing 0DTE position past 3:45 PM ET.**

In the final 15 minutes, liquidity deteriorates, bid/ask spreads widen, and gamma is at its absolute peak. Closing a loser at 3:45 PM for a defined loss is always preferable to the binary outcome of the last 15 minutes. The market maker spread alone in the closing minutes can cost more than the additional time decay you might capture. This is a hard rule, not a guideline — treat it like a margin call.

## Scenario 4: The Reversal Play (Speculative)

If the underlying has moved against one side of your IC and you have strong conviction — from price action, volume drying up, or a visible intraday support/resistance level — that the move is exhausted, there is an asymmetric play available:

1. Close **only the short option** on the tested side (buy back the short strike).
2. Hold the long option on the same side.

You are now long a naked call or put, which will pay off if the underlying reverses sharply before close. The cost is the premium you pay to close the short, partially offset by the credit you collected at entry.

> [!warning]
> This is a speculative directional bet, not a neutral adjustment. "Convinced the move is exhausted" is subjective, and intraday reversals in high-momentum 0DTE markets are less common than they appear in hindsight. Size accordingly — if you do this, treat it as a lottery ticket, not a high-probability trade. See [[0DTE-Credit-Spread]] for how individual spread legs behave in isolation.

## Decision Sequence Summary

![[0dte-adjustment-decision-tree.png]]

When the position is being tested, work through this sequence in order:

1. Check short-strike delta. At or above 0.40 → close the full IC, no further analysis.
2. Below 0.40 but approaching your pre-written stop price → begin preparing the close order.
3. Time is 3:45 PM or later and the position is a loser → close immediately.
4. If attempting a conversion (Scenario 2), act early — delta < 0.30 on the tested side is the latest reasonable entry point for a conversion.
5. The reversal play (Scenario 4) is only for traders with demonstrated intraday tape-reading skill and should not be a default behavior.

## Related Notes

- [[0DTE-Overview]] — mechanics and risk profile of same-day expiry trading
- [[0DTE-Iron-Condor]] — structure, entry, and profit targets for 0DTE ICs
- [[0DTE-Credit-Spread]] — single-spread version and how legs behave individually
- [[Adjust-vs-Close]] — general decision framework applicable beyond 0DTE
