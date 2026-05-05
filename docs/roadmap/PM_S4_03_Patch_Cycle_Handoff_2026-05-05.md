# PM Handoff - S4-03 Patch Cycle (Pre vs Post)

Date: 2026-05-05
Owner handoff scope: summarize what changed after first-principles patches, what improved, what is still blocked, and how to refine acceptance criteria.

## Executive Takeaway

- Patch cycle closed key experiment-integrity risks (profile divergence enforced, history leakage guardrails, QC-only detection input, attrition reporting).
- This changed the evidence surface materially: full-span run now produces decision-relevant sample volume.
- S4-03 still does **not** pass business gates because baseline and candidate outcomes remain identical in current data/config.

## What Was Patched

1. **A/B integrity**: baseline/candidate now run with explicit profiles and different config hashes.
2. **Detection input scope**: metric series now uses QC-eligible rows (`qc_pass=true`) and enforces no-future filtering.
3. **Diagnostics visibility**: non-execution states enabled for EOD diagnostics runs.
4. **Gate observability**: explicit attrition reports added per window.

Primary implementation refs:

- `scripts/materialize_s4_tracks_from_eod.py`
- `src/core/compute_snapshot.py`
- `scripts/report_s4_gate_attrition.py`
- `config/profile_s4_baseline.yaml`
- `config/profile_s4_candidate.yaml`

## Pre vs Post Snapshot

| Window | Pre-patch alerts (base/cand) | Post-patch alerts (base/cand) | Post status |
| --- | ---: | ---: | --- |
| 2010-01-01 to 2012-12-31 | 0 / 0 | 0 / 0 | blocked_pending_precision_labels |
| 2023-01-01 to 2023-12-31 | 0 / 0 | 0 / 0 | blocked_pending_precision_labels |
| 2010-01-01 to 2023-12-31 | 0 / 0 | 695 / 695 | failed_gate |

Pre-patch source:

- `docs/roadmap/OptionTrader_S4_03_Window_Matrix_Results.md`

Post-patch sources:

- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_2010_2012.md`
- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_2023.md`
- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_full_span.md`

## Post-Patch Findings

### 1) Integrity evidence is now explicit

- Full-span artifact records distinct run/profile/hash pairs:
  - baseline: `run_id=19`, `profile=baseline_rv_only`, `config_hash=e6a5...`
  - candidate: `run_id=20`, `profile=candidate_multi_signal`, `config_hash=1a7f...`

Source:

- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_full_span.md`

### 2) Sparse windows remain non-informative

- 2010-2012 and 2023 still produce zero alerts even after integrity fixes.
- Attrition reports show no pass-through beyond early gates in those windows.

Sources:

- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_2010_2012.md`
- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_2023.md`

### 3) Full-span is statistically populated, but incremental value still absent

- Full-span now has enough volume (`695` alerts per track, `683` outcomes per track; min sample gate passes).
- Precision is equal across tracks (`0.0776` vs `0.0776`, delta `0.0`), so precision gate fails.
- Transition FP gate remains non-decisionable (`transition_alerts=0`).

Sources:

- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_full_span.md`
- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_full_span.md`

## Recommended PM Acceptance-Criteria Update

Use a two-stage acceptance contract for this topic:

### Stage A - Engineering Integrity (must pass before business decisioning)

- Distinct baseline/candidate profiles enforced and persisted (`profile_id`, `config_hash`).
- Alert history path proves no lookahead and no cross-underlying contamination.
- Gate attrition report exists for every evaluated window.

### Stage B - Business Effectiveness (only after Stage A)

- Evaluate only windows with decision-grade sample volume.
- If sample is below threshold, classify as `insufficient_statistical_power` (not pass/fail on feature value).
- If sample is adequate and precision/guardrails still show no uplift, classify as `no_incremental_edge_observed` under current signal design.

## Suggested Next Actions

1. Add explicit PM state labels in S4 reporting output: `insufficient_statistical_power`, `no_incremental_edge_observed`, `promotable`.
2. Define stress/transition episode windows where transition-density gate can be evaluated (current full-span has `transition_alerts=0`).
3. Run one additional cycle focused on episode windows before final S4 closure recommendation.
