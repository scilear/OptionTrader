# OptionTrader S4-03 Transition FP Remediation and Adversarial Review

Date: 2026-05-18
Owner: PM (lead solution design)
Scope: Find a practical fix for the remaining S4-03 blocker and stress-test it adversarially.

## 1) Problem statement

After warm-up exclusion and labeling fixes, S4-03 remains blocked by one substantive issue:

- Transition false-positive density worsens in candidate vs baseline.

Full-span post-warm-up evidence:

- Baseline transition FP density: `0.5961538461538461`
- Candidate transition FP density: `0.6595744680851063`
- Delta: `+0.06342062193126019` (worse)

Source: `docs/roadmap/OptionTrader_S4_03_Release_Validation_Payload_full_span_post_warmup.json`

## 2) Root-cause diagnosis (from current runs)

Transition alert mix (candidate run) is dominated by RR alerts with very high FP concentration:

- `RR_EXTREME`: `114` alerts, `93` FP (FP density `0.8158`)
- `TERM_KINK`: `55` alerts, `17` FP (FP density `0.3091`)
- `FLY_EXTREME`: `19` alerts, `14` FP (FP density `0.7368`)

Baseline also has RR-heavy transition noise, but candidate amplifies RR transition volume sharply.

Inference:

- Main practical blocker is **RR transition over-triggering**.

## 3) Candidate solution set (what-if analysis)

What-if simulation was run by filtering existing candidate alerts (full span, post warm-up) and
recomputing metric outcomes analytically. This is directional evidence; final decisions still require
full pipeline reruns after implementation.

Baseline reference:

- Alerts: `426`
- Precision: `0.1478`
- Transition FP density: `0.5962`

What-if scenarios:

| Policy | Alerts | Volume vs baseline | Precision | Transition FP density |
|---|---:|---:|---:|---:|
| Current candidate | 1014 | +138.0% | 0.1659 | 0.6596 |
| RR global threshold z>=5 | 381 | -10.6% | 0.3050 | 0.5426 |
| RR global threshold z>=6 | 343 | -19.5% | 0.3464 | 0.4881 |
| RR z>=5 in Calm/Stress, z>=6 in Transition | 371 | -12.9% | 0.3149 | 0.4881 |
| Drop RR+FLY in Transition | 881 | +106.8% | 0.1893 | 0.3091 |

Observations:

1. Raising RR threshold is the strongest lever for transition FP reduction.
2. A regime-specific RR policy can pass transition density and keep volume near guardrails.
3. Term signal appears materially cleaner than RR in Transition.

## 4) Proposed solution (PM recommendation)

Implement **Regime-Conditioned RR Gating v1**:

1. Keep `TERM_KINK` unchanged.
2. For `RR_EXTREME`:
   - `Transition`: require `abs(zscore_mid) >= 6.0`
   - `Calm`/`Stress`: require `abs(zscore_mid) >= 5.0`
3. Keep `FLY_EXTREME` unchanged in v1 (observe impact first).

Why this first:

- Targets the dominant FP source directly.
- Preserves signal family diversity (does not hard-disable RR).
- Expected to improve transition density while keeping volume in a controllable band.

## 5) Adversarial review - Round 1

### Attack A - Overfitting to one window

Risk:

- Thresholds tuned on full span may not generalize.

Mitigation:

- Validate on at least 2010-2012 and full span using same fixed thresholds.
- Keep 2023 as sparsity monitor, not decision anchor.

Verdict: manageable if thresholds are frozen pre-rerun.

### Attack B - Killing true positive crises

Risk:

- Higher RR threshold might remove true stress signals.

Check:

- Current RR transition TP count is very low (2), while FP burden is very high.

Mitigation:

- Start with transition-only stricter threshold; keep stress RR at a lower but stricter-than-current level.

Verdict: acceptable tradeoff for v1.

### Attack C - Hidden precision inflation by collapsing volume

Risk:

- Precision can rise simply by suppressing too many alerts.

Mitigation:

- Keep explicit volume delta guardrail check vs baseline in rerun acceptance.

Verdict: controlled.

## 6) Adversarial review - Round 2 (fine-tuning)

### Attack D - RR not the only offender (FLY still noisy)

Risk:

- FLY transition FP density remains high.

Mitigation:

- If v1 still fails, run v2 with additional transition-only FLY tightening or suppression.

Verdict: reserve for v2; do not bundle in v1.

### Attack E - Regime quality itself still weakly independent

Risk:

- Stress proxy is highly correlated with VIX (`corr=1.0`), reducing true independence.

Mitigation:

- Track as parallel hardening item; do not block v1 RR remediation on this.

Verdict: separate structural follow-up.

## 7) Dev implementation instructions (v1)

Files expected:

- `src/core/compute_snapshot.py`
- `config/config-v1.yaml`
- `config/config-eod-truth.yaml`
- `config/config-test.yaml`
- `tests/test_alerts_logic.py`
- `tests/test_regime_filter.py`

Changes:

1. Add configurable regime-conditioned alert-type overrides:
   - `alerts.regime_overrides.Transition.RR_EXTREME.min_abs_zscore`
   - `alerts.regime_overrides.Calm.RR_EXTREME.min_abs_zscore`
   - `alerts.regime_overrides.Stress.RR_EXTREME.min_abs_zscore`
2. Enforce override gate in compute path before alert persistence.
3. Emit explicit explain reason when blocked by regime override.

Test requirements:

- Transition RR alert blocked below threshold.
- Transition RR alert passes above threshold.
- Calm/Stress RR thresholds applied correctly.
- Non-RR alert types unaffected by RR override.

## 8) Acceptance criteria for closure decision

Run required windows after v1 implementation:

- 2010-2012 post warm-up
- full span post warm-up

Pass criteria:

1. Transition FP density non-worsening vs baseline.
2. Precision non-regression vs baseline.
3. Volume guardrail within agreed tolerance.
4. Evidence-valid taxonomy (not `invalid_evidence`).

If any fail:

- move to v2 (add Transition FLY tightening), then rerun.
