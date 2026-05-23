---
title: Bear Call Credit Spread
tags:
  - strategy
  - defined-risk
  - credit-spread
  - bearish
  - income
aliases:
  - Bear Call Spread
  - Call Credit Spread
  - Short Call Vertical
status: draft
related:
  - "[[Bull-Put-Spread]]"
  - "[[Iron-Condor]]"
  - "[[Rolling-Credit-Spreads]]"
  - "[[IV-Rank]]"
---

# Bear Call Credit Spread

A bear call credit spread is a two-leg, defined-risk options strategy that collects premium by expressing a bearish-to-neutral view on the underlying. You sell a call at a lower strike and simultaneously buy a higher-strike call at the same expiration, receiving a net credit. Both maximum profit and maximum loss are fixed at trade entry.

> [!note]
> This is the call-side mirror image of a [[Bull-Put-Spread]]. Combining both on the same underlying and expiry — a bear call above the market and a bull put below it — produces an [[Iron-Condor]].

## Structure

| Leg | Action | Strike | Role |
|-----|--------|--------|------|
| Short call | Sell | Lower (closer to ATM) | Credit leg — defines the directional exposure |
| Long call | Buy | Higher (further OTM) | Hedge leg — caps maximum loss |

Both legs share the same expiration. The spread width is the difference between the two strikes. The short call is OTM at entry; the position profits if the underlying stays below the short strike through expiry.

## Entry Criteria

Parameters are informed by TastyTrade mechanical backtest data on SPX and liquid ETFs (rule-of-thumb ranges, not a guarantee):

- **Delta of short call:** 0.25–0.35 (approximately 1–2 standard deviations OTM)
- **Spread width:** 5–10 points for SPX; scaled to underlying price for other assets
- **Days to expiration (DTE):** 21–45 DTE — sits in the zone where [[theta]] decay accelerates without excessive gamma risk
- **[[IV-Rank]]:** above 40 — ensures you are selling inflated premium relative to the past year's range

> [!tip]
> Align the short strike with a recognizable technical resistance level on the chart. Selling calls at a price where sellers have historically capped rallies gives the trade a dual justification: statistical edge from premium and structural market context.

## Reward and Risk

Given a $50-wide spread with $15 net credit received:

| Metric | Formula | Example |
|--------|---------|---------|
| Max profit | Net credit received | $15 per share ($1,500/contract) |
| Max loss | Spread width - credit | $35 per share ($3,500/contract) |
| Breakeven at expiry | Short strike + net credit | 5150 + 15 = **5165** |
| Credit as % of width | Credit / width | 30% — within the 25–33% target |

A credit of 25–33% of spread width is the practical target. Below 20% the risk/reward is poor; above 33% often means the short strike is too close to the money and probability of profit is insufficient.

## Concrete Example: SPX

SPX is trading at 5000. IV Rank is 52. You identify 5150 as a prior swing high and known resistance level.

- **Sell** SPX 5150 call (approx. 0.30 delta), 35 DTE
- **Buy** SPX 5200 call, same expiry
- **Net credit received:** $15 ($1,500/contract)
- **Spread width:** $50 ($5,000/contract)
- **Max profit:** $1,500 — achieved if SPX closes below 5150 at expiry
- **Max loss:** $3,500 — achieved if SPX closes at or above 5200 at expiry
- **Breakeven:** 5165

![[pnl-bear-call-spread.png]]

## Trade Management

Rules are supported by TastyTrade mechanical backtest data showing that early profit-taking and a fixed loss multiple outperform holding to expiry in aggregate (data-backed, not infallible):

- **Take profit** at 50% of max profit — close the spread when the credit has decayed by half. In the example above, buy back the spread when it is worth $7.50. Frees capital and eliminates remaining gamma risk.
- **Stop loss** at 200% of credit received — if the spread has moved against you by 2x the premium collected, exit. In the example above, exit when the spread is worth $30 (a $15 loss on $15 credit collected, netting a $15 debit to close).
- **Expiry management:** Never hold through expiration with a short naked call risk. If you cannot close at your target before expiry, close by 21 DTE regardless.

> [!tip]
> For [[Rolling-Credit-Spreads]], a tested alternative to stopping out is rolling the spread up and out to a later expiry for a net credit. Only do this if the underlying thesis is intact and the new short strike remains above a meaningful resistance level.

## Combining into an Iron Condor

Pairing a bear call spread above the market with a [[Bull-Put-Spread]] below it — same underlying, same expiry — creates an [[Iron-Condor]]. The structure doubles the credit but narrows the profit zone; manage each wing independently if one side is tested.

## Common Mistakes

1. **Selling too close to ATM for yield:** A 0.40-delta short call collects more credit but has a far higher probability of closing in the money. Stay at 0.25–0.35.
2. **Ignoring IV Rank:** Selling calls when [[IV-Rank]] is below 25 means collecting thin premium relative to the risk; any sustained rally overwhelms the edge.
3. **Forgetting assignment risk:** SPX options are cash-settled (European exercise), but equity options carry early assignment risk on short calls — especially around ex-dividend dates. Know your underlying.
4. **No exit plan:** Holding a losing spread hoping for a reversal is the primary way defined-risk trades produce maximum losses.

> [!warning]
> Although maximum loss is defined, it is still 2–3x the credit received in a standard setup. A single max-loss trade wipes out the profits from two to three winning trades. Position size so that a max-loss event is a manageable drawdown, not an account-threatening event.

> [!danger]
> Bear call spreads that are rolled repeatedly on an underlying in a strong uptrend can accumulate losses far exceeding the original risk if each roll is placed for a net credit but the underlying continues higher. Rolling is an adjustment tool, not a rescue mechanism — re-evaluate the thesis before each roll.
