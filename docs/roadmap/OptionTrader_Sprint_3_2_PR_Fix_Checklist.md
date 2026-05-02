# OptionTrader Sprint 3.2 PR Fix Checklist

Date: 2026-04-30
Purpose: Required fixes before S3.2 sign-off

## 1) Fix config-contract failures from new regime keys

- Files:
  - `src/core/config.py`
  - `tests/test_config_contract.py`
- Issue:
  - `config/config-v1.yaml` and `config/config-test.yaml` include new `regime.*` keys, but
    config contract does not recognize them.
- Actions:
  - Add these keys to `ACTIVE_CONFIG_KEYS`:
    - `regime.event_path`
    - `regime.stress_proxy_ticker`
    - `regime.weights.vix`
    - `regime.weights.rv20`
    - `regime.weights.drawdown`
    - `regime.weights.event`
    - `regime.weights.stress_proxy`
  - Add relevant keys to `HIGH_IMPACT_ACTIVE_KEYS` (at minimum all materially impactful
    `regime.*` thresholds/weights).
  - Add `CONTRACT_TEST_COVERAGE` entries for the new keys, mapped to appropriate regime tests.
- Acceptance:
  - `tests/test_config_contract.py` passes.

## 2) Fix deterministic test for expanded regime_state schema

- File:
  - `tests/test_determinism.py`
- Issue:
  - Test uses `INSERT INTO regime_state VALUES (...)` with 7 values, but table now has 13 columns.
- Actions:
  - Use explicit column-list insert, for example:
    - `INSERT INTO regime_state (regime_date, vix_percentile, rv20_percentile, drawdown_percent, regime_score, regime_label, regime_config_hash) VALUES (...)`
  - Keep new columns default/null unless required by this test.
- Acceptance:
  - `tests/test_determinism.py` passes and remains safe under additive schema changes.

## 3) Make QC health-check script interpreter-robust

- File:
  - `scripts/qc_health_check.sh`
- Issue:
  - Script invokes bare `python`, which fails when venv is not activated or alias is missing.
- Actions:
  - Resolve interpreter in this order:
    1. `$VIRTUAL_ENV/bin/python` (if present)
    2. `python3`
    3. `python`
    4. otherwise fail with clear error
  - Use resolved interpreter variable for the embedded Python execution.
- Acceptance:
  - Script runs with activated venv and also works in non-venv shells with `python3`.

## 4) Resolve S4 expected-file consistency

- Files:
  - `config/regime_events_v1.yaml` (add) OR
  - `docs/roadmap/OptionTrader_Sprint_4_Execution_Plan.md`
  - `docs/roadmap/OptionTrader_Sprint_4_Dev_Ticket_Sheet.md`
- Issue:
  - S4 docs list `config/regime_events_v1.yaml` as expected, but file does not exist.
- Actions (choose one):
  - Option A (preferred): add `config/regime_events_v1.yaml` with minimal valid schema and
    placeholder sample events.
  - Option B: remove/defer the file reference from S4 docs until S4 implementation starts.
- Acceptance:
  - Repo files and planning docs are consistent.

## Regression Commands

```bash
source .venv/bin/activate
pytest tests/test_config_contract.py tests/test_determinism.py
bash scripts/qc_health_check.sh --window-hours 1 --threshold 0.20 --consecutive 3 --min-snapshots 30
pytest -q
```
