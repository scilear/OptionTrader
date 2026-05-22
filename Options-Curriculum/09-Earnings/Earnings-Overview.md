---
title: Earnings Options Trading — Overview
tags:
  - earnings
  - iv-crush
  - volatility
  - strategy
  - premium-selling
aliases:
  - Earnings Overview
  - Earnings IV Strategy
status: draft
related:
  - "[[Earnings-Ticker-Selection]]"
  - "[[IV-Crush-Mechanics]]"
  - "[[Earnings-IC-Playbook]]"
  - "[[Earnings-Tools]]"
---

# Earnings Options Trading — Overview

Earnings announcements create a predictable, repeatable volatility cycle that options traders can exploit. The core opportunity does not depend on predicting whether a company beats or misses — it depends on understanding how **implied volatility behaves around the event itself**.

## The Core Insight: IV Accumulation and Crush

In the days leading up to an earnings release, market makers inflate options premiums to reflect the uncertainty of the binary event. This is called **IV accumulation**. Once earnings are reported — typically before market open or after the close — the uncertainty resolves and IV collapses rapidly back toward its baseline. This collapse is [[IV-Crush-Mechanics|IV crush]].

![[chart-earnings-iv-crush.png]]

The crush is mechanical and nearly universal. It does not require the stock to move in any particular direction. A stock that gaps up 8% on strong earnings will still see its options IV drop sharply the morning after — the event is over, the uncertainty is gone.

> [!note]
> IV crush is largest in single-name stocks where earnings are the dominant event driver. Index options (SPX, QQQ) crush far less because no single earnings report dominates the index.

## The Data-Driven Edge

Backtests across liquid underlyings (S&P 500 constituents, 2010–2023) consistently show that the **implied earnings move overstates the actual move roughly 60% of the time**. The implied move is typically derived from the at-the-money straddle price as a percentage of the stock price. When actual moves are smaller than implied moves, premium sellers profit.

This overstatement is not random noise — it reflects a structural premium that market makers charge for warehousing binary risk. It is the foundational reason premium-selling around earnings has a positive expected value over large sample sizes.

> [!warning]
> The 60% figure is a historical average across diversified samples. For any single stock in any single quarter, the outcome is binary. Catastrophic gaps — 20%, 30%, or more — do occur and can cause outsized losses that dwarf many winning trades.

## Two Core Approaches

### 1. Sell Premium (Capture IV Crush)

Enter a **short premium** position 1–5 days before earnings. The position profits if the post-earnings move is smaller than the options predicted. Common structures:

- **Iron Condor (IC)**: defined-risk short strangle with wings. Best for high-IV, liquid tickers where you want capped downside. See [[Earnings-IC-Playbook]].
- **Short Strangle**: undefined-risk, higher credit, requires sufficient margin and risk tolerance.

Exit the morning after earnings at open, once IV crush has fully repriced the options.

> [!danger]
> Naked short strangles around earnings carry undefined downside. A stock that gaps 3× the expected move can generate losses that exceed weeks or months of premium collected. This structure is unsuitable for undercapitalized accounts or beginners.

### 2. Buy Premium (Bet on a Larger-Than-Expected Move)

Enter a **long premium** position — typically an ATM straddle or a debit spread — when you believe the market is underpricing the likely move. This is the less common approach, appropriate when:

- The implied move is historically low relative to past earnings moves for that ticker
- A catalyst (sector disruption, guidance pre-announcement, macro regime shift) suggests unusual volatility

> [!tip]
> Long straddles into earnings have negative expected value on average due to IV overpricing. Use them selectively, only when historical move analysis shows the stock consistently gaps beyond its implied move — see [[Earnings-Ticker-Selection]] for the screening process.

## Strategy Selection Framework

| Condition | Structure |
|---|---|
| Implied move > median historical move | Sell IC or strangle |
| Implied move < median historical move | Buy straddle or debit spread |
| High IV rank (>70), liquid ticker | Sell IC (defined risk) |
| Uncertain directional bias | Sell symmetric strangle |
| Strong directional conviction + cheap vol | Buy debit spread |

## Timing

- **Entry**: 1–5 days before earnings. Entering earlier captures more IV accumulation but adds time-decay and pre-earnings price drift risk.
- **Exit**: Next morning at open, after the IV crush has priced in. Holding beyond that converts the trade from a vol event into a directional bet.

Use [[Earnings-Tools]] to identify upcoming earnings dates, screen for implied-vs-historical move ratios, and filter for liquidity.
