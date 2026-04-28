# OptionTrader Sprint 2 Dev Ticket Sheet

Date: 2026-04-28
Source plan: `docs/roadmap/OptionTrader_Sprint_2_Execution_Plan.md`
Sprint: Week 2

## How to Use This Sheet

- One ticket maps to one Sprint 2 work item (`S2-00` to `S2-06`).
- Keep scope fixed to config truth/drift removal (no surface-model redesign in this sprint).
- Complete acceptance checkboxes before moving ticket to done.

## Ticket S2-00 - Close Sprint 1 Reset-Path Blocker

- **Objective:** prevent manifest/snapshot FK breakage when reset env is enabled.
- **Estimate:** 0.25 day
- **Priority:** P0
- **Dependencies:** none
- **Owner:** TBD

- **Files**
- `src/ingest/ingest_yfinance.py`
- `scripts/run_pipeline.py`
- `tests/test_run_manifest.py`

- **Implementation tasks**
- Remove `init_db()` from yfinance ingest pipeline path.
- Keep init/reset ownership in pipeline orchestrator.
- Add regression test for reset-path successful run linkage.

- **Acceptance checklist**
- [ ] No DB init call remains in ingest runtime path.
- [ ] Pipeline with reset env writes manifest + linked snapshot.
- [ ] Existing Sprint 1 manifest tests still pass.

## Ticket S2-01 - Config Contract Matrix and Enforcement

- **Objective:** create explicit field-to-behavior contract.
- **Estimate:** 0.75 day
- **Priority:** P0
- **Dependencies:** S2-00
- **Owner:** TBD

- **Files**
- `docs/roadmap/OptionTrader_Config_Contract_Matrix.md` (new)
- `src/core/config.py`
- `tests/test_config_contract.py` (new)

- **Implementation tasks**
- Build matrix: key path -> status(active/deprecated) -> code path -> test file.
- Add helper(s) to validate expected/deprecated keys.
- Add runtime warning path for unknown high-impact keys.
- Add test coverage that fails on unknown/missing high-impact contract coverage.

- **Acceptance checklist**
- [ ] Contract matrix includes all high-impact keys from Sprint 2 plan.
- [ ] Active keys have mapped runtime path and test.
- [ ] Deprecated keys are explicitly declared.
- [ ] Unknown high-impact keys produce runtime warnings and test failures.

## Ticket S2-02 - Ingestion Source Routing Truth

- **Objective:** make `data.source` actually control routing.
- **Estimate:** 0.5 day
- **Priority:** P0
- **Dependencies:** S2-01
- **Owner:** TBD

- **Files**
- `src/ingest/dispatcher.py`
- `tests/test_ingest_routing.py` (new)

- **Implementation tasks**
- If `data.source == 'yfinance'`, bypass IB and ingest yfinance directly.
- If `data.source == 'ib'`, preserve current IB-first fallback behavior.
- Add deterministic tests for both modes.

- **Acceptance checklist**
- [ ] `data.source='yfinance'` never calls IB path.
- [ ] `data.source='ib'` retains fallback behavior.
- [ ] Routing behavior differences are test-verified.

## Ticket S2-03 - Metrics Delta Points and Tier Threshold Wiring

- **Objective:** remove hardcoded metric/tier assumptions.
- **Estimate:** 1.0 day
- **Priority:** P0
- **Dependencies:** S2-01
- **Owner:** TBD

- **Files**
- `src/core/metrics.py`
- `tests/test_tier_logic.py`
- `tests/test_config_contract.py` (updated)

- **Implementation tasks**
- Wire `metrics.delta_points` to delta bucket extraction.
- Wire `quality.min_valid_points_core/full` to tier assignment with explicit membership checks:
  - `Core`: ATM + 25C + 25P required.
  - `Full`: ATM + 25C + 25P + 10C + 10P required.
- Preserve current default behavior when defaults unchanged.

- **Acceptance checklist**
- [ ] Changing `delta_points` changes selected smile points in tests.
- [ ] Tier transitions respect min-valid-point thresholds and required-bucket membership.
- [ ] Default config reproduces baseline behavior.

## Ticket S2-04 - Alerts and Regime Config Truth

- **Objective:** make alert/regime thresholds config-driven.
- **Estimate:** 0.75 day
- **Priority:** P0
- **Dependencies:** S2-01
- **Owner:** TBD

- **Files**
- `src/core/alerts.py`
- `src/core/regime.py`
- `tests/test_alerts_logic.py`
- `tests/test_regime.py`

- **Implementation tasks**
- Wire `alerts.pessimistic_gate` behavior toggle.
- Load `regime.*` thresholds into `RegimeParams` from config path.
- Add stale-regime warning when thresholds change but stored regime rows were computed under prior thresholds.
- Add tests showing behavior shifts when thresholds change.

- **Acceptance checklist**
- [ ] Toggling `pessimistic_gate` changes alert outcomes under fixture.
- [ ] Changing regime thresholds changes computed labels under fixture.
- [ ] No hardcoded regime threshold values remain in active path.
- [ ] Runtime warning is emitted when regime thresholds change without recomputation.

## Ticket S2-05 - Structures Config Wiring in Trade Ideas

- **Objective:** remove hardcoded template parameters.
- **Estimate:** 0.75 day
- **Priority:** P0
- **Dependencies:** S2-01
- **Owner:** TBD

- **Files**
- `src/core/trade_ideas.py`
- `tests/test_trade_ideas.py`
- `tests/test_config_contract.py` (updated)

- **Implementation tasks**
- Use `structures.skew_fade.*`, `structures.fly.*`, `structures.calendar.*` in leg construction.
- Keep template identities stable while parameterizing legs.
- Add tests confirming config edits alter generated legs.

- **Acceptance checklist**
- [ ] Structure config changes propagate to generated leg deltas/tenors.
- [ ] Existing template names remain backward-compatible.
- [ ] Trade idea tests cover config-driven parameterization.

## Ticket S2-06 - UI Parity and Deprecation Cleanup

- **Objective:** align UI/runtime with config and close low-impact drift.
- **Estimate:** 0.5 day
- **Priority:** P1
- **Dependencies:** S2-01
- **Owner:** TBD

- **Files**
- `src/app/streamlit_app.py`
- `config/config-v1.yaml`
- `config/config-test.yaml`
- `docs/roadmap/OptionTrader_Config_Contract_Matrix.md`

- **Implementation tasks**
- Read metric buckets from `metrics.expiry_buckets_days` in UI selectors.
- Decide status for `storage.engine`, `data.snapshot_tags`, `app.mode`:
  - wire now, or mark deprecated in matrix/config comments.

- **Acceptance checklist**
- [ ] UI bucket list is config-driven.
- [ ] Low-impact drift keys are explicitly active or deprecated.
- [ ] No ambiguous keys remain undocumented.

## Suggested Delivery Order

1. S2-00
2. S2-01
3. S2-02
4. S2-03
5. S2-04
6. S2-05
7. S2-06

## End-of-Sprint Verification Commands

```bash
source .venv/bin/activate
pytest tests/test_config_contract.py tests/test_ingest_routing.py
pytest tests/test_alerts_logic.py tests/test_tier_logic.py tests/test_regime.py tests/test_trade_ideas.py
pytest tests/test_run_manifest.py tests/test_config_digest.py tests/test_determinism.py tests/test_pricing_inputs.py
python scripts/run_pipeline.py
```
