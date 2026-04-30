# OptionTrader Surface Model Card (Sprint 3)

Date: 2026-04-29
Status: Selected, implemented, and post-review hardened (S3.2 closure)
Owner: Core quant engineering
Scope: `src/core/surface_fit.py`, `src/core/surface_qc.py`, `src/core/compute_snapshot.py`

## Purpose

Define the surface fit model, diagnostics, acceptance thresholds, fallback policy, and QC hard-block behavior used to gate alert generation.

## Candidate Models Evaluated

| Candidate | Description | Pros | Cons | Decision |
|---|---|---|---|---|
| `linear_delta_v1` | Piecewise linear interpolation in delta space per tenor and side (C/P), with exact-delta pass-through. | Deterministic, transparent, stable under one-strike perturbations, easy to unit-test and audit. | Not globally smooth; may underfit highly curved smiles. | **Selected** |
| `nearest_neighbor_v0` | Pick nearest strike by absolute delta distance. | Very simple and fast. | Discontinuous bucket jumps under small strike-set changes; weakest robustness profile. | Rejected (kept only as degraded fallback mode) |

## Selected Model

- Model name: `linear_delta_v1`
- Version id: `linear_delta_v1`
- Code path: `src/core/surface_fit.py`
- Effective date: 2026-04-29

## Input Domain and Preconditions

- Required per-tenor support:
  - minimum 2 quotes per side (`C` and `P`) for interpolation-grade status.
- Required per-wing support:
  - target delta must be bracketed by same-side solved deltas for interpolated `ok` status.
  - exact delta hit is accepted as `ok` with `fit_model_id=exact_delta_v1`.
- Quote quality prerequisites:
  - points come from solved quotes only (`iv_mid is not None`),
  - quote-level quality gate from `spread_gate_pct` remains upstream in `compute_iv_points`.

## Fit Diagnostics

- Primary residual metric:
  - `fit_residual`: local bracket IV span `|iv_upper - iv_lower|`.
- Secondary stability/health metrics:
  - `fit_support`: available same-side support size,
  - `fit_confidence`: normalized confidence score in `[0, 1]`,
  - `fit_reason_codes`: machine-readable fit caveats.
- Confidence score definition:
  - interpolated/exact: based on available point quality,
  - degraded fallback: downweighted confidence (`0.25 * quality`).

## Acceptance Thresholds

- Fit residual threshold (operational):
  - persisted for monitoring; no standalone hard-block threshold in Sprint 3.
- Stability threshold:
  - adversarial stability score target: `max ΔIV <= 0.02` under one-OTM strike removal test fixture.
- Support threshold:
  - `< 2` same-side support for target delta is degraded.

## Rejection and Fallback Policy

- Rejection conditions (fit-level):
  - insufficient same-side support (`insufficient_support`),
  - target delta outside side support range (`delta_out_of_range`).
- Fallback mode:
  - nearest available side quote with explicit `fit_model_id=nearest_fallback_v1`.
- Fallback alerting policy:
  - **not allowed**; any degraded point triggers QC hard block.
- Degraded fallback marker:
  - `solve_status="degraded"` (required and enforced).

## No-Arbitrage and QC Integration

- Vertical consistency checks:
  - RR magnitude inversion guard,
  - negative fly guards for 25d/10d wings.
  - RR inversion is a conservative policy gate (signal-quality heuristic), not a strict no-arbitrage identity.
- Calendar consistency checks:
  - total variance monotonicity check across tenors:
    - fail when `sigma_far^2 * T_far + epsilon < sigma_near^2 * T_near`.
  - this permits normal contango and focuses on backwardation-style variance inversion.
- Numerical tolerance:
  - split tolerances by domain:
    - `qc.no_arb_epsilon_iv` for IV-space vertical checks,
    - `qc.no_arb_epsilon_var` for variance-space calendar checks.
  - legacy `qc.no_arb_epsilon` remains as backward-compatible fallback.
- Check order:
  - vertical first, calendar second.
- QC reason code taxonomy:
  - `vertical_rr_magnitude_inversion`
  - `vertical_negative_fly25`
  - `vertical_negative_fly10`
  - `calendar_total_variance_violation:<near_bucket>-><far_bucket>`
  - `degraded_surface_fit`
  - `empty_surface_metrics`
- Hard-block behavior:
  - alerts/trade ideas are suppressed when QC fails.

## Validation Evidence

- Baseline/compare harness:
  - adversarial fixtures in `tests/test_surface_adversarial.py` and deterministic fit/QC tests.
- Metrics used:
  - status codes, reason codes, fit diagnostics, and Stability Score surrogate.
- Stability Score:
  - implemented as max bucket IV deviation under one-strike removal fixture; asserted bounded in tests.
- Current test evidence:
  - `tests/test_surface_fit.py`
  - `tests/test_surface_qc.py`
  - `tests/test_surface_adversarial.py`

## Known Failure Modes

- Sparse chain side support produces degraded buckets and alert hard block.
- Severe tenor inversion in noisy/illiquid windows can block all alerts for a snapshot.
- Linear interpolation can smooth over local convexity detail not captured by sparse quotes.

## Operational Notes

- Recompute triggers:
  - any config change under `metrics.*`, `quality.*`, `qc.*`, or quote ingestion behavior.
- Backfill policy:
  - additive schema; recompute snapshots to populate new diagnostics historically.
- Monitoring hooks:
  - track `qc_pass`, `qc_reason_codes`, `surface_quality_score`, and degraded fit incidence.

## Post-Review Closure Notes

- S3.1-01 completed:
  - epsilon semantics split by domain with backward compatibility (`no_arb_epsilon` fallback).
- S3.1-02 completed:
  - snapshot-scope indexes added on `iv_points(snapshot_id)` and `surface_metrics(snapshot_id)`.
- S3.1-03 completed:
  - model card, execution plan, and ticket sheet synchronized with final reason-code and tolerance policy.
- S3.2-02 completed:
  - QC monitoring and reason-code rollups operationalized via `scripts/qc_health_check.sh`.
- S3.2-01 completed:
  - replay artifact published at `docs/roadmap/OptionTrader_Sprint_3_2_Replay_Artifact.md`
    using locked contract window and lineage fields.
