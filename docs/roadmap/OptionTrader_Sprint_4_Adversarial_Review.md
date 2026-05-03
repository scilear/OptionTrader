# Adversarial Review: Sprint 4 (Regime Model Independence)

**Date**: 2026-05-02
**Reviewer**: Gemini CLI (Adversarial Auditor)
**Status**: 🔴 CRITICAL FINDINGS

## 1. Executive Summary
The Sprint 4 implementation ("Regime Model Independence") currently suffers from a disconnect between the code logic, the database schema, and the validation gates. While the code attempts to transition to a multi-signal model, it is effectively non-functional in its current state due to missing database columns and circular logic dependencies.

## 2. Critical Findings

### ⚠️ A. Schema-Code Desynchronization
**File**: `src/core/regime.py` vs `src/db/schema.sql`
- **Issue**: The implementation of `compute_regime_state` attempts to write to 6 columns that do not exist in the master schema: `vix_spot`, `rv20_value`, `drawdown_value`, `event_score`, `stress_proxy_score`, and `decomposition`.
- **Impact**: **Immediate Runtime Failure**. Any attempt to persist a regime state will trigger a SQL error (`column does not exist`).
- **Recommendation**: Synchronize `src/db/schema.sql` and provide a migration path in `src/db/init_db.py`.

### ⚠️ B. Logical Circularity (The "RV-Only" Trap)
**File**: `src/core/regime.py` (L186-L187)
- **Issue**: The code aliases `vix_pct` directly to `rv_pct`:
  ```python
  vix_pct = float(row["rv_pct"])
  rv20_pct = float(row["rv_pct"])
  ```
- **Impact**: The "Multi-Signal" model is an illusion. VIX (Implied Volatility) is not actually used; the system remains 100% dependent on Realized Volatility (RV). This violates the core objective of Sprint 4.
- **Recommendation**: Update `compute_regime_state` to pull actual VIX data from snapshots or an external ticker source.

### ⚠️ C. Invalid Ablation Gates
**File**: `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact.md`
- **Issue**: The ablation gate for new features (`event`, `stress_proxy`) failed not because the features were "bad," but because "outcome labels are not currently persisted in v1 schema."
- **Impact**: Without "Good/Bad" labels on historical trades, the system cannot mathematically prove incremental value. Disabling these features based on a "failed gate" with zero data is a procedural error.
- **Recommendation**: Implement Trade Outcome persistence before concluding the S4-03 Ablation task.

## 3. Adversarial Edge Cases

1.  **Cold-Start Failure**: The regime requires a 63-day lookback for drawdown. In a fresh database, the first 62 days of snapshots will result in `NaN` regime scores. There is currently no user-facing warning explaining why regime data is missing during this "warm-up" period.
2.  **Config Hash Fragility**: The `regime_config_hash` includes the `event_path`. If the project is moved to a different absolute path, the hash will change, falsely indicating a "threshold change" and triggering unnecessary recompute warnings.
3.  **Stress Proxy Mockery**: `_stress_proxy_score` is currently a deterministic function of `rv20_pct`. It does not provide any independent cross-domain signal, making it redundant.

## 4. Required Mitigations (Action Plan)

1.  **Fix Schema**: Add missing columns to `regime_state` table.
2.  **Fetch Actual VIX**: Break the link between `vix_pct` and `rv_pct`.
3.  **Persistence of Outcomes**: Add a table or column to track trade performance (e.g., `realized_pnl` or `is_winner`) to enable valid ablation testing.
4.  **Warm-up Validation**: Add a check for `len(snapshots) >= 63` before attempting regime calculation, with a clear log message if failed.
