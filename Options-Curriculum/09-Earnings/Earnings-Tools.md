---
title: Earnings Tools for Options Research
tags:
  - earnings
  - tools
  - research
  - volatility
  - iv-crush
aliases:
  - Earnings Research Tools
  - Earnings Options Tools
status: draft
related:
  - "[[Earnings-Overview]]"
  - "[[Earnings-Ticker-Selection]]"
  - "[[Screener-Setup]]"
---

# Earnings Tools for Options Research

Effective earnings options research requires a small stack of specialized tools. No single platform gives you everything — combine at least two to cross-validate implied moves and historical outcomes before entering a position.

---

## 1. Market Chameleon (marketchameleon.com)

**Best for:** Historical implied vs. actual move comparison, IV rank around earnings, earnings calendar screening.

**Cost:** Free tier covers most historical data; Pro (~$40/month) unlocks full history and bulk export.

**Key workflow:**
Navigate to a ticker → *Earnings* tab → look at the earnings history table. Columns that matter:

| Column | What it tells you |
|---|---|
| Implied Move % | Market's expected 1-day move priced into straddle at close before earnings |
| Actual Move % | Realized next-day open-to-open or close-to-close move |
| Beat / Miss | EPS surprise direction |
| IV Rank (pre) | Where IV sat before earnings vs. the prior 52-week range |

The ratio of average implied move to average actual move is your historical edge signal. If the ticker routinely moves less than implied (ratio < 1.0), premium selling has had a systematic edge. Rule of thumb: require at least 8 earnings observations before treating the ratio as meaningful.

> [!tip] Look for tickers where the actual/implied ratio is below 0.85 over 8+ events. That gap is the margin of safety for short premium plays — but confirm it hasn't narrowed in the last 2–3 events, which may signal a regime change in that stock's earnings volatility.

---

## 2. Earnings Whispers (earningswhispers.com)

**Best for:** Whisper numbers (unofficial buy-side consensus), after-hours gapper tracking, high-conviction calendar screening.

**Cost:** Free for basic calendar; Gold ($20/month) for whisper numbers and full historical data.

**Key workflow:** Check the earnings calendar 1–2 weeks out to build your watchlist. The *whisper number* vs. consensus gap is a directional signal — stocks with whispers far above consensus tend to sell off even on beats if results don't clear the whisper. This is context for whether to hold a short straddle into the number vs. flattening delta exposure. After-hours gappers section shows realized overnight moves in real-time, useful for post-earnings forensics.

> [!note] Whisper numbers reflect informal expectations aggregated from buy-side analysts. They are not official guidance and should be treated as directional color, not precise forecasts.

---

## 3. Barchart (barchart.com)

**Best for:** Visualizing the IV spike into earnings and the IV crush the morning after.

**Cost:** Free for most options IV charts; Premier (~$20/month) for full history.

**Key workflow:** Ticker → *Options* → *Volatility Chart*. The 30-day and 60-day IV charts show the characteristic ramp into the event and the cliff-drop after. Use this to time entry: entering a short vega position 5–10 days before earnings captures more of the ramp than entering the day before, but adds overnight gap risk from an unexpected pre-announcement.

> [!warning] IV crush is guaranteed only in direction (IV falls after the event). The magnitude varies widely — a stock that moves 15% on earnings can still crush IV if the move was already priced in, but a stock that moves 3% on a 2% implied move may not crush IV enough to overcome theta decay losses on long premium plays.

---

## 4. ThinkorSwim Earnings Calendar (thinkorswim.com)

**Best for:** Watchlist filtering by days-to-earnings inside your broker platform.

**Cost:** Free with TD Ameritrade / Schwab account.

**Key workflow:** Open *MarketWatch* → *Earnings*. Use the *Upcoming Earnings* screener to filter by 1–14 days. Add columns for IV Rank and option volume. You can then right-click any ticker to open the options chain directly. ThinkorSwim also lets you set up a custom watchlist column — `daysToEarnings()` — so your standard watchlist shows DTE to the next event without leaving the platform.

---

## 5. ORATS (orats.com)

**Best for:** Systematic backtesting of earnings premium strategies across a large universe; the most complete historical earnings data available to retail traders.

**Cost:** Starts at ~$100/month for the data API; Wheel tool (web UI) is cheaper. Not appropriate as a first tool.

**Key workflow:** ORATS provides per-ticker historical straddle P&L at various entry windows (1 day before, 5 days before, etc.), broken out by IV rank bucket. This lets you answer: "Does selling straddles when IV rank > 60 perform better than when IV rank < 40, for this specific ticker?" The backtester accounts for actual bid/ask spreads using historical NBBO data.

> [!danger] ORATS backtests assume fills at mid. Real fills on illiquid underlyings can be significantly worse. Do not run live earnings trades based solely on backtest results without verifying current liquidity and spread width on the day of entry.

---

## 6. Free Options: Yahoo Finance & Finviz

**Best for:** Basic scheduling and quick earnings date lookup when you don't need historical IV data.

- **Yahoo Finance** (*Earnings Calendar* tab): lists upcoming earnings by day, EPS estimate vs. prior. No IV data.
- **Finviz** (finviz.com/calendar): similar calendar, plus stock screener filters for *Earnings Date* that integrate with fundamental filters. Useful for [[Screener-Setup]] workflows to narrow a universe before pulling IV data from Market Chameleon or Barchart.

---

## Recommended Stack by Experience Level

| Level | Tools |
|---|---|
| Beginner | Yahoo Finance (dates) + Market Chameleon (history) |
| Intermediate | + Barchart (IV chart) + ThinkorSwim watchlist |
| Advanced | + ORATS backtester + Earnings Whispers (whisper numbers) |

See [[Earnings-Ticker-Selection]] for how to apply this data to choose which earnings to trade, and [[Earnings-Overview]] for the full strategic framework.
