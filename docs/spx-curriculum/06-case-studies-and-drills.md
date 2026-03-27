# Module 6 - Case Studies and Drills

Use this module as a practical lab. Each case emphasizes reasoning quality over outcome chasing.

## Case A - RR spike with clean data and strong worst confirmation

### Observation

- `RR_EXTREME` appears with persistence.
- `rr25_mid` and `rr25_worst` both confirm.
- coverage and cadence are stable.

### Decision process

- Signal gate: pass because `zscore_mid` and `zscore_worst` both exceed threshold and persistence is met.
- Data gate: pass because bucket coverage is complete, cadence is interpretable, and no unresolved ingest anomaly is present.
- Regime gate: pass/neutral because regime does not suppress RR signal and no near-term event contradiction dominates thesis.
- Execution gate: pass because tradability/spread conditions remain inside allowed limits for intended structure.
- Risk gate: pass because max loss, invalidation trigger, and size constraints are explicitly defined.

### Example decision

- label: `Trade now` (risk-defined structure).
- invalidation: persistence fails on next evaluation or execution quality worsens.

### Evidence card example (format)

- `Signal`: `zscore_mid=...`, `zscore_worst=...`, `persistence=...` -> pass
- `Data`: `metrics_rows=...`, `iv_points=...`, `max_gap=...`, `source=...` -> pass
- `Regime`: `regime_label=...`, `event_context=...` -> neutral/pass
- `Execution`: `tradability_score=...`, spread check -> pass
- `Risk`: `max_loss=...`, invalidation defined, size rule satisfied -> pass

### Discussion prompt

- What evidence would downgrade this to `Watch`?

## Case B - FLY extreme with poor spread conditions

### Observation

- strong convexity dislocation signal,
- weak tradability/spread quality.

### Example decision

- label: `Research only`.
- rationale: edge not executable despite statistical signal.

Evidence focus:

- strong signal evidence alone is not sufficient,
- failure is in execution gate (spread/slippage burden),
- decision remains non-live until execution evidence improves.

### Discussion prompt

- What specific execution improvement would justify promotion to `Watch` or `Trade`?

## Case C - TERM kink during event cluster

### Observation

- term distortion appears meaningful,
- near-term macro event risk elevated.

### Example decision

- label: `Watch for confirmation`.
- rationale: event repricing may be rational and persistent.

Evidence focus:

- signal may pass,
- regime/event gate is only neutral at best pre-event,
- wait for post-event confirmation before promoting to trade.

### Discussion prompt

- Which post-event signals confirm true dislocation vs justified term repricing?

## Drill Pack

For each new week:

1. Select 5 alerts.
2. Fill the scorecard template for each.
3. Compare your labels with realized outcomes one week later.
4. Identify one process upgrade from mismatch cases.

Template paths:

- `docs/templates/decision-scorecard-template.md`
- `docs/templates/decision-scorecard-template.csv`
