# OptionTrader Sprint 1 Execution Plan

Date: 2026-04-28
Sprint window: Week 1
Parent roadmap: `docs/roadmap/OptionTrader_Next_Level_Plan.md`
Upstream critique map: `docs/roadmap/OptionTrader_Critique_to_Action_Map.md`

## Sprint Objective

Freeze a reproducible baseline and make every pipeline run and alert auditable.

Sprint 1 is successful only if all three are true:

- identical input data + config + code state produce identical metrics, alerts, and trade ideas,
- every persisted alert carries machine-readable decision evidence,
- rates and dividend assumptions are explicit runtime inputs, not hidden `0.0` defaults.

## Current Baseline Facts

These are the gaps visible in the current code:

- `scripts/run_pipeline.py` orchestrates the run but does not persist run provenance.
- `src/core/compute_snapshot.py` persists a thin `explain` payload and hardcodes `rate=0.0` and `div=0.0` when building trade ideas.
- `src/core/metrics.py` hardcodes `rate=0.0` and `div=0.0` when solving IV and selecting the forward-based ATM point.
- `src/ingest/dispatcher.py`, `src/ingest/ingest_ib.py`, and `src/ingest/ingest_yfinance.py` insert snapshots without any run linkage.
- The pricing primitives in `src/core/iv_solve.py` already support non-zero `rate` and `div`, so the main gap is caller plumbing, not model replacement.

## Assumptions

- Sprint 1 is a hardening sprint for the current v1 pipeline, not a surface-model or signal-model redesign sprint.
- Reproducibility means same config hash + same code version + same stored input data should yield the same downstream rows.
- The simplest acceptable provenance design is one run-manifest table plus a direct link from snapshots to the run that produced them.

## Explicit Tradeoffs

- Prefer `pipeline_runs` + `snapshots.run_id` over a separate mapping table.
  - Reason: one snapshot-producing pipeline path exists today, so extra indirection is unnecessary.
- Capture `code_version` as `git_sha` plus optional dirty marker, not a full diff archive.
  - Reason: enough provenance for Sprint 1 without introducing artifact storage.
- Thread pricing inputs through the existing compute path instead of changing `src/core/iv_solve.py` behavior.
  - Reason: smaller change set and lower regression risk.

## Implementation Decisions (Locked)

- Add a nullable `run_id` foreign key on `snapshots`.
  - Reason: keeps migration additive and avoids breaking legacy/manual inserts.
- Pass `run_id` explicitly through ingest function signatures.
  - `scripts/run_pipeline.py` calls `run_ingest(run_id=run_id)`.
  - `src/ingest/dispatcher.py` forwards `run_id` to IB/yfinance ingest paths.
  - `src/ingest/ingest_ib.py` and `src/ingest/ingest_yfinance.py` include `run_id` in snapshot inserts.
- Replace global snapshot lookup in pipeline with run-scoped lookup.
  - `_latest_snapshot_id()` must become `_latest_snapshot_id(run_id: int)` and query by `WHERE run_id = ?`.
- Introduce explicit config keys for pricing assumptions under a new top-level block:
  - `pricing.rate`
  - `pricing.dividend_yield`

## In Scope

- Run manifest persistence with terminal status tracking.
- Stable config digest generation and tests.
- Structured alert decision trace persistence.
- Explicit pricing baseline inputs for rates and dividend yield.
- Determinism and provenance regression tests for the above.

## Out of Scope

- Surface fitting or no-arbitrage engine work.
- Regime redesign.
- Signal state-machine redesign.
- Execution impact or edge-after-friction redesign.

## Expected Files

- `scripts/run_pipeline.py`
- `src/ingest/dispatcher.py`
- `src/ingest/ingest_ib.py`
- `src/ingest/ingest_yfinance.py`
- `src/core/compute_snapshot.py`
- `src/core/config.py`
- `src/core/metrics.py`
- `config/config-v1.yaml`
- `src/db/schema.sql`
- `tests/test_schema.py`
- `tests/test_alerts_logic.py`
- `tests/test_iv_solve.py`
- new tests for run manifest, config digest, determinism, and rate/dividend sensitivity

## Work Breakdown

### S1-01: Run Manifest and Snapshot Linkage

Goal:
- Persist enough provenance to attribute every pipeline output to one run.

Change:
- Add `pipeline_runs` to `src/db/schema.sql` with `run_id`, timestamps, `status`, `config_hash`, `code_version`, and `error_message`.
- Add nullable `snapshots.run_id` (FK to `pipeline_runs.run_id`) so downstream rows can be traced through `snapshot_id`.
- Update `scripts/run_pipeline.py` to:
  - create run row and capture `run_id` before ingest,
  - call `run_ingest(run_id=run_id)`,
  - resolve snapshot using run-scoped lookup (`WHERE run_id = ?`),
  - close run row as `success` or `failed` in a `finally` path.
- Update ingest path signatures and inserts:
  - `src/ingest/dispatcher.py::run_ingest(run_id: int | None = None)`
  - `src/ingest/ingest_ib.py::try_ingest_ib(config: dict, run_id: int | None = None)`
  - `src/ingest/ingest_yfinance.py::run_ingest(run_id: int | None = None)`
  - all snapshot inserts write `run_id` when provided.

Verify:
- one pipeline invocation writes exactly one terminal manifest row,
- failed runs persist `status='failed'` and a non-empty error message,
- snapshot row created by the pipeline has non-null `run_id` matching manifest row,
- `_latest_snapshot_id(run_id)` never returns a snapshot from another run,
- schema tests cover the new table and linkage column.

### S1-02: Stable Config Digest and Code Version Capture

Goal:
- Make config and code provenance deterministic and testable.

Change:
- Extend `src/core/config.py` with canonical config serialization and SHA-256 digest helpers.
- Capture `git` revision metadata in `scripts/run_pipeline.py` with an explicit fallback token when unavailable.

Verify:
- reordered config keys produce the same digest,
- effective config value changes produce a different digest,
- every manifest row contains a non-empty `code_version`.

### S1-03: Gate-by-Gate Alert Decision Trace

Goal:
- Persist a decision contract that explains why an alert was allowed through.

Change:
- Replace the current thin `explain` payload in `src/core/compute_snapshot.py` with normalized gate objects for:
  - z-score,
  - persistence,
  - data/tier quality,
  - regime,
  - tradability.
- Each gate should include `status`, the inputs used, and a compact `reason_code` where useful.

Verify:
- every persisted alert contains the required gate objects,
- no gate payload is missing `status`,
- alert logic tests cover both pass and block paths.

### S1-04: Rates and Dividend Baseline Inputs

Goal:
- Remove hidden zero-rate and zero-dividend assumptions from the active compute path.

Change:
- Add explicit baseline pricing inputs to `config/config-v1.yaml` under:
  - `pricing.rate`
  - `pricing.dividend_yield`
- Thread those values through `src/core/metrics.py` and `src/core/compute_snapshot.py` (including `IdeaContext`).
- Reuse the existing pricing primitives in `src/core/iv_solve.py`; do not redesign them.

Verify:
- controlled tests show pricing and derived metrics move in the expected direction when `rate` or `dividend_yield` changes,
- trade-idea context no longer uses hardcoded zeros.

### S1-05: Determinism and Provenance Regression Pack

Goal:
- Lock the Sprint 1 contract into tests.

Change:
- Add targeted tests for:
  - manifest lifecycle,
  - run-scoped snapshot linkage through ingest paths,
  - config digest stability,
  - decision trace completeness,
  - deterministic repeatability on identical inputs,
  - rate/dividend sensitivity.

Verify:
- targeted Sprint 1 tests pass without flakiness,
- repeated identical compute runs produce identical downstream rows in the test harness.

## Delivery Sequence

1. Schema and run lifecycle.
   verify: manifest table exists, snapshot link exists, failed and successful runs are both test-covered
2. Config digest and code version capture.
   verify: digest stability tests pass and manifest rows show `config_hash` + `code_version`
3. Alert decision trace.
   verify: explain payload shape is complete and covered by alert tests
4. Rate/dividend plumbing.
   verify: sensitivity tests prove non-zero inputs affect behavior
5. Determinism pass.
   verify: repeated same-input runs produce identical outputs

## Definition of Done

Sprint 1 is done only when all are true:

1. Every pipeline run is attributable to `run_id + config_hash + code_version`.
2. Every snapshot produced by the pipeline is linked back to its run.
3. Every alert row has complete machine-readable gate evidence.
4. Rates and dividend yield are active config-driven inputs in the compute path.
5. Determinism and provenance checks are enforced by tests.

## Validation Commands

```bash
source .venv/bin/activate
pytest tests/test_schema.py tests/test_alerts_logic.py tests/test_iv_solve.py
pytest tests/test_run_manifest.py tests/test_config_digest.py tests/test_determinism.py tests/test_pricing_inputs.py
python scripts/run_pipeline.py
```

## QA Queries (Post-Implementation)

Run these checks against the DB after one successful pipeline run:

```sql
SELECT run_id, status, config_hash, code_version
FROM pipeline_runs
ORDER BY run_id DESC
LIMIT 1;
```

```sql
SELECT snapshot_id, run_id, ts, source
FROM snapshots
ORDER BY snapshot_id DESC
LIMIT 1;
```

```sql
SELECT a.alert_id, a.snapshot_id, s.run_id, a.alert_type, a.explain
FROM alerts a
JOIN snapshots s ON s.snapshot_id = a.snapshot_id
ORDER BY a.alert_id DESC
LIMIT 5;
```

## Risks and Controls

- Risk: schema change breaks existing DB initialization.
  - Control: keep changes additive and covered by `tests/test_schema.py`.
- Risk: gate payload shape drifts across alert paths.
  - Control: build the trace through one helper and test required keys.
- Risk: rate/dividend values get wired into one path but not another.
  - Control: cover both metric computation and trade-idea context in sensitivity tests.

## Handoff to Sprint 2

- Sprint 2 should treat Sprint 1 as the baseline contract for config truth and dead-knob removal.
- Do not start surface-model or regime redesign work until Sprint 1 determinism and provenance gates pass.
