---
title: "0DTE Butterfly Spreads on SPX"
tags:
  - options
  - 0DTE
  - butterfly
  - SPX
  - intraday
  - spreads
aliases:
  - 0DTE Fly
  - Same-Day Butterfly
status: draft
related:
  - "[[0DTE-Overview]]"
  - "[[Butterfly]]"
  - "[[0DTE-Iron-Condor]]"
  - "[[Superfly]]"
---

# 0DTE Butterfly Spreads on SPX

A 0DTE butterfly is a same-day directional bet that SPX will close at or very near a specific price. Unlike the [[0DTE-Iron-Condor]], which profits from a range of outcomes, the fly demands precise pinning — and rewards it with a much higher potential return on debit.

> [!warning]
> Butterflies require precise pinning — they can expire nearly worthless even if you're right directionally but off by 10 points. A $5 debit position can return $20 at perfect pin or $0 at expiry if SPX drifts just half a wing width away from center. Being "roughly right" is not enough.

---

## Structure

A **call butterfly** on SPX consists of three strikes at equal width:

- **Buy 1** lower call (long wing)
- **Sell 2** middle calls (short body — the "pin" target)
- **Buy 1** upper call (long wing)

The **put butterfly** is structurally identical but uses puts instead. For ATM placement on 0DTE, call flies and put flies are roughly equivalent in cost due to SPX put-call parity at expiry. Use calls when you expect a slight upward drift to your target; puts when drifting slightly lower.

> [!note]
> The butterfly is a net debit strategy. Maximum profit equals the wing width minus the debit paid. For a $25-wide fly purchased at $5 debit: max profit = $25 − $5 = $20 per contract ($2,000 notional). Maximum loss is capped at the debit paid.

---

## When to Use

Use a 0DTE butterfly when:

1. You have a **specific EOD price target** — not just a directional lean, but a conviction that SPX closes within roughly ±5 points of your center strike.
2. SPX is trading **near a strong magnet level** — round numbers (5000, 5050), prior day close, or a VWAP level that has acted as a gravitational pin in recent sessions.
3. The day's **implied move is muted** — a wide expected range kills butterfly edge because SPX is less likely to pin. Check the 0DTE straddle price; if the straddle implies a move larger than your wing width, the fly is a low-probability bet. (Rule of thumb, not data-backed.)
4. You want **higher reward than an IC** and accept the tradeoff of a narrower profit zone.

See [[0DTE-Overview]] for context on when 0DTE strategies are appropriate in general.

---

## Entry

**Window:** 10:00–11:00 AM Eastern. Earlier than 10:00 AM introduces open-auction noise; after 11:00 AM compresses time value and reduces the debit you pay, but the window for price discovery narrows.

**Center strike selection:** Place the body at your EOD price target. If SPX is at 5000 and you expect a quiet close near that level, center at 5000 (ATM fly). If there is visible support at 4975 from yesterday's range, center there instead.

**Wing width:** $25 wings are the standard for SPX 0DTE. $50 wings are available and cheaper in percentage terms, but require even more precise pinning. Start with $25. See [[Butterfly]] for a full discussion of wing-width tradeoffs.

---

## Cost and Profit Targets

| Wing Width | Typical Debit | Max Profit | Profit at Pin |
|------------|---------------|------------|---------------|
| $25        | $3–$7         | $18–$22    | 100%–200% on debit (rule of thumb) |
| $50        | $5–$12        | $38–$45    | 100%–200% on debit (rule of thumb) |

These ranges are rule of thumb based on typical SPX 0DTE mid-morning pricing under normal volatility. Actual cost varies with IV, distance from ATM, and time of entry.

**Target:** Close the position at 100%–200% profit on debit. For a $5 debit, that means exiting at $10–$15 before expiry rather than holding for the full $20 max. Taking 100% at 1:00–2:00 PM is often better than gambling on a perfect pin at 4:00 PM.

---

## Worked Example

SPX is trading at **5000** at 10:15 AM. You believe it will close near 5000.

- **Trade:** Buy 1 SPX 4975 call / Sell 2 SPX 5000 calls / Buy 1 SPX 5025 call
- **Debit paid:** $5.00 ($500 per 1-lot)
- **Max profit:** $25 − $5 = $20 ($2,000) if SPX expires exactly at 5000
- **Breakevens:** Approximately 4980 and 5020 (debit paid away from each wing)
- **Stop:** Exit immediately if SPX moves more than $12–$13 from 5000 (half of $25 wing)

![[0dte-butterfly-payoff.png]]

---

## Trade Management

**Stop rule:** If the underlying moves more than **half the wing width** from your center strike, close the position. For a $25-wide fly centered at 5000, exit if SPX trades below 4987 or above 5013 intraday. At that point the fly is likely worth less than $1 and you are better off recycling the remaining capital. (Rule of thumb.)

**Profit rule:** Do not hold to expiry fishing for max profit. The payoff curve is extremely peaked — a $5 fly worth $12 at 2:00 PM can be worth $2 by 3:30 PM if SPX drifts 8 points. Set a limit order to close at 100% gain when you enter.

For a higher-conviction, wider version of this trade, see [[Superfly]].

---

## Position Sizing

> [!warning]
> Limit total risk to **0.5% of portfolio** per butterfly position. On a $100,000 account that means risking no more than $500 — one 1-lot at a $5 debit, or two 1-lots at a $2.50 debit. This is a high-loss-rate strategy; you will lose the full debit on most days where SPX does not pin.

> [!danger]
> Beginners should paper trade butterflies for at least 30 sessions before committing real capital. The strategy looks cheap in debit terms, but a string of full-debit losses (which is normal) can quickly compound. The 0DTE butterfly is not suitable for traders who have not internalized how rapidly theta and gamma interact in the final hour of trading.

---

## Related Notes

- [[0DTE-Overview]] — framework for same-day strategies
- [[Butterfly]] — general butterfly mechanics and strike selection
- [[0DTE-Iron-Condor]] — lower-reward, wider-profit-zone alternative
- [[Superfly]] — wider-wing variation for stronger conviction setups
