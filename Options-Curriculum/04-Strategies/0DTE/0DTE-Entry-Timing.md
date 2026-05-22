---
title: 0DTE Entry Timing
tags:
  - 0DTE
  - SPX
  - entry-timing
  - iron-condor
  - intraday
aliases:
  - 0DTE Timing
  - Zero DTE Entry Windows
status: draft
related:
  - "[[0DTE-Overview]]"
  - "[[0DTE-Iron-Condor]]"
  - "[[Intraday-Timing-Open]]"
---

# 0DTE Entry Timing

Entry timing is the single most consequential skill in [[0DTE-Overview|0DTE trading]]. A structurally sound iron condor placed at the wrong time of day can be killed by intraday momentum before [[Theta|theta]] has a chance to work. The goal is to enter after price discovery is complete and before premium has decayed to unworkable levels.

![[chart-intraday-profile.png]]

---

## Time-of-Day Decision Table

| Window | Time (ET) | Priority | Condition to Enter | Preferred Structure |
|---|---|---|---|---|
| Opening gap play | 9:30–9:45 | Low | Gap >0.5% and fills by 9:45 | IC (wait for settle) |
| Mid-morning | 10:00–11:00 | **High** | IV normalized, no trend | IC or credit spread |
| Midday | 11:00–13:00 | Medium | Clear range confirmed | IC only if range tight |
| Afternoon | 13:00–14:00 | Aggressive | Strong theta; contained range | IC with 10–20% PT |
| Late session | 14:00+ | Avoid | Risk/reward collapses | No new entries |

---

## 1. Opening Gap Plays (9:30–9:45 AM)

If SPX gaps more than 0.5% at the open, the first 15 minutes are price discovery — not a trading window.

- **Do not enter** during the first 15 minutes of a significant gap day. Bid/ask spreads are wide, fills are poor, and direction is undetermined.
- If the gap **fills by 9:45 AM**, the session range is likely set. This is an actionable signal: the market has rejected the overnight move and traders are fading back to the prior close. Enter an [[0DTE-Iron-Condor]] around the established range.
- If the gap **holds** (no fill by 9:45), skip this window. Trending opens create directional risk that invalidates neutral IC structure.

> [!warning]
> Entering an IC in the first 15 minutes on a gap day is one of the most common beginner mistakes. Premium is elevated but so is directional risk — you are paying for vol while taking a position that needs the market to stop moving.

---

## 2. Mid-Morning Entries (10:00–11:00 AM)

This is the **primary entry window** for 0DTE. By 10:00 AM, several things have aligned:

- Price discovery is largely complete for normal (non-news) days.
- The opening IV spike has already crushed — you are not fighting inflated vega.
- A support/resistance range is visible on the 5-minute chart.
- VIX has typically settled from its open print.

Enter an [[0DTE-Iron-Condor]] or credit spread when VIX is stable or declining and the 5-minute chart shows a **consolidation candle** (narrow high-low range, body less than 30% of the prior candle's range). This consolidation candle signals that market participants have absorbed the open and are waiting.

> [!tip]
> Rule of thumb (experience-based, not backtested): the 10:00–10:30 window produces the best premium-to-risk ratio because IV is normalized but decay has barely started. Most experienced 0DTE traders aim to be positioned by 10:30 AM.

---

## 3. Midday Entries (11:00 AM–1:00 PM)

Lower priority. Premium has declined from mid-morning levels but the session range is well-defined. Only enter if:

- A clear support/resistance range has formed and held for at least two 15-minute candles.
- VIX has not re-spiked (a re-spike mid-session signals a potential trend resumption).
- Credit collected on the IC is still above your minimum threshold (rule of thumb: at least $1.00 for a 5-point-wide SPX IC).

---

## 4. Afternoon Entries (1:00–2:00 PM)

Aggressive theta decay is working in your favor, but the risk profile has changed. The P&L window is compressed:

- Profit targets should be set at **10–20% of max credit** rather than the typical 25–50%, because there is not enough time for larger gains.
- Position size should be reduced vs. morning trades — gamma risk per dollar of premium is highest near expiration.
- Only enter if the range is tight and there is no major news catalyst (Fed speakers, economic data) scheduled for the afternoon.

> [!danger]
> Afternoon 0DTE entries are unsuitable for beginners. Gamma near expiry can produce $10–20 SPX point moves in a single 5-minute candle. A position that appears safe at 1:30 PM can breach a strike by 2:15 PM with no adjustment time remaining.

---

## 5. Entry Triggers (All Windows)

Before pulling the trigger in any window, confirm all three:

1. **5-minute consolidation candle**: narrow range body signals local equilibrium — see [[Intraday-Timing-Open]].
2. **VIX stable or declining**: a rising VIX into an IC entry means you are selling into increasing demand for protection.
3. **No binary event in session**: earnings, FOMC, CPI are deal-breakers regardless of timing.

---

## 6. Delta Selection by Risk Tolerance

Wing placement determines the trade-off between premium and probability.

| Delta (each wing) | Probability of Profit (approx.) | Notes |
|---|---|---|
| 0.10–0.15 | ~70–75% | More premium; wings closer; higher risk of breach on move |
| 0.05–0.08 | ~85–90% | Less premium; wider buffer; better for volatile open days |

> [!note]
> These probability estimates are derived from delta as a rough proxy for the option's moneyness probability — not from empirical 0DTE backtest data. Actual fill probabilities depend on realized intraday volatility distributions, which differ from implied.

---

## Related Notes

- [[0DTE-Overview]] — strategy framework and risk limits
- [[0DTE-Iron-Condor]] — structure mechanics and adjustment triggers
- [[Intraday-Timing-Open]] — detailed open analysis methodology
