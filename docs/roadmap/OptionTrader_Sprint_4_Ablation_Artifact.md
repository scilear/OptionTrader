# OptionTrader Sprint 4 Ablation Artifact

Generated at: 2026-05-02T17:25:24.039434Z
Source script: `scripts/generate_regime_ablation_artifact.py`

## Locked Gate Evaluation

- Minimum sample gate (`>=50` total and `>=10` per active bucket): FAIL
- Precision lift gate (`>= +0.03`): FAIL
- Volume guardrail (`[-15%, +15%]`): FAIL
- Transition FP density worsening (`<= +0.02`): FAIL
- Overall retention gate: FAIL

## Summary Payload

```json
{
  "baseline_track": "rv_only_reference",
  "candidate_track": "multi_signal_s4",
  "feature_decisions": [
    {
      "evidence": "insufficient alert sample and no precision labels",
      "feature": "event",
      "reason": "s4_03_gate_failed",
      "status": "disabled"
    },
    {
      "evidence": "insufficient alert sample and no precision labels",
      "feature": "stress_proxy",
      "reason": "s4_03_gate_failed",
      "status": "disabled"
    }
  ],
  "gates": {
    "min_sample_pass": false,
    "overall_pass": false,
    "precision_delta": null,
    "precision_gate_pass": false,
    "transition_false_positive_density_worsening": null,
    "transition_fp_gate_pass": false,
    "volume_delta_pct": null,
    "volume_gate_pass": false
  },
  "sample": {
    "alerts_by_regime": {},
    "alerts_total": 0
  },
  "window": {
    "end_ts": "2026-04-15T23:59:59Z",
    "start_ts": "2026-04-01T00:00:00Z",
    "underlying": "SPX"
  }
}
```

## Feature Decisions

- `event`: disabled in runtime defaults (`regime.weights.event=0.00`).
- `stress_proxy`: disabled in runtime defaults (`regime.weights.stress_proxy=0.00`).

## Notes

- This run uses the locked S3.2 window by default.
- Precision and transition false-positive density require outcome labels that are not
  currently persisted in v1 schema; gates are treated as failed until evidence is available.
