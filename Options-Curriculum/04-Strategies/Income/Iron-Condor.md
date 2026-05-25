---
title: Iron Condor
tags:
  - income
  - defined-risk
  - premium-selling
  - neutral
  - SPX
aliases:
  - IC
  - short-condor
status: draft
related:
  - "[[Bull-Put-Spread]]"
  - "[[Bear-Call-Spread]]"
  - "[[Rolling-Iron-Condors]]"
  - "[[Market-Condition-Classification]]"
  - "[[Adjust-vs-Close]]"
---

# Iron Condor

An Iron Condor (IC) is a four-leg, defined-risk, market-neutral premium-selling strategy. You simultaneously sell a [[Bull-Put-Spread]] below the market and a [[Bear-Call-Spread]] above the market on the same underlying and the same expiry. The structure creates a profit zone bounded by the two short strikes, and the wings cap your maximum loss on either side.

**Structure summary:**
- **Buy** 1 far-OTM put (lower wing)
- **Sell** 1 OTM put (short put strike)
- **Sell** 1 OTM call (short call strike)
- **Buy** 1 far-OTM call (upper wing)

All four legs share the same expiry. The net result is a credit received upfront, which is your maximum profit.

![[pnl-iron-condor.png]]

---

## When to Use an Iron Condor

The IC earns its keep when the underlying grinds sideways inside a range. Three conditions should align before entry:

1. **IV Rank > 50** — you are selling elevated implied volatility. Below IVR 50 the credit is thin and the edge deteriorates quickly. This is data-backed: elevated IVR meaningfully predicts IV mean reversion (Cboe research on VIX seasonality, various sell-vol backtests). See [[Market-Condition-Classification]] for how to measure IVR systematically.
2. **Range-bound price action** — no strong trending structure on the daily chart. Trending markets increase the probability that one side is tested before expiry.
3. **No known catalysts inside the trade window** — earnings, FOMC, CPI, or major macro events within the DTE window can gap price through a wing. Check the economic calendar before every entry. Rule of thumb: avoid holding through a binary event unless the credit specifically prices that event.

> [!warning]
> An IC profits in approximately 68% of cases mathematically, but a single black swan — a gap open, an emergency Fed cut, a geopolitical shock — can wipe out multiple wins in one trade. Always use defined risk (buy the wings). Never sell naked strangles as a substitute.

---

## Entry Rules

| Parameter | Guideline |
|---|---|
| Short strike delta | 0.16 – 0.25 (1.0 SD to 1.3 SD from spot) |
| Wing width (SPX) | 50 points per side |
| Wing width (equities) | 5 – 10% of stock price |
| DTE at entry | 21 – 45 days |
| Minimum credit | 25 – 33% of the spread width |

The **Expected Move (EM)** is your primary sizing compass. Short strikes must sit outside the 1-EM range implied by the market:

```
Expected Move = Spot × IV_ATM × √(DTE/365)
```

Many platforms quote the EM directly from the ATM straddle price (approximately ATM call + ATM put). Placing short strikes inside 1 EM defeats the probability edge of the structure.

**Minimum credit rule** (data-backed via tastytrade research): accepting less than 25% of the spread width produces a negative expected value after commissions and slippage in most market regimes. At 33%+ of width, the risk/reward becomes structurally favorable over a sample of 30+ trades.

---

## SPX Example

*Hypothetical entry — numbers are illustrative, not live quotes.*

- **Underlying:** SPX at 5 500, 30 DTE
- **IVR:** 62 (elevated — favorable)
- **Expected Move:** 5 500 × 0.165 × √(30/365) ≈ ±215 points

| Leg | Strike | Action | Premium |
|---|---|---|---|
| Long put | 5 200 | Buy | –$3.50 |
| Short put | 5 250 | Sell | +$6.50 |
| Short call | 5 750 | Sell | +$5.50 |
| Long call | 5 800 | Buy | –$2.50 |
| **Net credit** | | | **+$6.00** |

- **Spread width:** 50 points per side
- **Credit as % of width:** $6.00 / $50.00 = **12%** — *below the 25% minimum threshold*

In practice you would widen the condor or compress the wings until you collect at least $12.50 ($12.50/$50 = 25%). If the credit is not there, do not force the trade. A narrow credit means the market is not offering sufficient compensation for the risk.

At $12.50 credit:
- **Max profit:** $1 250 per condor (100× multiplier on SPX)
- **Max loss:** $3 750 per condor ($50 – $12.50 = $37.50 × 100)
- **Breakevens:** 5 237.50 on the downside / 5 762.50 on the upside

---

## Trade Management

### 1. Take Profit at 50%

Close the entire IC when the position reaches 50% of max profit. Rule of thumb (tastytrade, Karen the Supertrader methodology, multiple vendor backtests): staying in past 50% profit materially increases gamma risk without proportionate reward. At 50% profit you have captured the bulk of the theta decay while dramatically reducing pin risk and gap risk.

### 2. Roll the Untested Side (IV Drop)

If IV drops sharply after entry, the untested spread may collapse to near zero while the tested side remains elevated. Roll the profitable spread closer to the money to collect additional credit, improving your overall break-even. See [[Rolling-Iron-Condors]] for mechanical roll criteria.

> [!tip]
> Roll only when you can bring in at least $0.25 net additional credit and the new short strike is still outside the current 1-EM range. Rolling for a debit is almost always wrong.

### 3. Adjustment When Tested

When price moves toward one short strike, evaluate the position. Do not wait passively for expiry.

**Adjustment triggers** (either condition sufficient):
- Short strike delta reaches **0.30 or higher**
- Unrealized loss exceeds **1× the original credit received**

When triggered, consult [[Adjust-vs-Close]] for the decision framework. Common adjustments:
- **Close the losing spread, keep the winning spread** — converts the IC into a single vertical, reducing capital at risk.
- **Roll the tested short strike further OTM** — requires paying a debit; only valid if IV has risen enough to offer a favorable roll.
- **Add a directional hedge** (long vertical in the direction of the move) — used by experienced traders; adds complexity.

> [!danger]
> Holding an untested Iron Condor into the final week before expiry with one side deep ITM is one of the fastest ways to realize a maximum loss. Gamma accelerates sharply inside 7 DTE. If you have not already adjusted, closing at a manageable loss is almost always preferable to a max-loss outcome.

---

## Key Metrics to Track

- **Delta of each short strike** — monitor daily; flag at ±0.30
- **Net theta** — confirm the position is earning decay at entry
- **Net vega** — IC is short vega; a vega spike (VIX surge) will hurt both sides simultaneously
- **P&L vs. days held** — at 50% profit, exit regardless of DTE remaining

> [!note]
> IVR and IVP (IV Percentile) are related but distinct. IVR compares current IV to its 52-week range; IVP is a percentile rank of all historical readings. Either works for condor entry screens, but be consistent across your journal.

---

## Related Notes

- [[Bull-Put-Spread]] — the lower half of the Iron Condor
- [[Bear-Call-Spread]] — the upper half of the Iron Condor
- [[Rolling-Iron-Condors]] — mechanics of rolling legs for credit
- [[Market-Condition-Classification]] — IVR/IVP regime framework used at entry
- [[Adjust-vs-Close]] — decision framework when a short strike is tested
