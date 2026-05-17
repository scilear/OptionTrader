# OptionTrader S4-03 Dev Instructions - Warm-up Exclusion Policy (A)

Date: 2026-05-17
Owner: Dev implementation
Requested by: PM
Decision: Use Policy A - exclude pre-regime-ready snapshots from S4/S7 evaluation and gates.

## Why this is required

Current evidence is polluted by pre-warm-up dates where regime rows do not exist yet.

Observed in local EOD truth runs (`run_id=33/34`):

- `regime_state` coverage starts at `2010-04-05`.
- Alerts still exist on `2010-01-22` to `2010-02-12` with `regime_label='Unknown'`.
- This forces `taxonomy_verdict='invalid_evidence'` even when non-warm-up data is valid.

Warm-up exclusion is mandatory for valid falsification.

## Policy definition (must implement exactly)

For any evaluation window, define `effective_start_ts` as:

- max(user-provided `start_ts`, first date where regime is ready for that run/config)

All S4/S7 evidence metrics must use `effective_start_ts`:

- alert counts,
- outcome counts,
- regime coverage,
- transition FP density,
- ablation metrics,
- final release gate verdicts.

Pre-warm-up rows must be excluded from evaluation, not labeled as gate-failing `Unknown`.

## Implementation tasks

### 1) Add regime-ready boundary helper

- Files: `src/core/regime.py` (or new helper module under `src/core/`)
- Add function to return first regime-ready date for current config/data.
- Use the same readiness logic as regime computation (rolling windows / non-null features).

Acceptance:

- Boundary is deterministic for same DB + config.
- Boundary can be queried by validator scripts.

### 2) Apply boundary in validator

- File: `scripts/validate_release.py`
- Before computing gates, resolve `effective_start_ts`.
- Apply `effective_start_ts` consistently in all gate queries.
- Add payload fields:
  - `effective_start_ts`
  - `warmup_excluded_days`
  - `warmup_exclusion_applied` (bool)

Acceptance:

- `unknown_regime_count == 0` for warm-up-only unknowns.
- No gate fails solely due to pre-warm-up unknown rows.

### 3) Apply boundary in ablation artifact

- File: `scripts/generate_regime_ablation_artifact.py`
- Use same `effective_start_ts` logic as validator.
- Emit `effective_start_ts` in artifact payload/markdown.

Acceptance:

- Alert/outcome/regime counts align with validator for same window.

### 4) Apply boundary in attrition report

- File: `scripts/report_s4_gate_attrition.py`
- Use same boundary helper and include both:
  - requested window,
  - effective window after warm-up exclusion.

Acceptance:

- Attrition counts reconcile with validator/ablation for same lineage and window.

### 5) Keep runtime behavior unchanged

- File: `src/core/compute_snapshot.py`
- Do not alter live compute gating semantics in this task.
- This change is evaluation-layer hygiene, not production signal policy.

Acceptance:

- No runtime signal-state regression introduced by warm-up exclusion work.

## Tests to add/update

- `tests/test_validate_release.py`
  - verifies `effective_start_ts` fields exist and warm-up exclusion is applied.
- `tests/test_regime.py`
  - verifies regime-ready boundary helper behavior.
- add or update tests for ablation/attrition scripts
  - verifies counts are computed from effective window, not raw start window.

## Required validation commands

```bash
source .venv/bin/activate
pytest tests/test_regime.py tests/test_validate_release.py -q
python scripts/validate_release.py --config-path config/config-eod-truth.yaml --start-ts 2010-01-01T00:00:00Z --end-ts 2023-12-31T23:59:59Z --underlying SPX --baseline-lineage 3b024c9 --candidate-lineage 5128e8e --train-size 252 --test-size 63 --step-size 63 --horizon-days 5
```

## Done criteria

Task is done only when all are true:

1. Warm-up exclusion is consistently applied across validator, ablation, and attrition scripts.
2. Payloads explicitly show requested vs effective window.
3. Unknown labels caused by pre-warm-up dates are eliminated from evaluation metrics.
4. Remaining failures (if any) reflect true model behavior, not initialization artifacts.
