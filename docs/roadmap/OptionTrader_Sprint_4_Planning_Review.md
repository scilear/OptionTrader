# OptionTrader Sprint 3.2 & Sprint 4 Planning Review

Date: 2026-04-30
Reviewer: Gemini CLI
Status: **APPROVED FOR ASSIGNMENT**

## 1. Executive Summary

A comprehensive adversarial review was performed on the Sprint 3.2 (Closure) and Sprint 4 (Regime Model Independence) planning package. The package is high-signal, architecturally sound, and adheres to the program's core principles of "Uncertainty First-Class" and "Fail Closed."

## 2. Adversarial Review Report

### 2.1 Sprint 3.2 (Closure)
This phase bridges the technical wins of Sprint 3 to system-wide observability.

*   **Risk: The "Vague Window" (S3.2-01)**
    *   *Critique:* If the replay window is not explicitly fixed, the comparison baseline vs. S3 is prone to selection bias.
    *   *Recommendation:* Hard-code the `start_ts` and `end_ts` for the "Official Sprint 3 Baseline" in the Execution Plan (e.g., "April 1-15, 2026, SPX quotes").
*   **Risk: "Operational Blindness" (S3.2-02)**
    *   *Critique:* QC frequency monitoring is useless if not checked proactively. Developers may ignore it until all alerts stop.
    *   *Recommendation:* Mandate that S3.2-02 includes a health check script (`scripts/qc_health_check.sh`) that returns a non-zero exit code if the block rate exceeds 20% over a 1-hour window.

### 2.2 Sprint 4 (Regime Model Independence)
Sprint 4 transitions from simple proxy logic to a multi-signal regime model.

*   **Risk: "Data Source Gap" (S4-02)**
    *   *Critique:* Integration of FOMC/CPI flags is a P0 dependency but lacks an ingestion path definition.
    *   *Recommendation:* Clarify if "Scheduled Events" are fetched via API or a manual JSON/YAML file. If manual, add the file path to the "Expected Files" list for S4.
*   **Risk: "Feature Overfitting" (S4-03)**
    *   *Critique:* New regime features may look good in-sample but add no predictive value.
    *   *Recommendation:* Define the "Lift" metric explicitly. I recommend **"Alert Precision improvement while maintaining volume"** as the primary gate for feature retention.

## 3. Owner Assignment Matrix (Proposed)

| Ticket | Role | Est. | Dependency | Primary Risk |
| :--- | :--- | :--- | :--- | :--- |
| **S3.2-01** | Lead Quant | 1.0 Day | S3.1 Closure | Inconsistent window selection |
| **S3.2-02** | Ops/Full-Stack | 1.0 Day | S3.1 Schema | Hidden QC blocks in sparse tenors |
| **S4-00** | DB/Data Eng | 0.5 Day | S3.2 Closure | Schema migration friction |
| **S4-01** | Core Quant | 1.5 Days | S4-00 | Over-weighting specific features |
| **S4-02** | Data Eng | 1.5 Days | S4-01 | Unreliable macro-event source |
| **S4-03** | Lead Quant | 1.0 Day | S4-02 | Overfitting to the replay window |
| **S4-04** | Core Dev | 0.5 Day | S4-01 | Silent hash-check bypass |

## 4. Final Verdict

The planning package is **Ready for Assignment**. The dependencies (S3.2 -> S4) are correctly mapped, and the "Ablation Gate" (S4-03) provides the necessary discipline to prevent model bloat.
