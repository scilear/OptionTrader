---
title: "Superfly — 0DTE OTM Butterfly for Explosive Gamma Returns"
tags:
  - options/strategy
  - options/0DTE
  - options/butterfly
  - options/SPX
  - options/gamma
  - risk/high
aliases:
  - superfly
  - 0dte-superfly
  - otm-butterfly-0dte
status: draft
related:
  - "[[0DTE-Butterfly]]"
  - "[[0DTE-Overview]]"
  - "[[Gamma]]"
  - "[[Portfolio-Allocation]]"
---

# Superfly — 0DTE OTM Butterfly for Explosive Gamma Returns

The **Superfly** is an aggressive 0DTE directional bet that uses a tightly priced out-of-the-money butterfly spread on SPX to target 100–300% returns within minutes. It is essentially a lottery ticket structured around [[Gamma]] explosion near expiry. The trade wins rarely but wins large.

> [!danger]
> This trade expires worthless 85–95% of the time. Only use a small speculative allocation. It is **NOT** a reliable income strategy and has no place as a core position. Beginners should paper-trade this for at least three months before risking real capital.

---

## Structure

A Superfly is a standard long [[0DTE-Butterfly]] centered on an OTM strike:

- **Buy** 1 OTM call (or put) at the lower wing
- **Sell** 2 calls (or puts) at the center strike
- **Buy** 1 call (or put) at the upper wing

All legs share the same expiry (today) and the same wing width. A typical configuration on SPX:

| Parameter | Typical Value |
|---|---|
| Wing width | $25 each side ($50 total spread) |
| Distance OTM | 20–40 points from current spot |
| Net debit | $0.50–$2.00 |
| Max value at expiry | $25.00 (at center strike) |

The center strike is placed **at or just inside a key intraday support/resistance level** — the bet is that SPX will reach and settle near that level by 4:00 PM ET.

![[chart-superfly-gamma.png]]

---

## Why OTM Butterflies Explode in Value Before Expiry

Near expiry, [[Gamma]] is concentrated at the money. As SPX trends toward an OTM center strike, the delta of the inner short legs accelerates faster than the delta of the outer long legs. This differential gamma effect reprices the butterfly dramatically before the center strike is actually touched.

> [!note]
> A fly purchased for $1.00 when SPX is 35 points away from center can be worth $8–$12 when SPX is only 10 points away — before the maximum payout of $25 is ever reachable. The gamma-driven path is often more valuable than waiting for the full payout.

This is why experienced Superfly traders often **exit at 5–10× the debit paid** rather than holding for the full $25 theoretical maximum. Holding through the center strike risks a rapid collapse in value if SPX overshoots.

---

## Entry Criteria

All four conditions should be met before entering:

1. **Directional trend is established** — SPX is moving clearly toward the target level, not ranging. A confirmed break of an intraday pivot is better than a test.
2. **VIX is elevated** — higher implied volatility means wider expected moves, which raises the probability of reaching the center strike. Rule of thumb (not backtested): VIX above 18 improves odds meaningfully.
3. **Timing window: 30–60 minutes before close** — gamma is highest in the final hour, so debit is cheapest relative to expected payout. Entries earlier than 90 minutes before close reduce gamma efficiency.
4. **Clean technical level** — round numbers, prior day highs/lows, VWAP, and session open are the most reliable center-strike candidates.

> [!tip]
> If the directional move has already traveled more than half the distance to the target strike, the fly will be expensive and the edge is largely gone. The optimal entry is early in the trending move, not after a 20-point run.

---

## Cost and Payout Profile

| Scenario | Outcome |
|---|---|
| SPX misses center strike by >10 points | Expires near worthless — full debit lost |
| SPX approaches but does not reach center | Partial gamma gain — exit at 3–8× debit |
| SPX settles at center strike | Maximum payout: $25 per spread |
| SPX blows through center strike | Rapidly loses value — exit immediately |

At $1.00 debit per spread, a $25 max value represents a 25× return. In practice, traders target the 5–10× gamma pop and close before expiry.

---

## Position Sizing

The Superfly belongs in the **speculative sleeve** of a portfolio, never in the core income or hedging allocation. See [[Portfolio-Allocation]] for the full framework.

- **Hard cap: 0.25% of total portfolio per trade**
- For a $100,000 account: maximum $250 at risk per Superfly entry
- At $1.00 debit on a 25-wide fly, $250 buys 10 spreads — a notional max payout of $25,000 that almost never materializes

> [!warning]
> Sizing above 0.25% of portfolio converts a lottery ticket into a portfolio risk. A string of losses — which is the statistical norm — will cause meaningful drawdown at larger sizes. Do not increase size after wins; the base rate of loss does not improve.

---

## Exit Rules

1. **Take profit at 5–10× the debit paid** — do not hold for the $25 maximum
2. **Stop loss: full debit** — there is no stop-loss to manage; the position either moves or it does not
3. **Hard exit at 3:55 PM ET** — do not hold into the final 5 minutes; bid/ask spreads widen and fills become unreliable

---

## Related Notes

- [[0DTE-Butterfly]] — standard mechanics and Greeks for 0DTE butterflies
- [[0DTE-Overview]] — full landscape of 0DTE strategy types
- [[Gamma]] — why gamma is the engine that powers this trade
- [[Portfolio-Allocation]] — speculative sleeve sizing and capital rules
