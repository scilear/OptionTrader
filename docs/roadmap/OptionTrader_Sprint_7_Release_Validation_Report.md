# OptionTrader Sprint 7 Release Validation Report

Generated at: 2026-05-11T07:06:20.620469Z
Source script: `scripts/validate_release.py`

## Contract

- Contract ID: `S7-CONTRACT-v1`
- Config path: `config/config-eod-truth.yaml`
- Underlying: `SPX`
- Start: `2010-01-01T00:00:00Z`
- End: `2023-12-31T23:59:59Z`
- Baseline lineage: `3b024c9`
- Candidate lineage: `5128e8e`

## Gate Evaluation

- Walk-forward deterministic gate: PASS
- Adversarial resilience gate: PASS
- Regime falsification gate: FAIL
- Ablation ledger gate: PASS
- Overall release gate: FAIL

## Recommendation

- Final recommendation: `not_promotable`

## Summary Payload

```json
{
  "ablation_ledger": {
    "component_ledger": [
      {
        "component": "vix",
        "status": "retained",
        "weight": 0.25
      },
      {
        "component": "rv20",
        "status": "retained",
        "weight": 0.25
      },
      {
        "component": "drawdown",
        "status": "retained",
        "weight": 0.25
      },
      {
        "component": "event",
        "status": "ablated",
        "weight": 0.0
      },
      {
        "component": "stress_proxy",
        "status": "ablated",
        "weight": 0.0
      }
    ],
    "ideas_with_ranking": 5,
    "mean_edge_after_cost": 17013.489688957932,
    "mean_total_friction_cost": 17.21802978316799,
    "pass": true
  },
  "adversarial": {
    "details": {
      "discontinuous_chain_snapshots": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_discontinuous_chain_snapshots_emit_no_false_alert",
        "stderr": [],
        "stdout": [
          "1 passed in 0.57s"
        ]
      },
      "missing_tenors": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_missing_tenors_term_slope_remains_null",
        "stderr": [],
        "stdout": [
          "1 passed in 0.61s"
        ]
      },
      "sparse_wings": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_sparse_wings_emit_degraded_status",
        "stderr": [],
        "stdout": [
          "1 passed in 0.83s"
        ]
      },
      "stale_books": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_stale_books_emit_no_alert",
        "stderr": [],
        "stdout": [
          "1 passed in 0.61s"
        ]
      }
    },
    "pass": true,
    "scenarios": {
      "discontinuous_chain_snapshots": true,
      "missing_tenors": true,
      "sparse_wings": true,
      "stale_books": true
    }
  },
  "contract": {
    "baseline_lineage": "3b024c9",
    "candidate_lineage": "5128e8e",
    "config_path": "config/config-eod-truth.yaml",
    "end_ts": "2023-12-31T23:59:59Z",
    "horizon_days": 5,
    "id": "S7-CONTRACT-v1",
    "start_ts": "2010-01-01T00:00:00Z",
    "underlying": "SPX",
    "walk_forward": {
      "step_size": 63,
      "test_size": 63,
      "train_size": 252
    }
  },
  "gates": {
    "ablation_ledger_pass": true,
    "adversarial_resilience_pass": true,
    "overall_pass": false,
    "regime_falsification_pass": false,
    "walk_forward_pass": true
  },
  "generated_at": "2026-05-11T07:06:20.620469Z",
  "lineage_metadata": {
    "baseline": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68",
      "profile_id": "baseline_rv_only",
      "run_id": 23
    },
    "candidate": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
      "profile_id": "candidate_multi_signal",
      "run_id": 24
    }
  },
  "recommendation": "not_promotable",
  "regime_falsification": {
    "baseline": {
      "fp": 225,
      "outcomes_observed": 232,
      "precision": 0.03017241379310345,
      "tp": 7,
      "transition_alerts": 0,
      "transition_fp": 0,
      "transition_fp_density": null
    },
    "baseline_by_regime": {
      "Neutral": {
        "alerts": 236,
        "fp": 225,
        "precision": 0.03017241379310345,
        "tp": 7
      }
    },
    "candidate": {
      "fp": 225,
      "outcomes_observed": 232,
      "precision": 0.03017241379310345,
      "tp": 7,
      "transition_alerts": 0,
      "transition_fp": 0,
      "transition_fp_density": null
    },
    "candidate_by_regime": {
      "Neutral": {
        "alerts": 236,
        "fp": 225,
        "precision": 0.03017241379310345,
        "tp": 7
      }
    },
    "horizon_days": 5,
    "missing_regimes": [
      "Calm",
      "Transition",
      "Stress"
    ],
    "observed_regimes": [
      "Neutral"
    ],
    "pass": false,
    "precision_non_regression": true,
    "regime_coverage_pass": false,
    "required_regimes": [
      "Calm",
      "Transition",
      "Stress"
    ],
    "transition_fp_density_blocked_reason": "missing_transition_alerts",
    "transition_fp_density_non_worsening": false
  },
  "walk_forward": {
    "deterministic_schedule": true,
    "pass": true,
    "split_count": 28,
    "step_size": 63,
    "test_size": 63,
    "test_window_lengths": [
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63,
      63
    ],
    "train_size": 252
  }
}
```

## Reproducibility

```bash
source .venv/bin/activate
python scripts/validate_release.py --config-path config/config-eod-truth.yaml --start-ts 2010-01-01T00:00:00Z --end-ts 2023-12-31T23:59:59Z --underlying SPX --baseline-lineage 3b024c9 --candidate-lineage 5128e8e --train-size 252 --test-size 63 --step-size 63 --horizon-days 5
```

