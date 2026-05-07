#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${1:-config/config-eod-truth.yaml}"

if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

python scripts/validate_release.py --config-path "${CONFIG_PATH}"
