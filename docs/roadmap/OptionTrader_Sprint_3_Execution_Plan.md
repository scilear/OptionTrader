# OptionTrader Sprint 3 Execution Plan

Date: 2026-04-29
Last updated: 2026-04-30
Sprint window: Weeks 3-4
Parent roadmap: `docs/roadmap/OptionTrader_Next_Level_Plan.md`
Prior sprint: `docs/roadmap/OptionTrader_Sprint_2_Execution_Plan.md`

## Sprint Objective

Deliver a fit-driven, quality-scored implied-volatility surface with hard QC blocking so alerts and trade ideas are emitted only from geometrically coherent surfaces.

## Delivered Scope

Implemented:

- Fit/interpolation engine for standardized delta buckets (`src/core/surface_fit.py`).
- Fit diagnostics propagation to `IvPoint` and persistence layers.
- Surface QC module with vertical/calendar checks and configurable tolerance (`src/core/surface_qc.py`).
- Hard-block integration in compute path (`src/core/compute_snapshot.py`).
- Additive schema and migration extensions for fit/QC diagnostics.
- Adversarial + unit test coverage for fit stability and QC block behavior.
- Updated model card with selected model and fallback policy.

Not implemented in Sprint 3 package:

- Full historical replay automation/report publication pipeline.
- Regime redesign or signal state-machine redesign (deferred by roadmap).

## S3 Ticket Outcomes

### S3-00 Baseline Freeze and Measurement Contract

Status: completed (test-contract level)

- Stability contract encoded in adversarial tests as bounded `max ΔIV` under one-strike removal.
- Deterministic check path preserved in test suite.

### S3-01 Surface Model Selection Protocol

Status: completed

- Selected model: `linear_delta_v1`.
- Rejected baseline: nearest-neighbor-only extraction.
- Model card finalized at `docs/roadmap/OptionTrader_Surface_Model_Card.md`.

### S3-02 Fit/Interpolation Engine Wiring

Status: completed

- Added `src/core/surface_fit.py` and integrated into `compute_iv_points`.
- Added exact-hit and interpolated paths with explicit fallback to degraded nearest mode.
- Fit diagnostics carried in `IvPoint` fields:
  - `fit_model_id`, `fit_residual`, `fit_support`, `fit_confidence`, `fit_reason_codes`.

### S3-03 Surface QC Module

Status: completed (post-review corrected)

- Added `src/core/surface_qc.py` with:
  - vertical checks,
  - calendar checks,
  - degraded-fit blocker,
  - quality score output.
- Config tolerance key wired: `qc.no_arb_epsilon`.
- Calendar criterion corrected after code review:
  - replaced ATM-IV-direction check with total-variance monotonicity check,
  - violation now emitted as `calendar_total_variance_violation:<near_bucket>-><far_bucket>`.

### S3-04 Hard-Block Integration

Status: completed

- QC evaluation runs after surface metrics are computed.
- Alerts/trade ideas are suppressed when QC fails.
- Explain payload now contains `surface_qc` gate evidence.

### S3-05 Schema and Persistence

Status: completed

- `iv_points` now persists fit diagnostics.
- `surface_metrics` now persists fit + QC summary diagnostics.
- `init_db` migration path updated with additive columns for existing DBs.

### S3-06 Adversarial Test Pack

Status: completed (code-level)

- Added adversarial tests for one-strike-removal stability and sparse-wing degradation.
- QC and fit test packs added and passing.

## File-Level Change Map

- New:
  - `src/core/surface_fit.py`
  - `src/core/surface_qc.py`
  - `tests/test_surface_fit.py`
  - `tests/test_surface_qc.py`
  - `tests/test_surface_adversarial.py`
- Updated runtime:
  - `src/core/metrics.py`
  - `src/core/compute_snapshot.py`
  - `src/db/schema.sql`
  - `src/db/init_db.py`
  - `src/core/config.py`
  - `config/config-v1.yaml`
  - `config/config-test.yaml`
- Updated tests/regressions:
  - `tests/test_schema.py`
  - `tests/test_explainability.py`
  - `tests/test_tier_logic.py`
  - `tests/test_pricing_inputs.py`
  - `tests/test_regime_filter.py`
  - `tests/test_determinism.py`

## Validation Results

Executed successfully:

```bash
source .venv/bin/activate
pytest -q
```

Result:

- `69 passed`

## Adversarial Review Pass

Adversarial review concerns from `docs/roadmap/OptionTrader_Sprint_3_Review_Report.md` were explicitly integrated:

- Added `qc.no_arb_epsilon` to avoid false hard-blocks from numerical noise.
- Enforced degraded fallback trap: any degraded fit triggers QC failure and alert block.
- Kept fit logic in standalone module for swap/testability.
- Corrected calendar QC directionality to variance-monotonic rule so normal contango is not falsely blocked.

## Remaining Follow-Ups

- Produce a persisted baseline-vs-sprint3 replay artifact in docs with alert-density deltas.
- Add operational dashboard counters for QC reason-code frequencies.
- Split epsilon semantics by domain:
  - keep IV-space epsilon for vertical checks,
  - add dedicated variance-space epsilon for calendar checks.
- Add indexes for scale/perf hardening:
  - `iv_points(snapshot_id)`,
  - `surface_metrics(snapshot_id)`.
- Optionally evaluate higher-order constrained fit class as Sprint 3.1 if needed.
