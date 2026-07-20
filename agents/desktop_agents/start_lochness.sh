#!/usr/bin/env bash
# Start Lochness Monster Coinbase bots (public channels)
set -euo pipefail

AGENTS_ROOT="/home/tehlappy/Desktop/Lilith/Core_Systems/AI/abyssal-agents"
LOG="${AGENTS_ROOT}/lochness.log"
PIDFILE="${AGENTS_ROOT}/lochness.pid"

if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "Lochness already running (PID $(cat "$PIDFILE"))"
    exit 0
fi

cd "$AGENTS_ROOT"
ABYSSAL_API_URL="${ABYSSAL_API_URL:-http://localhost:8008}" LOCHNESS_DAEMON=1 nohup python3 deploy_public_bots.py --daemon >> "$LOG" 2>&1 &
echo $! > "$PIDFILE"
echo "Lochness started (PID $(cat "$PIDFILE"))"
echo "Log: $LOG"