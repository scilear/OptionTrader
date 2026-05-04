# OptionTrader Sprint 4 Dev Ticket Sheet

Date: 2026-04-30
Source plan: `docs/roadmap/OptionTrader_Sprint_4_Execution_Plan.md`
Sprint: Weeks 5-6

## Ticket Board Snapshot

| Ticket | Objective | Priority | Status | Evidence |
|---|---|---|---|---|
| S4-00 | Regime feature contract + data plumbing | P0 | Done | `src/db/schema.sql`, `src/db/init_db.py`, `tests/test_schema.py` |
| S4-01 | Multi-signal scoring engine | P0 | Done | `src/core/regime.py`, `tests/test_regime.py` |
| S4-02 | Event + cross-domain stress inputs | P0 | Done | `config/regime_events_v1.yaml`, `src/core/regime.py`, `tests/test_regime.py` |
| S4-03 | Ablation and incremental value gate | P0 | Blocked | `scripts/generate_regime_ablation_artifact.py`, `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact.md` |
| S4-04 | Drift/config safety guardrails | P1 | Done | `src/core/compute_snapshot.py`, `tests/test_regime_filter.py` |

## Ticket Details

### S4-00 - Regime Feature Contract and Data Plumbing

- Objective:
  - Ensure every regime-scoring feature is explicitly modeled and test-traceable.
- Files:
  - `src/db/schema.sql`
  - `src/db/init_db.py`
  - `docs/roadmap/OptionTrader_Config_Contract_Matrix.md`
  - `tests/test_schema.py`
- Tasks:
  - Add/confirm storage fields for regime feature components.
  - Update config contract matrix mappings for all regime keys.
  - Add migration-safe schema coverage tests.
- Acceptance:
  - [ ] Feature fields are present on fresh and migrated DBs.
  - [ ] Contract matrix maps each active regime key to code + tests.

### S4-01 - Multi-Signal Regime Scoring Engine

- Objective:
  - Implement transparent, non-RV-dominant regime scoring.
- Files:
  - `src/core/regime.py`
  - `src/core/config.py`
  - `tests/test_regime.py`
- Tasks:
  - Refactor scoring to componentized, config-driven logic.
  - Add decomposition outputs (`component -> contribution`).
  - Remove lingering hardcoded thresholds.
- Acceptance:
  - [ ] Regime decision is reproducibly decomposed.
  - [ ] Config threshold edits change labels in deterministic fixtures.

### S4-02 - Event and Cross-Domain Stress Inputs

- Objective:
  - Add independent forward-looking and cross-domain stress signals.
- Files:
  - `src/core/regime.py`
  - `config/config-v1.yaml`
  - `config/config-test.yaml`
  - `config/regime_events_v1.yaml`
  - `tests/test_regime.py`
- Tasks:
  - Integrate scheduled-event feature (FOMC/CPI style) from `config/regime_events_v1.yaml`.
  - Integrate one cross-domain stress proxy.
  - Add fixture tests for known stress windows.
- Acceptance:
  - [ ] At least one event feature and one cross-domain feature are active.
  - [ ] Stress labels move appropriately on fixture dates.

### S4-03 - Ablation and Incremental Value Gate

- Objective:
  - Enforce falsification discipline before accepting new regime complexity.
- Files:
  - `src/core/replay.py` (or helper scripts)
  - `docs/roadmap/OptionTrader_Sprint_4_Execution_Plan.md`
- Tasks:
  - Run RV-only baseline vs multi-signal variant.
  - Generate feature-ablation table and conclusion.
  - Record retention/removal decisions for each feature.
- Acceptance:
  - [ ] Ablation artifact is published and reproducible.
  - [ ] Minimum sample met: `>=50` alerts total and `>=10` per active regime bucket.
  - [ ] Primary lift gate met: precision delta `>= +0.03` with volume within `[-15%, +15%]`.
  - [ ] Transition false-positive density does not worsen by more than `+0.02`.
  - [ ] Each retained feature has explicit incremental-value evidence.

### S4-04 - Regime Drift and Config Safety Guardrails

- Objective:
  - Prevent stale historical regime-state reuse under new thresholds.
- Files:
  - `src/core/compute_snapshot.py`
  - `src/core/regime.py`
  - `tests/test_regime_filter.py`
- Tasks:
  - Tighten stale-hash checks and warning messages.
  - Add tests for mismatch and non-mismatch paths.
  - Document recompute runbook in sprint docs.
- Acceptance:
  - [ ] Runtime warning appears on threshold-hash mismatch.
  - [ ] Warning path is covered by tests.

## Suggested Delivery Order

1. S4-00
2. S4-01
3. S4-02
4. S4-04
5. S4-03

## End-of-Sprint Validation Commands

```bash
source .venv/bin/activate
pytest tests/test_regime.py tests/test_regime_filter.py tests/test_config_contract.py
pytest -q
```
