# OptionTrader Sprint 1 Dev Ticket Sheet

Date: 2026-04-28
Source plan: `docs/roadmap/OptionTrader_Sprint_1_Execution_Plan.md`
Sprint: Week 1

## How to Use This Sheet

- One ticket maps to one Sprint 1 work item (`S1-01` to `S1-05`).
- Keep scope fixed to Sprint 1 hardening goals (no model redesign).
- Mark every acceptance checkbox before moving ticket to done.

## Ticket S1-01 - Run Manifest and Snapshot Linkage

- **Objective:** persist run provenance and link each pipeline-created snapshot to its run.
- **Estimate:** 1.0 day
- **Priority:** P0
- **Dependencies:** none
- **Owner:** TBD

- **Files**
- `src/db/schema.sql`
- `scripts/run_pipeline.py`
- `src/ingest/dispatcher.py`
- `src/ingest/ingest_ib.py`
- `src/ingest/ingest_yfinance.py`
- `tests/test_schema.py`
- `tests/test_run_manifest.py` (new)

- **Implementation tasks**
- Add `pipeline_runs` table and nullable `snapshots.run_id` foreign key.
- Create run row at pipeline start and close it in `finally` as `success` or `failed`.
- Pass `run_id` through ingest signatures and include it in snapshot inserts.
- Replace global latest-snapshot query with run-scoped lookup (`WHERE run_id = ?`).

- **Acceptance checklist**
- [ ] A single pipeline run creates exactly one terminal row in `pipeline_runs`.
- [ ] Failed run persists `status='failed'` and non-empty `error_message`.
- [ ] Snapshot created by pipeline has non-null `run_id` matching manifest row.
- [ ] Run-scoped snapshot lookup does not read snapshots from other runs.
- [ ] `tests/test_schema.py` validates `pipeline_runs` and `snapshots.run_id`.

## Ticket S1-02 - Stable Config Digest and Code Version

- **Objective:** make config and code provenance deterministic.
- **Estimate:** 0.5 day
- **Priority:** P0
- **Dependencies:** S1-01
- **Owner:** TBD

- **Files**
- `src/core/config.py`
- `scripts/run_pipeline.py`
- `tests/test_config_digest.py` (new)
- `tests/test_run_manifest.py` (new/updated)

- **Implementation tasks**
- Add canonical config serialization and SHA-256 digest helpers.
- Compute `config_hash` once at pipeline start from effective config.
- Capture `code_version` as git SHA with optional dirty marker.
- Add explicit fallback token if git metadata is unavailable.

- **Acceptance checklist**
- [ ] Reordered config keys produce identical digest.
- [ ] Effective config value changes produce different digest.
- [ ] Every manifest row has non-empty `config_hash` and `code_version`.
- [ ] Fallback code path for unavailable git metadata is tested.

## Ticket S1-03 - Gate-by-Gate Alert Decision Trace

- **Objective:** make alert decisions machine-auditable.
- **Estimate:** 1.0 day
- **Priority:** P0
- **Dependencies:** none
- **Owner:** TBD

- **Files**
- `src/core/compute_snapshot.py`
- `tests/test_alerts_logic.py`
- `tests/test_explainability.py`

- **Implementation tasks**
- Replace thin `explain` payload with structured gate objects.
- Required gates: `zscore`, `persistence`, `data_tier_quality`, `regime`, `tradability`.
- Include per-gate `status`, key inputs, and `reason_code` where relevant.
- Build payload via one helper to keep structure consistent.

- **Acceptance checklist**
- [ ] Every persisted alert includes all required gate objects.
- [ ] Every gate object includes `status`.
- [ ] Alert tests cover both pass and block paths.
- [ ] Explain payload remains JSON-serializable and stable.

## Ticket S1-04 - Rates and Dividend Baseline Inputs

- **Objective:** remove hidden zero-rate and zero-dividend assumptions.
- **Estimate:** 0.75 day
- **Priority:** P0
- **Dependencies:** none
- **Owner:** TBD

- **Files**
- `config/config-v1.yaml`
- `src/core/metrics.py`
- `src/core/compute_snapshot.py`
- `src/core/config.py` (if helper needed for defaults)
- `tests/test_iv_solve.py`
- `tests/test_pricing_inputs.py` (new)

- **Implementation tasks**
- Add `pricing.rate` and `pricing.dividend_yield` config keys.
- Thread pricing inputs into IV solve path and ATM/forward logic in metrics.
- Thread pricing inputs into trade idea context in compute path.
- Keep `src/core/iv_solve.py` behavior unchanged unless plumbing requires minor signatures.

- **Acceptance checklist**
- [ ] No hardcoded `rate=0.0` or `div=0.0` remains in active compute path.
- [ ] Sensitivity tests confirm metric/pricing directionality under rate and dividend perturbations.
- [ ] Trade-idea context uses config-driven pricing inputs.
- [ ] Defaults are explicit and documented in config.

## Ticket S1-05 - Determinism and Provenance Regression Pack

- **Objective:** enforce Sprint 1 contract in tests.
- **Estimate:** 0.75 day
- **Priority:** P0
- **Dependencies:** S1-01, S1-02, S1-03, S1-04
- **Owner:** TBD

- **Files**
- `tests/test_determinism.py` (new)
- `tests/test_run_manifest.py` (new/updated)
- `tests/test_config_digest.py` (new/updated)
- `tests/test_pricing_inputs.py` (new/updated)
- `tests/test_alerts_logic.py` (updated)

- **Implementation tasks**
- Add same-input repeatability test harness.
- Add run lifecycle and linkage assertions.
- Add config digest and code version assertions.
- Add decision trace shape assertions.
- Add pricing-input sensitivity assertions.

- **Acceptance checklist**
- [ ] Repeated identical runs produce identical downstream rows in test harness.
- [ ] Provenance/linkage tests pass consistently.
- [ ] Decision trace completeness tests pass.
- [ ] Pricing sensitivity tests pass.
- [ ] New tests are non-flaky across multiple local executions.

## Suggested Delivery Order

1. S1-01
2. S1-02
3. S1-03
4. S1-04
5. S1-05

## End-of-Sprint Verification Commands

```bash
source .venv/bin/activate
pytest tests/test_schema.py tests/test_alerts_logic.py tests/test_iv_solve.py
pytest tests/test_run_manifest.py tests/test_config_digest.py tests/test_determinism.py tests/test_pricing_inputs.py
python scripts/run_pipeline.py
```

## SQL QA Checks (After One Successful Pipeline Run)

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
