# Module 10 - Decision Assistant Blueprint (From Signals to Reflexion)

## Why this module exists

Today, OptionTrader computes alerts and trade idea templates, but final decision quality still depends on human interpretation.

This module defines a concrete decision/reflexion layer so the system can guide judgment in a structured way.

## 1) Current vs Target Behavior

Current behavior:

- compute metrics and alerts,
- apply threshold + persistence + pessimistic checks,
- generate template trade ideas per alert family.

Target behavior (decision assistant):

- produce gate-by-gate evidence,
- produce decision label with rationale,
- produce confidence grade,
- produce explicit invalidation and monitoring plan.

## 2) Decision Object Schema (proposed)

For each alert candidate, output:

- `signal_evidence`: z-scores, persistence, family,
- `data_evidence`: coverage, cadence, source continuity,
- `regime_evidence`: regime label + event context,
- `execution_evidence`: tradability + spread burden,
- `risk_evidence`: max loss, size, invalidation,
- `decision_label`: Trade / Watch / Research / Reject,
- `decision_reasoning`: short structured paragraph,
- `monitoring_plan`: what to re-check next snapshot.

## 3) Deterministic Decision Logic (proposed)

Pseudo-logic:

1. If `risk_fail` -> `Reject`.
2. Else if `signal_fail` -> `Reject`.
3. Else if `execution_fail` -> `Research only`.
4. Else if `data_fail` -> `Research only`.
5. Else if `regime_fail` -> `Watch` or `Reject` depending on contradiction strength.
6. Else if all pass and regime not contradictory -> `Trade now`.
7. Else -> `Watch for confirmation`.

This avoids ambiguous narrative decisions.

## 4) Confidence Tiers for Decisions (proposed)

- `A`: all gates pass with strong evidence.
- `B`: all hard gates pass; one soft uncertainty remains.
- `C`: signal exists but one major non-risk gate is weak.
- `D`: weak or contradictory evidence; mostly reject/research.

## 5) Validation Loop for the Assistant

Track assistant output quality monthly:

- precision of `Trade now` labels,
- false-positive rate of `Watch` promotions,
- proportion of `Research only` later upgraded to valid trades,
- rule stability (whether frequent overrides are needed).

If override frequency is high, refine gate definitions, not discretionary judgment.

## 6) Implementation Path

Phase 1 (documentation + manual workflow):

- use this logic in analyst scorecards.

Phase 2 (app augmentation):

- add a Decision Summary panel in Streamlit,
- auto-populate gate evidence from snapshot data,
- output proposed decision label with rationale text.

Phase 3 (feedback learning):

- persist outcomes,
- calibrate gate thresholds/process rules by evidence.

## 7) Guardrails

- No decision without explicit risk fields.
- No trade recommendation when data integrity fails.
- No hidden magic numbers beyond documented config.

The point is not automation for its own sake. The point is auditable, repeatable decision quality.
