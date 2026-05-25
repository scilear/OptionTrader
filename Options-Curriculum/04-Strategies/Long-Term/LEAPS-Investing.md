---
title: LEAPS as a Long-Term Investing Tool
tags:
  - strategy
  - LEAPS
  - directional
  - long-term
  - stock-replacement
aliases:
  - LEAPS Investing
  - LEAPS Stock Replacement
status: draft
related:
  - "[[LEAPS]]"
  - "[[PMCC]]"
  - "[[PMCC-Income]]"
  - "[[Zero-Risk-Collar]]"
---

# LEAPS as a Long-Term Investing Tool

[[LEAPS]] (Long-term Equity AnticiPation Securities) are options contracts with expirations of at least one year. Used as a directional investing tool — not for income generation via [[PMCC]] — they let you build long-term bullish exposure in a high-conviction stock or ETF while committing materially less capital than an outright stock purchase.

> [!warning]
> LEAPS are leveraged instruments. If the underlying drops significantly or moves sideways for long enough, you can lose your entire premium — a loss that would not occur in an equivalent stock position. Defined max loss is a feature, not a safety guarantee.

---

## 1. LEAPS as Stock Replacement

Buying a deep in-the-money call LEAPS replicates most of the economic behavior of holding 100 shares, at roughly 70–80% of the capital required.

**Why it works:** A 70–80 delta call moves approximately $0.70–$0.80 for every $1.00 move in the stock. You capture most of the upside, carry defined downside (max loss = premium paid), and free up the remaining capital.

**Example (rule-of-thumb, not live data):** If a stock trades at $200 and the 1.5-year $160 call (deep ITM) costs $52, you control 100 shares for $5,200 instead of $20,000. That is ~26% of the capital for ~75 delta of exposure — capital efficiency with capped downside.

![[chart-leaps-vs-stock.png]]

> [!note]
> The comparison versus stock only holds cleanly if you are not collecting dividends. If the underlying pays a significant dividend, the stock position gains an income stream the LEAPS does not replicate. Factor this into your thesis.

---

## 2. How to Size: Equivalent Stock Exposure

One LEAPS contract = 100 shares of delta exposure at your chosen delta level.

**Sizing formula:**

```
Equivalent shares = number of contracts × 100 × delta
```

If you buy 2 contracts at 0.75 delta, you have the equivalent of 150 shares of directional exposure. To replicate a 200-share stock position, buy 3 contracts at ~0.67 delta or 2 contracts at ~0.80 delta — and accept the difference in leverage profile.

> [!tip]
> Size your LEAPS to match the *dollar* risk of the position, not the share count. Compute the max loss (total premium paid) and ask whether you accept losing that amount fully. If the answer is no, reduce contracts.

---

## 3. Strike Selection

| Strike | Delta | Character |
|--------|-------|-----------|
| Deep ITM (e.g., 85–90% moneyness) | 0.75–0.85 | Stock-like behavior; lower leverage; higher premium |
| Moderate ITM | 0.65–0.75 | Balanced; recommended starting point |
| ATM | ~0.50 | Cheaper entry; higher leverage; more theta drag |

**Deep ITM (70–80 delta) is the standard stock-replacement approach.** The option has high intrinsic value, low extrinsic value, and behaves like a stock for small price moves. ATM LEAPS are cheaper but you are buying mostly time value, making you more exposed to theta decay and requiring a stronger directional move to profit.

---

## 4. DTE: Buy 1.5–2 Years Out

Buy LEAPS with 18–24 months to expiration. This serves two purposes:

1. **Thesis runway** — Long-term conviction plays need time. A 6-month option punishes you for slow movers. 18–24 months gives the thesis room to develop.
2. **Theta drag is lower** — Theta decay is not linear. It accelerates in the final 60–90 days. At 18+ months, daily theta on a deep ITM LEAPS is small relative to the position size. This is data-backed behavior from the Black-Scholes model; theta scales roughly with 1/√T.

> [!tip]
> Avoid buying LEAPS inside 12 months. At that point the "long-term" premium has eroded and you are back in a regime where theta drag becomes a meaningful daily headwind.

---

## 5. Exit Planning: Roll When 6–9 Months Remain

Do not hold to expiration. When your LEAPS reaches approximately 6–9 months to expiry:

- **Roll forward** — sell the existing position and buy a new LEAPS at 18–24 months out in the same (or adjusted) strike.
- **Reassess the thesis** — rolling costs money (you are buying more extrinsic value). If conviction has faded, close rather than roll.

Rolling preserves your directional exposure and restarts the clock on theta favorability. The cost of the roll is the net debit — treat it as a carrying cost of the position.

---

## 6. Best Tickers for LEAPS Investing

LEAPS work best on:

- **High-conviction, high-liquidity single stocks** where you have a specific multi-year thesis (earnings growth, product cycle, market share expansion).
- **Broad ETFs** (SPY, QQQ, IWM) for index-level bullish exposure with capital efficiency.
- **Sector ETFs** for a thematic macro bet with defined risk.

Avoid LEAPS on low-liquidity names (wide bid-ask spreads destroy your edge) and on stocks with near-term binary events (earnings, FDA decisions) unless you specifically want that exposure.

---

## 7. Tax Treatment

> [!note]
> This is a general rule of thumb, not tax advice. Consult a tax professional for your specific situation.

LEAPS held as long options (you buy and hold the call, never sell it short as part of a spread) and **held for more than 12 months** qualify for long-term capital gains tax rates upon sale in the US. This is a meaningful advantage over short-term options plays taxed as ordinary income.

**Caution:** If you use the LEAPS as the long leg of a [[PMCC]] (selling short calls against it), the tax treatment changes — the covered call activity can reset or complicate the holding period. See [[PMCC-Income]] for that structure. If you want purely directional long-term exposure with LTCG treatment, keep the LEAPS uncovered.

A [[Zero-Risk-Collar]] layered on top of a LEAPS position can reduce downside but may also affect the holding period — verify with a tax advisor before structuring.

---

## Summary

| Parameter | Recommended Setting |
|-----------|-------------------|
| Delta | 0.70–0.80 (deep ITM) |
| DTE at entry | 18–24 months |
| Roll trigger | 6–9 months remaining |
| Max loss | Full premium paid |
| Tax advantage | LTCG if held > 12 months, uncovered |

LEAPS investing is a capital-efficient, defined-risk alternative to stock ownership — appropriate for long-horizon, high-conviction positions where you want to participate in appreciation without committing full share capital.
