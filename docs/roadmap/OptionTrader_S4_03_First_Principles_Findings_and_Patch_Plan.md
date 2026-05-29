# OptionTrader S4-03 First-Principles Findings and Patch Plan

Date: 2026-05-05
Scope: Diagnose why S4-03 remains statistically non-informative on EOD truth data and define exact
engineering patch sequence.

## Executive Diagnosis

Current S4-03 evidence is not decision-grade yet, primarily because experiment integrity and detection
pipeline behavior are misaligned with the intended ablation contract.

This is not sufficient evidence to reject the business idea. It is sufficient evidence to patch the
spec/implementation before drawing business conclusions.

## Confirmed Findings (with Sources)

1. Baseline/candidate tracks are not proven behaviorally distinct in current workflow.
   - Source code path: `scripts/materialize_s4_tracks_from_eod.py`.
   - Both tracks are cloned then computed through the same active compute path with no explicit
     profile switch.
   - Local DB overlap check (2026-05-05) showed identical metric values for overlapping rows.

2. QC failure dominates metric rows and suppresses downstream signal opportunities.
   - Local DB check on `/mnt/Data/EVA/optiontrader_eod_truth.duckdb` (2026-05-05):
     - baseline metrics rows: 794,
     - QC pass rows: 57,
     - QC fail rows: 737.
   - Dominant reason code: `vertical_negative_fly25`.
   - Source logic: `src/core/surface_qc.py` hard-fails when `fly25_mid < -epsilon`.

3. Alert detection currently uses all metric rows (including QC-failed rows) for z-score generation.
   - Source code path: `src/core/compute_snapshot.py` (`metric_series` query has no `qc_pass` filter).
   - Local first-principles check (2026-05-05):
     - `compute_alerts()` on all rows: 0 alerts,
     - `compute_alerts()` on QC-pass-only rows: 3 alerts (same params).

4. Observability is reduced in diagnostics mode.
   - `config/config-eod-truth.yaml` sets `alerts.emit_non_execution_states: false`.
   - This hides Candidate/Validated states that are useful during attrition debugging.

5. Validation data quality itself is not the primary blocker.
   - Source: `docs/roadmap/OptionTrader_S4_03_EOD_Validation_Report.md`.
   - Hard checks passed; DB has high row counts and no obvious key/quote integrity failures.

## Root-Cause Hypothesis (Ranked)

P0 root causes:

- A/B experiment contract violation risk (label-level lineage, no enforced model divergence).
- Detection series contamination by QC-failed metrics in anomaly scoring input.

P1 root causes:

- QC criterion calibration mismatch (`vertical_negative_fly25` as dominant hard fail across this EOD
  representation).
- Insufficient diagnostic visibility due to suppressed non-execution states.

## Patch Plan (Exact Sequence)

### Patch 1 (P0): Enforce true baseline/candidate divergence

Files:

- `scripts/materialize_s4_tracks_from_eod.py`
- `config/` profile files for baseline vs candidate

Changes:

- Add explicit run profiles:
  - baseline profile (RV-only behavior),
  - candidate profile (multi-signal behavior).
- Persist profile identifier in `pipeline_runs` metadata or run notes.
- Fail materialization if both profiles resolve to the same effective config hash.

Acceptance:

- Baseline/candidate effective config hashes are different by design.
- Artifact includes profile IDs and hashes for both tracks.

### Patch 2 (P0): Restrict detection input to quality-eligible metrics

Files:

- `src/core/compute_snapshot.py`
- `tests/test_alerts_logic.py`
- `tests/test_regime_filter.py`

Changes:

- Build `metric_series` for alert scoring from QC-eligible rows (or add explicit config knob with
  strict default in EOD evidence mode).
- Keep execution gating fail-closed.

Acceptance:

- Alert-generation scope is deterministic and test-covered.
- No cross-track contamination or lookahead leakage in metric history path.

### Patch 3 (P1): Add gate-attrition waterfall reporting

Files:

- new `scripts/report_s4_gate_attrition.py`
- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report.md`

Changes:

- Report counts through gates in order:
  1) QC,
  2) z-score threshold,
  3) persistence,
  4) regime block,
  5) tradability,
  6) lifecycle promotion.

Acceptance:

- Report generated per lineage and per window.
- Dominant bottleneck gate is explicitly visible.

### Patch 4 (P1): QC criterion review and calibration protocol

Files:

- `src/core/surface_qc.py`
- `tests/test_surface_qc.py`
- roadmap docs

Changes:

- Reassess `vertical_negative_fly25` as a hard fail for this EOD representation.
- If retained as hard fail, document rationale and expected pass-rate band.
- If adjusted, implement as controlled contract change with before/after evidence.

Acceptance:

- QC policy is explicit and justified by reproducible diagnostics, not ad hoc tuning.

### Patch 5 (P1): Diagnostics mode visibility

Files:

- `config/config-eod-truth.yaml`
- runbook docs

Changes:

- Set diagnostics runs to `alerts.emit_non_execution_states: true`.
- Keep production recommendation path unchanged unless separately approved.

Acceptance:

- Candidate and Validated counts are observable in evidence runs.

## Re-run Matrix After Patches

Run windows:

1. 2010-01-01 to 2012-12-31
2. 2023-01-01 to 2023-12-31
3. full available span in EOD DB
4. additional windows once 2018-2022 are ingested

For each window, publish:

- snapshots per lineage,
- alerts per lineage,
- outcomes observed,
- precision and transition FP density,
- attrition waterfall.

## Decision Rule After Patch Cycle

- If counts and gates become adequate: proceed to S4-03 closure recommendation.
- If counts remain tiny after integrity fixes: classify as `insufficient_statistical_power` and
  evaluate as low-frequency overlay under revised acceptance criteria.

## Suggested Owner Mapping

- Experiment integrity and track materialization: S4-03 issue `#13`
- Detection input and gate attrition diagnostics: S4-03 issue `#16`
- QC calibration review: S4-03 issue `#14`
- Parser/idempotency/data guarantees: S4-03 issues `#12`, `#15`
