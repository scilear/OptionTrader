---
title: Ticker Selection System
tags:
  - finding-opportunities
  - ticker-selection
  - workflow
  - screeners
  - iv-rank
aliases:
  - ticker selection workflow
  - options ticker scan
status: draft
related:
  - "[[Ticker-Criteria-Technical]]"
  - "[[Ticker-Criteria-Fundamental]]"
  - "[[Screener-Setup]]"
  - "[[High-Probability-Setup-Checklist]]"
  - "[[IV-Rank]]"
---

# Ticker Selection System

The goal of this system is to move from a universe of thousands of optionable tickers down to 2–5 high-probability setups per week in under 10 minutes. It works as a two-stage funnel: broad screening first, then a structured checklist applied to each surviving candidate.

> [!note]
> "High-probability" in options trading refers to setups where the statistical edge—premium richness, defined risk, liquidity—is confirmed before entry, not to win-rate guarantees. See [[High-Probability-Setup-Checklist]] for the full criteria.

---

## Stage 1 — Generate Candidates with a Screener

Start with a screener rather than scanning by feel. The [[Screener-Setup]] note documents the exact filters to configure in Barchart, Finviz, or Market Chameleon. Core screener parameters:

- **Open interest floor**: ≥ 500 contracts at the target expiry (liquidity gate, non-negotiable)
- **Average volume**: ≥ 1 million shares/day on the underlying
- **Bid/ask spread on options**: ≤ 10% of mid-price for near-ATM strikes
- **IV Rank ≥ 30** (or ≥ 50 for premium-selling setups): see [[IV-Rank]] for calculation details

This typically returns 20–60 tickers depending on market regime. Do not skip the screener step and work from a watchlist alone — survivor bias from familiar names is a documented source of poor ticker selection. (Rule of thumb, not formally backtested here.)

---

## Stage 2 — Apply the Two-Filter Funnel

Work through surviving screener candidates in two ordered passes.

### Pass A — Liquidity and Fundamental Filters

Check [[Ticker-Criteria-Fundamental]] first. Eliminate any ticker that fails on:

1. Upcoming binary event (earnings within the expiry window) unless the strategy explicitly targets the event
2. Pending M&A, FDA decision, or regulatory ruling
3. Average daily options volume too thin to absorb a multi-leg position at mid

This pass takes roughly 30 seconds per ticker. Eliminate fast — you are looking for reasons to cut, not reasons to keep.

### Pass B — Technical Setup Confirmation

Apply [[Ticker-Criteria-Technical]] to the survivors. A valid technical setup requires at least one of:

- Clear range-bound structure (defined support/resistance for mean-reversion strategies)
- Confirmed trend with a defined pullback level (for directional debit spreads)
- Post-event consolidation (elevated IV with fading realized volatility)

Tickers that pass both passes are promoted to the decision tree below.

---

## Decision Tree

Use this as a verbal checklist, not a rigid algorithm. Work top-to-bottom; the first "No" exits the ticker.

```
Does the ticker meet liquidity criteria (OI, spread, volume)?
  → No:  Eliminate immediately. Return to screener list.
  → Yes: Continue.

Does IV Rank qualify for the intended strategy?
  → No:  Add to watch list. Re-check next week.
  → Yes: Continue.

Is a technical setup confirmed (range, trend, or consolidation)?
  → No:  Watch list. IV alone is not a trade.
  → Yes: Proceed to position sizing and entry via [[High-Probability-Setup-Checklist]].
```

> [!warning]
> Skipping the technical confirmation step and trading on [[IV-Rank]] alone is a common beginner error. Elevated IV rank means options are rich relative to their own history — it does not mean the underlying will stay inside a range. Selling premium into a trending move without a defined technical thesis has caused outsized losses in practice.

---

## Weekly Routine (Under 10 Minutes)

| Step | Time | Action |
|------|------|--------|
| 1 | 2 min | Run screener with saved filter set (see [[Screener-Setup]]) |
| 2 | 3 min | Pass A: eliminate binary-event and thin-market tickers |
| 3 | 3 min | Pass B: chart review, confirm technical structure |
| 4 | 2 min | Rank survivors by IV rank + setup quality → top 2–5 |

Aim for 2–5 active setups per week. More than 5 concurrent positions in the same expiry cycle degrades your ability to manage each one and clusters [[Correlation-Risk]] (especially during drawdowns when underlying correlations spike).

> [!tip]
> Keep a rolling watch list of tickers that failed only the IV rank gate. These are tickers with confirmed technical setups but insufficient premium. When IV spikes on one of them — often around a macro event — you already have the technical thesis ready and can act quickly.

---

## Related Notes

- [[Ticker-Criteria-Technical]] — Detailed technical setup rules with chart examples
- [[Ticker-Criteria-Fundamental]] — Binary event screen, liquidity thresholds, sector concentration limits
- [[Screener-Setup]] — Saved filter configurations for Barchart, Finviz, Market Chameleon
- [[High-Probability-Setup-Checklist]] — Entry checklist applied after ticker selection
- [[IV-Rank]] — Calculation, interpretation, and regime-adjusted thresholds
