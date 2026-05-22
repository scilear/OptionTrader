python scripts/validate_release.py \                                                                            --config-path config/config-eod-truth.yaml \
       --underlying SPX \
       --start-ts 2010-01-01T00:00:00Z \
       --end-ts 2023-12-31T23:59:59Z \
       --baseline-lineage 3b024c9 \
       --candidate-lineage 5128e8e-v2a \
       --train-size 252 --test-size 63 --step-size 63 --horizon-days 5 \
       --report-path docs/roadmap/OptionTrader_S4_03_Release_Validation_Report_full_span_v2a.md \
       --payload-path docs/roadmap/OptionTrader_S4_03_Release_Validation_Payload_full_span_v2a.json \
       --baseline-capture-path docs/roadmap/OptionTrader_S4_03_Baseline_Capture_full_span_v2a.json | tee
     logs/validate_full_v2a.log

     python scripts/validate_release.py \
       --config-path config/config-eod-truth.yaml \
       --underlying SPX \
       --start-ts 2010-01-01T00:00:00Z \
       --end-ts 2023-12-31T23:59:59Z \
       --baseline-lineage 3b024c9 \
       --candidate-lineage 5128e8e-v2b \
       --train-size 252 --test-size 63 --step-size 63 --horizon-days 5 \
       --report-path docs/roadmap/OptionTrader_S4_03_Release_Validation_Report_full_span_v2b.md \
       --payload-path docs/roadmap/OptionTrader_S4_03_Release_Validation_Payload_full_span_v2b.json \
       --baseline-capture-path docs/roadmap/OptionTrader_S4_03_Baseline_Capture_full_span_v2b.json | tee
     logs/validate_full_v2b.log

python scripts/report_s4_gate_attrition.py \
       --config-path config/config-eod-truth.yaml \
       --underlying SPX \
       --start-ts 2010-01-01T00:00:00Z \
       --end-ts 2023-12-31T23:59:59Z \
       --baseline-lineage 3b024c9 \
       --candidate-lineage 5128e8e-v2a \
       --output docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_full_span_v2a.md | tee logs/attrition_full_v2a.log

     python scripts/report_s4_gate_attrition.py \
       --config-path config/config-eod-truth.yaml \
       --underlying SPX \
       --start-ts 2010-01-01T00:00:00Z \
       --end-ts 2023-12-31T23:59:59Z \
       --baseline-lineage 3b024c9 \
       --candidate-lineage 5128e8e-v2b \
       --output docs/roadmap/OptionTrader_S4_03_Gate_Attrition_Report_full_span_v2b.md | tee logs/attrition_full_v2b.log

     python scripts/generate_regime_ablation_artifact.py \
        --config-path config/config-eod-truth.yaml \
       --underlying SPX \
       --start-ts 2010-01-01T00:00:00Z \
       --end-ts 2023-12-31T23:59:59Z \
       --baseline-lineage 3b024c9 \
       --candidate-lineage 5128e8e-v2a \
       --horizon-days 5 \
       --output docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_full_span_v2a.md | tee logs/
     ablation_full_v2a.log
     python scripts/generate_regime_ablation_artifact.py \
       --config-path config/config-eod-truth.yaml \
       --underlying SPX \
       --start-ts 2010-01-01T00:00:00Z \
       --end-ts 2023-12-31T23:59:59Z \
       --baseline-lineage 3b024c9 \
       --candidate-lineage 5128e8e-v2b \
       --horizon-days 5 \
       --output docs/roadmap/OptionTrader_Sprint_4_Ablation_Artifact_full_span_v2b.md | tee logs/
     ablation_full_v2b.log


