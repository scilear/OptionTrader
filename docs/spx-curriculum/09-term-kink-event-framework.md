# Module 9 - TERM Kink Event Framework

## Learning Objectives

- Interpret term-slope alerts in event and non-event regimes.
- Separate justified term repricing from temporary dislocation.
- Apply a structured framework for TERM_KINK decisions.

## 1) Formula and Context

For two maturities `T_near` and `T_far`:

- `TERM = sigma_ATM(T_near) - sigma_ATM(T_far)`

In the pipeline, `term_slope_mid` and `term_slope_worst` are derived between adjacent configured buckets.

Interpretation:

- higher positive near-far slope can indicate concentrated near-term event premium,
- flattening can indicate event decay or broader regime repricing,
- inversion can signal unusual maturity structure shifts.

## 2) Why Event Context Is Critical

Term distortions are often rational around catalysts (macro releases, central bank meetings, earnings clusters for constituents).

A key mistake is treating every term kink as mean-reversion opportunity.

Framework principle:

- first ask "is this justified by event timing?",
- only then ask "is this mispricing likely to normalize?"

## 3) Event vs Non-Event Decision Matrix

| Context | Signal characteristics | Default stance | Escalation condition |
|---|---|---|---|
| non-event week | persistent kink + clean data | consider normalization thesis | worst-case + persistence + tradability all pass |
| pre-event window | near term elevated fast | cautious/watch | wait for post-event confirmation unless edge is exceptional |
| immediate post-event | decay expected but uncertain speed | watch first | trade only if decay pattern confirms across snapshots |
| mixed event noise | unstable oscillation | research only | require cleaner cadence and repeated confirmation |

## 4) TERM_KINK Process Checklist

1. Confirm slope direction and magnitude in both mid and worst variants.
2. Check if front maturity contains known catalyst premium.
3. Validate persistence beyond one isolated point.
4. Verify data quality and source consistency.
5. Assess carry/slippage burden for intended structure.
6. Define invalidation before entry.

## 5) Typical Failure Modes

- entering mean reversion before event risk passes,
- ignoring carry cost in calendar-style structures,
- overconfident interpretation from sparse snapshots,
- misclassifying rational repricing as anomaly.

## 6) TERM Case Framing Template

For each TERM alert, write:

- event status: `non-event` / `pre-event` / `post-event` / `mixed`,
- slope thesis: `normalization` / `continuation` / `unclear`,
- execution burden: `low` / `medium` / `high`,
- decision label: `Trade` / `Watch` / `Research` / `Reject`,
- invalidation condition.

## 7) Drill

Choose 8 historical TERM alerts and split them into event categories.

For each alert:

1. state expected slope path over next snapshots,
2. compare expectation with realized behavior,
3. log one rule adjustment if expectation failed.
