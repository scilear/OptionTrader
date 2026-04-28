# OptionTrader Config Contract Matrix

Date: 2026-04-28
Owner: Core engineering
Related sprint: `docs/roadmap/OptionTrader_Sprint_2_Execution_Plan.md`

## Purpose

Define a single, testable source of truth for configuration behavior.

Rules:

- Every high-impact key must be exactly one of: `active` or `deprecated`.
- `active` keys must map to runtime code path(s) and at least one test.
- `deprecated` keys must have an explicit rationale and migration/removal note.
- No key may remain in ambiguous state.
- Unknown high-impact keys must generate runtime warnings and test-time failures.

## Status Definitions

- `active`: key changes runtime behavior now and is test-covered.
- `deprecated`: key is retained temporarily for compatibility/docs, but is not expected to affect runtime behavior.

## Matrix

| Key Path | Status | Runtime Path(s) | Test Coverage | Notes |
|---|---|---|---|---|
| `app.mode` | deprecated | none | none | Not used in runtime dispatch. Keep only if legacy tooling still reads it. |
| `logging.level` | active | `src/core/logging_utils.py` | `tests/test_health.py` (indirect), TODO direct test | Direct unit test should assert level application. |
| `logging.file` | active | `src/core/logging_utils.py` | TODO | Add direct test for file handler creation. |
| `data.underlying` | active | `src/ingest/ingest_ib.py`, `src/ingest/ingest_yfinance.py` | TODO | Should be asserted in inserted snapshot rows. |
| `data.symbol` | active | `src/ingest/ingest_yfinance.py` | TODO | Add routing/ingest fixture assertion. |
| `data.dte_min` | active | `src/ingest/ingest_yfinance.py`, `src/core/compute_snapshot.py` | existing + TODO targeted | Covered in behavior; add explicit contract test. |
| `data.dte_max` | active | `src/ingest/ingest_yfinance.py`, `src/core/compute_snapshot.py` | existing + TODO targeted | Same as `dte_min`. |
| `data.snapshot_tags` | deprecated | none | none | Currently not consumed by ingest or pipeline. |
| `data.source` | active | `src/ingest/dispatcher.py` | TODO `tests/test_ingest_routing.py` | Must control IB-first vs yfinance-direct behavior. |
| `data.capture_all_expiries` | active | `src/ingest/ingest_yfinance.py` | TODO | Add contract test for include/exclude behavior. |
| `ib.hosts` | active | `src/ingest/ingest_ib.py` | existing indirect + TODO | Add deterministic test via monkeypatch. |
| `ib.port` | active | `src/ingest/ingest_ib.py` | TODO | Include in ingest routing tests. |
| `ib.client_id` | active | `src/ingest/ingest_ib.py` | TODO | Verify passed to IB connect call. |
| `ib.timeout_seconds` | active | `src/ingest/ingest_ib.py` | TODO | Verify passed to IB connect call. |
| `ib.strike_pct_range` | active | `src/ingest/ingest_ib.py` | TODO | Verify strike filtering behavior. |
| `ib.max_strikes_per_right` | active | `src/ingest/ingest_ib.py` | TODO | Verify cap behavior. |
| `storage.engine` | deprecated | none | none | Runtime always uses DuckDB connection path today. |
| `storage.path` | active | `src/db/connection.py` | `tests/test_run_manifest.py` (indirect), TODO direct | Should add direct connection-path test. |
| `pricing.rate` | active | `src/core/compute_snapshot.py`, `src/core/metrics.py` | `tests/test_pricing_inputs.py` | Implemented in Sprint 1. |
| `pricing.dividend_yield` | active | `src/core/compute_snapshot.py`, `src/core/metrics.py` | `tests/test_pricing_inputs.py` | Implemented in Sprint 1. |
| `metrics.delta_points` | active (target) | `src/core/metrics.py` | TODO | Must be wired in Sprint 2. |
| `metrics.zscore_window_days` | active | `src/core/compute_snapshot.py` | `tests/test_alerts_logic.py` (indirect), TODO direct | Add explicit config-effect test. |
| `metrics.expiry_buckets_days` | active | `src/core/compute_snapshot.py`, `src/app/streamlit_app.py` | TODO | UI currently hardcoded; Sprint 2 target is config-driven UI parity. |
| `quality.spread_gate_pct` | active | `src/ingest/ingest_yfinance.py`, `src/core/compute_snapshot.py`, `src/core/tradability.py` | existing + TODO contract | Add explicit gate sensitivity test. |
| `quality.allow_zero_bid` | active | `src/ingest/ingest_yfinance.py`, `src/ingest/ingest_ib.py` | existing indirect + TODO | Add direct quote-QC behavior test. |
| `quality.min_valid_points_full` | active (target) | `src/core/metrics.py` | TODO | Must drive tier logic in Sprint 2. |
| `quality.min_valid_points_core` | active (target) | `src/core/metrics.py` | TODO | Must drive tier logic in Sprint 2. |
| `alerts.z_threshold` | active | `src/core/compute_snapshot.py`, `src/core/alerts.py` | `tests/test_alerts_logic.py` | Existing behavior. |
| `alerts.persistence_snapshots` | active | `src/core/compute_snapshot.py`, `src/core/alerts.py` | `tests/test_alerts_logic.py` | Existing behavior. |
| `alerts.pessimistic_gate` | active (target) | `src/core/alerts.py` | TODO | Currently drift key; Sprint 2 wiring required. |
| `regime.vix_pct_calm` | active (target) | `src/core/regime.py` | TODO | Must map into `RegimeParams`. |
| `regime.vix_pct_stress` | active (target) | `src/core/regime.py` | TODO | Must map into `RegimeParams`. |
| `regime.rv20_pct_calm` | active (target) | `src/core/regime.py` | TODO | Must map into `RegimeParams`. |
| `regime.rv20_pct_stress` | active (target) | `src/core/regime.py` | TODO | Must map into `RegimeParams`. |
| `regime.drawdown_calm` | active (target) | `src/core/regime.py` | TODO | Must map into `RegimeParams`. |
| `regime.drawdown_stress` | active (target) | `src/core/regime.py` | TODO | Must map into `RegimeParams`. |
| `structures.skew_fade.short_put_delta` | active (target) | `src/core/trade_ideas.py` | TODO | Must drive RR template leg construction. |
| `structures.skew_fade.long_put_delta` | active (target) | `src/core/trade_ideas.py` | TODO | Must drive RR template leg construction. |
| `structures.fly.wing_delta` | active (target) | `src/core/trade_ideas.py` | TODO | Must drive fly template leg construction. |
| `structures.calendar.front_dte_min` | active (target) | `src/core/trade_ideas.py` | TODO | Must influence calendar template tenor selection. |
| `structures.calendar.front_dte_max` | active (target) | `src/core/trade_ideas.py` | TODO | Must influence calendar template tenor selection. |
| `structures.calendar.back_dte_min` | active (target) | `src/core/trade_ideas.py` | TODO | Must influence calendar template tenor selection. |
| `structures.calendar.back_dte_max` | active (target) | `src/core/trade_ideas.py` | TODO | Must influence calendar template tenor selection. |

## Runtime and Test Enforcement Rules

- Runtime behavior:
  - unknown high-impact keys must emit a warning at startup (or first config load),
  - deprecated keys should emit informational warning when present.
- Test behavior:
  - unknown high-impact keys must fail config contract tests,
  - every high-impact `active` key must have at least one explicit behavior test.

## Regime Threshold Drift Note

When `regime.*` threshold values change, previously persisted `regime_state` rows may no longer be consistent with current config assumptions.

- Sprint 2 requirement:
  - emit runtime warning if current regime-threshold config hash differs from the hash used to compute stored regime rows.
- Operational expectation:
  - recompute regime history before using replay/backtest comparisons under new thresholds.

## Sprint 2 Completion Checklist

- [ ] Remove all `(target)` markers by implementing and testing the wiring.
- [ ] Add or update tests for every `TODO` in Test Coverage column.
- [ ] Confirm every `deprecated` key has clear migration/removal note.
- [ ] Add CI check that fails if high-impact active keys are untested.

## Change Log

- 2026-04-28: Initial matrix scaffold created for Sprint 2 handoff.
