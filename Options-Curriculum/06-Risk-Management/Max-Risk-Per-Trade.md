---
title: Max Risk Per Trade
tags:
  - risk-management
  - position-sizing
  - execution
aliases:
  - Max Risk Rules
  - Per-Trade Risk Limits
status: draft
related:
  - "[[Position-Sizing]]"
  - "[[Portfolio-Allocation]]"
  - "[[Leverage-and-Margin]]"
  - "[[Kelly-Criterion]]"
---

# Max Risk Per Trade

**Per-position risk limits** prevent a single trade from blowing up your account. These rules are **independent of portfolio allocation** — they define how much capital is exposed on each leg, not how many positions to take overall.

> [!warning]
> These are **maximum** risk caps, not targets. Trading at the limit on every position will exhaust your account rapidly. Use 50–70% of these limits in practice and reduce during drawdowns.

## Risk Limits by Strategy

| Strategy | Max Risk per Trade | Notes |
|----------|-------------------|-------|
| **Covered Call** | Notional of stock position (size stock to 5–10% of portfolio) | Risk is stock draw-down; sell calls ≤ target strike. Total position capped at 10% portfolio. |
| **Cash-Secured Put (CSP)** | 5% of portfolio | Max loss = (strike − premium) × 100. Size position so max loss ≤ 5%. |
| **Bull Put Spread** | 2% of portfolio | Max loss = (width − credit) × 100. Sell 1–2 contracts per 1 contract size. |
| **Bear Call Spread** | 2% of portfolio | Max loss = (width − credit) × 100. Same logic as Bull Put. |
| **Iron Condor (IC)** | 2–3% of portfolio | Max loss = (width on wider side − credits) × 100. Typical width 5–10 pts. |
| **Iron Fly** | 2% of portfolio | Max loss = 1-point width × 100 (if 1pt wings). Usually smaller notional than IC. |
| **Butterfly** | 1% of portfolio | Max loss = 1-point wings × 100 (minimal risk structure). |
| **Calendar Spread** | 1% of portfolio | Max loss = debit paid. Small, theta-grinding risk. |
| **PMCC** (Put-secured Call Spread) | 5% on short LEAPS leg; check overall position notional | Max loss on short put = (strike − premium) × 100. Covered call notional ≤ 10%. |
| **0DTE Credit Spread** | 0.5–1% of portfolio | Explosive vega/gamma risk near expiry. Tight stops required (close at 50% max profit or 21% loss). |
| **0DTE Iron Condor** | 1% of portfolio | Wide-delta risk on both sides. Close by 10:30 ET to avoid pinning chaos. |
| **Earnings Trade** (straddle/strangle/spreads) | 1–2% of portfolio | IV crush risk post-earnings. Use spreads or defined-risk structures. Implied move often exceeds realized. |

> [!danger]
> 0DTE credit spreads and earnings plays are **unsuitable for beginners**. Gamma risk can wipe a 50% loss in minutes. Do not attempt until you can close profitably under stress and have a tested stop-loss system.

## What Counts as Max Loss

**Credit Spreads** (Bull Put, Bear Call, IC, Iron Fly):
- Max loss = **(spread width − net credit received) × 100**
- Example: Sell 1 SPX 6240/6245 Bull Put at 1.50 credit. Max loss = (5 − 1.50) × 100 = $350.

**Cash-Secured Put**:
- Max loss = **(strike − premium received) × 100**
- Example: Sell 1 SPX 6200 Put at 2.00 credit. Max loss = (6200 − 2) × 100 = $619,800. Size position accordingly.

**Covered Call**:
- Max loss = **stock position cost − call credit** (but stock can fall 100%). Cap notional at 5–10% portfolio; then sell calls to reduce cost.

**Debit Spreads** (Vertical call/put spreads, butterflies, calendars):
- Max loss = **debit paid**. This is fixed upfront; risk is predictable.

**LEAPS / Long Options**:
- Max loss = **premium paid**. Define-risk structures cap losses naturally.

## Implementation Rules

1. **Size to 5–10% portfolio first**, then apply per-trade limits.
   - If your account is $100k, max trade position is 5–10k notional. Don't use all of it on the first opportunity.

2. **Reduce at drawdown** (account down 10–15% from high):
   - Scale down from 5% to 3% per trade.
   - Tighten stops to 15% loss instead of 21%.

3. **Count aggregate notional** for multi-leg positions:
   - IC = max loss on call side + max loss on put side. **Total ≤ 3% portfolio**.
   - Pair-trading (long/short different expirations) = count both legs.

4. **Use hard stops**:
   - Exit at 2× max loss (e.g., CSP losing 10% of portfolio = exit).
   - Credit spreads: close at 50% max profit OR 21% loss, whichever comes first.

5. **Test position size in backtests**:
   - Validate that 2–3 losses in a row don't breach 10% account drawdown. Adjust down if needed.

> [!note]
> **These limits are not aggressive.** A $100k account risking 2% per trade can take 50 trades before a 100% loss scenario. In reality, traders with 55% win rates at 2% risk see 15–20% annual returns with 8–12% max drawdowns.

---

**See also:** [[Position-Sizing]], [[Portfolio-Allocation]], [[Kelly-Criterion]], [[Stop-Loss-Rules]]
