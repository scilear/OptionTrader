# OptionTrader Sprint 5 Execution Plan

Date: 2026-05-04
Last updated: 2026-05-04 (initial sprint plan)
Sprint window: Weeks 7-8
Parent roadmap: `docs/roadmap/OptionTrader_Next_Level_Plan.md`
Prior sprint: `docs/roadmap/OptionTrader_Sprint_4_Execution_Plan.md`
Ticket sheet: `docs/roadmap/OptionTrader_Sprint_5_Dev_Ticket_Sheet.md`

## Sprint Objective

Redesign the signal engine so alerts are robust, regime-aware, uncertainty-aware, and
promotable through an explicit lifecycle (`Candidate -> Validated -> ExecutionReady`) instead of a
single static z-score gate.

## Carryover Context from Sprint 4

- Sprint 4 implementation quality is materially improved, but S4-03 remains operationally blocked
  by locked-window data sparsity (zero alerts in the locked comparison window).
- Sprint 5 starts in parallel with S4-03 carryover tracking, without weakening fail-closed defaults.
- Production thresholds and runtime safety posture remain unchanged unless separately approved.

## Scope

In scope:

- Robust anomaly scoring in `src/core/alerts.py` (less sensitivity to outliers and sparse tails).
- Signal lifecycle state machine in compute path.
- Uncertainty-aware gating integrated with existing QC and regime safety checks.
- Identifiability guardrails to prevent double-counting correlated evidence (RR/FLY/TERM).
- Deterministic replay artifact for S5 baseline-vs-candidate signal quality checks.

Out of scope:

- Execution-aware trade idea ranking (Sprint 6 scope).
- Changes to trade template inventory.
- Relaxing fail-closed QC policy.

## Planned Tickets

### S5-00 Baseline Freeze and Evaluation Contract

Goal:

- Lock the S5 evaluation contract so redesign work is measured consistently.

Deliverables:

- S5 evaluation contract section in roadmap docs (window, lineages, metrics, reporting format).
- Baseline signal snapshot from current mainline behavior.

Acceptance:

- S5 metrics are reproducible from one command set with no manual interpretation.

### S5-01 Robust Scoring Core

Goal:

- Replace fragile static-only anomaly behavior with robust scoring primitives.

Deliverables:

- Updated scoring path in `src/core/alerts.py` (robust location/dispersion handling).
- Deterministic handling for sparse/flat histories (explicit no-signal outcomes, not silent drift).

Acceptance:

- Robust scoring logic is unit-tested for sparse, noisy, and flat-series edge cases.

### S5-02 Signal Lifecycle State Machine

Goal:

- Introduce explicit signal states and deterministic transitions.

Deliverables:

- Lifecycle states persisted/exposed in compute outputs:
  - `Candidate`
  - `Validated`
  - `ExecutionReady`
- Transition reasons emitted in explain payloads.

Acceptance:

- Transition rules are deterministic and test-covered.

### S5-03 Uncertainty-Aware Gating

Goal:

- Block promotion when uncertainty or quality conditions are not met.

Deliverables:

- Compute-path gating that incorporates:
  - surface QC status,
  - fit confidence/quality,
  - regime-state staleness/hash mismatch warnings,
  - worst-case metric coherence.

Acceptance:

- Uncertainty and worst-case block paths are explicitly tested.

### S5-04 Identifiability and Correlation Guardrails

Goal:

- Prevent inflated confidence from correlated metric co-moves.

Deliverables:

- Guard logic that downweights or de-duplicates overlapping RR/FLY/TERM evidence.
- Explain payload extension for "evidence overlap" diagnostics.

Acceptance:

- Perturbation tests show ranking/order stability under correlated metric shocks.

### S5-05 Replay Evidence and Release Gate

Goal:

- Prove S5 redesign improves signal quality without unsafe alert inflation.

Deliverables:

- S5 replay artifact comparing baseline vs redesigned signal engine.
- False-positive density and volume delta summary by regime.

Acceptance:

- Transition-regime false-positive density is lower than baseline on the locked S5 evaluation contract.
- Alert volume inflation is bounded by the agreed guardrail in the S5 contract.
- Promotion decision documented as pass/fail with machine-readable evidence.

## Expected Files

- `src/core/alerts.py`
- `src/core/compute_snapshot.py`
- `src/db/schema.sql` (only if lifecycle persistence requires schema extension)
- `src/db/init_db.py` (migration-safe updates if schema changes)
- `src/app/streamlit_app.py` (state visibility only, no major UI redesign)
- `tests/test_alerts_logic.py`
- `tests/test_regime_filter.py`
- `tests/test_s4_ablation.py` (if shared gate helpers are reused)
- new S5 tests for lifecycle, uncertainty paths, and identifiability perturbations
- `docs/roadmap/OptionTrader_Sprint_5_Dev_Ticket_Sheet.md`

## Definition of Done

Sprint 5 is done only when all are true:

1. Signal lifecycle states are deterministic and explainable.
2. Uncertainty and worst-case paths are fail-closed and test-covered.
3. Correlation/identifiability guardrails reduce evidence double-counting risk.
4. Replay evidence shows quality improvement without unsafe alert-volume inflation.
5. Promotion decision is documented with reproducible artifact output.

## Validation Commands

```bash
source .venv/bin/activate
pytest tests/test_alerts_logic.py tests/test_regime_filter.py -q
pytest -q
```
