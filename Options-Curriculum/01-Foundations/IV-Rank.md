---
title: IV Rank
tags:
  - foundations
  - volatility
  - screening
  - premium-selling
aliases:
  - IVR
  - IV Rank
status: draft
related:
  - "[[IV-Percentile]]"
  - "[[IV-vs-HV]]"
  - "[[Screener-Setup]]"
  - "[[High-IV-Playbook]]"
---

# IV Rank (IVR)

IV Rank is a normalized measure that tells you where current [[IV|implied volatility]] sits relative to its own 52-week range. It answers a practical question: *is IV high or low right now compared to its recent history for this specific underlying?*

![[chart-ivr-distribution.png]]

## Formula

$$
\text{IVR} = \frac{\text{Current IV} - \text{52w Low IV}}{\text{52w High IV} - \text{52w Low IV}} \times 100
$$

**Example:** If SPY's 30-day IV is currently 22%, its 52-week low was 12%, and its 52-week high was 45%, then:

$$
\text{IVR} = \frac{22 - 12}{45 - 12} \times 100 \approx 30
$$

IVR of 30 means current IV is in the bottom third of its annual range — relatively depressed.

> [!note] The "IV" in the formula is typically the 30-day at-the-money implied volatility, sometimes called VIX-style implied vol for individual underlyings. Different platforms may use slightly different tenor conventions, so compare IVR values only within the same platform.

## Interpreting the 0–100 Scale

| IVR Range | Market Condition | Preferred Strategy Type |
|-----------|-----------------|------------------------|
| 0–30 | Depressed IV | Avoid selling premium; consider long vol or debit spreads |
| 30–50 | Neutral / transitional | Selective — favor defined-risk structures |
| 50–75 | Elevated IV | Core premium-selling zone: short strangles, iron condors, cash-secured puts |
| 75–100 | Historically high IV | Aggressive premium collection; but verify the *reason* for the spike |

> [!warning] High IVR does not mean IV cannot go higher. Earnings surprises, macro shocks, or liquidity crises can push IV well above its prior 52-week high, rendering the IVR calculation meaningless until the range updates. Selling premium into a volatility spike without understanding the catalyst is a common source of large, rapid losses.

### Practical Thresholds (Rule of Thumb)

- **IVR > 50** — IV is elevated relative to recent history. This is the primary trigger for premium-selling strategies in the [[High-IV-Playbook]]. The edge in selling options comes from IV mean-reversion; elevated IVR is a precondition, not a guarantee.
- **IVR < 30** — IV is depressed. Selling premium here typically offers poor credit for the risk taken. Consider debit spreads or long [[Vega|vega]] plays, or simply wait for a better entry.

> [!tip] Many experienced premium sellers — including the tastytrade research team — use IVR > 50 as a hard filter before entering any undefined-risk short-vol position. This is data-backed: their published studies show higher average P&L and better win rates for trades entered above that threshold.

## IV Rank vs IV Percentile

IVR and [[IV-Percentile]] are often confused but measure different things:

- **IVR** uses only the 52-week high and low — two data points. One outlier spike can compress the entire scale.
- **IV Percentile** counts the percentage of *days* in the past year where IV was *below* the current level. It uses all 252 trading days and is more robust to single-day outliers.

A stock can have IVR of 40 and IV Percentile of 70 if there was one brief volatility spike during the year that set a high-water mark. For screening, [[IV-Percentile]] is often the more stable metric; IVR is faster to calculate and widely available.

## Where to Find IVR

| Platform | Location |
|----------|----------|
| thinkorswim (TOS) | Market Watch → Quote columns → add "IVR" or "IV Rank" |
| Barchart | Options page for any ticker → Implied Volatility section |
| Market Chameleon | Ticker page → Volatility → IV Rank table |
| tastytrade | Watchlist columns or the stock's volatility page |

For building a systematic screener using IVR thresholds, see [[Screener-Setup]].

## Relationship to Historical Volatility

IVR tells you where IV is relative to *itself* historically — not relative to realized moves. A stock with IVR of 80 could still have IV below its [[IV-vs-HV|historical volatility (HV)]], meaning options are not necessarily overpriced in an absolute sense. Always cross-check IVR with the IV/HV ratio to confirm the volatility premium exists before selling.
