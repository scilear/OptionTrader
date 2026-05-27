---
title: Rolling Options Positions — Basics
tags:
  - options/adjustments
  - options/rolling
  - options/management
  - options/theta
aliases:
  - Rolling Options
  - How to Roll Options
  - Roll a Position
status: draft
related:
  - "[[Rolling-Credit-Spreads]]"
  - "[[Rolling-Iron-Condors]]"
  - "[[Adjust-vs-Close]]"
  - "[[Adjustment-Decision-Tree]]"
  - "[[Rolling-for-Credit]]"
  - "[[Losing-Trade-Mindset]]"
---

# Rolling Options Positions — Basics

Rolling is the most common adjustment technique for short-premium traders. It means **closing an existing option leg and simultaneously opening a replacement leg** in a single combined order — not two separate orders. Executing both legs together eliminates leg-out risk.

## Types of Rolls

### Rolling Out (Same Strike, Later Expiry)

You keep the strike and push the expiration further into the future. The new expiry collects additional time premium, which — if [[IV-vs-HV]] has not collapsed — typically allows you to receive a net credit.

Use case: the underlying is near your strike but has not broken through. You still like the position, you just need more time.

### Rolling Out and Up / Down (New Strike, Later Expiry)

You change both the expiry and the strike simultaneously. "Up" means moving the strike higher; "down" means lower.

Use case: the underlying has moved against you and your original strike is too close to or beyond the current price. Moving the strike creates additional buffer — but it usually reduces the credit available, sometimes to near zero.

> [!note]
> Rolling out and down on a short put is a common response to a falling stock. You accept a lower strike (more room to run) in exchange for keeping the position alive and, ideally, collecting a small credit.

## Rolling for Credit vs. Rolling for Debit

This is the single most important rule in rolling:

**Always attempt to roll for a net credit, or at worst breakeven.** Rolling for a debit means paying to stay in a losing position — compounding the loss before time decay helps. If the market will not give a credit at any reasonable combination of strike and expiry, close the position outright. See [[Adjust-vs-Close]] for the full decision framework.

> [!tip]
> Collect at least $0.10–$0.20 in net credit before committing to a roll. Smaller credits may be eaten entirely by bid/ask spread slippage. This is a rule of thumb, not a hard statistical threshold.

## Rolling Rules (Data-Backed Where Noted)

1. **Roll with ≥21 DTE remaining.** Inside 21 DTE, [[Gamma]] accelerates and the position becomes harder to manage. Rolling before that threshold gives the new expiry time to decay favorably. (The 21-DTE management trigger is widely cited in tastytrade research on short premium mechanics.)

2. **Watch the new expiry window.** If rolling out would place you beyond 60 DTE, pause. Longer-dated options carry more vega exposure and less theta efficiency. Ask: is a 75-DTE short put actually the trade you want to own right now?

3. **Limit yourself to two rolls maximum** (rule of thumb, not a law). After two rolls the original thesis has likely failed. Close the position, take the loss, and redeploy capital.

> [!warning]
> Indefinite rolling is not a free repair strategy. Every extension of duration also extends capital commitment and vega exposure. Markets can trend against you for months; no roll transforms a wrong directional bet into a winner.

## Step-by-Step Example

**Setup:** You sold a $50-strike naked put, 30 DTE. The stock drops from $52 to $48 — the put is now $2 in the money.

**Decision point:** 30 DTE remain (within the rolling window); position is against you but not at max loss.

**Action:** Roll the $50 put down to the $47 put in the next monthly expiry (approximately 58 DTE away).

- Buy to close: $50 put (debit ~$2.80 mid)
- Sell to open: $47 put, next month (credit ~$3.00 mid)
- **Net credit: $0.20**

**Result:** $0.20 additional premium collected. The new break-even moves from $50 to $46.80 (original premium + roll credit), adding $1.20 of cushion before the new put goes in the money.

> [!danger]
> This example uses a naked short put — theoretically unlimited downside to zero. Naked short options are unsuitable for beginners. Spreads such as [[Rolling-Credit-Spreads]] define your maximum loss before entry.

## When Not to Roll

- A credit is unavailable at any reasonable strike or expiry combination.
- You have already rolled twice (maximum limit reached).
- The new expiry exceeds 60 DTE and that duration is not the trade you want.
- A catalyst (earnings, FDA decision) now falls inside the new window and was not part of your original thesis.

Consult [[Adjust-vs-Close]] and [[Adjustment-Decision-Tree]] before acting in any of these cases.
