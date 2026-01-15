#!/bin/bash
# Daily cleanup — rotate logs, purge old tty captures, prune downloads
# sarah, 2025-12-10: initial
# mkaur, 2026-02-20: added download cache pruning

set -euo pipefail

LOGS_DIR="/opt/hp-ops/logs"
COWRIE_LOG="/var/lib/docker/volumes/hp-ops_cowrie_logs/_data"
TTY_DIR="$COWRIE_LOG/tty"
DL_DIR="/var/lib/docker/volumes/hp-ops_cowrie_downloads/_data"

echo "[$(date -Is)] cleanup started"

# Rotate cowrie.json if > 100MB
COWRIE_SIZE=$(stat -c%s "$COWRIE_LOG/cowrie.json" 2>/dev/null || echo 0)
if [ "$COWRIE_SIZE" -gt 104857600 ]; then
    ARCHIVE="$COWRIE_LOG/cowrie.json.$(date +%Y-%m-%d).gz"
    gzip -c "$COWRIE_LOG/cowrie.json" > "$ARCHIVE"
    : > "$COWRIE_LOG/cowrie.json"
    chown 2000:2000 "$COWRIE_LOG/cowrie.json"
    echo "rotating cowrie.json ($(numfmt --to=iec $COWRIE_SIZE) → archived as $(basename $ARCHIVE))"
fi

# Purge old tty logs (>30 days)
if [ -d "$TTY_DIR" ]; then
    COUNT=$(find "$TTY_DIR" -type f -mtime +30 | wc -l)
    if [ "$COUNT" -gt 0 ]; then
        SIZE=$(find "$TTY_DIR" -type f -mtime +30 -exec du -ch {} + | tail -1 | cut -f1)
        find "$TTY_DIR" -type f -mtime +30 -delete
        echo "purging tty logs older than 30d: removed $COUNT files ($SIZE)"
    fi
fi

# Purge old downloads (>14 days)
if [ -d "$DL_DIR" ]; then
    COUNT=$(find "$DL_DIR" -type f -mtime +14 | wc -l)
    if [ "$COUNT" -gt 0 ]; then
        SIZE=$(find "$DL_DIR" -type f -mtime +14 -exec du -ch {} + | tail -1 | cut -f1)
        find "$DL_DIR" -type f -mtime +14 -delete
        echo "purging download cache older than 14d: removed $COUNT files ($SIZE)"
    fi
fi

# Report disk
BEFORE=$(df / | awk 'NR==2 {print $5}')
echo "disk before: $BEFORE | disk after: $(df / | awk 'NR==2 {print $5}')"
echo "[$(date -Is)] cleanup done"
