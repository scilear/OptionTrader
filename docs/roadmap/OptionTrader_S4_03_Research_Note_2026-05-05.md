# OptionTrader S4-03 Research Note (2026-05-05)

Date: 2026-05-05
Scope: Research framing after patch cycle and full-span ablation evidence.
Key references:
- `docs/roadmap/PM_S4_03_Patch_Cycle_Handoff_2026-05-05.md`
- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_full_span.md`
- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_full_span.md`

## Current Conclusion

S4-03 is not promotable under the current signal/feature design.

- Engineering integrity is now materially improved (A/B profile separation, leakage controls,
  QC-aware detection path, attrition reporting).
- Business gate result still fails on full-span evidence due no incremental uplift:
  - precision delta = `0.0`
  - transition gate non-decisionable in current windows (`transition_alerts=0`)

Status classification:

- full-span: `no_incremental_edge_observed`
- sparse windows: `insufficient_statistical_power`

## What This Means

- This does not invalidate the overall roadmap.
- It does invalidate the current S4-03 claim that retained independent regime features improve
  outcomes under the measured contract.
- Runtime safety posture should remain conservative (`event` and `stress_proxy` disabled by default)
  until a revised design demonstrates measurable uplift.

## Research Questions (Next Cycle)

1. Are current event/stress features too weak/noisy relative to existing gates?
2. Are we measuring uplift on the right regime windows (especially Transition episodes)?
3. Is outcome labeling horizon appropriate for this strategy class (calendar-day vs trading-day)?
4. Are we dealing with a genuinely low-frequency overlay where event-based evaluation is more
   appropriate than broad precision uplift?

## Research Work Package (Time-boxed)

Time-box: 2-3 weeks max.

R1. Feature redesign candidates

- propose 1-2 stronger independent stress/event feature variants,
- include explicit rationale and expected directional effect.

R2. Episode-window contract

- define fixed stress/transition episode windows,
- rerun baseline vs candidate only on those documented windows,
- publish decision metrics with same reproducibility standards.

R3. Outcome-label robustness

- test horizon sensitivity (`horizon_days` variants),
- document whether conclusions are stable across reasonable horizons.

R4. Decision framework update

- if still no uplift: formally retire current S4-03 feature branch and keep disabled defaults,
- if uplift appears in episode windows: propose revised acceptance contract with explicit scope limits.

## Exit Criteria for Research Cycle

Research cycle ends with one of two outcomes:

1. `promotable`:
   - reproducible incremental uplift under revised, approved contract.
2. `retire_current_design`:
   - no reproducible uplift after time-boxed redesign attempts.

No third indefinite state.
