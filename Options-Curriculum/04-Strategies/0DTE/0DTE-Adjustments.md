---
title: 0DTE Adjustments — Same-Day Position Management
tags:
  - 0dte
  - adjustments
  - risk-management
  - intraday
aliases:
  - Same-day adjustments
  - 0DTE position rolls
status: draft
related:
  - "[[0DTE-Overview]]"
  - "[[0DTE-Iron-Condor]]"
  - "[[0DTE-Credit-Spread]]"
  - "[[Adjust-vs-Close]]"
  - "[[Rolling-Basics]]"
---

# 0DTE Adjustments — Same-Day Position Management

0DTE positions require adjustment logic entirely different from multi-week trades. When you have 6 hours until expiration, theta accelerates, gamma explodes, and traditional adjustment windows close fast. The window to react is measured in *minutes*, not days.

## Why 0DTE Adjustments Are Different

| Factor | Multi-Week | 0DTE |
|--------|-----------|------|
| Theta decay per hour | ~2–5 bp | 50–200 bp (explosive) |
| Gamma reaction | Manageable | Extreme — $1 move changes delta by 10–15 |
| Adjustment window | Hours to days | Minutes to 1–2 hours |
| Fill risk | Moderate | Very high (tight spreads, fast execution) |
| Cost to adjust | Known | Highly variable (spreads can double intraday) |

In a 0DTE position, delaying an adjustment by 30 minutes can mean the difference between salvaging 50% of max profit or taking a full loss.

## The 0DTE Adjustment Ladder

### Level 1: Intraday Monitoring (8:00 AM – 2:00 PM ET)

**Trigger:** Position is up 50% max profit
- **Action:** Exit immediately or scale out 50% of position
- **Reason:** Theta is accelerating, gamma is high, liquidity can vanish in final hour
- **Execution:** Limit orders, not market

**Trigger:** Position is breakeven or slightly positive
- **Action:** Continue to monitor. Do not adjust yet unless tested.
- **Reason:** You have time. Let theta work through final hours.

### Level 2: Protective Adjustment (2:00 PM – 3:30 PM ET)

**Trigger:** Short strike tested and broken *slightly* (e.g., SPX condor short call broken by <$10)

- **Call break adjustment:** Roll the short call up 10–20 points and back 1–2 hours (if time allows)
- **Put break adjustment:** Roll the short put down 10–20 points and back 1–2 hours

**Execution priority:**
1. Immediate: Roll to the next 30-min or hourly expiry if available (SPX 0DTE has micro-expiries)
2. Fallback: Roll same-day short slightly OTM again if micro-expiries are illiquid
3. Last resort: Close entire position if break is deep or spreads have widened to >30% of max risk

**Cost consideration:** A roll costs 2 spreads (close + open). In final 2 hours, spreads can be 1–2 vol points wide. This eats into max profit quickly. Only adjust if remaining profit is >2x the adjustment cost.

### Level 3: Emergency Close (3:30 PM – 3:59 PM ET)

**Trigger:** Position shows loss >5–10% of max risk, or short strike broken significantly (>$20)

- **Action:** Close the entire position immediately
- **Reason:** With <30 min to expiry, adjustment risk outweighs benefit
- **Execution:** Accept market price if necessary. Liquidity can evaporate in final minutes

> [!danger]
> Do not hold into final 15 minutes. Even if the position is profitable, the risk of a gap-down or technical order flow can wipe out the trade. Take the W and move on.

## Adjustment Decision Tree

```
Position Status?
├─ Up 50%+ profit → EXIT immediately
├─ Up 20–49% profit → Monitor, let theta work
├─ Up 0–19% profit → Wait for expiration unless tested
├─ Down 0–5% → Adjust if SHORT strike tested
├─ Down 5–10% → Close position
└─ Down >10% → Close immediately, do not adjust
```

## Calendar Context Matters

**Before 9:30 AM open:** Do not enter 0DTE trades unless you have a *specific* catalyst (earnings, macro data) known.

**9:30 AM – 11:00 AM:** Entry window for 0DTE. Early morning volatility offers cleaner entries.

**11:00 AM – 2:00 PM:** Position monitoring, potential scale-out of profitable trades.

**2:00 PM – 3:59 PM:** Final adjustment window. Any new adjustment after 3:30 PM is usually a mistake.

## Common 0DTE Adjustments — Pros and Cons

### Vertical Spread → Tighter Vertical

**When:** Short call of a call spread gets tested
- Close current call spread at loss
- Sell new, tighter call spread further OTM
- **Cost:** 1 full spread close + 1 new spread entry. Very expensive in final hours.
- **Use if:** You have >2–3 hours remaining and belief in the short strike holding

### Iron Condor → Fly Conversion

**When:** One side tested, max profit on other side secure
- Close one side entirely
- Tighten the other side into a fly
- **Cost:** 1 spread close + conversion adjustment. Moderate cost
- **Use if:** One wing is in danger but the other is rock-solid profitable

### Scale Out

**When:** Position is profitable, time is <2 hours
- Close 25–50% of position at limit
- Let remainder run into expiration
- **Cost:** Negligible (just close half)
- **Use if:** You want to lock in gains without the full adjustment cost

## Key Principles

1. **Speed is cost.** Every minute saved is a spread point saved. React fast.
2. **Gamma explosion near expiration.** A position that moves $500 pre-1pm can move $2000 post-3pm. Respect it.
3. **Adjust early, close late.** Adjust your directional risk while spreads are tight. Let theta finish the job in final hour if profitable.
4. **Accept small losses.** Taking a -2% loss at 3:00pm is better than a -10% loss at 3:59pm trying to adjust.
5. **Liquidity vanishes.** In final 30 min, bid/ask spreads can widen to 2–3x normal. Plan exits in advance.

## When NOT to Adjust

- **Spread is already tight** (0.10 wide or less) — closing and reopening will be more expensive than the risk
- **Time remaining is <30 min** — adjustment risk outweighs any remaining theta benefit
- **Loss is >10% of max risk** — you have already failed risk management; cutting is the only answer
- **Liquidity has evaporated** — if you can't get a 2-wide bid/ask, don't trade
