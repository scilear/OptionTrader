# OptionTrader S3.2 Re-Review Dev Instructions

Date: 2026-04-30
Scope reviewed: `f582c35`, `82c8b45`
Reviewer outcome: S3.2 closure is accepted; proceed to Sprint 4 execution.

## Review Outcome

- Fixed items are confirmed:
  - config contract updated for new `regime.*` keys (`src/core/config.py`)
  - determinism test made schema-safe (`tests/test_determinism.py`)
  - QC health-check script interpreter fallback improved (`scripts/qc_health_check.sh`)
  - scheduled-events seed file added (`config/regime_events_v1.yaml`)
- Test status:
  - `pytest tests/test_config_contract.py tests/test_determinism.py` -> pass
  - `pytest -q` -> pass (`71 passed`)

## Important Runtime Note

- `scripts/qc_health_check.sh` requires a Python interpreter with `duckdb` installed.
- In this repo, the supported path is the project venv.
- Always run health checks after activating venv.

## Required Execution Pattern

```bash
source .venv/bin/activate
python scripts/generate_replay_artifact.py --start-ts 2026-04-01T00:00:00Z --end-ts 2026-04-15T23:59:59Z
bash scripts/qc_health_check.sh --window-hours 1 --threshold 0.20 --consecutive 3 --min-snapshots 30
pytest -q
```

## Sprint 4 Start Instructions

Use these docs as the source of truth:

- `docs/roadmap/OptionTrader_Sprint_4_Execution_Plan.md`
- `docs/roadmap/OptionTrader_Sprint_4_Dev_Ticket_Sheet.md`
- `docs/roadmap/OptionTrader_Sprint_4_Planning_Review.md`

Execute in this order:

1. `S4-00` Regime feature contract and data plumbing
2. `S4-01` Multi-signal scoring engine
3. `S4-02` Scheduled event + cross-domain stress inputs
4. `S4-04` Drift/config safety guardrails
5. `S4-03` Ablation and incremental value gate

## Sprint 4 Guardrails (Do Not Skip)

- Keep `config/regime_events_v1.yaml` as v1 event source unless formally changed.
- Any new active `regime.*` config key must be added in all three places:
  - `ACTIVE_CONFIG_KEYS`
  - `HIGH_IMPACT_ACTIVE_KEYS` (if materially impactful)
  - `CONTRACT_TEST_COVERAGE`
- Enforce S4 locked ablation gate thresholds from the Sprint 4 execution plan before retaining
  new features.
