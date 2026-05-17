# PM Delta - S4-03 Warm-up Exclusion Evidence

Date: 2026-05-17
Owner handoff: Dev -> PM
Scope: post-warm-up full-span rerun only (`2010-01-01` to `2023-12-31` request)

## Outcome

- Warm-up exclusion is now applied automatically via Policy A in S4/S7 validators and reports.
- Effective evaluation window shifted to `2010-04-05T00:00:00Z` (`warmup_excluded_days=94`).
- Final release recommendation remains `not_promotable` under fail-closed policy.

## New Evidence (Post-Warm-up Full Span)

Source payload: `docs/roadmap/OptionTrader_S4_03_Release_Validation_Payload_full_span_post_warmup.json`

- `window.requested_start_ts`: `2010-01-01T00:00:00Z`
- `window.effective_start_ts`: `2010-04-05T00:00:00Z`
- `window.warmup_exclusion_applied`: `true`
- `window.warmup_excluded_days`: `94`
- `regime_falsification.unknown_regime_count`: `0`
- `regime_falsification.unknown_regime_pass`: `true`
- `regime_falsification.precision_non_regression`: `true`
- `regime_falsification.baseline.precision`: `0.14779874213836477`
- `regime_falsification.candidate.precision`: `0.16586151368760063`

## Active Blocker (Only)

- `regime_falsification.transition_fp_density_non_worsening`: `false`
- Baseline transition FP density: `0.5961538461538461`
- Candidate transition FP density: `0.6595744680851063`
- Delta (candidate - baseline): `+0.06342062193126019`

Blocking taxonomy in payload:

- `taxonomy_verdict`: `invalid_evidence`
- `recommendation`: `not_promotable`
- `regime_falsification.blocked_reasons`: `["transition_fp_density_worsened"]`

## Artifact Set Regenerated

- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_full_span_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_full_span_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Report_full_span_post_warmup.md`
- `docs/roadmap/OptionTrader_S4_03_Release_Validation_Payload_full_span_post_warmup.json`
- `docs/roadmap/OptionTrader_S4_03_Baseline_Capture_full_span_post_warmup.json`

## PM Decision Frame

- Evidence-shape blockers from regime warm-up are closed.
- Promotion is still blocked by substantive transition false-positive behavior.
