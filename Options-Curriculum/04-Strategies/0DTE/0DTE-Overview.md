---
title: 0DTE Overview
tags:
  - 0dte
  - options
  - strategies
  - spx
  - qqq
  - theta
  - gamma
aliases:
  - Same-Day Expiry
  - Zero DTE
status: draft
related:
  - "[[0DTE-Credit-Spread]]"
  - "[[0DTE-Iron-Condor]]"
  - "[[0DTE-Butterfly]]"
  - "[[Superfly]]"
  - "[[SPX-vs-QQQ-0DTE]]"
---

# 0DTE Overview

0DTE (zero days to expiry) refers to options that expire on the same trading day they are traded. Since 2022, SPX options expire every Monday, Wednesday, and Friday, and QQQ options follow the same M/W/F schedule. This means a fresh expiry cycle is available three times per week, creating a distinct short-volatility opportunity that has attracted a large segment of retail and institutional flow.

> [!note]
> 0DTE options are not a separate product — they are standard listed options on their expiry date. The term simply describes where the contract sits in its lifecycle.

## What Makes 0DTE Different

Three forces combine to make 0DTE options behave unlike any longer-dated contract:

**Theta decay is violent.** An option with 24 hours remaining loses nearly all extrinsic value within those hours. Theta is at its mathematical maximum on expiry day, which rewards sellers — but only if price stays cooperative.

**Gamma is explosive.** Delta changes rapidly with every tick when expiry is hours away. A position that looks delta-neutral at 9:45 AM can carry significant directional exposure by 11:00 AM after a 10-point move in SPX. See [[0DTE-Iron-Condor]] for how this affects condor management.

**Bid-ask spreads widen in far-OTM strikes.** Liquidity concentrates near the at-the-money strikes. Wings more than 30–40 points away from spot in SPX can carry spreads of several dollars, which degrades fill quality and obscures true edge. Compare liquidity profiles in [[SPX-vs-QQQ-0DTE]].

## Who Should Trade 0DTE

> [!danger]
> 0DTE is not suitable for beginners. The combination of explosive gamma, fast intraday moves, and the psychological pull to "recover" a losing trade creates conditions where new traders frequently blow up small accounts in a single session. Master multi-week structures first.

0DTE is appropriate for traders who:
- Have at least one to two years of live options trading experience
- Can monitor positions actively throughout the session
- Have defined position-sizing and daily loss-limit rules in place before entry
- Understand [[Greeks]] deeply, particularly gamma and delta

## Advantages

- **Fast premium collection.** Credit spreads and iron condors can collect and expire worthless within hours rather than weeks.
- **No overnight risk.** All exposure is intraday; there is no gap risk through earnings, Fed announcements, or geopolitical events that occur after the close.
- **Defined entry and exit within one session.** The P&L story is complete by 4:00 PM ET, enabling rapid feedback loops and disciplined journaling.

## Risks

**Gamma causes rapid, non-linear loss.** A 0.05-delta short put spread can become a 0.40-delta position in minutes on a sharp move down. Loss can exceed the initial credit multiple times over before a trader can react. See [[0DTE-Risk-Rules]] for concrete stop-loss frameworks.

**Over-trading is the primary cause of account damage.** The daily availability of a new cycle invites revenge trading after losses. Three losing sessions per week compound faster than traders expect.

**Addictive feedback loop.** The rapid resolution of each trade — win or loss within hours — mimics variable-ratio reinforcement. Many traders find themselves increasing size and frequency without a rational edge driving the decision.

## Capital and Structure Requirements

> [!warning]
> 0DTE trading is NOT passive income — it requires active monitoring and fast decision-making. Do not participate on days you cannot watch the screen.

Use **defined-risk structures only**:
- [[0DTE-Credit-Spread]] — single-direction, simple to manage
- [[0DTE-Iron-Condor]] — collects credit on both sides, requires tighter gamma management
- [[0DTE-Butterfly]] and [[Superfly]] — low-cost directional or neutral structures with capped risk

**Never sell naked 0DTE options.** The margin requirement is large and the loss potential in a fast move is effectively unlimited in practical terms before a fill can be obtained.

A reasonable allocation per trade is 1–3% of the options sub-portfolio, not total net worth. Position size should be set so that a full loss on the trade is survivable without disrupting the overall plan.

## Daily Loss Limit

> [!tip]
> Set a hard daily max loss — 1% of the portfolio is a common practitioner rule — and stop trading for the day the moment it is hit. Write the number down before the open. Do not negotiate with yourself mid-session.

This rule is not about being overly conservative; it is about preserving the ability to trade the next session. A 2% loss requires a 2.04% gain to recover. A 10% loss requires an 11.1% gain. The math of drawdown recovery is unforgiving.

For tactical execution details, see [[0DTE-Entry-Timing]] and [[0DTE-Morning-Routine]].
