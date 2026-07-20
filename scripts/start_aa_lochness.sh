#!/usr/bin/env bash
# Start Abyssal Assets + Lochness Monster + NSSP Token Bridge stack
set -euo pipefail

AA_ROOT="/home/tehlappy/Desktop/Lilith/Core_Systems/AI/abyssal-assets"
AGENTS_ROOT="/home/tehlappy/Desktop/Lilith/Core_Systems/AI/abyssal-agents"
VENV="${AA_ROOT}/.venv-abyssal"
LOG_DIR="${AA_ROOT}/server/runtime"
ABYSSAL_PORT="${ABYSSAL_PORT:-8000}"
mkdir -p "$LOG_DIR"

# Use 8008 if 8000 is occupied by another service
if curl -sf "http://localhost:${ABYSSAL_PORT}/health" 2>/dev/null | grep -q abyssal; then
    : # already our service
elif lsof -i ":${ABYSSAL_PORT}" >/dev/null 2>&1; then
    echo "⚠ Port ${ABYSSAL_PORT} occupied — using 8008 for Abyssal Assets"
    ABYSSAL_PORT=8008
fi
export ABYSSAL_API_URL="http://localhost:${ABYSSAL_PORT}"
export ABYSSAL_PORT

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ABYSSAL ASSETS × LOCHNESS MONSTER — Integration Launch      ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# ── 1. NSSP Token Bridge (8010) ──
if ! curl -sf http://localhost:8010/api/tokens/btc/price >/dev/null 2>&1; then
    echo "▶ Starting NSSP Token Bridge (:8010)..."
    nohup python3 "${AGENTS_ROOT}/nssp_token_bridge.py" >> "${LOG_DIR}/nssp_token_bridge.log" 2>&1 &
    echo $! > "${AGENTS_ROOT}/nssp_token_bridge.pid"
    sleep 2
else
    echo "✓ NSSP Token Bridge already running (:8010)"
fi

# ── 2. Abyssal Assets API ──
if ! curl -sf "${ABYSSAL_API_URL}/health" 2>/dev/null | grep -q abyssal; then
    echo "▶ Starting Abyssal Assets API (:${ABYSSAL_PORT})..."
    cd "$AA_ROOT"
    export PYTHONPATH="${AA_ROOT}/server:${AA_ROOT}:${PYTHONPATH:-}"
    "${VENV}/bin/pip" install httpx -q 2>/dev/null || pip install httpx -q 2>/dev/null || true
    if [[ -x "${VENV}/bin/uvicorn" ]]; then
        nohup env PYTHONPATH="${PYTHONPATH}" "${VENV}/bin/uvicorn" server.main:app --host 0.0.0.0 --port "${ABYSSAL_PORT}" \
            >> "${LOG_DIR}/abyssal_api.log" 2>&1 &
    else
        nohup env PYTHONPATH="${PYTHONPATH}" python3 -m uvicorn server.main:app --host 0.0.0.0 --port "${ABYSSAL_PORT}" \
            >> "${LOG_DIR}/abyssal_api.log" 2>&1 &
    fi
    echo $! > "${LOG_DIR}/abyssal_api.pid"
    sleep 4
else
    echo "✓ Abyssal Assets API already running (${ABYSSAL_API_URL})"
fi

# ── 3. Lochness Monsters (Coinbase public bots) ──
LOCH_PID="${AGENTS_ROOT}/lochness.pid"
if [[ -f "$LOCH_PID" ]] && kill -0 "$(cat "$LOCH_PID")" 2>/dev/null; then
    echo "✓ Lochness Monsters already running (PID $(cat "$LOCH_PID"))"
else
    echo "▶ Starting Lochness Monsters (7 public Coinbase bots)..."
    cd "$AGENTS_ROOT"
    ABYSSAL_API_URL="${ABYSSAL_API_URL}" LOCHNESS_DAEMON=1 nohup python3 deploy_public_bots.py --daemon >> "${AGENTS_ROOT}/lochness.log" 2>&1 &
    echo $! > "$LOCH_PID"
    sleep 2
fi

# ── 4. Health check ──
echo ""
echo "── Status ──"
curl -sf "${ABYSSAL_API_URL}/health" 2>/dev/null | grep -q abyssal && echo "  Abyssal Assets ${ABYSSAL_API_URL} ✓" || echo "  Abyssal Assets ${ABYSSAL_API_URL} ✗"
curl -sf http://localhost:8010/api/tokens/btc/price 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Token Bridge :8010 ✓  BTC=\${d.get(\"price\",0):,.2f}')" 2>/dev/null || echo "  Token Bridge :8010 ✗"
curl -sf "${ABYSSAL_API_URL}/api/lochness/status" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Lochness Bridge ✓  online={d.get(\"lochness_online\")} bots={d.get(\"bots_active\",0)} btc=\${d.get(\"btc_usd\",0):,.0f}')" 2>/dev/null || echo "  Lochness Bridge (awaiting bot data)"

echo ""
echo "Commands:"
echo "  curl ${ABYSSAL_API_URL}/api/lochness/status"
echo "  curl ${ABYSSAL_API_URL}/api/lochness/feed"
echo "  python3 ${AGENTS_ROOT}/lochness_integration.py tokens"
echo "  Open GTC dashboard: ${ABYSSAL_API_URL}/gtc/"