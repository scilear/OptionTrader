#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash scripts/run_s4_eod_ingestion.sh
#   bash scripts/run_s4_eod_ingestion.sh "spx_eod_2023*.txt"
#
# Optional env overrides:
#   INPUT_DIR=/mnt/Data/OPTION_DATA
#   UNDERLYING=SPX
#   CONFIG_PATH=config/config-eod-truth.yaml
#   GLOB_PATTERN="spx_eod_2023*.txt"
#
# Resume behavior:
#   - Default: resume from previously processed files (idempotent)
#   - --no-resume: restart from scratch

INPUT_DIR="${INPUT_DIR:-/mnt/Data/OPTION_DATA}"
UNDERLYING="${UNDERLYING:-SPX}"
CONFIG_PATH="${CONFIG_PATH:-config/config-eod-truth.yaml}"
GLOB_PATTERN="${1:-${GLOB_PATTERN:-spx_eod_20*.txt}}"
RESUME="${RESUME:-true}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d ".venv" ]]; then
  echo "ERROR: .venv not found at $ROOT_DIR/.venv"
  exit 1
fi

if [[ ! -d "$INPUT_DIR" ]]; then
  echo "ERROR: input dir not found: $INPUT_DIR"
  exit 1
fi

source .venv/bin/activate
export OPTIONTRADER_CONFIG="$CONFIG_PATH"

echo "============================================================================="
echo "== S4 EOD Ingestion"
echo "============================================================================="
echo "Repo:        $ROOT_DIR"
echo "Config:      $OPTIONTRADER_CONFIG"
echo "Input dir:   $INPUT_DIR"
echo "Glob:        $GLOB_PATTERN"
echo "Underlying:  $UNDERLYING"
echo "Resume:      $RESUME"
echo "============================================================================="

# Count files to process
TOTAL_FILES=$(ls -1 "$INPUT_DIR"/$GLOB_PATTERN 2>/dev/null | wc -l)
echo "Found $TOTAL_FILES files matching pattern"
echo ""

# Run ingestion with progress
echo "== Step 1: Ingest EOD option data =="
if [[ "$RESUME" == "true" ]]; then
  python scripts/ingest_spx_eod_option_data.py \
    --input-dir "$INPUT_DIR" \
    --glob "$GLOB_PATTERN" \
    --underlying "$UNDERLYING" \
    --resume
else
  python scripts/ingest_spx_eod_option_data.py \
    --input-dir "$INPUT_DIR" \
    --glob "$GLOB_PATTERN" \
    --underlying "$UNDERLYING" \
    --no-resume
fi

echo ""
echo "== Step 2: Validate dataset =="
python scripts/validate_spx_eod_dataset.py \
  --db-path data/optiontrader_eod_truth.duckdb \
  --report docs/roadmap/OptionTrader_S4_03_EOD_Validation_Report.md

echo ""
echo "============================================================================="
echo "== DONE"
echo "============================================================================="
echo "- Validation report: docs/roadmap/OptionTrader_S4_03_EOD_Validation_Report.md"
echo "- To continue with track materialization:"
echo "  python scripts/materialize_s4_tracks_from_eod.py ..."
