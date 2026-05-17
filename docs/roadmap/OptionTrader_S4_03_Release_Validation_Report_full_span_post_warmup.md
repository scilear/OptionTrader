# OptionTrader Sprint 7 Release Validation Report

Generated at: 2026-05-17T17:04:03.831938Z
Source script: `scripts/validate_release.py`

## Contract

- Contract ID: `S7-CONTRACT-v1`
- Config path: `config/config-eod-truth.yaml`
- Underlying: `SPX`
- Start: `2010-01-01T00:00:00Z`
- Effective start (post warm-up): `2010-04-05T00:00:00Z`
- End: `2023-12-31T23:59:59Z`
- Baseline lineage: `3b024c9`
- Candidate lineage: `5128e8e`

## Gate Evaluation

- Walk-forward deterministic gate: PASS
- Adversarial resilience gate: PASS
- Regime falsification gate: FAIL
- Ablation ledger gate: PASS
- Overall release gate: FAIL

## Warm-up Exclusion

- Warm-up exclusion applied: `True`
- Warm-up excluded days: `94`
- Requested start: `2010-01-01T00:00:00Z`
- Effective start: `2010-04-05T00:00:00Z`

## Recommendation

- Final recommendation: `not_promotable`
- Taxonomy verdict: `invalid_evidence`

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
    "ideas_with_ranking": 343,
    "mean_edge_after_cost": 2748.037328471075,
    "mean_total_friction_cost": 3.218746721000351,
    "pass": true
  },
  "adversarial": {
    "details": {
      "discontinuous_chain_snapshots": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_discontinuous_chain_snapshots_emit_no_false_alert",
        "stderr": [],
        "stdout": [
          "1 passed in 0.60s"
        ]
      },
      "missing_tenors": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_missing_tenors_term_slope_remains_null",
        "stderr": [],
        "stdout": [
          "1 passed in 0.62s"
        ]
      },
      "sparse_wings": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_sparse_wings_emit_degraded_status",
        "stderr": [],
        "stdout": [
          "1 passed in 0.61s"
        ]
      },
      "stale_books": {
        "returncode": 0,
        "selector": "tests/test_surface_adversarial.py::test_stale_books_emit_no_alert",
        "stderr": [],
        "stdout": [
          "1 passed in 0.58s"
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
    "effective_start_ts": "2010-04-05T00:00:00Z",
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
  "event_governance": {
    "blocked_reasons": [],
    "effective_date_immutability_pass": true,
    "event_calendar_exists": true,
    "event_path": "config/regime_events_v1.yaml"
  },
  "gates": {
    "ablation_ledger_pass": true,
    "adversarial_resilience_pass": true,
    "event_governance_pass": true,
    "overall_pass": false,
    "regime_falsification_pass": false,
    "threshold_freeze_pass": true,
    "walk_forward_pass": true
  },
  "generated_at": "2026-05-17T17:04:03.831938Z",
  "independence_diagnostics": {
    "baseline": {
      "contribution_shares": {
        "drawdown": 0.13665254237288219,
        "event": 0.0,
        "rv20": 0.3520921610169513,
        "stress_proxy": 0.18697033898304588,
        "vix": 0.3242849576271206
      },
      "correlation_stress_vs_rv20": 0.7847293985911984,
      "correlation_stress_vs_vix": 1.0,
      "near_redundant_feature_warning": true,
      "samples": 3437
    },
    "candidate": {
      "contribution_shares": {
        "drawdown": 0.13665254237288219,
        "event": 0.0,
        "rv20": 0.3520921610169513,
        "stress_proxy": 0.18697033898304588,
        "vix": 0.3242849576271206
      },
      "correlation_stress_vs_rv20": 0.7847293985911984,
      "correlation_stress_vs_vix": 1.0,
      "near_redundant_feature_warning": true,
      "samples": 3437
    }
  },
  "lineage_metadata": {
    "baseline": {
      "code_version": "3b024c98c829a6406bbfcc08ea5c18a0c5bab41f+profile:baseline_rv_only",
      "config_hash": "ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68",
      "profile_id": "baseline_rv_only",
      "run_id": 33
    },
    "candidate": {
      "code_version": "5128e8e6f314f117e8f8eb29735d24f2bd4dd3d6+profile:candidate_multi_signal",
      "config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
      "profile_id": "candidate_multi_signal",
      "run_id": 34
    }
  },
  "recommendation": "not_promotable",
  "regime_falsification": {
    "baseline": {
      "fp": 271,
      "outcomes_observed": 318,
      "precision": 0.14779874213836477,
      "tp": 47,
      "transition_alerts": 104,
      "transition_fp": 62,
      "transition_fp_density": 0.5961538461538461
    },
    "baseline_by_regime": {
      "Calm": {
        "alerts": 126,
        "fp": 86,
        "precision": 0.13131313131313133,
        "tp": 13
      },
      "Stress": {
        "alerts": 196,
        "fp": 123,
        "precision": 0.1276595744680851,
        "tp": 18
      },
      "Transition": {
        "alerts": 104,
        "fp": 62,
        "precision": 0.20512820512820512,
        "tp": 16
      }
    },
    "blocked_reasons": [
      "transition_fp_density_worsened"
    ],
    "candidate": {
      "fp": 518,
      "outcomes_observed": 621,
      "precision": 0.16586151368760063,
      "tp": 103,
      "transition_alerts": 188,
      "transition_fp": 124,
      "transition_fp_density": 0.6595744680851063
    },
    "candidate_alert_count": 1014,
    "candidate_by_regime": {
      "Calm": {
        "alerts": 581,
        "fp": 226,
        "precision": 0.16911764705882354,
        "tp": 46
      },
      "Stress": {
        "alerts": 245,
        "fp": 168,
        "precision": 0.12953367875647667,
        "tp": 25
      },
      "Transition": {
        "alerts": 188,
        "fp": 124,
        "precision": 0.20512820512820512,
        "tp": 32
      }
    },
    "evidence_valid": false,
    "horizon_days": 5,
    "min_required_outcomes_per_regime": 5,
    "missing_regimes": [],
    "observed_regimes": [
      "Calm",
      "Stress",
      "Transition"
    ],
    "outcome_validity_pass": true,
    "pass": false,
    "per_regime_outcome_counts": {
      "Calm": 272,
      "Stress": 193,
      "Transition": 156
    },
    "per_regime_outcome_validity": {
      "Calm": true,
      "Stress": true,
      "Transition": true
    },
    "precision_non_regression": true,
    "regime_coverage_pass": true,
    "required_regimes": [
      "Calm",
      "Transition",
      "Stress"
    ],
    "taxonomy_verdict": "invalid_evidence",
    "transition_fp_density_blocked_reason": null,
    "transition_fp_density_non_worsening": false,
    "unknown_regime_count": 0,
    "unknown_regime_pass": true,
    "unknown_regime_share": 0.0
  },
  "taxonomy_verdict": "invalid_evidence",
  "threshold_freeze": {
    "baseline_config_hash": "ba56410eb197f5895a80d324d76769291595e0f645b97f52ba2e5ad60907de68",
    "blocked_reasons": [],
    "candidate_config_hash": "b0a92b8978a2afae3b4d0a7aaaded8d5a2c95d2da19d946fe6fc456c0bea5b36",
    "current_config_hash": "ec039d97d121f629cd73d47701c3461b281498f2ab93fac5af85cafdb5609e2e",
    "threshold_freeze_pass": true
  },
  "walk_forward": {
    "deterministic_schedule": true,
    "pass": true,
    "split_count": 50,
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
  },
  "window": {
    "effective_start_ts": "2010-04-05T00:00:00Z",
    "end_ts": "2023-12-31T23:59:59Z",
    "regime_ready_dates": {
      "baseline": "2010-04-05",
      "candidate": "2010-04-05"
    },
    "requested_start_ts": "2010-01-01T00:00:00Z",
    "underlying": "SPX",
    "warmup_excluded_days": 94,
    "warmup_exclusion_applied": true
  }
}
```

## Reproducibility

```bash
source .venv/bin/activate
python scripts/validate_release.py --config-path config/config-eod-truth.yaml --start-ts 2010-01-01T00:00:00Z --end-ts 2023-12-31T23:59:59Z --underlying SPX --baseline-lineage 3b024c9 --candidate-lineage 5128e8e --train-size 252 --test-size 63 --step-size 63 --horizon-days 5
```

