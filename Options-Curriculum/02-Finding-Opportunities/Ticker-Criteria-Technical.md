---
title: Ticker Criteria — Technical
tags:
  - finding-opportunities
  - ticker-selection
  - technical-analysis
  - options-playbook
aliases:
  - Technical Ticker Criteria
  - Ticker Technical Checklist
status: draft
related:
  - "[[Ticker-Criteria-Fundamental]]"
  - "[[Ticker-Selection-System]]"
  - "[[Entry-Confirmation-Signals]]"
---

# Ticker Criteria — Technical

Technical screening filters the universe of optionable stocks down to names where the chart gives you an edge: clear structure to lean against, sufficient liquidity to get filled, and no near-term binary events that would blow up a position-trade thesis.

Use this checklist before entering any options trade. Each item maps to a concrete rule, not a vague preference.

---

## The Technical Checklist

### 1. Trend or Range: Is the Tape Readable?

- [ ] Stock is in a **confirmed uptrend** (higher highs, higher lows), **downtrend** (lower highs, lower lows), or **defined range** (clear horizontal support and resistance).
- [ ] Avoid stocks with random, news-driven chop — no tradeable structure means no reliable anchor for your strikes.

> [!warning]
> Selling premium on a choppy stock feels safe until a sudden directional move breaches your strike. Defined structure is not a preference — it is your only risk anchor.

Model tickers with readable tape: **AAPL** (persistent uptrend with orderly pullbacks), **GLD** (range-bound to uptrend cycles), **SPY** (liquid, well-defined trend phases).

---

### 2. Support and Resistance: Know Where You'd Sell

- [ ] Identify **at least two swing lows** acting as support (candidate put-sell levels).
- [ ] Identify **at least one prior high or pivot** acting as resistance (candidate call-sell or call-spread level).
- [ ] S/R levels should be separated by at least 3–5% from the current price — levels too close to spot offer no buffer.

> [!tip]
> Rule of thumb (experienced traders): sell puts at or below the most recent swing low that held on a closing basis. One candle poke-through does not invalidate a level; a weekly close through it does.

---

### 3. Moving Averages as Dynamic Support

- [ ] The **20-day SMA** is intact as near-term dynamic support in an uptrend.
- [ ] The **50-day SMA** provides a secondary floor — strong stocks bounce here in normal pullbacks.
- [ ] The **200-day SMA** is the long-term trend filter: only sell puts on the put side if price is above the 200 SMA, or explicitly trading a mean-reversion setup.

**NVDA** example: in strong trending phases, the 21-day EMA acts as the first line of defense; a break of the 50-day has historically signaled deeper corrections of 15–25%.

> [!note]
> Moving averages are lagging by construction — they describe where price *has been*, not where it is going. Their value here is as a consensus anchor: many participants place stops and entries at round SMAs, making them self-fulfilling in liquid names.

---

### 4. Volume: Minimum Liquidity Floor

- [ ] Average daily share volume **≥ 1 million shares/day** (trailing 20-day average).
- [ ] Options open interest on target strikes ≥ 500 contracts; bid/ask spread ≤ 10% of mid.

Low-volume stocks produce wide option spreads that silently erode edge before you even put the trade on.

---

### 5. Price Range: $20–$500

- [ ] Stock price **between $20 and $500**.
- [ ] Avoid stocks under $20: elevated percentage moves, thin option chains, market-maker spread disadvantage.
- [ ] Avoid stocks over $500 unless you have the capital to deploy margin comfortably (AAPL, SPY, GLD all live comfortably in this range).

> [!danger]
> Penny stocks and sub-$10 names have options chains built for speculation, not premium selling. The math of a 50% move on a $5 stock is different from a 50% move on a $200 stock — the former is a common occurrence, not a tail risk.

---

### 6. Avoid List — Hard Filters

- [ ] **No earnings within 14 calendar days** — unless you are specifically running an [[Earnings-Volatility-Trade]] strategy.
- [ ] **No recent gap-up or gap-down (>5%)** in the last 5 trading days — gaps reset support/resistance structure and invalidate your prior level analysis.
- [ ] No pending FDA approvals, merger votes, or scheduled macro events that could produce a gap.

> [!warning]
> Earnings cause implied volatility to spike then collapse ("IV crush"). Selling premium into earnings without a dedicated strategy means you are accepting binary event risk priced as if you know the outcome. Most retail traders do not have an edge on earnings direction.

---

## Quick Reference: Model Tickers

| Ticker | Why It Passes |
|--------|--------------|
| AAPL   | $170–$200 range, 50M+ ADV, orderly trend, liquid options |
| NVDA   | Volatile but structured; high ADV; 50/200 SMA respected |
| SPY    | ETF with near-perfect liquidity; no single-stock gap risk |
| GLD    | Range-to-trend cycles; commodity hedge; no earnings risk |

---

## Related Notes

- [[Ticker-Criteria-Fundamental]] — earnings quality, sector filter, balance sheet
- [[Ticker-Selection-System]] — combining technical + fundamental into a scored watchlist
- [[Entry-Confirmation-Signals]] — after the ticker passes, confirming the entry timing
