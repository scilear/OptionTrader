# OptionTrader Sprint 4 Combined Findings and Action Plan

Date: 2026-05-03
Scope reviewed: S4 commits `2ab505b`, `9549d89`
Inputs:
- `docs/roadmap/OptionTrader_Sprint_4_Adversarial_Review.md`
- Internal code review findings on S4 sequence

## Executive Decision

Sprint 4 is **not ready for final sign-off** yet. Multiple S4 items are implemented, but there are
critical correctness gaps between runtime logic, schema, and ablation evidence.

## Combined Findings

### F1 - Schema/Runtime Desynchronization (Critical)

Agreement level: **Agree** (both reviews)

- `src/core/regime.py` writes these `regime_state` fields:
  - `vix_spot`, `rv20_value`, `drawdown_value`, `event_score`, `stress_proxy_score`, `decomposition`
- `src/db/schema.sql` currently does **not** define those columns in the `regime_state` table.
- `src/db/init_db.py` adds them for migrated DBs, so tests can pass while fresh-schema runtime can fail.

Risk:
- Fresh DB path can fail at runtime when regime rows are inserted.

Required fix:
1. Add missing columns to `regime_state` in `src/db/schema.sql`.
2. Keep additive migration in `src/db/init_db.py` (already present).
3. Extend `tests/test_schema.py` to verify both:
   - fresh schema contains new regime columns,
   - migrated legacy schema is upgraded correctly.
4. Add an integration test that runs `init_db()` + `compute_regime_state()` on a fresh DB.

### F2 - Multi-signal Independence Violation (Critical)

Agreement level: **Agree** (both reviews)

- In `src/core/regime.py`, `vix_pct` and `rv20_pct` are both derived from `rv_pct`.
- `_stress_proxy_score(...)` is a deterministic function of `rv20_pct`.

Risk:
- S4 objective (“regime model independence”) is not met; model remains RV-dominant in practice.

Required fix:
1. Replace `vix_pct = rv_pct` aliasing with an independent VIX signal path.
2. Replace RV-derived stress-proxy placeholder with an independent source tied to
   `regime.stress_proxy_ticker`.
3. Persist the independent raw values into `regime_state` (`vix_spot`, `stress_proxy_score` inputs).
4. Add tests proving label changes from independent feature perturbations, not just RV perturbations.

### F3 - Ablation Gate Methodology Invalid (High)

Agreement level: **Agree** (both reviews)

- `scripts/generate_regime_ablation_artifact.py` hardcodes baseline alert count to `0`.
- Precision metrics are unavailable because realized outcome labels are not persisted.
- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact.md` concludes feature disablement from
  gate failure without valid comparable baseline/outcome evidence.

Risk:
- Retention/removal decisions are not evidence-valid under locked S4 gate definitions.

Required fix:
1. Generate **real** baseline vs candidate tracks over the same window.
2. Do not hardcode baseline metrics.
3. Introduce outcome-label persistence required for precision-based gates (or explicitly mark S4-03 as
   blocked and remove “Done” status).
4. Re-run artifact and update sprint docs with valid gate results.

### F4 - Warm-up Behavior Not Explicit (Medium)

Agreement level: **Agree** (adversarial report + internal note)

- Regime calculations need rolling history; early windows may produce no rows.
- No explicit warm-up warning currently communicates this to operators.

Required fix:
1. Add explicit warm-up guard log when history is insufficient.
2. Add test asserting warning on insufficient lookback.

### F5 - Hash Fragility on Event Path (Medium)

Agreement level: **Partial agree**

- `regime_threshold_hash` includes `event_path` string.
- Path-string-only hashing can produce false drift when environment pathing changes.

Required fix:
1. Normalize `event_path` before hashing (prefer repo-relative normalization).
2. Optionally hash event-file content digest rather than path string.
3. Add test covering equivalent path representations.

## Required Status Corrections in Docs

Until F1-F3 are fixed, update these docs to avoid false completion signaling:

- `docs/roadmap/OptionTrader_Sprint_4_Dev_Ticket_Sheet.md`
  - mark `S4-01`, `S4-02`, `S4-03` as **In Progress** or **Blocked** (not Done).
- `docs/roadmap/OptionTrader_Sprint_4_Execution_Plan.md`
  - move “execution closure” wording to a provisional section with blockers listed.

## Dev Fix Order (Mandatory)

1. **F1 schema sync** (`schema.sql`, `init_db.py`, `tests/test_schema.py`).
2. **F2 independent signals** (`regime.py`, config wiring, tests).
3. **F4 warm-up guardrails** (`regime.py`, tests).
4. **F5 hash normalization** (`regime.py`, tests).
5. **F3 ablation validity** (`generate_regime_ablation_artifact.py`, artifact doc, status docs).

## Acceptance Checklist for Re-Review

- [ ] Fresh-schema and migrated-schema paths both support full regime writes.
- [ ] VIX and stress-proxy inputs are independent from RV in code and tests.
- [ ] Warm-up condition emits explicit warning and is tested.
- [ ] Regime hash behavior is stable under equivalent path references.
- [ ] Ablation artifact uses real baseline/candidate metrics and valid gate evidence.
- [ ] Sprint 4 ticket statuses reflect actual completion state.

## Regression Commands

```bash
source .venv/bin/activate
pytest tests/test_schema.py tests/test_regime.py tests/test_regime_filter.py tests/test_config_contract.py
python scripts/generate_regime_ablation_artifact.py --start-ts 2026-04-01T00:00:00Z --end-ts 2026-04-15T23:59:59Z
pytest -q
```
