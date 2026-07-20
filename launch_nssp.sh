#!/bin/bash
# NSSP Full Stack Launcher — MSN Router + Game + Lyra + Hermes + CP Telemetry
set -e

PUB_ROOT="${PUB_ROOT:-$HOME/Desktop/AI/Pub}"
VENV="$PUB_ROOT/.venv-pub"
ABYSSAL="$HOME/Desktop/AI/abyssal-assets"
INVITE="$HOME/Desktop/AI/invite"

echo "=========================================="
echo " NSSP FULL STACK LAUNCHER"
echo "=========================================="

# Preflight gates
SERVICE_GATE="$ABYSSAL/scripts/ai_service_health_gate.py"
ENDPOINT_GATE="$ABYSSAL/scripts/ai_endpoint_health_gate.py"
GPU_GATE="$ABYSSAL/scripts/gpu_vram_policy.py"
OLLAMA_GUARD="$ABYSSAL/scripts/ollama_vram_guard.py"

if [[ -x "$SERVICE_GATE" ]]; then
    echo "[Preflight] AI service health..."
    SERVICE_GATE_JSON="$("$SERVICE_GATE" 2>/tmp/nssp_service_gate.err || true)"
    if [[ -n "$SERVICE_GATE_JSON" ]]; then
        printf '%s\n' "$SERVICE_GATE_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(f"  AI services: {d.get(\"running_count\", 0)}/{d.get(\"expected_count\", 0)} running | ok={d.get(\"ok\")}")'
    else
        echo "  Service gate unavailable: $(cat /tmp/nssp_service_gate.err 2>/dev/null)"
    fi
fi

if [[ -x "$ENDPOINT_GATE" ]]; then
    echo "[Preflight] AI endpoint health..."
    ENDPOINT_GATE_JSON="$("$ENDPOINT_GATE" 2>/tmp/nssp_endpoint_gate.err || true)"
    if [[ -n "$ENDPOINT_GATE_JSON" ]]; then
        printf '%s\n' "$ENDPOINT_GATE_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(f"  AI endpoints: required_failures={d.get(\"required_failure_count\", 0)} optional_failures={d.get(\"optional_failure_count\", 0)} | ok={d.get(\"ok\")}")'
    else
        echo "  Endpoint gate unavailable: $(cat /tmp/nssp_endpoint_gate.err 2>/dev/null)"
    fi
fi

if [[ -x "$GPU_GATE" ]]; then
    echo "[Preflight] GPU/VRAM policy..."
    GPU_GATE_JSON="$("$GPU_GATE" 2>/tmp/nssp_gpu_gate.err || true)"
    if [[ -n "$GPU_GATE_JSON" ]]; then
        printf '%s\n' "$GPU_GATE_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); p=d["policy"]; print(f"  GPU policy: {p[\"status\"]} | free={p.get(\"free_mb\", \"n/a\")} MiB | Ollama={p.get(\"ollama_compute_mb\", 0)} MiB | {p[\"reason\"]}")'
    else
        echo "  GPU gate unavailable: $(cat /tmp/nssp_gpu_gate.err 2>/dev/null)"
    fi
fi

if [[ -x "$OLLAMA_GUARD" ]]; then
    echo "[Preflight] Ollama VRAM guard..."
    OLLAMA_GUARD_JSON="$("$OLLAMA_GUARD" 2>/tmp/nssp_ollama_guard.err || true)"
    if [[ -n "$OLLAMA_GUARD_JSON" ]]; then
        printf '%s\n' "$OLLAMA_GUARD_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); models=", ".join(m["name"] for m in d.get("loaded_models", [])) or "none"; p=d["gpu_policy_before"]["policy"]; print(f"  Ollama loaded: {models} | GPU policy={p[\"status\"]}")'
    else
        echo "  Ollama guard unavailable: $(cat /tmp/nssp_ollama_guard.err 2>/dev/null)"
    fi
fi

# Report existing ports. Killing is opt-in to avoid interrupting active agents.
echo "[Preflight] Checking existing service ports..."
for port in 8000 8007 3211 4242 8768; do
    pid=$(lsof -ti :$port 2>/dev/null || true)
    if [[ -n "$pid" ]]; then
        if [[ "${NSSP_KILL_EXISTING:-0}" == "1" ]]; then
            kill $pid 2>/dev/null && echo "  Freed port $port"
        else
            echo "  Port $port already in use by PID(s): $pid"
        fi
    fi
done
sleep 1

start_if_port_free() {
    local port="$1"
    local label="$2"
    shift 2
    if lsof -ti :"$port" >/dev/null 2>&1; then
        echo "  $label already active on port $port; skipping duplicate start"
        return 0
    fi
    nohup "$@" >/tmp/"$label".log 2>&1 &
    echo "  PID $!"
}

# Start MSN Router (28 agents, port 8007)
echo "[1/4] MSN Router (28 agents, port 8007)..."
source "$VENV/bin/activate"
start_if_port_free 8007 msn_router python "$ABYSSAL/msn_router.py" 8007

# Start Game Server (port 8000)
echo "[2/4] Abyssal Assets Game Server (port 8000)..."
start_if_port_free 8000 abyssal_game python "$ABYSSAL/server/main.py"

# Wait for MSN
echo "[Wait] Waiting for MSN Router..."
for i in $(seq 1 15); do
    if curl -sf http://localhost:8007/api >/dev/null 2>&1; then
        echo "  MSN Router ready"
        break
    fi
    sleep 1
done

# Start MSN Coordination (port 8768)
echo "[3/4] MSN Coordination Server (port 8768)..."
start_if_port_free 8768 msn_coordination "$VENV/bin/python" \
    "$HOME/.local/share/Steam/steamapps/common/Cyberpunk 2077/r6/mods/msn_integration/msn_coordination_server.py"

# Verify agents
echo "[4/4] Verifying deployment..."
source "$VENV/bin/activate"
python "$ABYSSAL/deploy_waves.py" 8007 2>&1 | head -5

echo ""
echo "=========================================="
echo " NSSP STACK READY"
echo "=========================================="
echo " MSN Router:   http://localhost:8007  (28 agents)"
echo " Game Server:  http://localhost:8000"
echo " Lyra:         http://localhost:3211"
echo " Hermes:       http://localhost:4242"
echo " MSN Coord:    ws://localhost:8768"
echo ""
echo " NSSP API:     http://localhost:8007/api/nssp"
echo "  - /nssp/status, /nssp/roast, /nssp/sovereignty"
echo "  - /nssp/nessie/status, /nssp/nessie/sighting"
echo "  - /nssp/abyssal/status, /nssp/bridge/telemetry"
echo "  - /nssp/integration (full system health)"
echo ""
echo " To play: steam steam://rungameid/1091500"
echo "=========================================="
