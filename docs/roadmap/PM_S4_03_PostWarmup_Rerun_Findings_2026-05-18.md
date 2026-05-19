# PM Handoff - S4-03 Post-Warmup Rerun Findings

Date: 2026-05-18
Owner handoff: PM orchestration update
Scope: Taxonomy fix + post-warm-up reruns (2010-2012, 2023, full span)

## Executive Outcome

- Warm-up exclusion (Policy A) remains correctly applied.
- Taxonomy logic has been corrected in validator classification.
- Promotion remains blocked for S4-03.

## What Changed in Logic

Updated in `scripts/validate_release.py`:

- `incremental_edge_confirmed` now requires transition non-worsening in addition to precision lift.
- Valid-evidence-but-failed-performance cases now classify as `no_incremental_edge_observed`.
- `invalid_evidence` is reserved for true evidence invalidity/sparsity.

## Window Results

### 1) Full span (post warm-up)

Artifacts:

- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Report_full_span_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Payload_full_span_post_warmup.json`
- `docs/roadmap/OptionTrader_S4_03_Baseline_Capture_full_span_post_warmup.json`

Result:

- `taxonomy_verdict`: `no_incremental_edge_observed`
- `recommendation`: `not_promotable`
- Baseline precision: `0.14779874213836477`
- Candidate precision: `0.16586151368760063`
- Transition FP density baseline: `0.5961538461538461`
- Transition FP density candidate: `0.6595744680851063`
- Transition delta: `+0.06342062193126019` (worse)

### 2) 2010-2012 (post warm-up)

Artifacts:

- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Report_2010_2012_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Payload_2010_2012_post_warmup.json`
- `docs/roadmap/OptionTrader_S4_03_Baseline_Capture_2010_2012_post_warmup.json`

Result:

- `taxonomy_verdict`: `no_incremental_edge_observed`
- `recommendation`: `not_promotable`
- Baseline precision: `0.14545454545454545`
- Candidate precision: `0.14545454545454545`
- Transition FP density baseline: `0.38596491228070173`
- Transition FP density candidate: `0.4533333333333333`
- Transition delta: `+0.06736842105263158` (worse)

### 3) 2023

Artifacts:

- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Report_2023_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Payload_2023_post_warmup.json`
- `docs/roadmap/OptionTrader_S4_03_Baseline_Capture_2023_post_warmup.json`

Result:

- `taxonomy_verdict`: `invalid_evidence`
- `recommendation`: `not_promotable`
- Reason: no candidate alerts/outcomes in window (`candidate_alert_count=0`).

## Supporting Artifacts (Ablation + Attrition)

- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_full_span_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_full_span_post_warmup.md`
- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_2010_2012_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_2010_2012_post_warmup.md`
- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_2023_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_2023_post_warmup.md`

## PM Decision Frame

- Evidence-shape blockers from regime warm-up are resolved.
- Promotion remains blocked by substantive transition false-positive degradation.
- Next dev focus should be narrow and explicit: reduce Transition FP density without inflating alert volume.
