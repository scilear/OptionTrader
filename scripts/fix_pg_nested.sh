#!/usr/bin/env bash
# fix_pg_nested.sh — fix nested /main/main after loop mount
# Run: bash scripts/fix_pg_nested.sh
set -euo pipefail
echo "=== current mount ==="
mount | grep -E "postgresql|loop" || true
ls -ld /var/lib/postgresql/16/main || true
echo "--- as fabien (will fail on 0700) ---"
ls -la /var/lib/postgresql/16/main 2>&1 | head -n 50 || true

echo "=== checking for nested main/ ==="
# This needs sudo — will prompt for password
sudo ls -la /var/lib/postgresql/16/main/ 2>&1 | head -n 50
if sudo test -f /var/lib/postgresql/16/main/main/PG_VERSION; then
  echo "FOUND nested cluster at /var/lib/postgresql/16/main/main/PG_VERSION"
  sudo cat /var/lib/postgresql/16/main/main/PG_VERSION
  echo "Fixing: moving files up one level..."
  # Ensure target not already has PG_VERSION (would clash)
  if sudo test -f /var/lib/postgresql/16/main/PG_VERSION; then
    echo "ERROR: both /var/lib/postgresql/16/main/PG_VERSION and /main/main/PG_VERSION exist — manual check needed"
    sudo ls -la /var/lib/postgresql/16/main/PG_VERSION /var/lib/postgresql/16/main/main/PG_VERSION 2>&1
    exit 1
  fi
  # Glob must expand as root — plain sudo mv .../* expands as fabien and fails on 0700
  sudo bash -c 'shopt -s dotglob; mv /var/lib/postgresql/16/main/main/* /var/lib/postgresql/16/main/'
  sudo rmdir /var/lib/postgresql/16/main/main
  sudo chown -R postgres:postgres /var/lib/postgresql/16/main
  sudo chmod 0700 /var/lib/postgresql/16/main
  echo "--- after fix ---"
  sudo ls -la /var/lib/postgresql/16/main/ | head -n 40
  sudo cat /var/lib/postgresql/16/main/PG_VERSION
else
  echo "No nested dir — checking for direct PG_VERSION"
  sudo cat /var/lib/postgresql/16/main/PG_VERSION 2>&1 || echo "PG_VERSION missing — image may be empty/corrupt"
fi

echo "=== starting cluster ==="
sudo pg_ctlcluster 16 main start || { sudo journalctl -u postgresql@16-main --since "5 min ago" 2>&1 | tail -n 100; cat /var/log/postgresql/postgresql-16-main.log 2>&1 | tail -n 100; exit 1; }
sleep 2
pg_lsclusters
pg_isready
psql "host=/var/run/postgresql dbname=optiontrader user=fabien" -c "SELECT count(*) FROM pipeline_runs;" 2>&1 | head -n 20

echo "=== pipeline dry-run ==="
cd /home/fabien/Documents/OptionTrader
source .venv/bin/activate
OPTIONTRADER_CONFIG=config/config-v1.yaml python scripts/run_pipeline.py 2>&1 | tail -n 80
echo "=== done ==="
tail -n 30 logs/optiontrader.log 2>&1 | tail -n 30
