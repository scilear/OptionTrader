---
title: Ticker Criteria Fundamental
tags:
  - finding-opportunities
  - ticker-selection
  - liquidity
  - fundamental-analysis
aliases:
  - fundamental ticker criteria
  - options liquidity requirements
  - binary event screening
status: draft
related:
  - "[[Ticker-Selection-System]]"
  - "[[Screener-Setup]]"
  - "[[Ticker-Criteria-Technical]]"
  - "[[High-Probability-Setup-Checklist]]"
---

# Ticker Criteria Fundamental

Before entering any position, verify that the underlying and its options meet hard liquidity and fundamental thresholds. Poor liquidity is a silent killer—bid/ask slippage can erase a profitable trade before you exit. Binary events can spike volatility beyond model assumptions, turning defined-risk structures into undefined disasters. This note covers the minimum standards for tradable tickers.

---

## Options Liquidity Requirements

Options that are illiquid or undergoing adverse selection will cost you more on entry and exit than the premium edge can support.

**Open Interest Floor (Mandatory)**

- Minimum **500 contracts** at your target strike and expiry
- This is non-negotiable. Below 500 OI, bid-ask spreads widen dramatically and market makers defend with wider quotes
- Front-month at-the-money typically has the best liquidity; check liquidity *at your intended strike*, not average OI across the expiry

**Bid-Ask Spread Limits**

- Options under $1.00: spread ≤ $0.10 (hard rule)
- Options $1.00–$5.00: spread ≤ 10% of mid-price
- Options above $5.00: spread ≤ 5% of mid-price

> [!tip]
> Use the **mid-price** (not bid or ask) as your fill benchmark. If you want to exit quickly, subtract 50% of the spread from your entry before committing capital. This "slippage discount" ensures your expected profit survives round-trip costs.

**Bid-Ask Verification**

Always pull a live quote within 15 minutes of screening. Option chain websites can be stale; bid-ask spreads widen intraday, especially before market close or during earnings uncertainty. If the spread has widened by >50% since your screener results, cut the ticker and move to the next candidate.

---

## Underlying Liquidity Requirements

A liquid option on an illiquid stock is a trap. The stock itself must have sufficient trading volume to support large option positions without underlying repricing.

**Average Daily Volume (ADV)**

- Minimum **500,000 shares/day** over the past 20 trading days
- This ensures you can leg into or out of positions at reasonable slippage
- ADV < 500K often correlates with wider option spreads and adverse selection

**Market Capitalization**

- Minimum **$1 billion** market cap
- Below $1B, corporate news and insider activity drive unpredictable gaps
- Leverage the [[Screener-Setup]] to auto-filter on market cap

---

## Binary Event Screening

> [!warning]
> Earnings, FDA decisions, court rulings, and M&A announcements can cause gap moves of 10%+ in a single session. If you are not explicitly trading the event, you must exclude the window. A 30-delta debit spread with 15% theoretical theta decay can be eliminated by a 5% overnight gap in the wrong direction.

**Mandatory Exclusions (Unless Trading the Event)**

- **Earnings announcement** within the intended expiry window (e.g., if selling a 21-DTE strangle and earnings are in 14 days, skip)
- **FDA decisions or regulatory rulings** (pharma, biotech, medical device)
- **Court rulings or litigation decisions** (especially patent or antitrust cases)
- **M&A announcements or pending regulatory approval** (potential deal failure or arbitrage unwind)
- **Economic data releases** directly affecting the ticker (major macros for broad indices)

**Quick Event Check**

Use your broker's event calendar or Barchart's earnings calendar. Most screeners can auto-exclude earnings; enable this filter and refine manually only when you are explicitly trading the event window.

> [!tip]
> Mark non-event tickers on a "watch list" after their earnings. If IV spikes post-earnings, you may have a high-IV-rank setup with less event risk ahead.

---

## Preferred Vehicles for Defined-Risk Strategies

**ETFs over Single Stocks**

For defined-risk structures (credit spreads, iron condors, calendars), prefer broad-based ETFs over single stocks:

- **SPY** (S&P 500): deepest liquidity, tightest spreads, institutional flow
- **QQQ** (Nasdaq 100): tech-heavy, strong IV term structure
- **IWM** (Russell 2000): small-cap rotation plays, solid liquidity
- **GLD** (Gold ETF): commodity volatility, earnings-independent
- **TLT** (20+ Year Treasury): directional rates trading, low event risk

ETFs offer:
- No earnings surprises (composite of many holdings)
- Tighter bid-ask spreads due to arbitrage activity
- Reduced single-stock idiosyncratic risk
- Better liquidity in further-out expirations

> [!danger]
> Single stocks with elevated IV rank often have wider option spreads and higher event risk than you expect. Beginners should avoid single-stock strategies until they have 50+ completed paper trades on ETF structures. The learning curve on risk management is lower on composite vehicles.

---

## Pass/Fail Checklist

Use this table to quickly eliminate tickers that fail hard criteria.

| Criterion | Pass | Fail |
|-----------|------|------|
| **Options OI at target strike** | ≥ 500 contracts | < 500 contracts |
| **Options bid-ask spread** | Per table above | Exceeds limits |
| **Underlying ADV** | ≥ 500K shares/day | < 500K shares/day |
| **Market cap** | ≥ $1B | < $1B |
| **Binary event in window?** | None, or intentionally trading it | Earnings, FDA, M&A, court ruling |
| **Strategy type** | Using ETFs for defined-risk | Single stock without 50+ trades experience |

**Triage Rule**: If any criterion is "Fail" and you are not trading the binary event, **cut the ticker immediately**. Marginal candidates become disasters in live trading.

---

## Integration with the Ticker Selection System

This note covers **Stage 2, Pass A** of the [[Ticker-Selection-System]] workflow. After running your [[Screener-Setup]], apply this fundamental filter to eliminate tickers with poor liquidity or upcoming events. Survivors then proceed to [[Ticker-Criteria-Technical]] (Pass B) for setup confirmation.

Estimated time per ticker: **30 seconds**. Target elimination rate: **50%** of initial screener output, leaving 10–30 tickers for technical review.

---

## Related Notes

- [[Ticker-Selection-System]] — Two-stage funnel workflow
- [[Screener-Setup]] — Barchart and Finviz filter configurations
- [[Ticker-Criteria-Technical]] — Setup recognition rules
- [[High-Probability-Setup-Checklist]] — Entry validation checklist
