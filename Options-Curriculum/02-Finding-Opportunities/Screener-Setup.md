---
title: Screener Setup
tags:
  - finding-opportunities
  - screeners
  - workflow
  - iv-rank
  - tools
aliases:
  - Options Screener Setup
  - Screener Workflow
status: draft
related:
  - "[[Ticker-Selection-System]]"
  - "[[IV-Rank]]"
  - "[[High-Probability-Setup-Checklist]]"
  - "[[Earnings-Calendar-System]]"
---

# Screener Setup

A repeatable screener routine compresses opportunity search from hours to under fifteen minutes. The goal is not to find every trade — it is to surface candidates that already pass the first two gates of [[IV-Rank]] elevation and liquidity, so you spend cognitive time on [[High-Probability-Setup-Checklist]] evaluation, not data hunting.

> [!warning]
> High IV rank alone does not justify a trade. It signals that options are expensive relative to history, but it does not predict direction or mean-reversion timing. Always confirm through the full [[High-Probability-Setup-Checklist]] before committing capital.

---

## Platform 1: Barchart Options Screener

**URL:** barchart.com → Options → Screener

### Filter Configuration

| Filter | Value | Rationale |
|---|---|---|
| IV Rank | > 50 | Only elevated-IV candidates |
| Underlying Volume | > 500,000 | Ensures liquid underlying |
| Open Interest (target strikes) | > 500 | Confirms tradable strikes exist |
| Option Volume | > 5,000 | Filters illiquid chains |

### Setup Steps

1. Navigate to the Screener tab and click "Add Filter."
2. Under Volatility, add **IV Rank (1-Year)** and set minimum to 50.
3. Under Underlying, add **Average Volume** and set minimum to 500,000.
4. Run the scan. Click any result to open the chain, and confirm OI > 500 at your target delta strikes before adding to watchlist.
5. Export: click the download icon (CSV) to pull the filtered list into a spreadsheet.

### What to Look For

Prioritize results where IV rank is in the 60–85 range. Stocks above 90 often have known binary events (earnings, FDA) — treat those through [[Earnings-Calendar-System]] logic, not standard premium-selling setups.

---

## Platform 2: Market Chameleon

**URL:** marketchameleon.com → Options → IV Rank Screener

### Setup Steps

1. Open the IV Rank Screener. Set **IV Rank > 50** and **IV Percentile > 50** (use both — they diverge on skewed distributions).
2. Cross-reference against the **Earnings Calendar** tab. Market Chameleon shows expected move (EM) in dollar and percentage terms derived from ATM straddle pricing — this is rule-of-thumb implied pricing, not a guarantee of realized move.
3. Check the **Term Structure** tab for each candidate. A steeply inverted front-to-back term structure (near-term IV > back-month IV) reinforces a short-vega thesis.
4. Export: use the "Export to CSV" button at the top of the screener results.

> [!note]
> Market Chameleon's expected move figures are calculated from the near-term ATM straddle price divided by the underlying spot price. They reflect market-implied one-standard-deviation moves, not analyst forecasts. See [[IV-Rank]] for the derivation.

### What to Look For

Candidates where front-month IV rank > 60 and the term structure is inverted are the strongest short-vol setups. Flat or upward-sloping term structures suggest the market is not pricing near-term risk heavily — less edge for short premium.

---

## Platform 3: thinkorswim (ToS) — Stock Hacker

**Path:** Scan → Stock Hacker

### Setup Steps

1. Open **Scan → Stock Hacker**.
2. Click "Add Study Filter." Select **ImpVolatility_Hist_Pct** (this is ToS's IV Percentile measure).
3. Set condition: **ImpVolatility_Hist_Pct is greater than 50**.
4. Add a second filter: **Volume is greater than 500000** (found under the Price/Volume group).
5. Click Scan. Results populate in the lower panel.
6. Right-click any result → **Add to Watchlist** to save directly into a ToS watchlist for monitoring.

> [!tip]
> Save this scan as a preset ("Save Scan Query") so you can rerun it in one click each Monday morning. Name it something explicit like "IV-Rank-50plus-Liquid" — generic names cause confusion when you accumulate multiple saved scans over time.

> [!danger]
> ToS's `ImpVolatility_Hist_Pct` uses a 52-week lookback by default. This is consistent with the [[IV-Rank]] definition used in this curriculum, but verify the lookback period when comparing results across platforms — some use 30-day or 6-month windows, which produce materially different rank values.

---

## Weekly Workflow

| Day | Action |
|---|---|
| **Monday** | Run all three screeners. Cross-reference overlapping names. Build a watchlist of 8–15 candidates that pass all three platforms. Check each against [[Ticker-Selection-System]] criteria. |
| **Tuesday – Thursday** | Monitor watchlist daily. Enter setups that confirm through [[High-Probability-Setup-Checklist]]. Prefer Tuesday or Wednesday entries to preserve theta decay advantage over the weekend. |
| **Friday** | No new entries. Manage existing positions only — adjust, roll, or close. New Friday entries sacrifice a weekend of theta while carrying full gap risk. |

> [!tip]
> Limit active positions to 6–8 underlyings at once during the learning phase. More positions than that makes Friday management chaotic and increases the chance of mismanaging a losing trade due to attention fragmentation.

---

## Cross-Platform Confirmation Rule

A candidate that appears on **two or more** screeners independently is higher priority than one that appears on only one. Overlapping results suggest the IV elevation is robust across different data providers and calculation methodologies — not a single-source artifact.

This is a rule of thumb, not statistically validated against a backtested dataset.

---

## Related Notes

- [[Ticker-Selection-System]] — fundamental and technical criteria applied after screening
- [[IV-Rank]] — how IV rank and IV percentile are calculated and interpreted
- [[High-Probability-Setup-Checklist]] — the gate every screener result must pass before entry
- [[Earnings-Calendar-System]] — separate workflow for earnings-driven elevated IV
