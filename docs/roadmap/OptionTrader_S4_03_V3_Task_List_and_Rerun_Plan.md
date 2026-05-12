# OptionTrader S4-03 V3 Task List and Rerun Plan

Date: 2026-05-12
Owner split: Dev implements, PM/agent validates
Purpose: Merge remaining Spec-to-Code gaps with one concrete rerun plan.

## Goal

Complete S4-03 V3 evidence validity so regime conclusions are trustworthy.

This plan assumes the already-fixed items remain intact:

- explicit `Unknown` handling (no silent `Neutral` fallback),
- regime precompute in materialization path,
- unknown-regime blocking in release gate.

## Task List (Dev)

### T1 - Scope-safe regime labeling (remove global date-table ambiguity)

- Files: `src/core/regime.py`, `src/core/compute_snapshot.py`, `src/db/schema.sql`, `src/db/init_db.py`, `scripts/validate_release.py`, `scripts/generate_regime_ablation_artifact.py`
- Work:
  - Ensure regime label assignment is snapshot/run scoped, not only global `regime_date` lookup.
  - Preferred: persist `snapshot_id -> regime_label` contract used by alert compute and validators.
- Acceptance:
  - No cross-run contamination risk from shared date-only keys.
  - Same snapshot always resolves to same regime label regardless of unrelated runs.

### T2 - Causality-safe percentile features (remove lookahead)

- Files: `src/core/regime.py`, `tests/test_regime.py`
- Work:
  - Replace full-sample percentile ranking with trailing/expanding history-only percentile logic.
  - Keep deterministic behavior and document warm-up policy.
- Acceptance:
  - No feature at date `t` depends on data after `t`.
  - Tests explicitly fail if lookahead path is reintroduced.

### T3 - Minimum per-regime outcome validity checks

- Files: `scripts/validate_release.py`, `scripts/generate_regime_ablation_artifact.py`, tests
- Work:
  - Add per-regime minimum outcome-count gate for `Calm`, `Transition`, `Stress`.
  - Distinguish invalid evidence from true pass/fail.
- Acceptance:
  - Payload includes per-regime outcome counts and validity booleans.
  - Regime gate cannot pass on sparse/imbalanced outcomes.

### T4 - Threshold freeze audit

- Files: `scripts/validate_release.py`, `src/core/regime.py`, docs/tests
- Work:
  - Add explicit audit that thresholds/config hash were frozen before test window.
  - Emit blocker if freeze evidence is missing or mismatched.
- Acceptance:
  - Validator payload has `threshold_freeze_pass` (or equivalent).
  - Test covers mismatch and aligned cases.

### T5 - Independence diagnostics

- Files: `scripts/validate_release.py`, optionally helper script, docs/tests
- Work:
  - Add component contribution and correlation diagnostics (at least vs VIX and RV20).
  - Flag near-redundant features.
- Acceptance:
  - Payload contains contribution shares and correlation metrics.
  - Diagnostics are generated for baseline and candidate tracks.

### T6 - Event governance checks

- Files: `src/core/regime.py`, `scripts/validate_release.py`, docs/tests
- Work:
  - Extend event governance beyond digest-only: include effective-date immutability checks in validation.
- Acceptance:
  - Validator reports event-calendar governance status and blocks if policy fails.

### T7 - Decision taxonomy alignment (V3)

- Files: `scripts/validate_release.py`, report rendering/tests
- Work:
  - Replace binary recommendation-only semantics with V3 taxonomy:
    - `invalid_evidence`
    - `no_incremental_edge_observed`
    - `incremental_edge_confirmed`
- Acceptance:
  - Final payload/report includes taxonomy verdict and supporting reasons.

### T8 - Fix `unknown_regime_share` denominator

- Files: `scripts/validate_release.py`, tests
- Work:
  - Compute share against candidate alert count (not outcomes observed).
- Acceptance:
  - Payload field definition and value are mathematically correct under sparse outcomes.

## Required Tests (Dev must add/update)

- `tests/test_regime.py` (causality + warm-up)
- `tests/test_regime_filter.py` (unknown handling + scope-safe labeling)
- `tests/test_validate_release.py` (new gate fields, taxonomy, denominator fix)
- New tests for threshold-freeze and per-regime outcome validity.

## Rerun Matrix (after T1-T8)

Run all windows with the same command order.

Windows:

1. `2010-01-01T00:00:00Z` to `2012-12-31T23:59:59Z`
2. `2023-01-01T00:00:00Z` to `2023-12-31T23:59:59Z`
3. `2010-01-01T00:00:00Z` to `2023-12-31T23:59:59Z`

Shared lineages/profiles:

- baseline lineage: `3b024c9`
- candidate lineage: `5128e8e`
- baseline profile: `config/profile_s4_baseline.yaml`
- candidate profile: `config/profile_s4_candidate.yaml`

### Command sequence per window

```bash
source .venv/bin/activate
python scripts/materialize_s4_tracks_from_eod.py \
  --baseline-lineage 3b024c9 \
  --candidate-lineage 5128e8e \
  --baseline-profile config/profile_s4_baseline.yaml \
  --candidate-profile config/profile_s4_candidate.yaml \
  --underlying SPX \
  --start-ts <START_TS> \
  --end-ts <END_TS>

python scripts/evaluate_alert_outcomes.py --horizon-days 5 --overwrite

python scripts/generate_regime_ablation_artifact.py \
  --underlying SPX \
  --start-ts <START_TS> \
  --end-ts <END_TS> \
  --baseline-lineage 3b024c9 \
  --candidate-lineage 5128e8e \
  --horizon-days 5 \
  --output <ABLATION_OUTPUT_MD>

python scripts/report_s4_gate_attrition.py \
  --underlying SPX \
  --start-ts <START_TS> \
  --end-ts <END_TS> \
  --baseline-lineage 3b024c9 \
  --candidate-lineage 5128e8e \
  --output <ATTRITION_OUTPUT_MD>

python scripts/validate_release.py \
  --config-path config/config-eod-truth.yaml \
  --underlying SPX \
  --start-ts <START_TS> \
  --end-ts <END_TS> \
  --baseline-lineage 3b024c9 \
  --candidate-lineage 5128e8e \
  --train-size 252 \
  --test-size 63 \
  --step-size 63 \
  --horizon-days 5 \
  --report-path <VALIDATION_REPORT_MD> \
  --payload-path <VALIDATION_PAYLOAD_JSON> \
  --baseline-capture-path <BASELINE_CAPTURE_JSON>
```

## Expected Output Files

Use window-specific outputs to avoid overwriting canonical artifacts.

- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_2010_2012.md`
- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_2010_2012.md`
- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Report_2010_2012.md`
- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Payload_2010_2012.json`
- `docs/roadmap/OptionTrader_S4_03_Baseline_Capture_2010_2012.json`
- Same 5-file set for `2023` and `full_span`.

## Validation Checklist (PM/agent after dev delivery)

### Code-level validation

1. Run targeted tests:
   - `pytest tests/test_regime.py tests/test_regime_filter.py tests/test_validate_release.py -q`
2. Verify new payload fields exist and are populated:
   - per-regime outcome validity,
   - threshold freeze audit,
   - independence diagnostics,
   - V3 taxonomy verdict.

### Data/result validation per window

1. No silent fallback behavior:
   - no `Neutral` used as missing-regime placeholder.
2. Unknown handling correctness:
   - `unknown_regime_count` and `unknown_regime_share` are correct,
   - unknown-regime gate behavior matches policy.
3. Regime validity:
   - required regimes present or verdict is `invalid_evidence` with explicit reason.
4. Incremental value decision:
   - if evidence valid and candidate lift absent -> `no_incremental_edge_observed`.
   - if evidence valid and lift present -> `incremental_edge_confirmed`.

## Definition of done for this plan

Done only when all are true:

1. T1-T8 are implemented and test-covered.
2. Three-window rerun artifacts are generated with window-specific outputs.
3. Validation checklist passes with explicit taxonomy verdict per window.
4. Sprint docs + issue statuses are updated with evidence links and final state.
