# OptionTrader S4-03 Alert Scarcity Assessment and Window Expansion Plan

Date: 2026-05-05
Scope: Diagnose extremely low alert frequency before final S4-03 business conclusions.
Related docs:
- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact.md`
- `docs/roadmap/PM_S4_03_Status_Update_2026-05-05.md`
- `docs/roadmap/OptionTrader_S4_03_EOD_Source_Truth_Spec.md`

## Executive Position

Observed scarcity (1 alert per track over 2023) is too low for reliable statistical inference under
the current gate contract. This does not prove the business idea is bad. It also does not prove the
detection is sound. It indicates we must first separate three possibilities:

1. signal is genuinely rare but valuable,
2. gates are overly restrictive for this dataset,
3. implementation/evaluation path has correctness issues.

## Why This Still Matters in the Big Picture

S4-03 is a falsification gate, not a volume target. Its job is to prevent adding complexity that does
not improve outcomes. Even if the signal is rare, the gate framework is useful because it protects us
from promoting non-incremental features.

However, if sample size is persistently tiny, we must switch from high-frequency style metrics to
event-driven validation metrics (coverage and quality on stress episodes), while preserving strict
reproducibility.

## High-Priority Correctness Checks (Before Business Conclusion)

### C1. Baseline vs Candidate Path Integrity

Current track materialization script clones snapshots then computes both tracks using the same active
runtime code path, which risks relabeling instead of true baseline/candidate model divergence.

- File: `scripts/materialize_s4_tracks_from_eod.py`
- Risk: lineages may be tags only if model/profile differs are not enforced.

Required check:

- prove baseline and candidate use distinct regime/signal profiles at compute time,
- persist profile identifiers used for each run.

### C2. Alert Time-Series Scope Integrity

Alert generation currently builds metric history from broad surface-metrics selection in compute path.
Any missing filter by underlying/run/allowed history horizon can cause contamination or lookahead bias.

- File: `src/core/compute_snapshot.py`

Required check:

- enforce metric history scope to intended underlying and allowed temporal boundary,
- add regression tests for no cross-track contamination and no future leakage.

### C3. Gate Attrition Waterfall

Need explicit per-gate pass/fail counts:

- surface_qc gate,
- z-score threshold,
- persistence gate,
- regime gate,
- tradability gate.

If one gate removes ~all candidates, scarcity may be a calibration/data-path issue, not idea failure.

## Statistical Interpretation Rule

Do not interpret precision deltas with effectively one observation per track.

Minimum practical evidence thresholds for production ablation decision:

- alerts per track: `>= 100` (preferred),
- outcomes observed per track: `>= 60`,
- transition alerts per track: `>= 20`.

If below threshold, status remains `insufficient_statistical_power` even when scripts run correctly.

## Window Expansion Plan (Production Evidence)

### W0. Keep Contract Deterministic

- fixed underlying: `SPX`
- fixed data source: EOD truth DB
- fixed lineages/profiles recorded in run metadata
- no hidden threshold changes

### W1. Evaluate Multiple Fixed Windows

Run S4-03 evidence on predefined windows:

1. `2018-01-01` to `2019-12-31`
2. `2020-01-01` to `2021-12-31`
3. `2022-01-01` to `2023-12-31`
4. full span available in truth DB (as stress test)

For each window, publish:

- snapshot/alert/outcome counts by lineage,
- gate status,
- per-gate attrition waterfall.

### W2. Episode-Based Slice (If Still Sparse)

Add stress-episode slices (documented and fixed list), e.g.:

- COVID shock window,
- 2022 inflation tightening regime,
- any other predefined macro-stress windows.

Evaluate whether signal coverage is concentrated but meaningful in those regimes.

### W3. Decision Outcomes

- If counts become adequate and gates pass: move to S4-03 closure recommendation.
- If counts remain inadequate after correctness fixes and wider windows:
  - classify engine as low-frequency overlay,
  - re-spec S4-03 acceptance to event-driven metrics,
  - keep production defaults conservative until approved.

## Dev Task Addendum

Add to S4-03 implementation backlog:

1. enforce true baseline/candidate profile divergence in materialization workflow,
2. add contamination/lookahead tests in compute path,
3. produce gate-attrition report script,
4. run window expansion matrix and publish a consolidated evidence table.

## Suggested Output Artifacts

- `docs/roadmap/OptionTrader_S4_03_Window_Matrix_Results.md`
- `docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report.md`
- updated `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact.md`
