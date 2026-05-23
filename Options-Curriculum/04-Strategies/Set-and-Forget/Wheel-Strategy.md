---
title: Wheel Strategy
tags:
  - set-and-forget
  - income
  - csp
  - covered-call
  - assignment
  - theta-decay
aliases:
  - The Wheel
  - Wheel of Fortune Strategy
  - Triple Income Strategy
status: draft
related:
  - "[[CSP-Cash-Secured-Put]]"
  - "[[Covered-Call]]"
  - "[[Ticker-Criteria-Technical]]"
  - "[[Rolling-Credit-Spreads]]"
---

# Wheel Strategy

The Wheel is a systematic, three-phase income cycle that strings together two core strategies — the [[CSP-Cash-Secured-Put]] and the [[Covered-Call]] — into a repeating loop. Each phase earns premium. Assignment is not a failure state; it is the planned transition between phases.

![[pnl-wheel-cycle.png]]

> [!note]
> The Wheel is sometimes called the "Triple Income" strategy because you collect premium in Phase 1, dividends in Phase 2 (if the stock pays them), and premium again in Phase 3. In practice, most of the edge comes from the two layers of option premium, not dividends.

---

## Phase 1 — Sell a Cash-Secured Put (CSP)

**Goal:** collect premium; acquire shares at a discount if assigned.

| Parameter | Rule |
|---|---|
| Delta | 0.20 – 0.30 |
| DTE | 21 – 45 days |
| Strike | At or below a support level you're willing to own at |
| Profit target | Close at 50% of max credit (rule-of-thumb, TastyTrade-derived) |
| Loss management | If the put reaches 2× the initial credit, reassess (see "When the Wheel Breaks") |

Selling the put obligates you to buy 100 shares at the strike price. You must hold the full cash equivalent in your account — this is the capital requirement that makes the strategy conservative relative to naked puts on margin.

If the put expires worthless or you close it at 50% profit, you return to the start of Phase 1 with your capital freed. If the stock closes below your strike at expiration, you are **assigned** and move to Phase 2.

---

## Phase 2 — You Own the Stock

**Goal:** reduce your effective cost basis by selling calls against the shares.

After assignment your cost basis is:

```
Effective cost basis = Strike price − Total premium collected (Phase 1 + any prior wheels)
```

Immediately — meaning the next trading day — sell a [[Covered-Call]] against your 100 shares.

| Parameter | Rule |
|---|---|
| Strike | At or **above** your effective cost basis |
| Delta | 0.25 – 0.35 |
| DTE | 21 – 45 days |
| Profit target | Close at 50% of max credit |

> [!warning]
> Never sell the covered call with a strike below your cost basis unless you are intentionally exiting the position at a loss. Selling below cost basis guarantees a net loss on the stock leg no matter what happens with the call premium.

---

## Phase 3 — Covered Call Management and Exit

**Goal:** continue reducing cost basis; exit the stock position when called away.

- Close the covered call at **50% profit** and immediately sell a new one (same rules as Phase 2).
- If the stock is called away at expiration (assigned on the short call), you sell shares at the strike price and collect the premium. Your net result is: `(Strike − Effective cost basis) + all premiums collected`.
- Once the stock is called away, return to **Phase 1** and begin the cycle again.

---

## Ticker Selection — The Most Critical Decision

The Wheel is only as good as the underlying you choose. A bad ticker turns a systematic income strategy into a bag-holding exercise.

> [!tip]
> Wheel only stocks or ETFs you would be comfortable holding for 6–12 months if every put gets assigned and every covered call expires worthless. If you would not buy the stock outright, do not sell a put on it.

**Acceptable underlyings (data-backed — liquid, low gap risk, mean-reverting):**
- SPY, QQQ, IWM — broad ETFs; no single-name event risk
- AAPL, MSFT, AMZN — mega-cap, high options liquidity, tight bid/ask
- GLD — low correlation to equities; useful for diversification

**Avoid:**
- Meme stocks (GME, AMC, etc.) — implied volatility is high for a reason; gap risk is extreme
- Biotech with binary catalysts — a single FDA decision can cut the stock 50% overnight
- Any stock where the IV spike is driven by an upcoming event you cannot price

See [[Ticker-Criteria-Technical]] for a full screening checklist including minimum average volume, bid/ask spread thresholds, and IV rank filters.

---

## When the Wheel Breaks

The Wheel's failure mode is a sustained underlying decline of 20%+ below your put strike.

If this happens:

1. **Do not mechanically keep selling covered calls below your cost basis.** Each call you sell below cost basis caps your recovery and guarantees a realized loss on the shares.
2. Assess whether the decline is a temporary drawdown or a change in business fundamentals.
3. If the thesis is broken, sell the stock, book the loss, and redeploy capital. Sunk-cost reasoning is the primary way traders turn a manageable loss into a catastrophic one.
4. If the stock is merely down in a market-wide selloff and the business is intact, you may choose to hold and continue wheeling — but move strikes lower in line with the new price level, not with your original cost basis.

> [!warning]
> **Capital requirements and true max loss.** The CSP requires you to hold 100 × strike price in cash per contract. A single contract on a $200 stock ties up $20,000. The maximum loss in Phase 1 is the stock going to zero: you pay $20,000 for shares now worth $0, minus all premium collected. Premiums collected reduce but do not eliminate downside. Never allocate more than 10–15% of a portfolio to a single Wheel position.

> [!danger]
> Running the Wheel on a highly volatile single name (beta > 1.5, earnings-driven stock, or any recent meme) dramatically increases the probability of a large gap-down that cannot be managed with normal rolling techniques. The strategy is unsuitable for beginners on individual names; start with SPY or QQQ where gap risk is structurally lower.

---

## Rolling to Manage Assignments

If you want to avoid assignment on the CSP, you can roll it out in time for a net credit — see [[Rolling-Credit-Spreads]] for mechanics and constraints. Rolling is not always the right answer; sometimes taking assignment and moving to Phase 2 is more capital-efficient than rolling for a tiny credit.

---

## Summary Checklist

- [ ] Ticker passes [[Ticker-Criteria-Technical]] screen
- [ ] Full cash secured (no margin) for Phase 1
- [ ] CSP delta 0.20–0.30, DTE 21–45
- [ ] Close CSP at 50% profit
- [ ] On assignment: sell CC at or above effective cost basis, delta 0.25–0.35
- [ ] Close CC at 50% profit
- [ ] Single position ≤ 15% of portfolio
- [ ] No wheeling of meme stocks, biotech, or earnings-adjacent setups
