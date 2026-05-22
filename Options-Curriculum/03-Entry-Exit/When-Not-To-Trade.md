---
title: When Not To Trade
tags:
  - entry-exit
  - discipline
  - risk-management
  - macro-events
aliases:
  - no-trade-conditions
  - sit-on-hands
status: draft
related:
  - "[[Building-Discipline]]"
  - "[[Entry-Confirmation-Signals]]"
  - "[[Drawdown-Management]]"
---

# When Not To Trade

> [!note]
> Tastyworks research on thousands of retail accounts found: "The biggest gains come from staying out of bad trades, not finding more trades." This note outlines the conditions that should produce a hard stop before any new position is opened. Treat this as a checklist that runs *before* [[Entry-Confirmation-Signals]], not after.

Knowing when to step aside is a higher-leverage skill than finding the next trade. The six conditions below are not suggestions — each one has a specific, documented mechanism through which it destroys premium-selling edge.

---

## 1. FOMC Decision Days

The Federal Reserve publishes its rate decision on a fixed schedule (eight times per year, released at 2:00 PM ET). The subsequent press conference extends uncertainty until roughly 3:30 PM ET.

> [!warning]
> **Do not open new short-gamma positions on FOMC decision day.** VIX term structure frequently inverts, and intraday moves of 1–2% in SPX are routine even when the decision itself is "expected." If you hold short-gamma positions (short straddles, short iron condors) through the meeting, close or hedge the gamma exposure by the morning session before the announcement.

Rule of thumb: treat the entire decision day as a no-entry day for undefined-risk structures. Calendar spreads and long-vega plays have a different profile and may be appropriate *before* the announcement, not after.

---

## 2. CPI and Nonfarm Payrolls Days

Major macro prints — CPI (released second or third Tuesday of the month, 8:30 AM ET) and the Nonfarm Payrolls report (first Friday of the month, 8:30 AM ET) — produce pre-open vol spikes that are structurally similar to FOMC. The difference is they can move *against* consensus more frequently, because the market has already priced the consensus move.

> [!warning]
> **Avoid entering new positions in the 30 minutes before and 60 minutes after a CPI or NFP print.** Bid-ask spreads in SPX options widen by 2–5x during this window, giving away edge immediately. This is data-backed: CBOE trade-cost studies show retail executions within 15 minutes of a macro print pay a measurable premium over mid-market.

---

## 3. Earnings Within 14 Days

Implied volatility in individual equities is directionally unreliable within two weeks of an earnings announcement. The volatility risk premium (VRP) collapses asymmetrically, and realized moves routinely exceed what the options implied.

> [!danger]
> **Never sell naked or undefined-risk premium in a single stock within 14 days of its earnings date unless the entire thesis is earnings-driven and defined-risk.** This applies to cash-secured puts, naked calls, and short strangles. An earnings play with defined risk (iron condor, debit spread) is a separate strategy — size it to withstand a 1.5× the implied move.

Use the [[Entry-Confirmation-Signals]] earnings filter before any equity options entry.

---

## 4. VIX Above 35

When spot VIX exceeds 35, tail risk is no longer priced normally. The distribution of SPX daily returns widens, skew steepens violently, and margin requirements can gap overnight.

> [!danger]
> **All undefined-risk strategies are off the table when VIX > 35.** Short strangles, naked puts, and unhedged short straddles have historically produced account-level drawdowns exceeding 50% in this regime. Refer to [[Drawdown-Management]] for the mathematical basis. If you trade at all, use spreads with maximum defined loss no larger than 1% of account.

---

## 5. Your Emotional State

Fear, euphoria, and revenge trading after a loss are not personality flaws — they are hard-wired cognitive responses. They are also measurable: studies in behavioral finance (Odean, 1998; Barber & Odean, 2001) show retail traders increase trade frequency and size significantly following a loss, and outcomes deteriorate.

> [!warning]
> **If you have taken a loss exceeding your pre-defined daily stop, do not open another position that day.** This is a rule, not a guideline. Write it in your trading journal before you open the platform. See [[Building-Discipline]] for the journal protocol and the session-stop trigger.

Signs you should not trade: scanning for a trade to "get back" what you lost, increasing size relative to your standard, overriding your own entry criteria.

---

## 6. Illiquid Market Conditions

Options markets during US holidays (early close or full close), the two weeks around Christmas/New Year, and any day with SPX volume below the 30-day average by more than 30% produce artificially wide spreads and unreliable fills.

> [!tip]
> Check total SPX volume by 10:30 AM ET. If volume is tracking more than 25% below the prior 20-day average, treat it as a reduced-size day or no-entry day. This is a rule of thumb, not data-backed to a specific threshold, but experienced traders widely apply a similar filter.

---

## Summary Checklist

Before any new entry, run through this list in order:

1. Is today an FOMC, CPI, or NFP day?
2. Does the underlying have earnings within 14 days?
3. Is VIX above 35?
4. Have I already hit my daily loss stop?
5. Is market volume materially below average?

If any answer is yes, the default action is no trade. Override requires an explicit written justification in your journal. See [[Entry-Confirmation-Signals]] for the affirmative criteria that must be satisfied once all five are cleared.
