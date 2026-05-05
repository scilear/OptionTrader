# PM Findings - S4-03 Alert Scarcity (2010-2012)

Date: 2026-05-05

## Scope Executed

Followed `docs/roadmap/OptionTrader_S4_03_Alert_Scarcity_Assessment_and_Window_Expansion_Plan.md` for the fixed window:

- Start: `2010-01-01T00:00:00Z`
- End: `2012-12-31T23:59:59Z`
- Underlying: `SPX`
- Data source: `data/optiontrader_eod_truth.duckdb`
- Lineages: baseline `3b024c9`, candidate `5128e8e`

## What Was Run

1. Materialization: `scripts/materialize_s4_tracks_from_eod.py`
2. Outcome evaluation: `scripts/evaluate_alert_outcomes.py --horizon-days 5 --overwrite`
3. Ablation artifact generation: `scripts/generate_regime_ablation_artifact.py`

Output artifact:

- `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_2010_2012.md`

## Findings

### F1. Window is large enough in snapshots, but still produced zero alerts

- Source EOD snapshots in window: `745`
- Materialized snapshots per track: baseline `745`, candidate `745`
- Alerts per track in ablation output: baseline `0`, candidate `0`

Interpretation: alert scarcity persists even after expanding to 2010-2012.

### F2. Gate status remains blocked/failed

From `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_2010_2012.md`:

- `status`: `blocked_pending_precision_labels`
- `min_sample_pass`: `false`
- `precision_gate_pass`: `false`
- `transition_fp_gate_pass`: `false`
- `volume_gate_pass`: `false`
- `overall_pass`: `false`

### F3. Available attrition proxy indicates suppression before alert stage

From DB checks on track runs (`run_id=9`, `run_id=10`):

- `surface_metrics` rows: `25` per run
- `surface_metrics.qc_pass=true`: `23` per run
- `alerts` rows: `0` per run

Interpretation: with current data/fit support, the pipeline produces very few eligible surface metric rows and no alert emissions in this window.

## Plan Alignment Status (from Scarcity Plan)

- W1 (fixed-window expansion): **Partially executed** for one window (`2010-2012`).
- C1 (baseline/candidate path integrity proof): **Not fully closed** in evidence artifacts.
- C2 (history contamination/lookahead regression proof): **Not fully closed** in evidence artifacts.
- C3 (explicit gate-attrition waterfall report): **Not fully closed**; current report includes only a proxy waterfall.

## Recommendation to PM (Acceptance Criteria Refinement)

Given persistent zero-alert output in a 745-snapshot window, treat this as **insufficient statistical power** for business acceptance decisions, not as proof of feature value/failure.

Proposed acceptance refinement for this topic:

1. Require correctness evidence first (C1/C2/C3 complete) before business decisioning.
2. Classify current state as `insufficient_statistical_power` when alerts/outcomes are below practical thresholds.
3. Run the remaining W1 windows from the plan (`2018-2019`, `2020-2021`, `2022-2023`, full-span stress window) and publish a consolidated matrix before final S4-03 judgment.

## File References

- Plan followed: `docs/roadmap/OptionTrader_S4_03_Alert_Scarcity_Assessment_and_Window_Expansion_Plan.md`
- Window artifact: `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_2010_2012.md`
- Materialization workflow: `scripts/materialize_s4_tracks_from_eod.py`
- Outcome labeling: `scripts/evaluate_alert_outcomes.py`
- Ablation generator: `scripts/generate_regime_ablation_artifact.py`
