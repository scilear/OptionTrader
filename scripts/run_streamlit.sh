#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-dev}"

if [[ "$MODE" == "prod" ]]; then
  export OPTIONTRADER_CONFIG="config/config-v1.yaml"
elif [[ "$MODE" == "dev" ]]; then
  export OPTIONTRADER_CONFIG="config/config-test.yaml"
else
  echo "Usage: $0 [prod|dev]"
  exit 1
fi

streamlit run src/app/streamlit_app.py
