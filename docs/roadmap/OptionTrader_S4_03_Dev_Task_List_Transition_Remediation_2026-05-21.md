# OptionTrader S4-03 Dev Task List: Transition Remediation

Date: 2026-05-21
Owner: PM
Assigned to: Dev
Issue anchor: #16
Status: Ready for execution

## Objective

Resolve the remaining S4-03 blocker (candidate transition false-positive density worsening vs baseline)
using a short, bounded experiment cycle with strict rerun lineage and contract gates.

## Non-negotiable guardrails

1. Use canonical config for strict runs: `config/config-eod-truth.yaml`.
2. Run strict matrix from materialization, not partial downstream-only reruns.
3. Evaluate only post-warmup effective window (`effective_start_ts` must be present).
4. Do not relax gate definitions or taxonomy semantics.
5. Evidence must be reproducible and machine-readable in roadmap artifacts.

## Dev tasks

### T1 - Implement policy variant v2a (Transition tightening)

- Priority: High
- Goal: Reduce transition FP density while preserving reasonable alert volume.
- Change set:
  - Tighten Transition-only RR policy (and optional Transition FLY tightening if already parameterized).
  - Keep TERM behavior unchanged.
- Files likely touched:
  - `src/core/compute_snapshot.py`
  - `config/config-eod-truth.yaml`
  - `config/config-v1.yaml`
  - `config/config-test.yaml`
- Definition of done:
  - Configurable thresholds present.
  - Explain/blocker reasons emitted when alerts are suppressed by new Transition policy.

### T2 - Implement policy variant v2b (Transition TERM-only hard bound)

- Priority: High
- Goal: Establish hard upper bound on transition noise reduction.
- Change set:
  - In Transition regime, suppress RR and FLY (TERM-only behavior).
- Definition of done:
  - Variant can be selected/configured independently from v2a.
  - Non-Transition behavior remains unchanged.

### T3 - Add/extend tests for regime-conditioned gating

- Priority: High
- Required tests:
  - Transition RR blocked below threshold and allowed above threshold.
  - Transition FLY behavior per variant definition.
  - TERM unaffected by RR/FLY Transition gating.
  - Non-Transition regimes unaffected by Transition-only rules.
- Files likely touched:
  - `tests/test_alerts_logic.py`
  - `tests/test_regime_filter.py`
- Definition of done:
  - Target test files pass under `.venv`.

### T4 - Run strict materialization for 2010-2012 (both variants)

- Priority: High
- Command pattern:
  - `python scripts/materialize_s4_tracks_from_eod.py --config-path config/config-eod-truth.yaml --baseline-lineage <baseline_sha> --candidate-lineage <candidate_sha_or_label> --start-ts 2010-01-01T00:00:00Z --end-ts 2012-12-31T23:59:59Z --underlying SPX`
- Definition of done:
  - Materialization succeeds for each variant.
  - Run IDs, snapshot counts, and lineage are captured in artifacts.

### T5 - Run strict materialization for full span (both variants)

- Priority: High
- Command pattern:
  - `python scripts/materialize_s4_tracks_from_eod.py --config-path config/config-eod-truth.yaml --baseline-lineage <baseline_sha> --candidate-lineage <candidate_sha_or_label> --start-ts 2010-01-01T00:00:00Z --end-ts 2023-12-31T23:59:59Z --underlying SPX`
- Definition of done:
  - Materialization succeeds for each variant.
  - No DB targeting ambiguity in logs/errors.

### T6 - Regenerate contractual artifacts per window/variant

- Priority: High
- Required artifact families:
  - `OptionTrader_S4_03_Release_Validation_Report_*`
  - `OptionTrader_S4_03_Release_Validation_Payload_*`
  - `OptionTrader_S4_03_Baseline_Capture_*`
  - `OptionTrader_S4_03_Gate_Attrition_Report_*`
  - `OptionTrader_Sprint_4_Ablation_Artifact_*`
- Definition of done:
  - 2010-2012 and full-span outputs exist for each variant and are internally consistent.

### T7 - Evaluate pass/fail against fixed gate contract

- Priority: High
- Required checks (both windows):
  1. `evidence_valid == true`
  2. Transition FP density non-worsening vs baseline
  3. Precision non-regression vs baseline
  4. Volume within existing guardrail tolerance
  5. Taxonomy not `invalid_evidence`
- Definition of done:
  - One explicit verdict per variant: `pass_all_gates` or `fail_gates` with exact failed checks.

### T8 - Publish decision pack to Issue #16

- Priority: High
- Deliverables:
  - Short execution log (commands, run IDs, config hash/lineage).
  - Metric table baseline vs v2a vs v2b for both windows.
  - Recommended decision:
    - Promote chosen variant, or
    - Keep `not_promotable` and close cycle.
- Definition of done:
  - Issue #16 has enough evidence for PM final go/no-go without additional reruns.

## Stop rule (strict)

If both v2a and v2b fail contractual gates on 2010-2012 and full span, stop tuning in this cycle,
record `not_promotable`, and close S4-03 as strategy-limited (not plumbing-limited).
