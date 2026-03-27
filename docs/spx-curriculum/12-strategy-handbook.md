# Module 12 - Strategy Handbook (Detailed)

This module is the dedicated strategy reference.

It explains:

- what each strategy is expressing,
- when it should (and should not) be used,
- how to validate setup quality,
- how to manage risk and invalidation.

The structures below map to current system templates in `src/core/trade_ideas.py`.

## 1) Strategy Card: SkewFade_PutSpread (RR)

Template mapping:

- alert family: `RR_EXTREME`
- legs: sell `-0.25P`, buy `-0.10P`

### What this strategy expresses

- A view that downside skew is temporarily too rich and may normalize.
- Defined-risk expression of skew normalization on put wing.

### Market regime fit

- Better fit: post-shock stabilization, improving execution conditions.
- Poor fit: accelerating stress where skew steepening is structural.

### Entry validation (must all pass)

1. `rr25_mid` extreme vs own history.
2. `rr25_worst` confirms direction and significance.
3. Persistence passes configured requirement.
4. Data integrity is clean (coverage/cadence/source).
5. Regime/event context does not favor continued stress acceleration.

### Risk profile intuition

- Short downside convexity relative to a long lower strike hedge.
- Benefits if skew richening partially mean-reverts.
- Can lose if downside repricing accelerates beyond expected path.

### Invalidation examples

- RR continues steepening with persistence.
- execution quality deteriorates (tradability/spreads worsen).
- regime shifts toward stronger stress continuation.

### Management notes

- keep size modest in uncertain regimes,
- avoid adding complexity before setup confirms,
- review near-term catalysts before holding through events.

### This is not

- a directional crash bet,
- a strategy for unresolved data integrity windows.

## 2) Strategy Card: Fly_1x2x1 (FLY)

Template mapping:

- alert family: `FLY_EXTREME`
- legs: buy `-0.25P`, sell `-0.50P` x2, buy `-0.10P`

### What this strategy expresses

- A convexity normalization view: wing-center relation is distorted.
- Structured expression of smile shape adjustment.

### Market regime fit

- Better fit: non-chaotic repricing where convexity dislocation is clear.
- Poor fit: unstable event windows with spread instability.

### Entry validation (must all pass)

1. `fly25_mid` extreme relative to own distribution.
2. `fly25_worst` confirms.
3. Decomposition clarity: wing-led vs center-led move understood.
4. Persistence and integrity checks pass.
5. Execution quality supports multi-leg structure.

### Risk profile intuition

- Strong shape dependence and pin/path sensitivity.
- Multi-leg execution friction can materially alter realized edge.

### Invalidation examples

- convexity distortion keeps expanding without stabilization,
- adjacent buckets contradict thesis,
- slippage/spreads consume expected edge.

### Management notes

- require stronger execution quality than simpler spreads,
- avoid in thin/erratic conditions,
- predefine response if central strike pin dynamics dominate.

### This is not

- a default strategy for every `FLY_EXTREME` print,
- a good fit for weak tradability regimes.

## 3) Strategy Card: ATM_Calendar (TERM)

Template mapping:

- alert family: `TERM_KINK`
- concept: short front ATM call, long back ATM call

### What this strategy expresses

- A view that near-vs-far term mismatch will normalize.
- Term-structure expression rather than pure directional expression.

### Market regime fit

- Better fit: post-event normalization or non-event maturity mispricing.
- Poor fit: pre-event windows with justified near-term premium.

### Entry validation (must all pass)

1. `term_slope_mid` extreme vs own history.
2. `term_slope_worst` confirms.
3. Event context reviewed (pre/post-event classification).
4. Persistence/integrity pass.
5. Carry + slippage burden acceptable.

### Risk profile intuition

- Sensitive to time decay differential and realized path.
- Can underperform if term premium remains justified longer than expected.

### Invalidation examples

- event repricing remains persistent post-event,
- slope keeps moving against thesis with persistence,
- carry burden dominates expected normalization.

### Management notes

- avoid forcing pre-event mean reversion,
- favor post-event confirmation when possible,
- define exit rules for unresolved normalization.

### This is not

- a universal response to every term kink,
- a replacement for event-aware risk planning.

## 4) Branching: Not All Signals Become Trades

Before selecting a strategy card, choose branch:

1. **Reversion branch** -> strategy candidate may be valid.
2. **Continuation branch** -> strategy may be delayed/reframed.
3. **No-trade branch** -> document and stand down.

The branch decision is part of edge. Not trading is often the correct decision.

## 5) Validation-to-Execution Checklist

Use this sequence for every candidate:

1. signal validity,
2. data validity,
3. regime/event validity,
4. execution viability,
5. risk worksheet completion,
6. final label.

If any hard gate fails, do not export execution plan.

## 6) Suggested Future Expansion

Add strategy cards for:

- explicit continuation strategies (not only reversion templates),
- event-hedged versions of term structures,
- low-liquidity fallback structures.
