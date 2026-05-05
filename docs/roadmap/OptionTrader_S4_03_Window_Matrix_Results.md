# OptionTrader S4-03 Window Matrix Results

Date: 2026-05-05
Scope: Execute W1 window expansion from `docs/roadmap/OptionTrader_S4_03_Alert_Scarcity_Assessment_and_Window_Expansion_Plan.md` and summarize outcomes for PM acceptance refinement.

## Data Availability Check

Source truth DB (`data/optiontrader_eod_truth.duckdb`) has SPX EOD snapshots for:

- 2010: 250
- 2011: 245
- 2012: 250
- 2013: 69
- 2023: 249

No source snapshots are present for 2018-2022 in current local DB, so two planned W1 windows are not executable yet.

## Executed Windows and Outcomes

Lineages used in all executable windows:

- Baseline: `3b024c9`
- Candidate: `5128e8e`

| Window | Executable with current DB | Baseline snapshots | Candidate snapshots | Baseline alerts | Candidate alerts | Baseline outcomes | Candidate outcomes | Gate status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2010-01-01 to 2012-12-31 | Yes | 745 | 745 | 0 | 0 | 0 | 0 | blocked_pending_precision_labels |
| 2018-01-01 to 2019-12-31 | No (no source snapshots) | 0 | 0 | 0 | 0 | 0 | 0 | not_executable |
| 2020-01-01 to 2021-12-31 | No (no source snapshots) | 0 | 0 | 0 | 0 | 0 | 0 | not_executable |
| 2022-01-01 to 2023-12-31 | Yes (2023 only in practice) | 249 | 249 | 0 | 0 | 0 | 0 | blocked_pending_precision_labels |
| 2010-01-01 to 2023-12-31 (full available span) | Yes | 1063 | 1063 | 0 | 0 | 0 | 0 | blocked_pending_precision_labels |

## Artifact References

- 2010-2012 artifact: `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_2010_2012.md`
- 2022-2023 artifact: `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_2022_2023.md`
- Full-span artifact: `docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_full_span.md`

## Interpretation

1. Alert scarcity persists after widening to all currently available historical data (`2010-2023` span present locally).
2. Current evidence remains below practical statistical power thresholds in the scarcity plan, so business performance interpretation is not reliable.
3. The originally planned W1 windows for `2018-2019` and `2020-2021` cannot be assessed until those years are ingested into the truth DB.

## PM-Oriented Recommendation

For acceptance criteria on this topic, classify current state as:

- `insufficient_statistical_power` (not pass/fail on feature value), and
- `data-completeness-limited` for W1 matrix execution.

Before final S4-03 closure decision, complete:

1. ingest missing years covering `2018-2022`,
2. rerun full W1 matrix exactly as specified,
3. publish C1/C2/C3 correctness evidence (profile divergence proof, leakage/contamination tests, explicit gate-attrition waterfall).
