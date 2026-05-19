# OptionTrader S4-03 Regime Labeling Review and Adversarial Assessment

Date: 2026-05-18
Owner: PM
Scope: Decide whether regime labeling/classification must be rethought after post-warm-up reruns.

## Executive answer

Short answer: **you are not missing the point**.

- We fixed **labeling integrity plumbing** (no silent fallback, warm-up exclusion, scope-safe joins).
- We have **not** yet proven that the current regime classification logic is the right one for
  decision quality.

So the correct PM stance is:

- **keep** the plumbing,
- **rethink/tune** parts of the classification design (especially transition behavior).

## What is fixed vs not fixed

### Fixed (infrastructure)

1. Missing regimes are explicit (`Unknown`) and no longer hidden by silent `Neutral` fallback.
2. Warm-up period is excluded from evaluation windows (Policy A).
3. Release payload distinguishes invalid evidence vs no incremental edge.
4. Regime coverage in full-span post-warm-up run is valid (`Calm`, `Transition`, `Stress` observed).

### Not fixed (model quality)

1. Transition-regime false-positive behavior is still worse in candidate vs baseline.
2. Independence is weak:
   - `stress_proxy` is effectively redundant with VIX in current setup
   - payload diagnostics show `correlation_stress_vs_vix = 1.0` and redundancy warning.
3. Event feature is currently disabled (`weight=0.0`), so claimed multi-signal benefit is limited.

## Current evidence snapshot (full span, post-warm-up)

Source: `docs/roadmap/OptionTrader_S4_03_Release_Validation_Payload_full_span_post_warmup.json`

- Baseline precision: `0.14779874213836477`
- Candidate precision: `0.16586151368760063` (non-regression/improvement)
- Transition FP density baseline: `0.5961538461538461`
- Transition FP density candidate: `0.6595744680851063` (worse)
- Taxonomy verdict: `no_incremental_edge_observed`
- Recommendation: `not_promotable`

Interpretation:

- Classification pipeline now works,
- but transition quality gate still fails on substantive behavior.

## Adversarial review (Round 1)

### Attack A - "This is still a labeling bug"

Hypothesis:

- Transition failure is from missing/incorrect labels, not model behavior.

Check:

- Warm-up unknowns removed (`unknown_regime_count=0`).
- Required regimes present.

Verdict:

- **Rejected**. This is no longer a missing-label artifact.

### Attack B - "You call it multi-signal, but signals are not independent"

Hypothesis:

- Classification gain is overstated because features are redundant.

Check:

- Stress proxy correlation to VIX is `1.0` in diagnostics.
- Event weight is zero.

Verdict:

- **Valid attack**. Current feature set does not satisfy strong independence intent.

### Attack C - "Transition gate is too harsh / metric is poorly framed"

Hypothesis:

- FP-density metric may be unstable or misaligned with available outcomes.

Check:

- Transition FP density worsens in both full-span and 2010-2012 reruns.
- Pattern is consistent across windows (not a one-off).

Verdict:

- **Partially valid**. Metric design may deserve refinement, but current evidence still indicates
  no transition-quality improvement.

## Adversarial review (Round 2)

### Attack D - "Maybe thresholds are not calibrated to this dataset"

Hypothesis:

- Regime boundaries (`score_calm_max`, `score_stress_min`) may be mismatched, pushing ambiguous days
  into Transition and inflating false positives.

Verdict:

- **Valid and likely**. Requires targeted threshold calibration protocol (train-only calibration,
  frozen test windows).

### Attack E - "Daily single-label state is too jumpy"

Hypothesis:

- One-day regime flips can create transition noise and unstable gating.

Verdict:

- **Plausible**. Add hysteresis/smoothing experiment as controlled ablation item.

## PM decision

Do we need to rethink regime labeling/classification?

- **Yes, partially**:
  - Not a full rewrite of infrastructure.
  - A targeted rethink of classification quality is required.

Keep:

- Current labeling pipeline, warm-up policy, and evidence contracts.

Rethink:

1. Transition-specific classification boundaries and/or gating policy.
2. Feature independence (replace redundant stress proxy; decide event activation policy).
3. Optional hysteresis to reduce transition label noise.

## Next implementation packet (dev focus)

1. Replace `stress_proxy_ticker` with a genuinely independent cross-asset stress proxy.
2. Add threshold calibration protocol (train-only) and freeze audit fields.
3. Add transition-focused ablation toggles:
   - current thresholds,
   - recalibrated thresholds,
   - optional hysteresis mode.
4. Rerun 2010-2012 + full span with identical artifact schema and compare:
   - transition FP density,
   - precision,
   - volume guardrails.

Exit criterion for S4-03 promotion:

- transition FP density non-worsening must pass,
- with evidence-valid taxonomy,
- and no regression on core precision/volume controls.
