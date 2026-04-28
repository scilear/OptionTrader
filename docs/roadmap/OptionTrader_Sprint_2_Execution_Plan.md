# OptionTrader Sprint 2 Execution Plan

Date: 2026-04-28
Sprint window: Week 2
Parent roadmap: `docs/roadmap/OptionTrader_Next_Level_Plan.md`
Prior sprint: `docs/roadmap/OptionTrader_Sprint_1_Execution_Plan.md`

## Sprint Objective

Eliminate config drift: every high-impact config key must be either fully operative (wired and tested) or explicitly deprecated with runtime visibility.

Sprint 2 is successful only if all are true:

- no high-impact config field remains silently ignored,
- config changes produce measurable runtime changes under tests,
- config behavior is documented in a versioned contract matrix.

## Pre-Sprint Gate (must close before S2 work)

- Fix the Sprint 1 reset-path blocker:
  - `src/ingest/ingest_yfinance.py` must not call `init_db()` from the pipeline path.
  - DB reset/init remains owned by `scripts/run_pipeline.py`.

## Current Baseline Facts

Observed config drift in current codebase:

- `data.source` is not respected by dispatcher routing (`src/ingest/dispatcher.py`).
- `metrics.delta_points` is not used in smile point selection (`src/core/metrics.py`).
- `quality.min_valid_points_full` and `quality.min_valid_points_core` are not used for tier gating (`src/core/metrics.py`).
- `alerts.pessimistic_gate` is not wired to alert behavior (`src/core/alerts.py`).
- `regime.*` thresholds in config are not used by regime computation (`src/core/regime.py`).
- `structures.*` settings are not used by trade idea templates (`src/core/trade_ideas.py`).
- UI metric bucket choices are hardcoded, not config-driven (`src/app/streamlit_app.py`).

## Scope Boundaries

In scope:

- Config contract matrix and enforcement tests.
- Wiring of high-impact keys listed below.
- Explicit deprecation path for non-operative low-impact keys.

Out of scope:

- Surface model redesign or no-arbitrage implementation.
- Regime feature expansion beyond existing regime structure.
- Signal-state redesign and execution-cost model redesign.

## Config Contract Matrix (Sprint 2 Target)

Create and maintain this as source-of-truth artifact in:

- `docs/roadmap/OptionTrader_Config_Contract_Matrix.md`

Initial target status for key groups:

| Key path | Current state | Sprint 2 target | Owner files |
|---|---|---|---|
| `data.source` | ignored | active | `src/ingest/dispatcher.py` |
| `data.dte_min`, `data.dte_max` | active | active | `src/ingest/*.py`, `src/core/compute_snapshot.py` |
| `data.capture_all_expiries` | active | active | `src/ingest/ingest_yfinance.py` |
| `metrics.delta_points` | ignored | active | `src/core/metrics.py` |
| `metrics.expiry_buckets_days` | active | active + UI parity | `src/core/compute_snapshot.py`, `src/app/streamlit_app.py` |
| `quality.spread_gate_pct` | active | active | existing |
| `quality.min_valid_points_core/full` | ignored | active | `src/core/metrics.py` |
| `alerts.z_threshold` | active | active | existing |
| `alerts.persistence_snapshots` | active | active | existing |
| `alerts.pessimistic_gate` | ignored | active | `src/core/alerts.py` |
| `regime.*` threshold keys | ignored | active | `src/core/regime.py` |
| `structures.*` keys | ignored | active | `src/core/trade_ideas.py` |
| `pricing.rate`, `pricing.dividend_yield` | active | active | existing |
| `storage.path` | active | active | `src/db/connection.py` |
| `storage.engine` | ignored | deprecated or active | `src/db/connection.py`, config docs |
| `data.snapshot_tags` | ignored | deprecated or active | ingest path + docs |
| `app.mode` | ignored | deprecated | config docs |

## Work Breakdown

### S2-00: Sprint 1 Blocker Closure

Goal:
- Ensure run provenance cannot be invalidated during ingest.

Change:
- Remove pipeline-path `init_db()` call from yfinance ingest.
- Keep reset/init only in pipeline orchestrator.

Verify:
- pipeline with reset env enabled still creates manifest + linked snapshot.

### S2-01: Config Contract Matrix + Validation Hooks

Goal:
- Make config behavior explicit and enforceable.

Change:
- Add `docs/roadmap/OptionTrader_Config_Contract_Matrix.md` with field-to-code-path mapping.
- Extend `src/core/config.py` with contract helpers:
  - expected key registry,
  - deprecated key registry,
  - startup warnings for unknown high-impact keys in runtime,
  - hard fail in tests for unknown high-impact keys.

Verify:
- matrix covers all top-level config groups,
- runtime logs emit a warning when unknown high-impact keys are supplied,
- tests fail if a declared active key has no behavior test.

### S2-02: Ingestion Source Routing Truth

Goal:
- make `data.source` operative.

Change:
- `src/ingest/dispatcher.py` must honor mode:
  - `ib`: try IB then fallback to yfinance,
  - `yfinance`: skip IB and use yfinance directly.

Verify:
- tests prove source routing differs when config changes.

### S2-03: Metrics and Quality Config Wiring

Goal:
- remove hardcoded metric assumptions.

Change:
- Wire `metrics.delta_points` into delta bucket extraction in `src/core/metrics.py`.
- Apply `quality.min_valid_points_core/full` to tier assignment logic with explicit tier requirements:
  - `Core` requires ATM and both 25-delta wings,
  - `Full` requires ATM, both 25-delta wings, and both 10-delta wings.
- Keep backward-compatible defaults for current 10/25/ATM behavior.

Verify:
- changing `delta_points` changes selected points/derived metrics under test,
- tier transitions honor both point-count thresholds and required-bucket membership under test.

### S2-04: Alerts and Regime Config Wiring

Goal:
- make alert/regime knobs actually control behavior.

Change:
- Wire `alerts.pessimistic_gate` in `src/core/alerts.py`.
- Build `RegimeParams` from config in `src/core/regime.py` using `regime.*` keys.
- Add explicit stale-regime warning when threshold config hash differs from the hash used for persisted `regime_state` rows.

Verify:
- toggling pessimistic gate changes alert outcome in deterministic test fixtures,
- changing regime thresholds changes regime labels under fixture replay,
- runtime emits warning when regime thresholds change without recomputing historical regime rows.

### S2-05: Structures Config Wiring

Goal:
- eliminate template hardcoding drift.

Change:
- Use `structures.skew_fade`, `structures.fly`, `structures.calendar` fields in `src/core/trade_ideas.py`.
- Maintain existing template names while parameterizing leg construction.

Verify:
- modifying structure config values changes generated legs in tests.

### S2-06: UI and Runtime Parity + Deprecation Pass

Goal:
- keep UI/runtime behavior aligned with config and close low-impact drift.

Change:
- Replace hardcoded metric buckets in Streamlit with `metrics.expiry_buckets_days`.
- Decide and document status for `storage.engine`, `data.snapshot_tags`, `app.mode`:
  - either wire fully now or mark deprecated in config + matrix.

Verify:
- UI bucket selector reflects config values,
- deprecated fields emit visible warnings or are removed from active config docs.

## Expected Files

- `docs/roadmap/OptionTrader_Config_Contract_Matrix.md` (new)
- `config/config-v1.yaml`
- `config/config-test.yaml`
- `src/core/config.py`
- `src/ingest/dispatcher.py`
- `src/ingest/ingest_yfinance.py`
- `src/core/metrics.py`
- `src/core/alerts.py`
- `src/core/regime.py`
- `src/core/trade_ideas.py`
- `src/app/streamlit_app.py`
- `tests/test_config_contract.py` (new)
- `tests/test_ingest_routing.py` (new)
- `tests/test_tier_logic.py` (updated)
- `tests/test_alerts_logic.py` (updated)
- `tests/test_regime.py` (updated)
- `tests/test_trade_ideas.py` (updated)

## Definition of Done

Sprint 2 is done only when all are true:

1. Contract matrix exists and maps high-impact keys to code + tests.
2. No high-impact key remains silently unused.
3. Source routing, delta/tier logic, pessimistic gate, regime thresholds, and structures are config-driven and test-covered.
4. UI bucket options are config-driven.
5. Deprecated keys are explicitly marked and surfaced.

## Validation Commands

```bash
source .venv/bin/activate
pytest tests/test_config_contract.py tests/test_ingest_routing.py
pytest tests/test_alerts_logic.py tests/test_tier_logic.py tests/test_regime.py tests/test_trade_ideas.py
pytest tests/test_run_manifest.py tests/test_config_digest.py tests/test_determinism.py tests/test_pricing_inputs.py
python scripts/run_pipeline.py
```

## Risks and Controls

- Risk: over-wiring low-impact fields increases complexity without value.
  - Control: classify each key as active or deprecated; avoid ambiguous middle state.
- Risk: behavior regressions from making previously ignored fields operative.
  - Control: fixture-based before/after tests and explicit default parity tests.
- Risk: config-key sprawl persists.
  - Control: keep contract matrix versioned and required in PR review.

## Handoff to Sprint 3

- Sprint 3 (surface integrity/no-arbitrage) starts only after Sprint 2 config contract is green.
- Surface model experiments must use Sprint 2 contract matrix as the single config truth layer.
