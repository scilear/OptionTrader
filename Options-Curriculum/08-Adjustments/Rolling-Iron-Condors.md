---
title: Rolling Iron Condors — Adjustment Playbook
tags:
  - adjustments
  - iron-condor
  - rolling
  - credit-spreads
  - risk-management
  - SPX
aliases:
  - IC Rolling
  - Iron Condor Adjustment
  - IC Repair
status: draft
related:
  - "[[Iron-Condor]]"
  - "[[Rolling-Basics]]"
  - "[[Adjust-vs-Close]]"
  - "[[Stop-Loss-Strategies]]"
  - "[[Rolling-Credit-Spreads]]"
  - "[[Adjustment-Decision-Tree]]"
---

# Rolling Iron Condors — Adjustment Playbook

The [[Iron-Condor]] is the most mechanically complex structure to adjust because you have four legs, two directional threats, and a credit that must be actively defended without turning a manageable loss into a catastrophic one. Most of the discipline in IC management is knowing which tool to reach for — and when to put all tools down.

> [!warning]
> Rolling does not eliminate a loss — it defers it and often increases position size. Every adjustment adds gamma risk, commission drag, and the possibility of being wrong twice. Never roll mechanically without re-evaluating the underlying thesis.

---

## The Four Adjustment Moves

### 1. Roll the Untested (Winning) Side In

**When to use:** The tested side is under pressure (price moving toward your short strike), but the untested side is sitting far OTM with high probability of expiring worthless. That far-OTM spread has little value left — you've captured most of its premium.

**Mechanics:** Close the winning spread for a debit (small, because it's nearly worthless), reopen it closer to the current price to collect a larger credit. Net result: additional credit received that offsets some of the unrealized loss on the tested side.

**SPX example:** You sold a 5500/5520 call spread and a 5300/5280 put spread for $4.00 total credit. SPX has dropped to 5340 — the put spread is now worth $3.20 (losing). The call spread is worth $0.20 (nearly fully captured). Close the call spread for $0.20 debit, reopen a 5420/5400 call spread for $1.10 credit — net +$0.90 additional credit, reducing max loss.

> [!tip]
> Only roll the untested side in if you can collect at least $0.50 in net credit after commissions on SPX. Less than that and the margin impact and gamma increase are not worth it.

**Risk:** You are now a tighter condor. If the move reverses, the newly repositioned call side is closer and more vulnerable.

---

### 2. Roll the Tested (Losing) Side Out

**When to use:** The tested spread has reached 2x the original premium received (a common stop-loss trigger — see [[Stop-Loss-Strategies]]) but you still have a valid thesis and sufficient DTE to recover.

**Mechanics:** Close the losing spread entirely. Reopen further OTM, ideally in the next expiry cycle, collecting enough credit to be net even or slightly positive on the combined transaction.

**SPX example:** Sold 5300/5280 put spread for $1.80. It's now worth $3.60. Close for $3.60 debit. Reopen a 5220/5200 put spread in the next monthly expiry for $2.10. Net adjustment cost: $1.50. You've given back some of your original credit but reduced your immediate risk.

**Condition that must be met:** You must be able to reopen at a strike with delta ≤ 0.20 and still collect net credit after the close. If you can't — do not roll. See [[Rolling-for-Credit]].

> [!note]
> "Rolling out" means extending time. "Rolling down/up" means moving the strikes. Most real adjustments do both simultaneously — roll out-and-down on a put spread, or out-and-up on a call spread.

---

### 3. Convert to a One-Sided Trade (Close the Winner, Keep the Loser)

**When to use:** One side of the condor is clearly going to be tested through expiry — for example, a strong trending move with no sign of reversal. Holding the opposing spread is now deadweight that ties up buying power.

**Mechanics:** Close the untested (winning) side for a small debit, freeing up the capital it was using as part of the IC structure. The remaining position is now a naked [[credit-spread]] on the losing side.

**SPX example:** SPX trending hard down. Your 5500/5520 call spread is worth $0.05. Close it for $0.05, freeing the $2,000 buying power per contract it was consuming. Now manage the put spread independently, with a tighter stop.

> [!tip]
> Closing the winner and "letting the loser ride" is only rational if you have a clear max-loss rule on the remaining spread. Without that rule, you now have an uncapped-loss mentality on a position that was originally structured to have defined risk.

---

### 4. The Inverted Condor — Immediate Close Required

**What it is:** If the underlying moves through both short strikes simultaneously (rare but possible during a crash or spike), your IC is now inverted — your short call strike is below your short put strike. This is the worst-case scenario because both spreads are simultaneously in-the-money and your loss is approaching maximum on both sides.

> [!danger]
> An inverted iron condor cannot be salvaged by adjustment. The risk/reward of continuing to hold or roll is deeply negative. Close all four legs immediately and accept the loss. Every minute of delay increases assignment risk and slippage on a widening position.

Historically this occurs in gap scenarios (e.g., overnight geopolitical events on broad indices) rather than intraday. It is a risk that cannot be adjusted away — only managed with position sizing before the trade is placed.

---

### 5. When Not to Adjust: The 14-DTE Rule

> [!warning]
> If you have fewer than 14 days to expiration, do not roll a losing IC into a new expiry. You are trading a short-dated, high-gamma position into a longer-dated, lower-premium one while paying closing costs on a stressed structure. The math almost never works in your favor.

**Rule of thumb (not data-backed):** At DTE < 14, evaluate only two choices:
1. Close the entire IC and take the loss.
2. Close only the untested side and manage the remaining spread to expiry with a hard stop.

Rolling into the next cycle at this stage typically results in carrying a larger notional position, lower net credit, and the psychological trap of "averaging down" on a losing thesis. See [[Adjust-vs-Close]] for the full framework.

---

## Decision Tree

```
IC is under pressure — what do I do?
│
├── DTE < 14?
│   └── YES → Do NOT roll. Close entirely or close winner and manage loser to expiry.
│
├── DTE ≥ 14 → evaluate the threat:
│   │
│   ├── Only ONE side is threatened:
│   │   ├── Untested side has value left (> $0.50)?
│   │   │   └── YES → Roll untested side in for additional credit (Move 1)
│   │   │
│   │   ├── Tested side at 2x loss and thesis still valid?
│   │   │   └── YES → Roll tested side out-and-away for net credit (Move 2)
│   │   │
│   │   └── Trend is strong, no reversal signal?
│   │       └── Close the winner, manage the loser as a credit spread (Move 3)
│   │
│   └── BOTH sides are threatened (inverted IC)?
│       └── Close ALL four legs immediately. No adjustment. (Move 4)
```

---

## Combining Moves

In practice, Moves 1 and 2 are often executed together: roll the winner in AND roll the loser out in the same order. This is called a "double adjustment" and maximizes the credit collected. However, it also results in a tighter, wider-striking structure in a new expiry — meaning you need the underlying to settle into a narrower range than originally planned.

Only attempt a double adjustment when:
- Net credit received from both moves combined is ≥ $0.75 (SPX, 5-wide spreads)
- New strikes have delta ≤ 0.20 on both sides
- The new expiry is 21–45 DTE

---

## Related Notes

- [[Rolling-Basics]] — Core mechanics of rolling any spread
- [[Rolling-Credit-Spreads]] — Single-leg rolling playbook
- [[Adjust-vs-Close]] — Framework for when adjustment is rational vs. when to cut losses
- [[Stop-Loss-Strategies]] — Setting position-level stop rules before the trade opens
- [[Iron-Condor]] — Full structure overview and setup criteria
- [[Adjustment-Decision-Tree]] — Visual decision framework across all adjustment types
