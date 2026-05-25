---
title: Earnings Execution Playbook
tags:
  - earnings
  - execution
  - workflow
  - playbook
  - options
aliases:
  - Earnings Workflow
  - Earnings Trade Process
status: draft
related:
  - "[[Earnings-Ticker-Selection]]"
  - "[[High-Probability-Setup-Checklist]]"
  - "[[Earnings-IC-Playbook]]"
  - "[[Earnings-Straddle-Strangle]]"
  - "[[Building-Discipline]]"
---

# Earnings Execution Playbook

Earnings trades live and die on process. The edge in earnings volatility selling is structural — IV almost always inflates into the event and collapses after — but that edge evaporates quickly if execution is sloppy. This playbook defines a repeatable weekly workflow: five steps, five days, minimal discretion.

> [!warning]
> Earnings announcements can produce gap moves that far exceed any premium collected. Even a well-constructed trade can lose more than its max-theoretical-loss when underlying gaps through strikes overnight. Position sizing and pre-defined exit rules are non-negotiable.

---

## Step 1 — Monday / Tuesday: Research

**Pull the week's earnings calendar.** Use Market Chameleon's earnings calendar filtered to the current week. Sort by market cap to focus on liquid names.

Screen each candidate against [[Earnings-Ticker-Selection]] criteria:

- IV Rank ≥ 50 (rule of thumb; higher is better but rarer)
- Liquid options market: bid/ask spread on ATM options ≤ 5% of mid, open interest > 500 on the strikes you plan to use
- Expected Move (EM) history: prior realized moves should be smaller than the implied EM in at least 60–70% of past events (data-backed threshold from Market Chameleon's historical EM table)
- No binary event overlap (FDA, legal ruling, merger vote) unless intentional
- Earnings date confirmed — do not trade unconfirmed dates

Log your shortlist in your trading journal. Three to five candidates is a workable number; more than that invites overtrading.

---

## Step 2 — Day Before Earnings (Before Market Close): Confirm and Enter

**Confirm the setup — do not skip this step even if it feels redundant.**

Run through [[High-Probability-Setup-Checklist]]:

1. Recheck IV Rank — has it moved materially since Monday? A drop below 40 may invalidate the trade thesis.
2. Pull the current straddle price and back-calculate the implied Expected Move as a percentage of spot. Compare to historical average EM. If the current EM is unusually small, the market may be under-pricing the event; if unusually large, premium looks rich.
3. Verify earnings date and time (AMC vs. BMO matters — it determines when you close).
4. Check for any same-day news that could distort the vol surface (macro prints, sector events).

**Enter 30–60 minutes before market close (roughly 3:00–3:30 PM ET).** This timing captures near-peak IV before the close without taking unnecessary overnight gap risk on the day before earnings. Avoid entering at or after 3:45 PM — spreads widen and fills deteriorate.

Refer to [[Earnings-IC-Playbook]] or [[Earnings-Straddle-Strangle]] for structure-specific leg selection and sizing.

> [!note]
> AMC (after market close) earnings are the standard case for this playbook — you enter the afternoon before, the announcement comes out that evening, and you exit the next morning. BMO (before market open) names require entering two days before and exiting the morning of the announcement. Adjust the calendar accordingly.

---

## Step 3 — Earnings Night: Do Nothing

The trade is on. The position is sized correctly. There is no adjustment to make before the number drops.

Do not watch the after-hours quote. Do not calculate real-time P&L from the after-hours move. The options market does not reprice efficiently after hours — the number you see does not reflect your actual exit price.

> [!tip]
> Set an alarm for 9:25 AM on the earnings day. Your job is to close the trade at open, not to evaluate it — you will evaluate it later.

---

## Step 4 — Next Morning (Earnings Day): Close at Open

**Close the trade between 9:30 and 9:45 AM ET. Use market orders.**

Do not use limit orders at the open. Limit orders frequently go unfilled in the first minutes after an earnings gap, leaving you with a partial position and an undefined risk profile. A market order guarantees the fill. The slippage cost is real but bounded; the cost of an unfilled exit is not.

If the position is a multi-leg spread, close all legs simultaneously using a spread order routed as a single market order where your broker supports it. If not, leg out of the short options first (the risk leg), then close the long hedge.

> [!danger]
> Do not attempt to "manage" an earnings position that has moved against you by rolling or adjusting at the open. You are in the highest-volatility window of the day, with the widest spreads and the most uncertain price discovery. The defined exit rule exists precisely for this moment. Take the loss and close.

**Do not hold through the 9:45 AM window** unless there is a broker outage or genuine fill failure. Holding past open forfeits the vol-collapse timing advantage and exposes you to intraday mean reversion risk on a position that is no longer sized for that regime.

---

## Step 5 — P&L Review: Log and Learn

After closing, record the outcome in your trading journal:

| Field | Detail |
|---|---|
| Ticker | e.g., AAPL |
| Structure | e.g., Iron Condor, Short Straddle |
| EM implied at entry | e.g., ±4.2% |
| Actual move | e.g., +6.8% |
| Premium collected | e.g., $2.40 |
| P&L at close | e.g., -$1.10 |
| Notes | Why did it miss? Was the setup valid? |

Compare the actual move to the EM implied at entry. Over time, this log is your primary data source for refining [[Earnings-Ticker-Selection]] thresholds. Do not draw conclusions from fewer than 20 trades — the sample size is too small for statistical significance.

> [!tip]
> Track win rate and average P&L separately. A strategy with a 65% win rate but large average losers can still be net-negative. What matters is expected value per trade, not batting average.

See [[Building-Discipline]] for journaling templates and the cognitive pitfalls most common after a losing earnings trade.

---

## Weekly Calendar Summary

| Day | Action |
|---|---|
| Monday / Tuesday | Pull calendar, screen candidates vs. [[Earnings-Ticker-Selection]] |
| Day before earnings (PM) | Confirm setup, run [[High-Probability-Setup-Checklist]], enter 30–60 min before close |
| Earnings night | Do nothing |
| Next morning 9:30–9:45 AM | Close all legs with market orders |
| Same day (afternoon) | Log outcome, compare to EM, update journal |
