# OptionTrader Sprint 7 Execution Plan

Date: 2026-05-07
Last updated: 2026-05-08 (canonical validation completed)
Sprint window: Weeks 11-12
Parent roadmap: `docs/roadmap/OptionTrader_Next_Level_Plan.md`
Prior sprint: `docs/roadmap/OptionTrader_Sprint_6_Execution_Plan.md`
Ticket sheet: `docs/roadmap/OptionTrader_Sprint_7_Dev_Ticket_Sheet.md`

## Sprint Objective

Enforce release-grade validation and governance so promotion decisions are blocked unless out-of-sample,
adversarial, and falsification evidence all pass under a locked contract.

## Carryover Context

- Sprint 6 closed with implementation-complete evidence and a promotable recommendation under
  `S6-CONTRACT-v1`.
- S4-03 remains an active research/governance stream and should not silently alter release standards.
- Sprint 7 is the release-control sprint: no production promotion without S7 gate pass.

## Scope

In scope:

- Walk-forward evaluation framework with deterministic split definitions.
- Release validation script that emits machine-readable pass/fail payload.
- Adversarial test suite for sparse/stale/discontinuous chain scenarios.
- Regime-stratified falsification report and component ablation ledger.
- Final release recommendation artifact and gate audit trail.

Out of scope:

- New alpha/signal feature invention.
- Major strategy redesign.
- Manual promotion decisions without artifact evidence.

## S7 Locked Validation Contract (v1)

Contract ID: `S7-CONTRACT-v1`

- Underlying: `SPX`
- Config baseline: `config/config-eod-truth.yaml` (or approved release config)
- Evaluation mode: deterministic walk-forward (fixed train/test cadence and horizon)
- Required evidence axes:
  1. OOS quality and stability,
  2. adversarial resilience,
  3. regime-stratified performance,
  4. component ablation sensitivity,
  5. release policy compliance.

Gate principles:

1. Promotion is blocked if any contract gate fails.
2. Gates must be computed by script, not manual spreadsheet logic.
3. Falsification findings must be recorded even when recommendation is promotable.

## Planned Tickets

### S7-00 Validation Contract Freeze and Baseline Capture

Goal:

- Lock split policy, gate thresholds, and report schema before final validation runs.

Deliverables:

- Contract section and baseline capture reference in docs.
- Versioned baseline validation payload.

Acceptance:

- Contract is explicit, reproducible, and versioned.

### S7-01 Walk-Forward Evaluation Hooks

Goal:

- Make replay evaluation walk-forward and deterministic.

Deliverables:

- Walk-forward hooks in replay/validation pipeline.
- Explicit split metadata in output payloads.

Acceptance:

- Same inputs produce identical split schedule and metrics.

### S7-02 Automated Release Validator

Goal:

- Implement one command that returns release pass/fail with gate breakdown.

Deliverables:

- `scripts/validate_release.py`.
- Machine-readable payload with per-gate decisions and final recommendation.

Acceptance:

- Script exits non-zero on failed release gate.
- Payload includes all required gate fields.

### S7-03 Adversarial Test Suite Hardening

Goal:

- Ensure system remains fail-closed under pathological market-data conditions.

Deliverables:

- Tests for sparse wings, stale books, missing tenors, discontinuous chain snapshots.
- Explicit expected blocker reasons in assertions.

Acceptance:

- Adversarial tests are deterministic and integrated into regular test workflow.

### S7-04 Regime-Stratified Falsification and Ablation Ledger

Goal:

- Prove gains are not concentrated in one narrow regime/component artifact.

Deliverables:

- Regime-stratified report (Calm/Transition/Stress).
- Ablation ledger documenting retained/removed components and evidence.

Acceptance:

- Ledger is complete, reproducible, and linked to final recommendation.

### S7-05 Final Release Report and Recommendation

Goal:

- Publish one PM/dev consumable report with release decision and rationale.

Deliverables:

- `docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Report.md`.
- Final recommendation label: `promotable` or `not_promotable`.

Acceptance:

- Report includes command block, payload summary, and gate-by-gate interpretation.

### S7-06 CI/Process Gate Integration

Goal:

- Ensure release-gate checks are enforceable and not optional.

Deliverables:

- CI hook or documented release command policy using `validate_release.py`.
- Issue/ticket closure checklist requiring attached evidence artifacts.

Acceptance:

- Release process cannot be completed without gate outputs.

## Expected Files

- `src/core/replay.py`
- `scripts/validate_release.py`
- `scripts/generate_replay_artifact.py` (or S7-specific artifact generator updates)
- `tests/` adversarial validation additions
- `docs/roadmap/OptionTrader_Sprint_7_Dev_Ticket_Sheet.md`
- `docs/roadmap/OptionTrader_Sprint_7_Release_Validation_Report.md`

## Definition of Done

Sprint 7 is done only when all are true:

1. Walk-forward outputs are deterministic and reproducible.
2. `validate_release.py` emits complete gate payload and final recommendation.
3. Adversarial suite passes and is integrated into validation workflow.
4. Regime-stratified and ablation evidence are included in release decision.
5. Promotion decision is script-backed and documented in final report.

## Validation Commands

```bash
source .venv/bin/activate
pytest -q
python scripts/validate_release.py --config-path config/config-eod-truth.yaml
```

## Progress Update (2026-05-07)

Completed this pass:

- `S7-01`: deterministic walk-forward replay hooks implemented in `src/core/replay.py`.
- `S7-02` (initial): release validator implemented in `scripts/validate_release.py` with
  machine-readable payload, artifact writing, and pass/fail exit codes.
- `S7-03` (partial): adversarial gate connected to currently available deterministic evidence
  and now backed by explicit pytest scenario selectors.
- `S7-04` (partial): validator now emits regime-stratified payload sections and a
  component ablation ledger sourced from active config weights.

Tests added:

- `tests/test_s7_walk_forward.py`
- `tests/test_validate_release.py`
- `tests/test_surface_adversarial.py` additions for S7 adversarial scenarios

Process hook added:

- `scripts/run_release_gate.sh` wraps mandatory `validate_release.py` invocation for
  release checks.

Pending in next pass:

- Deepen regime falsification gate thresholds once lineage window has sufficient observed outcomes
  (`S7-04`).
- Complete final report and process integration wiring (`S7-05`, `S7-06`).

## Resume Update (2026-05-08)

Canonical validation completed after lock release:

```bash
source .venv/bin/activate
python scripts/validate_release.py --config-path config/config-eod-truth.yaml
```

Outcome:

- Walk-forward gate: PASS
- Adversarial gate: PASS
- Ablation ledger gate: PASS
- Regime falsification gate: FAIL
- Overall gate: FAIL
- Recommendation: `not_promotable`

Blocking rationale captured by script payload:

- Required regime coverage (`Calm`, `Transition`, `Stress`) not satisfied for candidate window
  (observed regime labels contain only `Neutral`).
- Transition false-positive density comparison unavailable due to missing transition alerts.
