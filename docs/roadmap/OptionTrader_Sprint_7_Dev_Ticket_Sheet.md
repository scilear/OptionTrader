# OptionTrader Sprint 7 Dev Ticket Sheet

Date: 2026-05-07
Last updated: 2026-05-08 (canonical validation rerun)
Source plan: `docs/roadmap/OptionTrader_Sprint_7_Execution_Plan.md`
Sprint: Weeks 11-12

## Ticket Board Snapshot

| Ticket | Objective | Priority | Status | Evidence |
|---|---|---|---|---|
| S7-00 | Validation contract freeze + baseline capture | P0 | Done | `docs/roadmap/OptionTrader_Sprint_7_Execution_Plan.md`, `docs/roadmap/OptionTrader_Sprint_7_Baseline_Capture_v1.json` |
| S7-01 | Walk-forward replay hooks | P0 | Done | `src/core/replay.py`, `tests/test_s7_walk_forward.py` |
| S7-02 | Automated release validator | P0 | Done | `scripts/validate_release.py`, `tests/test_validate_release.py` |
| S7-03 | Adversarial suite hardening | P0 | Done | `tests/test_surface_adversarial.py`, validator adversarial gate checks |
| S7-04 | Regime falsification + ablation ledger | P0 | Done | regime-stratified payload + component ledger in validator output |
| S7-05 | Final release report + recommendation | P0 | Done | `docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Report.md`, `docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Payload.json` |
| S7-06 | CI/process gate integration | P1 | Done | `scripts/run_release_gate.sh`, `docs/roadmap/OptionTrader_Release_Gate_Checklist.md` |

## Ticket Details

### S7-00 - Validation Contract Freeze and Baseline Capture

- Objective:
  - Lock S7 contract and baseline payload before validation iteration.
- Files:
  - `docs/roadmap/OptionTrader_Sprint_7_Execution_Plan.md`
  - `docs/roadmap/OptionTrader_Sprint_7_Dev_Ticket_Sheet.md`
- Tasks:
  - Version contract (`S7-CONTRACT-v1`) with gate schema and threshold definitions.
  - Capture baseline payload and version in roadmap docs.
- Acceptance:
  - [x] Contract is explicit and versioned.
  - [x] Baseline capture artifact is committed.

### S7-01 - Walk-Forward Evaluation Hooks

- Objective:
  - Add deterministic walk-forward split logic to replay path.
- Files:
  - `src/core/replay.py`
  - replay artifact scripts
- Tasks:
  - Implement fixed split schedule and metadata emission.
  - Ensure reproducibility for identical inputs.
- Acceptance:
  - [x] Split schedule is deterministic and test-covered.

### S7-02 - Automated Release Validator

- Objective:
  - Produce script-first release decisioning.
- Files:
  - `scripts/validate_release.py`
  - tests for payload schema/gates
- Tasks:
  - Implement per-gate computations and final recommendation.
  - Return non-zero exit code on failed release gate.
- Acceptance:
  - [x] Full gate payload is emitted in machine-readable format.
  - [x] Script enforces pass/fail via exit code.

### S7-03 - Adversarial Test Suite Hardening

- Objective:
  - Validate fail-closed behavior under adverse data conditions.
- Files:
  - `tests/` adversarial cases
- Tasks:
  - Add sparse/stale/discontinuous and missing-tenor scenarios.
  - Assert deterministic blocker reasons.
- Acceptance:
  - [x] Adversarial tests pass and are integrated in validation workflow.

### S7-04 - Regime-Stratified Falsification and Ablation Ledger

- Objective:
  - Demonstrate robustness across regimes and components.
- Files:
  - stratified report and ablation ledger docs under `docs/roadmap/`
- Tasks:
  - Generate Calm/Transition/Stress-stratified metrics.
  - Document retained/removed component decisions with evidence references.
- Acceptance:
  - [x] Falsification and ablation artifacts are reproducible and complete.

### S7-05 - Final Release Report and Recommendation

- Objective:
  - Publish final S7 release decision package.
- Files:
  - `docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Report.md`
- Tasks:
  - Summarize gate results and final recommendation label.
  - Include exact command blocks and payload references.
- Acceptance:
  - [x] Report is self-contained and decision-ready.

### S7-06 - CI/Process Gate Integration

- Objective:
  - Prevent bypass of release-gate process.
- Files:
  - CI/policy docs and checklist artifacts
- Tasks:
  - Wire or document mandatory `validate_release.py` gate in release path.
  - Add closure checklist requiring evidence attachments.
- Acceptance:
  - [x] Release path cannot complete without gate evidence.

## Suggested Delivery Order

1. S7-00
2. S7-01
3. S7-02
4. S7-03
5. S7-04
6. S7-05
7. S7-06

## End-of-Sprint Validation Commands

```bash
source .venv/bin/activate
pytest -q
python scripts/validate_release.py --config-path config/config-eod-truth.yaml
```

## Progress Notes (2026-05-07)

- Implemented deterministic walk-forward replay hooks in `src/core/replay.py`:
  - `WalkForwardSplit`
  - `build_walk_forward_splits()`
  - `_fetch_ordered_snapshot_rows()`
  - `replay_walk_forward()`
- Added walk-forward tests in `tests/test_s7_walk_forward.py`.
- Implemented release validator script `scripts/validate_release.py`:
  - Emits machine-readable gate payload
  - Writes Sprint 7 report + JSON payload artifacts
  - Exits `0` on overall pass, `2` on gate failure, `3` on missing lineage data
- Added validator smoke test in `tests/test_validate_release.py`.
- Added adversarial scenario coverage in `tests/test_surface_adversarial.py` for:
  - sparse wings
  - stale books
  - missing tenors
  - discontinuous chain snapshots
- Wired validator adversarial gate to run those exact scenario tests via pytest selectors.
- Added regime-stratified payload sections and component ablation ledger extraction in validator.
- Added release gate wrapper command: `scripts/run_release_gate.sh`.

## Resume Update (2026-05-08)

- Canonical command rerun after DB lock release:
  - `python scripts/validate_release.py --config-path config/config-eod-truth.yaml`
- Generated/updated artifacts:
  - `docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Report.md`
  - `docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Payload.json`
  - `docs/roadmap/OptionTrader_Sprint_7_Baseline_Capture_v1.json`
- Gate results from canonical run:
  - `walk_forward_pass`: PASS
  - `adversarial_resilience_pass`: PASS
  - `ablation_ledger_pass`: PASS
  - `regime_falsification_pass`: FAIL
  - `overall_pass`: FAIL
- Recommendation: `not_promotable`.
- Blocking conditions in payload:
  - `missing_regimes`: required `Calm`, `Transition`, `Stress` not all present in observed data
    (observed: `Neutral` only).
  - `transition_fp_density_blocked_reason`: `missing_transition_alerts`.

## Update (2026-05-11)

- Canonical validation rerun executed:
  - `python scripts/validate_release.py --config-path config/config-eod-truth.yaml`
- Artifacts refreshed in-place:
  - `docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Report.md`
  - `docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Payload.json`
  - `docs/roadmap/OptionTrader_Sprint_7_Baseline_Capture_v1.json`
- Release-process enforcement documented explicitly:
  - `docs/roadmap/OptionTrader_Release_Gate_Checklist.md`
- Sprint 7 GitHub issue closure completed for S7-00 through S7-05; S7-06 is now doc-complete.
