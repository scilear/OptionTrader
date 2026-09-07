#!/usr/bin/env bash
# fix_postgres_pipeline.sh — recover OptionTrader PG 16 main + verify pipeline
# Run: bash scripts/fix_postgres_pipeline.sh
#      (will prompt for sudo password where needed)
set -euo pipefail

REPO="/home/fabien/Documents/OptionTrader"
PG_DATA_IMG="/mnt/Data/postgres/pg_data.img"
PG_MOUNT="/var/lib/postgresql/16/main"
PG_SYMLINK_TARGET_OLD="/mnt/Data/postgres_data/main"
PG_CANON_DIR="/mnt/Data/postgres/16/main"
PG_BAK="/var/lib/postgresql/16/main.bak.1782368585"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

log "=== 1. Pre-flight: current state ==="
echo "-- pg_lsclusters --"
pg_lsclusters || true
echo "-- symlink --"
ls -ld "$PG_MOUNT" || true
readlink -f "$PG_MOUNT" 2>&1 || true
echo "-- old symlink target --"
ls -la "$PG_SYMLINK_TARGET_OLD" 2>&1 | head -n 20 || true
echo "-- alternative dir --"
ls -la "$PG_CANON_DIR" 2>&1 | head -n 30 || true
echo "-- img --"
ls -lh "$PG_DATA_IMG" 2>&1 | head -n 5
file "$PG_DATA_IMG" 2>&1 | head -n 5 || true
echo "-- mounts --"
mount | grep -E "postgres|/mnt/Data|loop" || true
losetup -a || true
pg_isready 2>&1 || true

log "=== 2. Ensure /mnt/Data is mounted ==="
if ! mount | grep -q "on /mnt/Data "; then
  log "Trying sudo mount /mnt/Data"
  sudo mount /mnt/Data || { log "FATAL: cannot mount /mnt/Data — check fstab/NTFS"; exit 1; }
fi
ls -ld /mnt/Data | cat

log "=== 3. Decide data source: loop img vs directory ==="
# The cluster expects $PG_MOUNT. Historically it was a symlink to $PG_SYMLINK_TARGET_OLD (now empty).
# Current valid PG files were found at $PG_CANON_DIR (on NTFS, owned fabien) and also inside ext4 img.
# Prefer loop-mounted ext4 img (proper permissions, journaling). Fall through to dir if img missing.

if [[ -f "$PG_DATA_IMG" ]]; then
  log "Found loop image $PG_DATA_IMG — will loop-mount to $PG_MOUNT"
  # Remove stale symlink if present
  if [[ -L "$PG_MOUNT" ]]; then
    log "Removing stale symlink $PG_MOUNT -> $(readlink "$PG_MOUNT")"
    sudo rm "$PG_MOUNT"
  fi
  sudo mkdir -p "$PG_MOUNT"
  # Unmount if already mounted
  if mount | grep -q "on $PG_MOUNT "; then
    log "$PG_MOUNT already mounted — unmounting first"
    sudo umount "$PG_MOUNT" || true
  fi
  log "Mounting: sudo mount -o loop $PG_DATA_IMG $PG_MOUNT"
  sudo mount -o loop "$PG_DATA_IMG" "$PG_MOUNT"
  log "Mounted — verifying PG_VERSION"
  ls -la "$PG_MOUNT/PG_VERSION" 2>&1 | cat
  sudo chown -R postgres:postgres "$PG_MOUNT" 2>&1 | tail -n 5 || true
else
  log "No img at $PG_DATA_IMG — falling back to directory $PG_CANON_DIR"
  if [[ -d "$PG_CANON_DIR" && -f "$PG_CANON_DIR/PG_VERSION" ]]; then
    if [[ -L "$PG_MOUNT" ]]; then sudo rm "$PG_MOUNT"; fi
    if [[ -e "$PG_MOUNT" && ! -L "$PG_MOUNT" ]]; then
      # if it's a stale mountpoint, keep it
      :
    else
      sudo mkdir -p "$PG_MOUNT"
    fi
    # If $PG_MOUNT is empty and $PG_CANON_DIR has data, rsync or re-symlink
    if [[ -z "$(ls -A "$PG_MOUNT" 2>/dev/null)" ]]; then
      log "Copying $PG_CANON_DIR -> $PG_MOUNT (this may take a while)"
      sudo rsync -a "$PG_CANON_DIR/" "$PG_MOUNT/"
    fi
    sudo chown -R postgres:postgres "$PG_MOUNT"
  else
    log "FATAL: neither img nor $PG_CANON_DIR contains a valid cluster. Check $PG_BAK"
    ls -la "$PG_BAK" 2>&1 | head -n 30 || true
    exit 1
  fi
fi

log "=== 4. Permissions & ownership ==="
ls -ld "$PG_MOUNT" | cat
sudo chown postgres:postgres "$PG_MOUNT"
sudo chmod 0700 "$PG_MOUNT"
# /mnt/Data is ntfs-3g uid=1000 — loop mount fixes this; if using directory mode ensure postgres can traverse
id postgres | cat

log "=== 5. Start cluster ==="
echo "-- pg_ctlcluster 16 main start --"
sudo pg_ctlcluster 16 main start || {
  log "pg_ctlcluster start failed — check journal"
  sudo journalctl -u postgresql@16-main --since "1 hour ago" 2>&1 | tail -n 100 || true
  cat /var/log/postgresql/postgresql-16-main.log 2>&1 | tail -n 100 || true
  exit 1
}
sleep 2
pg_lsclusters | cat
pg_isready | cat
sudo -u postgres psql -c "SELECT version();" 2>&1 | head -n 5 || true

log "=== 6. Verify DB accessible as fabien (dsn: host=/var/run/postgresql dbname=optiontrader user=fabien) ==="
# Quick psql check
psql "host=/var/run/postgresql dbname=optiontrader user=fabien" -c "SELECT count(*) FROM pipeline_runs;" 2>&1 | head -n 20 || {
  log "psql as fabien failed — checking pg_hba.conf"
  sudo cat /etc/postgresql/16/main/pg_hba.conf 2>&1 | tail -n 30 || true
}

log "=== 7. Dry-run pipeline (no Telegram) ==="
cd "$REPO"
source .venv/bin/activate
# Run pipeline once — will create a new run_id
OPTIONTRADER_CONFIG=config/config-v1.yaml python scripts/run_pipeline.py 2>&1 | tail -n 50
PIPELINE_RC=${PIPESTATUS[0]:-0}
if [[ $PIPELINE_RC -ne 0 ]]; then
  log "Pipeline dry-run FAILED (rc=$PIPELINE_RC) — see logs/optiontrader.log"
  tail -n 100 logs/optiontrader.log 2>&1 | tail -n 50 || true
  tail -n 100 logs/pipeline_cron.log 2>&1 | tail -n 50 || true
  exit $PIPELINE_RC
fi
log "Pipeline dry-run succeeded"

log "=== 8. Tail logs ==="
tail -n 30 logs/optiontrader.log | cat
tail -n 30 logs/pipeline_cron.log | cat

log "=== 9. cron check (next runs) ==="
crontab -l | grep -E "option_trader|OptionTrader" | cat

log "=== DONE — if all green, re-enable cron will succeed at next 15:45/18:00/21:00 slot ==="
log "To persist loop mount across reboots, add to /etc/fstab:"
echo "  $PG_DATA_IMG  $PG_MOUNT  ext4  loop,nofail  0  0"
