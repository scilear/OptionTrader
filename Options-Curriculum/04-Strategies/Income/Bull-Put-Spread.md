---
title: Bull Put Credit Spread
tags:
  - strategy
  - defined-risk
  - credit-spread
  - bullish
  - income
aliases:
  - Bull Put Spread
  - Put Credit Spread
  - Short Put Vertical
status: draft
related:
  - "[[Bear-Call-Spread]]"
  - "[[Iron-Condor]]"
  - "[[Rolling-Credit-Spreads]]"
  - "[[IV-Rank]]"
---

# Bull Put Credit Spread

A bull put credit spread is a two-leg, defined-risk options strategy that collects premium by expressing a bullish-to-neutral view on the underlying. You sell a put at a higher strike and simultaneously buy a lower-strike put at the same expiration, receiving a net credit. Maximum profit and maximum loss are both capped at trade entry.

> [!note]
> This is the put-side mirror image of a [[Bear-Call-Spread]]. Combining both on the same underlying and expiry produces an [[Iron-Condor]].

## Structure

| Leg | Action | Strike | Role |
|-----|--------|--------|------|
| Short put | Sell | Higher (closer to ATM) | Credit leg — defines the directional exposure |
| Long put | Buy | Lower (further OTM) | Hedge leg — caps maximum loss |

Both legs share the same expiration. The spread width is the difference between the two strikes.

## Entry Criteria

These parameters are informed by mechanical backtest data from TastyTrade research on SPX and liquid ETF underlyings (rule-of-thumb ranges, not a guarantee):

- **Delta of short put:** 0.25–0.35 (approximately 1–2 standard deviations OTM)
- **Spread width:** 5–10 points for SPX; scaled to underlying price for other assets
- **Days to expiration (DTE):** 21–45 DTE — sits in the zone where [[theta]] decay accelerates without excessive gamma risk
- **[[IV-Rank]]:** above 40 — ensures you are selling inflated premium relative to the past year's range

> [!tip]
> Align the short strike with a recognizable technical support level on the chart. Selling at a price where buyers have historically stepped in gives the trade a dual justification: statistical edge from premium and structural market context.

## Reward and Risk

Given a $50-wide spread with $15 net credit received:

| Metric | Formula | Example |
|--------|---------|---------|
| Max profit | Net credit received | $15 per share ($1,500/contract) |
| Max loss | Spread width - credit | $35 per share ($3,500/contract) |
| Breakeven at expiry | Short strike - net credit | 4850 - 15 = **4835** |
| Credit as % of width | Credit / width | 30% — within the 25–33% target |

A credit of 25–33% of spread width is the practical target. Below 20% the risk/reward is poor; above 33% often means the short strike is too close to the money.

## Concrete Example: SPX

SPX is trading at 5000. IV Rank is 52. You identify 4850 as a prior swing low (technical support).

- **Sell** SPX 4850 put (approx. 0.30 delta), 35 DTE
- **Buy** SPX 4800 put, same expiry
- **Net credit received:** $15 ($1,500/contract)
- **Spread width:** $50 ($5,000/contract)
- **Max profit:** $1,500 — achieved if SPX closes above 4850 at expiry
- **Max loss:** $3,500 — achieved if SPX closes at or below 4800 at expiry
- **Breakeven:** 4835

![[pnl-bull-put-spread.png]]

## Trade Management

These rules are supported by TastyTrade mechanical backtest data showing that taking profits early and cutting losses at a fixed multiple outperforms holding to expiry in aggregate (data-backed, not infallible):

- **Take profit** at 50% of max profit — close the spread when the credit has decayed by half. Frees capital and eliminates remaining gamma risk.
- **Stop loss** at 200% of credit received — if the spread has moved against you by 2x the premium collected, exit. In the example above, exit when the spread is worth $30 (a $15 loss on $15 credit collected, netting a $15 debit to close).
- **Expiry management:** Never hold through expiration with a short naked put risk. If you cannot close at your target before expiry, close by 21 DTE regardless.

> [!tip]
> For [[Rolling-Credit-Spreads]], a tested alternative to stopping out is rolling the spread down and out to a later expiry for a net credit. Only do this if the underlying thesis is intact and the new position is still outside your original breakeven.

## Variations and Related Strategies

- Add a [[Bear-Call-Spread]] above the market to build an [[Iron-Condor]] — doubles the credit but adds upside risk
- Narrowing the spread width reduces both max profit and max loss; widening it does the opposite — adjust to match your conviction and account size
- See [[Rolling-Credit-Spreads]] for adjustment mechanics when the trade goes against you

## Common Mistakes

1. **Selling too close to ATM for yield:** A 0.40-delta short put collects more credit but has a much higher probability of closing in the money. Stay at 0.25–0.35.
2. **Ignoring IV Rank:** Selling puts when [[IV-Rank]] is below 25 means you are collecting thin premium relative to the risk; a spike in realized vol rapidly overwhelms the edge.
3. **No exit plan:** Holding a losing spread hoping for recovery is the primary way defined-risk trades produce maximum losses.

> [!warning]
> Although maximum loss is defined, it is still 2–3x the credit received in a standard setup. A single max-loss trade wipes out the profits from two to three winning trades. Position size so that a max-loss event is a manageable drawdown, not an account-threatening event.
