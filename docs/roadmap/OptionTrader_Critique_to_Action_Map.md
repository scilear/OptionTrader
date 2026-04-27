# OptionTrader Critique-to-Action Map

Date: 2026-04-27
Sources mapped:
- `reports/technical/OptionTrader_Assessment_SPX.md`
- `agents/vol-specialist/knowledge-base/journal/2026-04-27_decision-paths-adversarial-review.md`

## Purpose

Translate adversarial findings into concrete implementation actions, ownership scope, and measurable exit criteria.

## Mapping Table

### 1) "Surface is not a surface"

Critique:
- No smoothing/interpolation/error model; noisy points treated as structure.

Action:
- Introduce fitted smile/tenor extraction with explicit model-selection protocol.
- Persist fit residuals and confidence per bucket.
- Define decision thresholds: what residual level blocks signal generation.

Files:
- `src/core/metrics.py`
- `src/core/iv_solve.py`
- `src/db/schema.sql`

Exit criteria:
- Metric discontinuities from strike boundary transitions are materially reduced.
- Alerts auto-block when fit quality is below threshold.
- Chosen surface class beats alternatives in ablation on stability and OOS utility.

### 2) "Nearest-delta mapping biases metrics"

Critique:
- RR/FLY can become selection artifacts under sparse liquidity.

Action:
- Replace direct nearest pick with interpolation on standardized delta grid.
- Add minimum support checks per wing.

Files:
- `src/core/metrics.py`
- `tests/test_tier_logic.py`

Exit criteria:
- Reduced alert churn during small spot moves when chain composition changes.

### 3) "Z-score detection is regime-blind"

Critique:
- Regime-mixed distributions make static 2-sigma unreliable.

Action:
- Regime-conditional thresholds and robust anomaly score.
- Split signal states: candidate vs execution-ready.

Files:
- `src/core/alerts.py`
- `src/core/compute_snapshot.py`
- `tests/test_alerts_logic.py`

Exit criteria:
- Transition-regime false positives fall relative to baseline.
- Regime-conditional model outperforms global threshold baseline in OOS tests.

### 4) "Worst-case gate is shallow"

Critique:
- Deterministic penalty without execution model depth.

Action:
- Add friction model (spread + slippage proxy + liquidity depth proxy).
- Require edge-after-friction positive for execution-ready status.
- Add nonlinear impact function by size and convexity-aware cost stress.

Files:
- `src/core/tradability.py`
- `src/core/trade_ideas.py`
- `src/app/streamlit_app.py`

Exit criteria:
- No tradeable output when friction-adjusted edge <= 0.
- Ranking is robust under size-scaling and slippage-stress scenarios.

### 5) "Regime model is not independent"

Critique:
- RV used as VIX proxy introduces endogenous regime signal.

Action:
- Refactor regime features to independent signals; wire config thresholds.
- Persist component-level regime inputs.
- Add event-calendar features (FOMC/CPI) and at least one cross-domain stress proxy.

Files:
- `src/core/regime.py`
- `config/config-v1.yaml`
- `src/db/schema.sql`

Exit criteria:
- Regime labels are explainable by independent features, not RV-only behavior.
- Regime block shows incremental value vs endogenous-only baseline in ablation.

### 6) "No-arbitrage omission"

Critique:
- Surface geometry may be inconsistent, causing phantom anomalies.

Action:
- Add static no-arbitrage checks and use as hard blocker for alerting.

Files:
- `src/core/metrics.py`
- new `src/core/surface_qc.py`
- `tests/` new no-arbitrage tests

Exit criteria:
- Alerts are suppressed on arbitrage-violating surfaces.
- This path is a hard blocker, not informational tagging.

### 7) "Persistence window may lag fast dislocations"

Critique:
- Current persistence may miss short-half-life opportunities.

Action:
- Introduce horizon-specific persistence profiles by signal family.
- Keep conservative defaults for SPX unless validated otherwise.

Files:
- `src/core/alerts.py`
- `config/config-v1.yaml`

Exit criteria:
- Improved hit-rate/latency tradeoff in replay, without alert spam.

### 8) "Trade templates disconnected from edge decomposition"

Critique:
- Static mapping from alert type to structure is simplistic.

Action:
- Candidate generation with ranking by expected edge-after-cost and risk budget fit.

Files:
- `src/core/trade_ideas.py`
- `src/core/export.py`
- `src/app/streamlit_app.py`

Exit criteria:
- Top-ranked ideas consistently dominate lower-ranked candidates in replay stats.

### 9) "Config drift illusion"

Critique:
- Parameterized config with partially hardcoded behavior.

Action:
- Build config contract matrix and enforce via tests.

Files:
- `src/core/config.py`
- `config/config-v1.yaml`
- `tests/` config behavior tests

Exit criteria:
- Every high-impact config key has a test-proven runtime effect.

### 10) "No error propagation"

Critique:
- Noise compounds across solver -> mapping -> alerts without uncertainty tracking.

Action:
- Propagate uncertainty/confidence through each stage and gate on it.
- Treat uncertainty as a blocking control variable, never as standalone signal input.

Files:
- `src/core/iv_solve.py`
- `src/core/metrics.py`
- `src/core/compute_snapshot.py`
- `src/db/schema.sql`

Exit criteria:
- Each alert includes uncertainty fields and can be blocked for high uncertainty.
- Uncertainty calibration quality is measured; if uncalibrated, uncertainty remains gating-only metadata.

### 11) "Architecture growth may outpace falsification"

Critique:
- Capability and explainability can grow without predictive lift.

Action:
- Enforce per-sprint ablation and reduction: components without incremental OOS value are removed.

Files:
- `src/core/replay.py`
- new `scripts/validate_release.py`
- `docs/roadmap/OptionTrader_Next_Level_Plan.md`

Exit criteria:
- Release blocked unless each retained component demonstrates incremental OOS value.

## Pushback Register (Intentional Disagreements)

1. Persistence critique requires SPX-specific validation.
- We should not blindly reduce persistence globally; for index surfaces, slower persistence can reduce noise.

2. Dividend critique is lower priority than non-zero rates for SPX index-level signals.
- Updated stance: rates/dividend integration is promoted to immediate baseline (Sprint 1).

3. "VIX correlation gate" is insufficient by itself.
- We need a proper independent regime block, not a single additional feature gate.

## Priority Stack

P0 (must ship first):
- Config truth, decision trace, rates/dividend baseline, hard-block surface integrity checks, uncertainty gating.

P1 (next):
- Regime independence, robust anomaly logic, execution-aware ranking.

P2 (after validation):
- Additional model complexity only if OOS metrics justify it.

## Definition of Done

The critique is considered addressed only when:

- OOS execution-adjusted expectancy is positive,
- alert precision improves with stable or lower volume,
- all alerts are auditable and uncertainty-tagged,
- adversarial tests pass consistently,
- each retained major component passes ablation-based incremental value tests.
