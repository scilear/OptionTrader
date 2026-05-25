---
title: Iron Fly (Iron Butterfly)
tags:
  - strategy
  - income
  - defined-risk
  - volatility
  - neutral
aliases:
  - Iron Butterfly
  - Iron Fly
status: draft
related:
  - "[[Iron-Condor]]"
  - "[[Butterfly]]"
  - "[[Fly-vs-IC]]"
  - "[[Short-Straddle]]"
  - "[[IV-Rank]]"
  - "[[Delta-Neutral]]"
---

# Iron Fly (Iron Butterfly)

The Iron Fly is a four-leg, defined-risk income strategy built around the expectation that the underlying will stay pinned near its current price through expiration. It combines the high-credit potential of a [[Short-Straddle]] with the protection of an [[Iron-Condor]]-style wing hedge.

## Structure

| Leg | Strike | Direction |
|-----|--------|-----------|
| Short call | ATM | Sell |
| Short put | ATM | Sell |
| Long call (wing) | OTM (typically 1–2 SD above) | Buy |
| Long put (wing) | OTM (typically 1–2 SD below) | Buy |

The two short strikes are identical — both at the money. This is what distinguishes it from a standard [[Iron-Condor]], where short strikes are separated.

![[pnl-iron-fly.png]]

> [!note]
> The profit zone on an Iron Fly is shaped like a narrow tent, not a plateau. Maximum profit is earned only if the stock closes exactly at the short strike. In practice, any move away from the pin erodes the credit quickly.

## Key Metrics (rule of thumb, not data-backed)

- **Credit collected:** typically 40–50% of the wing width
- **Max profit:** full credit received (requires an exact pin at short strike)
- **Max loss:** wing width minus credit collected
- **Breakevens:** short strike ± credit collected
- **Typical DTE at entry:** 21–30 days

**Example:** Stock at $100, wing width $10 each side, credit $4.50.
- Max profit = $4.50
- Max loss = $10.00 − $4.50 = $5.50
- Breakevens: $95.50 / $104.50

## Entry Criteria

- **[[IV-Rank]] > 50** — elevated implied vol is essential; you are selling expensive premium and need a vol contraction or a pin to win.
- **Neutral [[Delta-Neutral]] posture** — enter when the underlying is near a well-defined technical level (support/resistance, post-earnings equilibrium) where pinning is plausible.
- **Wings 1–2 standard deviations away** — use the implied move (from ATM straddle price) or historical vol to size the wing distance. Wider wings increase max loss but also raise the credit as a percentage of width.
- **21–30 DTE** — theta decay accelerates inside 30 days. Going shorter increases pin sensitivity; going longer gives more time for adverse moves.

## Trade Management

> [!tip]
> The profit zone is narrow by design. Take profit early — waiting for expiration to pin exactly is a low-probability expectation. Most experienced traders close at 25–50% of max profit and redeploy.

- **Take profit at 25–50% of credit:** if you collected $4.50, close the position when it can be bought back for $2.25–$3.38.
- **Defend at 25% of credit remaining:** if the position is down to $1.12 (25% of $4.50 remaining), close to preserve capital. This is the equivalent of the "21 DTE close" heuristic in [[Iron-Condor]] management — don't let a loser ride.
- **Rolling:** difficult because both short strikes are ATM. A directional move that threatens one side usually means the opposite wing is nearly worthless; consider closing the whole position rather than legging.

## Iron Fly vs. Iron Condor

| Criterion | Iron Fly | [[Iron-Condor]] |
|-----------|----------|-----------------|
| Credit collected | Higher (40–50% of width) | Lower (20–33% of width) |
| Profit zone | Narrow tent | Wider plateau |
| Breakevens | Tighter | Wider |
| Ideal scenario | Pin near current price | Drift within a range |
| Best when IV rank | Very elevated (>60) | Elevated (>40) |

Prefer the Iron Fly over the [[Iron-Condor]] when:
- IV is very elevated and you expect a sharp vol crush after a known event (e.g., post-earnings equilibrium).
- You want maximum credit for a given wing width.
- You have conviction on a pin rather than merely a range.

See [[Fly-vs-IC]] for a side-by-side comparison with worked examples.

## Relationship to Other Strategies

- **[[Short-Straddle]]:** the Iron Fly is a capped version. It earns less total credit but the wing hedge caps the loss, making it viable in margin-constrained accounts.
- **[[Butterfly]]:** a put or call butterfly is the debit-spread cousin — same payoff shape but entered as a debit. Iron Fly generates a credit.
- **[[Iron-Condor]]:** split the short strikes apart and you get an IC. The Iron Fly is the highest-credit, highest-pin-sensitivity endpoint on that spectrum.

## Risk

> [!warning]
> Despite being defined-risk, the Iron Fly can lose more than the credit collected on both sides simultaneously if the stock makes a large directional move. Max loss is wing width minus credit — which in a $10-wide structure collecting $4.50 is still a $5.50 loss per contract ($550 notional). Size accordingly: this strategy should represent a small fraction of total portfolio risk.

> [!danger]
> Do not enter an Iron Fly purely because IV rank is high without confirming a neutral outlook. A stock with elevated IV often has a reason (pending catalyst, deteriorating fundamentals). If that catalyst resolves directionally, an Iron Fly can hit max loss in hours. This structure is not suitable for beginners managing multi-leg positions under real-time P&L pressure.
