---
title: "Adjust vs. Close — Decision Framework for Losing Positions"
tags:
  - options/adjustments
  - options/risk-management
  - options/discipline
  - options/closing
aliases:
  - "When to Adjust"
  - "When to Close"
  - "Adjust or Close"
status: draft
related:
  - "[[Rolling-Basics]]"
  - "[[Stop-Loss-Strategies]]"
  - "[[Building-Discipline]]"
  - "[[DTE-Management]]"
  - "[[IV-Expansion-Risk]]"
  - "[[Trade-Thesis-Framework]]"
---

# Adjust vs. Close — Decision Framework for Losing Positions

The hardest decision in options trading is not entry — it is managing a losing position. The temptation to adjust rather than close is overwhelmingly psychological, not logical. This note provides a structured framework so emotion stays out of the decision.

> [!warning]
> Most losing adjustments are made to avoid admitting a mistake. Before adjusting, ask: "Would I put this new trade on fresh right now, at today's prices, with today's IV?" If the honest answer is no, close the position. Adjusting to defer a loss is not risk management — it is loss deferral that usually amplifies the eventual damage.

---

## The Default Rule: When in Doubt, Close

Adjustments carry hidden costs: wider spreads on the new legs, additional margin consumption, and — critically — they lock in a new, larger position that still has to be right. Closing is always available; adjusting is a second trade layered on a first trade that already moved against you.

Rule of thumb (experienced traders): **Close unless you can articulate a clear, specific, logical reason to adjust.** "I don't want to take the loss" is not a reason.

---

## Criteria That Support Adjusting

All three conditions should be true simultaneously. If any one fails, the default rule applies.

1. **DTE > 21.** With fewer than 21 days to expiration, [[DTE-Management|theta decay accelerates]] and there is insufficient time for a thesis to reassert itself. Rolling short options under 21 DTE frequently extends duration without improving the position — it simply defers expiration risk.

2. **IV has not expanded dramatically.** When [[IV-Expansion-Risk|implied volatility has spiked]], the cost of rolling or adding legs reflects that spike. You are effectively buying high volatility to replace a position you sold at lower volatility — locking in losses and increasing vega exposure simultaneously. If IV has risen more than ~20–30% relative to the position entry level, rolling is expensive by construction.

3. **The trade thesis is still intact.** This is the most important criterion. Define the thesis explicitly before adjusting: *why* was the trade on? If you sold a put because the stock was holding a key support level and that support has since broken, the thesis is gone. No adjustment resurrects a broken thesis. See [[Trade-Thesis-Framework]] for how to document and verify thesis integrity.

---

## Criteria That Require Closing

Close without adjustment if *any* of the following apply:

- **DTE < 14.** Time has run out. Rolling extends risk, not opportunity.
- **IV has spiked.** Rolling is structurally expensive; you will pay the bid/ask spread into an elevated vol environment. See [[Rolling-Basics]] for the mechanics.
- **Thesis is broken.** Support broke. Earnings surprised. Macro regime shifted. The reason the trade existed is no longer valid.
- **Max loss already reached.** If your pre-defined [[Stop-Loss-Strategies|stop loss]] level has been hit, close. Adjusting past max loss is compounding a mistake with more capital.

> [!tip]
> Set your closing criteria *before* the trade is on. A stop rule written at entry is objective; a stop rule written mid-loss is rationalized.

---

## The Sunk Cost Trap

Sunk costs are irrelevant to forward decisions. The loss that already exists is gone regardless of whether you close or adjust. The only question is: **what is the expected value of the remaining or modified position from this point forward?**

Framed correctly, the adjust-vs-close question becomes: "If I had no position and someone offered me this adjusted trade at today's prices, would I take it?" If not, the adjustment is driven by sunk cost psychology, not edge. [[Building-Discipline]] covers techniques for breaking this cognitive pattern systematically.

> [!note]
> Sunk cost bias is well-documented in behavioral finance (Kahneman & Tversky, Thaler). It is not a character flaw — it is a universal cognitive bias. The antidote is process: written rules, pre-committed stops, and the "fresh trade" test above.

---

## Decision Tree

Use this sequence in order. Stop at the first "No" and close.

```
Is DTE > 21?
  └── No  → CLOSE
  └── Yes → Has IV remained roughly stable since entry (not spiked >20-30%)?
               └── No  → CLOSE
               └── Yes → Is the original trade thesis still valid?
                            └── No  → CLOSE
                            └── Yes → Would I put this adjusted trade on fresh today?
                                         └── No  → CLOSE
                                         └── Yes → ADJUST (document the reason)
```

![[adjust-vs-close-decision-tree.png]]

---

## Practical Checklist Before Any Adjustment

- [ ] DTE is above 21
- [ ] IV has not spiked materially since entry
- [ ] Thesis is still intact — written down, not just felt
- [ ] The adjusted position would be worth entering fresh at today's prices and IV
- [ ] The adjustment does not push total risk past the original max loss
- [ ] A stop level for the *adjusted* position is defined before executing

---

## Related Notes

- [[Rolling-Basics]] — mechanics of rolling short options, cost structure
- [[Stop-Loss-Strategies]] — pre-defining exit levels before entry
- [[Building-Discipline]] — cognitive bias and process-based decision-making
- [[DTE-Management]] — how time decay changes position dynamics
- [[IV-Expansion-Risk]] — what IV spikes do to adjustment costs
- [[Trade-Thesis-Framework]] — documenting and testing trade logic at entry
