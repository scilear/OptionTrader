# OptionTrader Sprint 3 Specification Review & Adversarial Pass

Date: 2026-04-29
Reviewer: Gemini CLI
Status: **APPROVED FOR EXECUTION**

## 1. Executive Summary

The Sprint 3 package (Execution Plan, Dev Ticket Sheet, and Surface Model Card) is technically sound and aligns with the core mandate of moving from "nearest-neighbor" picking to a "statistically stabilized surface." The plan correctly prioritizes structural integrity over signal volume by introducing fail-closed QC gates.

## 2. Adversarial Review Pass

I performed an adversarial review to identify failure modes where the plan might meet its "Done" criteria while failing its "Outcome" goals.

| Risk / Attack Vector | Impact | Analysis & Recommendations |
| :--- | :--- | :--- |
| **The "Silent Market" Risk** | High | Hard-blocking alerts on no-arbitrage failures (S3-04) might be too aggressive for noisy SPX quotes. If the QC module (S3-03) lacks an epsilon tolerance, the system may stop emitting alerts during volatile regimes exactly when they are most valuable. |
| **Recommendation** | - | **Action:** Add a `qc.no_arb_epsilon` config parameter to allow for minor numerical noise in consistency checks. |
| **Model Selection Latency** | Medium | S3-01 evaluation could become a "research rabbit hole," delaying the implementation of the fitting engine (S3-02). |
| **Recommendation** | - | **Action:** Timebox S3-01 to 0.75 day. If SVI/SSVI models show convergence issues, default to a constrained monotonic spline as a robust baseline. |
| **The "Fallback Trap"** | Medium | Fallback logic intended for robustness can silently reintroduce nearest-neighbor artifacts. |
| **Recommendation** | - | **Action:** Enforce that any "fallback" to nearest-neighbor logic MUST return a `solve_status="degraded"` which is a terminal block for the S3-04 alert path. |
| **Persistence Bloat** | Low | Storing full fit diagnostics (residuals, model params, quality scores) for every bucket in every snapshot may significantly increase DB size. |
| **Recommendation** | - | **Action:** Validate that S3-05 schema uses efficient types (e.g., float4/real) and consider a retention policy for raw diagnostics in non-alerting snapshots. |

## 3. Codebase Debt Review (Pre-Sprint Gates)

The plan correctly identifies two critical carry-over items that must be resolved before S3-02 starts:
1.  **Duplicate Tests:** `tests/test_alerts_logic.py` contains redundant function definitions that mask test failures.
2.  **Stray Code:** `src/core/metrics.py` has unreachable fragments after `return` statements that complicate static analysis.

## 4. Implementation Strategy Guidance

1.  **S3-02 (Fitting Engine):** Do not implement the fitter in-line within `compute_iv_points`. Create a standalone `src/core/surface_fit.py` to allow for independent testing and model swapping.
2.  **S3-03 (Surface QC):** Ensure vertical (strike) consistency is checked *before* calendar (tenor) consistency. A broken smile makes a broken term structure meaningless.
3.  **S3-06 (Adversarial Pack):** The success of the sprint hinges on the "Stability Score." Define this as the maximum change in bucket IV $(\Delta IV)$ resulting from the removal of a single OTM strike. Sprint 3 should show a $>50\%$ reduction in this metric vs baseline.

## 5. Final Verdict

The Sprint 3 package is **Ready for Execution**. The linear dependency from S3-00 to S3-06 is the correct path. No architectural changes are required before start, provided the "Silent Market" epsilon is addressed during S3-03 implementation.
