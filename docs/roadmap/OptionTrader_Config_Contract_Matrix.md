# OptionTrader Config Contract Matrix

Date: 2026-04-29
Owner: Core engineering
Related sprint: `docs/roadmap/OptionTrader_Sprint_2_Execution_Plan.md`
State: Post-Sprint-2 cleanup

## Purpose

Define a single, testable source of truth for configuration behavior.

Rules:

- Every high-impact key is exactly one of: `active` or `deprecated`.
- `active` keys map to runtime path(s) and test coverage.
- `deprecated` keys include rationale and migration/removal note.
- Unknown high-impact keys trigger runtime warnings and strict-mode test failures.

## Status Definitions

- `active`: key changes runtime behavior now.
- `deprecated`: key retained for compatibility/docs and not expected to alter runtime behavior.

## Matrix (As-Built)

| Key Path | Status | Runtime Path(s) | Test Coverage | Notes |
|---|---|---|---|---|
| `app.mode` | deprecated | none | none | Legacy metadata only. |
| `logging.level` | active | `src/core/logging_utils.py` | indirect only | Add direct logging behavior test later. |
| `logging.file` | active | `src/core/logging_utils.py` | indirect only | Add direct file-handler test later. |
| `data.underlying` | active | `src/ingest/ingest_ib.py`, `src/ingest/ingest_yfinance.py` | indirect | Used in snapshot writes. |
| `data.symbol` | active | `src/ingest/ingest_yfinance.py` | indirect | Used for yfinance ticker selection. |
| `data.dte_min` | active | `src/ingest/ingest_yfinance.py`, `src/core/compute_snapshot.py` | indirect | Ingest + compute filtering. |
| `data.dte_max` | active | `src/ingest/ingest_yfinance.py`, `src/core/compute_snapshot.py` | indirect | Ingest + compute filtering. |
| `data.snapshot_tags` | deprecated | none | none | Not consumed by pipeline/runtime. |
| `data.source` | active | `src/ingest/dispatcher.py` | `tests/test_ingest_routing.py` | Controls yfinance-direct vs IB-first fallback. |
| `data.capture_all_expiries` | active | `src/ingest/ingest_yfinance.py` | indirect | Add explicit behavior test later. |
| `ib.hosts` | active | `src/ingest/ingest_ib.py` | indirect | Used in IB host loop. |
| `ib.port` | active | `src/ingest/ingest_ib.py` | indirect | Connection parameter. |
| `ib.client_id` | active | `src/ingest/ingest_ib.py` | indirect | Connection parameter. |
| `ib.timeout_seconds` | active | `src/ingest/ingest_ib.py` | indirect | Connection parameter. |
| `ib.strike_pct_range` | active | `src/ingest/ingest_ib.py` | indirect | Contract filtering parameter. |
| `ib.max_strikes_per_right` | active | `src/ingest/ingest_ib.py` | indirect | Contract cap parameter. |
| `storage.engine` | deprecated | none | none | Runtime path uses DuckDB directly. |
| `storage.path` | active | `src/db/connection.py` | indirect (`tests/test_run_manifest.py`) | DB connection target. |
| `pricing.rate` | active | `src/core/compute_snapshot.py`, `src/core/metrics.py` | `tests/test_pricing_inputs.py` | Sprint 1 baseline. |
| `pricing.dividend_yield` | active | `src/core/compute_snapshot.py`, `src/core/metrics.py` | `tests/test_pricing_inputs.py` | Sprint 1 baseline. |
| `metrics.delta_points` | active | `src/core/metrics.py`, `src/core/compute_snapshot.py` | `tests/test_tier_logic.py`, `tests/test_config_contract.py` | Drives delta bucket selection. |
| `metrics.zscore_window_days` | active | `src/core/compute_snapshot.py` | indirect (`tests/test_alerts_logic.py`) | Add explicit config-effect test later. |
| `metrics.expiry_buckets_days` | active | `src/core/compute_snapshot.py`, `src/app/streamlit_app.py` | `tests/test_streamlit_config.py`, `tests/test_config_contract.py` | UI and compute parity implemented. |
| `quality.spread_gate_pct` | active | `src/ingest/ingest_yfinance.py`, `src/core/compute_snapshot.py`, `src/core/tradability.py` | indirect + `tests/test_qc.py` | Drives QC and tradability behavior. |
| `quality.allow_zero_bid` | active | `src/ingest/ingest_yfinance.py`, `src/ingest/ingest_ib.py` | `tests/test_qc.py` | Quote acceptance gate. |
| `quality.min_valid_points_full` | active | `src/core/metrics.py`, `src/core/compute_snapshot.py` | `tests/test_tier_logic.py`, `tests/test_config_contract.py` | Tier assignment threshold. |
| `quality.min_valid_points_core` | active | `src/core/metrics.py`, `src/core/compute_snapshot.py` | `tests/test_tier_logic.py`, `tests/test_config_contract.py` | Tier assignment threshold. |
| `alerts.z_threshold` | active | `src/core/compute_snapshot.py`, `src/core/alerts.py` | `tests/test_alerts_logic.py` | Alert threshold parameter. |
| `alerts.persistence_snapshots` | active | `src/core/compute_snapshot.py`, `src/core/alerts.py` | `tests/test_alerts_logic.py` | Persistence gate parameter. |
| `alerts.pessimistic_gate` | active | `src/core/alerts.py`, `src/core/compute_snapshot.py` | `tests/test_alerts_logic.py`, `tests/test_config_contract.py` | Operative pessimistic/worst-case behavior. |
| `regime.vix_pct_calm` | active | `src/core/regime.py` | `tests/test_regime.py`, `tests/test_config_contract.py` | Config-driven regime thresholds. |
| `regime.vix_pct_stress` | active | `src/core/regime.py` | `tests/test_regime.py`, `tests/test_config_contract.py` | Config-driven regime thresholds. |
| `regime.rv20_pct_calm` | active | `src/core/regime.py` | `tests/test_regime.py`, `tests/test_config_contract.py` | Config-driven regime thresholds. |
| `regime.rv20_pct_stress` | active | `src/core/regime.py` | `tests/test_regime.py`, `tests/test_config_contract.py` | Config-driven regime thresholds. |
| `regime.drawdown_calm` | active | `src/core/regime.py` | `tests/test_regime.py`, `tests/test_config_contract.py` | Config-driven regime thresholds. |
| `regime.drawdown_stress` | active | `src/core/regime.py` | `tests/test_regime.py`, `tests/test_config_contract.py` | Config-driven regime thresholds. |
| `regime.event_path` | active | `src/core/config.py`, `src/core/regime.py` (S4 wiring) | `tests/test_regime.py`, `tests/test_config_contract.py` | Scheduled-event source path (`config/regime_events_v1.yaml`). |
| `regime.stress_proxy_ticker` | active | `src/core/config.py`, `src/core/regime.py` (S4 wiring) | `tests/test_regime.py`, `tests/test_config_contract.py` | Cross-domain stress proxy ticker selector. |
| `regime.weights.vix` | active | `src/core/config.py`, `src/core/regime.py` (S4 wiring) | `tests/test_regime.py`, `tests/test_config_contract.py` | Multi-signal weight for VIX component. |
| `regime.weights.rv20` | active | `src/core/config.py`, `src/core/regime.py` (S4 wiring) | `tests/test_regime.py`, `tests/test_config_contract.py` | Multi-signal weight for RV20 component. |
| `regime.weights.drawdown` | active | `src/core/config.py`, `src/core/regime.py` (S4 wiring) | `tests/test_regime.py`, `tests/test_config_contract.py` | Multi-signal weight for drawdown component. |
| `regime.weights.event` | active | `src/core/config.py`, `src/core/regime.py` (S4 wiring) | `tests/test_regime.py`, `tests/test_config_contract.py` | Multi-signal weight for scheduled-event component. |
| `regime.weights.stress_proxy` | active | `src/core/config.py`, `src/core/regime.py` (S4 wiring) | `tests/test_regime.py`, `tests/test_config_contract.py` | Multi-signal weight for stress-proxy component. |
| `structures.skew_fade.short_put_delta` | active | `src/core/trade_ideas.py` | `tests/test_trade_ideas.py`, `tests/test_config_contract.py` | Template leg parameterized. |
| `structures.skew_fade.long_put_delta` | active | `src/core/trade_ideas.py` | `tests/test_trade_ideas.py`, `tests/test_config_contract.py` | Template leg parameterized. |
| `structures.fly.wing_delta` | active | `src/core/trade_ideas.py` | `tests/test_trade_ideas.py`, `tests/test_config_contract.py` | Template leg parameterized. |
| `structures.calendar.front_dte_min` | active | `src/core/trade_ideas.py` | `tests/test_trade_ideas.py`, `tests/test_config_contract.py` | Calendar leg parameterized. |
| `structures.calendar.front_dte_max` | active | `src/core/trade_ideas.py` | `tests/test_trade_ideas.py`, `tests/test_config_contract.py` | Calendar leg parameterized. |
| `structures.calendar.back_dte_min` | active | `src/core/trade_ideas.py` | `tests/test_trade_ideas.py`, `tests/test_config_contract.py` | Calendar leg parameterized. |
| `structures.calendar.back_dte_max` | active | `src/core/trade_ideas.py` | `tests/test_trade_ideas.py`, `tests/test_config_contract.py` | Calendar leg parameterized. |

## Runtime and Test Enforcement Rules

- Runtime behavior:
  - unknown high-impact keys emit warnings on config load,
  - deprecated keys emit informational warnings when present.
- Test behavior:
  - unknown high-impact keys fail strict validation,
  - high-impact active keys are checked against contract coverage in `tests/test_config_contract.py`.

## Regime Threshold Drift Note

When `regime.*` threshold values change, persisted `regime_state` rows may no longer align with current assumptions.

- Current implementation requirement:
  - emit runtime warning on threshold-hash drift.
- Operational expectation:
  - recompute regime history before replay/backtest comparisons under changed thresholds.

## Residual Gaps (Post-Sprint-2)

- Add direct tests for logging and connection-path behavior.
- Add explicit tests for `data.capture_all_expiries` and selected IB parameters.
- Add explicit config-effect tests for `metrics.zscore_window_days`.

## Change Log

- 2026-04-28: Initial scaffold created.
- 2026-04-29: Post-Sprint-2 as-built cleanup; removed stale target markers and aligned coverage mapping.
