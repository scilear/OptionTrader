#!/usr/bin/env bash
# Run EOD pipeline and send any new alerts to Telegram.
# Designed to run from cron — sources bashrc to pick up PATH and telegram-send config.

set -euo pipefail

# Load user environment so telegram-send config (~/.config/telegram-send.conf) is available
# shellcheck source=/dev/null
if [[ -f "$HOME/.bashrc" ]]; then
    source "$HOME/.bashrc"
fi

REPO="/home/fabien/Documents/OptionTrader"
VENV="$REPO/.venv"
TELEGRAM_SEND="$VENV/bin/telegram-send"
PYTHON="$VENV/bin/python"
LOG="$REPO/logs/pipeline_cron.log"

cd "$REPO"

echo "=== $(date) ===" >> "$LOG"

# Run the pipeline
if ! OPTIONTRADER_CONFIG=config/config-v1.yaml "$PYTHON" scripts/run_pipeline.py >> "$LOG" 2>&1; then
    "$TELEGRAM_SEND" --config "$HOME/.config/telegram-send.conf" \
        "❌ OptionTrader pipeline FAILED — check $LOG"
    exit 1
fi

# Fetch alerts from the latest snapshot
ALERTS=$("$PYTHON" - <<'EOF'
import sys, os
sys.path.insert(0, os.environ.get("REPO", "."))
os.environ.setdefault("OPTIONTRADER_CONFIG", "config/config-v1.yaml")
import duckdb
from src.core.config import load_config

cfg = load_config()
con = duckdb.connect(cfg["storage"]["path"], read_only=True)
rows = con.execute("""
    SELECT a.alert_type, a.expiry_bucket, a.severity, a.zscore_mid,
           a.confidence_tier, a.regime_label, a.tradability_score
    FROM alerts a
    JOIN snapshots s ON s.snapshot_id = a.snapshot_id
    WHERE s.snapshot_id = (SELECT MAX(snapshot_id) FROM snapshots)
    ORDER BY a.severity DESC
""").fetchall()
con.close()
for r in rows:
    print(f"{r[0]} | {r[1]} | sev={r[2]:.1f} z={r[3]:.2f} | {r[4]} | {r[5]} | trad={r[6]:.2f}")
EOF
)

if [[ -z "$ALERTS" ]]; then
    echo "No alerts on latest snapshot — no Telegram message sent." >> "$LOG"
    exit 0
fi

SNAPSHOT_DATE=$(date +"%Y-%m-%d")
MESSAGE="📊 OptionTrader — $SNAPSHOT_DATE

Alerts fired:
$ALERTS"

"$TELEGRAM_SEND" --config "$HOME/.config/telegram-send.conf" "$MESSAGE"
echo "Telegram notification sent." >> "$LOG"
