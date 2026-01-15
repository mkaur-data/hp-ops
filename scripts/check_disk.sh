#!/bin/bash
# quick disk check — originally just ran this manually, then added to cron
# sarah 2026-02-10
# DEPRECATED: replaced by verify_node.sh which checks disk + everything else
# keeping because cleanup.sh still sources the THRESHOLD from here

THRESHOLD=50
CURRENT=$(df --output=pcent /opt | tail -1 | tr -d ' %')

if [ "$CURRENT" -ge "$THRESHOLD" ]; then
    echo "WARN: disk at ${CURRENT}%"
    exit 1
fi
echo "OK: ${CURRENT}%"
