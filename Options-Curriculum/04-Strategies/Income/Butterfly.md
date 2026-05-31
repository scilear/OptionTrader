---
title: Butterfly Spread
tags:
  - income
  - defined-risk
  - debit-spread
  - directional
  - low-iv
aliases:
  - fly
  - long-fly
  - call-butterfly
  - put-butterfly
status: draft
related:
  - "[[Iron-Fly]]"
  - "[[Iron-Condor]]"
  - "[[Fly-vs-IC]]"
  - "[[Broken-Wing-Butterfly]]"
  - "[[Theta-Decay]]"
  - "[[Delta-Neutral]]"
---

# Butterfly Spread

A butterfly spread is a four-leg, defined-risk, debit trade that targets a single price pin at expiry. The structure earns its maximum profit when the underlying closes exactly at the middle (body) strike on expiration day. It is the most capital-efficient way to express a precise price target — whether bullish, bearish, or neutral.

**Core structure (call version):**
- **Buy** 1 lower-strike call (left wing)
- **Sell** 2 middle-strike calls (body)
- **Buy** 1 higher-strike call (right wing)
- All legs share the same expiry. Wings are equidistant from the body in the standard version.

**Put version** uses the identical wing layout with puts. Because of [[Put-Call-Parity]], a symmetric call fly and put fly on the same strikes produce nearly identical P&L profiles. The choice of calls vs. puts affects margin treatment and sometimes bid/ask friction, not the fundamental exposure.

![[pnl-butterfly.png]]

---

## Risk Profile

| Metric | Value |
|---|---|
| Max profit | Wing width − debit paid |
| Max loss | Debit paid (capped, occurs if stock moves beyond either wing at expiry) |
| Breakeven (low) | Lower strike + debit |
| Breakeven (high) | Upper strike − debit |
| Net Greeks at open | Near delta-neutral, long gamma at wings, short gamma at body |

> [!warning]
> Maximum loss equals the full debit paid. While the loss is capped and often small in dollar terms, losing 100% of the position cost is routine when the underlying moves away from the body strike. Size positions so a full loss is acceptable.

---

## Variations

### 1. Long Call Butterfly — Bullish Target

Place the body strike at or slightly above current price, at a resistance level or at a measured-move target. You profit if the stock rallies into the strike and stalls. Suitable when you expect a moderate, contained move up.

### 2. Long Put Butterfly — Bearish Target

Place the body strike at or slightly below current price, typically at support (where you expect the stock to find a floor and pin). Profits if the stock drifts down and stalls at that level.

### 3. Broken-Wing Butterfly (Skewed Fly)

One wing is wider than the other, creating an asymmetric structure. For a bullish broken-wing:
- Lower wing is narrower than the upper wing.
- This reduces or eliminates the debit, sometimes creating a small credit at entry.
- Max loss shifts: one side is now larger. The trade is no longer perfectly symmetric.
- Commonly used when you want to "finance" the fly by accepting more risk on the side you consider less likely.

See [[Broken-Wing-Butterfly]] for full treatment of skew and entry mechanics.

> [!tip]
> Broken-wing butterflies entered for a net credit have no loss on one side at expiry. This makes them attractive as a directional income structure — but the wider wing's risk must still be sized responsibly.

---

## Entry Guidelines

These are practitioner rules of thumb, not statistically validated optimal parameters. Treat them as starting defaults to test against your own data.

- **DTE:** 21–35 days. Short enough for theta to accelerate; long enough for the stock to reach the target.
- **Body strike placement:** Put the middle strike at your price target — resistance for a bearish fly, support for a bullish fly, or the at-the-money strike for a neutral play.
- **Cost target:** Aim to pay 20–30% of the wing width. Example: if wings are $5 wide, target a debit of $1.00–$1.50. Overpaying compresses the risk/reward significantly.
- **IV environment:** Butterflies are a [[Debit-Spread]] and therefore perform best when [[Implied-Volatility]] is low or contracting. High IV inflates the debit and makes the position harder to fill at attractive levels. This is a structural advantage over [[Iron-Condor]] and [[Iron-Fly]], which require elevated IV to collect meaningful credit.

> [!note]
> The butterfly is sometimes described as "long vol at the wings, short vol at the body." In practice, for short-DTE income flies, the dominant driver is delta (price pinning), not vega. Do not rely on this trade to profit from a volatility expansion.

---

## Trade Management

- **Profit target:** Close the position when it reaches **100% return on debit** (i.e., the position value doubles). This is a rule of thumb; capturing 50–75% of max profit is more realistic and reduces pin risk.
- **Time stop:** Close with **7 DTE remaining** regardless of P&L. Inside the final week, gamma risk around the body strike spikes sharply — a small adverse move can turn a winning trade into a full loser very quickly.
- **Loss management:** Because max loss is the debit, many traders simply let losers expire. However, closing at 50–100% of the debit paid (i.e., losing half to all of what you paid) can free capital for better setups.

> [!danger]
> Do not hold a butterfly into expiration hoping for a perfect pin. [[Pin-Risk]] is real: if the underlying closes within cents of the short body strike, your long and short options may settle differently depending on after-hours moves, especially on index products with cash settlement. Closing at 7 DTE eliminates this ambiguity.

---

## Butterfly vs. Iron Condor

| Attribute | Butterfly | [[Iron-Condor]] |
|---|---|---|
| Risk type | Debit (loss = debit paid) | Credit (loss = wing width − credit) |
| IV preference | Low IV | High IV |
| Profit condition | Pin at body strike | Stay inside a wide range |
| Directionality | Targeted | Neutral |
| Margin requirement | Debit only | Wing width − credit |

The butterfly is the better tool when you have a specific price target and are operating in a low-IV environment. The IC is better for neutral, high-IV environments where you want a wide profit zone. See [[Fly-vs-IC]] for a detailed comparison and regime-based selection framework.

---

## Related Notes

- [[Iron-Fly]] — The credit spread equivalent: sell the body, buy the wings. Net credit instead of debit.
- [[Iron-Condor]] — Wider profit zone, credit structure, neutral bias.
- [[Fly-vs-IC]] — Side-by-side comparison with regime guidance.
- [[Broken-Wing-Butterfly]] — Asymmetric version, often entered for a credit.
- [[Theta-Decay]] — How theta decay accelerates into expiry for the body short legs.
