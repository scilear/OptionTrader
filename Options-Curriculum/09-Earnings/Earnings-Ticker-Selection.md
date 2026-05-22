---
title: Earnings Ticker Selection
tags: [earnings, screening, volatility, IV-crush, liquidity]
aliases: [Earnings Stock Selection, Earnings Screener]
status: draft
related:
  - "[[Earnings-Overview]]"
  - "[[Earnings-Tools]]"
  - "[[Earnings-IC-Playbook]]"
---

# Earnings Ticker Selection

Not every earnings event is worth trading. The edge in earnings options comes from identifying stocks where [[Implied Volatility]] is systematically overpriced relative to subsequent realized moves. Before placing a trade, run each candidate through the four filters below.

---

## Filter 1 — Historical IV Crush Rate

The primary edge in short-volatility earnings plays (straddle sells, [[Iron Condor]], etc.) is that the market tends to price in a larger move than actually occurs.

- Use **Market Chameleon** or **Earnings Whispers** to pull each ticker's historical earnings move data.
- Calculate the percentage of past earnings where `actual move < implied move` at close of the earnings day.
- **Target threshold**: ≥ 60% of historical earnings show IV overestimation.

> [!note]
> This ratio is sometimes called the "IV crush hit rate." A reading of 70% means the stock moved less than implied in 7 of the last 10 earnings events — a statistically meaningful edge, though not a guarantee.

> [!warning]
> Past IV crush rates do not guarantee future performance. A single gap through the implied range can erase multiple cycles of premium collected. Always size positions to survive the outlier.

A useful secondary check: compare the **average implied move** against the **average actual move** across the last eight quarters. A ratio above 1.3x (implied 30% larger than actual) is a strong signal.

---

## Filter 2 — Liquidity

> [!danger]
> Earnings plays on illiquid underlyings are unsuitable for most traders. Wide bid-ask spreads on the options make entry and exit extremely costly, and slippage alone can eliminate any edge.

Minimum liquidity requirements before trading earnings:

- **Options volume**: must show a clear pre-earnings volume spike (visible on [[Earnings-Tools]] platforms like Market Chameleon's "Options Volume" tab).
- **ATM bid-ask spread**: ≤ $0.05 on the nearest-expiry ATM strike at entry. If the spread is $0.10 or wider, skip the trade.
- **Open interest**: at least several thousand contracts across the front expiry.

Mega-cap names routinely pass this filter. Smaller-cap names often fail it even when the IV crush rate looks attractive.

---

## Filter 3 — Implied Move Size

The size of the expected move determines which structures are practical:

| Implied Move | Assessment |
|---|---|
| < 3% | Too small — premium too thin to justify the binary risk |
| 3–4% | Marginal — works only with very tight structures |
| **4–10%** | **Ideal range for short-vol strategies** |
| 10–15% | Elevated risk; widen wings, reduce size |
| > 15% | Avoid — move size indicates event or sector risk |

> [!tip]
> For [[Iron Condor]] trades, an implied move of 5–8% tends to offer the best balance between wing premium and the probability that both short strikes expire worthless. Source: rule of thumb from earnings vol traders; not formally backtested in this system.

---

## Filter 4 — Avoid Binary Event Risk

Skip any ticker where the earnings report coincides with, or is likely to trigger, a binary non-earnings outcome:

- **Biotech / Pharma**: drug approval decisions, Phase 3 readouts, FDA action dates.
- **Clinical trial updates** embedded in the earnings call.
- **Regulatory or legal outcomes** expected around the earnings date.

These events produce fat-tailed return distributions that are structurally different from normal earnings vol. Short-vol strategies assume a roughly log-normal distribution — binary events violate that assumption.

---

## Best Candidates

Based on the four filters above, the most consistent earnings vol opportunities come from:

- **Mega-cap tech**: AAPL, MSFT, NVDA, META, GOOGL, AMZN — high liquidity, well-studied IV crush patterns, implied moves typically in the 4–10% range.
- **Large financials**: JPM, GS — report quarterly with transparent catalysts and liquid options markets.
- **Liquid reporting ETFs**: XLP and similar sector ETFs that file earnings-adjacent reports.

---

## Screening Workflow (Market Chameleon)

1. Navigate to **Market Chameleon → Earnings → Earnings Screener**.
2. Filter by upcoming earnings date (next 1–2 weeks).
3. Sort by **"Expected Move vs Historical Move"** — look for tickers where the historical actual move is consistently below implied.
4. Apply the **IV crush hit rate filter** (≥ 60%).
5. Click through to each ticker's **Options Volume** chart to confirm the pre-earnings liquidity spike.
6. Check the ATM straddle bid-ask on the nearest expiry to verify the ≤ $0.05 spread requirement.
7. Cross-reference against the implied move size filter (4–10% sweet spot).
8. Remove any biotech or binary-event names from the shortlist.

The surviving tickers are the candidates. From there, choose a structure based on regime and skew — see [[Earnings-IC-Playbook]] for execution.

---

## Related Notes

- [[Earnings-Overview]] — framework and vocabulary
- [[Earnings-Tools]] — platform guide for Market Chameleon, Earnings Whispers, and others
- [[Earnings-IC-Playbook]] — iron condor structure and sizing for qualifying tickers
