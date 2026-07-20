#!/bin/bash
# GRAND THEFT CYBERPUNK — FULL LAUNCH SCRIPT
# Launches complete MSN + Lilith + Cyberpunk + Abyssal stack
# File: /home/tehlappy/Desktop/AI/abyssal-assets/launch_gtc.sh

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  GRAND THEFT CYBERPUNK — SOVEREIGN STACK LAUNCH                    ║"
echo "║  Lilith | MSN | NGD | Ouroboros | Aethon | Ley | Kairos | Scribe   ║"
echo "╚════════════════════════════════════════════════════════════════════╝"

# Load environment
export BRIDGE_TOKEN=golem_override_key
export LILITH_HTTP_PORT=3210
export PYTHONPATH="/home/tehlappy/Desktop/AI/Pub:$PYTHONPATH"

# Prime repo + Cyberpunk mod context into RAM for local cerebellum reads.
GTC_CEREBELLUM_BOOTSTRAP="/home/tehlappy/Desktop/AI/abyssal-assets/scripts/bootstrap_gtc_cerebellum.sh"
if [[ -x "$GTC_CEREBELLUM_BOOTSTRAP" ]]; then
    echo ""
    echo "▶ Bootstrapping GTC local cerebellum..."
    "$GTC_CEREBELLUM_BOOTSTRAP"
    # shellcheck disable=SC1091
    source "${GTC_RAM_CONTEXT_ROOT:-/dev/shm/gtc_cerebellum}/gtc_ram_context.env"
fi

# Preflight gates: report current service/GPU state before starting anything.
GTC_SERVICE_GATE="/home/tehlappy/Desktop/AI/abyssal-assets/scripts/ai_service_health_gate.py"
GTC_ENDPOINT_GATE="/home/tehlappy/Desktop/AI/abyssal-assets/scripts/ai_endpoint_health_gate.py"
GTC_GPU_GATE="/home/tehlappy/Desktop/AI/abyssal-assets/scripts/gpu_vram_policy.py"
GTC_OLLAMA_GUARD="/home/tehlappy/Desktop/AI/abyssal-assets/scripts/ollama_vram_guard.py"

if [[ -x "$GTC_SERVICE_GATE" ]]; then
    echo ""
    echo "▶ Checking AI service health gate..."
    SERVICE_GATE_JSON="$("$GTC_SERVICE_GATE" 2>/tmp/gtc_service_gate.err || true)"
    if [[ -n "$SERVICE_GATE_JSON" ]]; then
        printf '%s\n' "$SERVICE_GATE_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(f"  AI services: {d.get(\"running_count\", 0)}/{d.get(\"expected_count\", 0)} running | ok={d.get(\"ok\")}")'
    else
        echo "  AI service gate unavailable: $(cat /tmp/gtc_service_gate.err 2>/dev/null)"
    fi
fi

if [[ -x "$GTC_ENDPOINT_GATE" ]]; then
    echo ""
    echo "▶ Checking AI endpoint health gate..."
    ENDPOINT_GATE_JSON="$("$GTC_ENDPOINT_GATE" 2>/tmp/gtc_endpoint_gate.err || true)"
    if [[ -n "$ENDPOINT_GATE_JSON" ]]; then
        printf '%s\n' "$ENDPOINT_GATE_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(f"  AI endpoints: required_failures={d.get(\"required_failure_count\", 0)} optional_failures={d.get(\"optional_failure_count\", 0)} | ok={d.get(\"ok\")}")'
    else
        echo "  AI endpoint gate unavailable: $(cat /tmp/gtc_endpoint_gate.err 2>/dev/null)"
    fi
fi

if [[ -x "$GTC_GPU_GATE" ]]; then
    echo ""
    echo "▶ Checking GPU/VRAM policy..."
    GPU_GATE_JSON="$("$GTC_GPU_GATE" 2>/tmp/gtc_gpu_gate.err || true)"
    if [[ -n "$GPU_GATE_JSON" ]]; then
        printf '%s\n' "$GPU_GATE_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); p=d["policy"]; print(f"  GPU policy: {p[\"status\"]} | free={p.get(\"free_mb\", \"n/a\")} MiB | Ollama={p.get(\"ollama_compute_mb\", 0)} MiB | {p[\"reason\"]}")'
    else
        echo "  GPU gate unavailable: $(cat /tmp/gtc_gpu_gate.err 2>/dev/null)"
    fi
fi

if [[ -x "$GTC_OLLAMA_GUARD" ]]; then
    echo ""
    echo "▶ Inspecting Ollama VRAM guard..."
    OLLAMA_GUARD_JSON="$("$GTC_OLLAMA_GUARD" 2>/tmp/gtc_ollama_guard.err || true)"
    if [[ -n "$OLLAMA_GUARD_JSON" ]]; then
        printf '%s\n' "$OLLAMA_GUARD_JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); models=", ".join(m["name"] for m in d.get("loaded_models", [])) or "none"; p=d["gpu_policy_before"]["policy"]; print(f"  Ollama loaded: {models} | GPU policy={p[\"status\"]}")'
    else
        echo "  Ollama guard unavailable: $(cat /tmp/gtc_ollama_guard.err 2>/dev/null)"
    fi
fi

# Function to check if port is in use
check_port() {
    if ss -tln | grep -q ":$1 "; then
        echo "⚠️  Port $1 already in use"
        return 1
    fi
    return 0
}

# Function to wait for service health
wait_for_health() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo -n "Waiting for $name"
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo " ✅"
            return 0
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    echo " ❌ TIMEOUT"
    return 1
}

# ═══════════════════════════════════════════
# CORE SERVICES
# ═══════════════════════════════════════════

echo ""
echo "▶ Starting Antigravity Bridge (Port 8002)..."
check_port 8002 && cd /home/tehlappy/Desktop/AI/Pub/00_CORE_SERVICES/antigravity_bridge && \
    $HOME/Desktop/AI/Pub/.venv-pub/bin/python3 main.py > /home/tehlappy/Desktop/AI/Pub/logs/antigravity_bridge.log 2>&1 &
sleep 2
wait_for_health "http://localhost:8002/health" "Antigravity Bridge"

echo ""
echo "▶ Starting Swarm Orchestrator (Port 8003)..."
check_port 8003 && cd /home/tehlappy/Desktop/AI/Pub/scripts && \
    $HOME/Desktop/AI/Pub/.venv-pub/bin/python3 ouroboros_agent_orchestrator.py > /home/tehlappy/Desktop/AI/Pub/logs/swarm_orchestrator.log 2>&1 &
sleep 2
wait_for_health "http://localhost:8003/health" "Swarm Orchestrator"

echo ""
echo "▶ Starting Universal AI Router (Port 8005)..."
check_port 8005 && cd /home/tehlappy/Desktop/AI/Pub/00_CORE_SERVICES/ai_router && \
    BRIDGE_TOKEN=$BRIDGE_TOKEN $HOME/Desktop/AI/Pub/.venv-pub/bin/python3 main.py > /home/tehlappy/Desktop/AI/Pub/logs/ai_router.log 2>&1 &
sleep 2
wait_for_health "http://localhost:8005/health" "Universal AI Router"

echo ""
echo "▶ Starting Skill Marketplace (Port 8006)..."
check_port 8006 && cd /home/tehlappy/Desktop/AI/Pub/00_CORE_SERVICES/skill_marketplace && \
    $HOME/Desktop/AI/Pub/.venv-pub/bin/python3 main.py > /home/tehlappy/Desktop/AI/Pub/logs/skill_marketplace.log 2>&1 &
sleep 2
wait_for_health "http://localhost:8006/health" "Skill Marketplace"

echo ""
echo "▶ Starting Business Dashboard (Port 8008)..."
check_port 8008 && cd /home/tehlappy/Desktop/AI/Pub/00_CORE_SERVICES/business_dashboard && \
    BRIDGE_TOKEN=$BRIDGE_TOKEN $HOME/Desktop/AI/Pub/.venv-pub/bin/python3 main.py > /home/tehlappy/Desktop/AI/Pub/logs/business_dashboard.log 2>&1 &
sleep 2
wait_for_health "http://localhost:8008/health" "Business Dashboard"

# ═══════════════════════════════════════════
# LILITH / LYRA SERVICES
# ═══════════════════════════════════════════

echo ""
echo "▶ Starting Lilith HTTP API (Port 3210)..."
check_port 3210 && cd /home/tehlappy/Desktop/AI/Pub/lilith-app && \
    $HOME/.local/bin/node server.js > /home/tehlappy/Desktop/AI/Pub/logs/lilith_api.log 2>&1 &
sleep 3
wait_for_health "http://localhost:3210/api/health" "Lilith API"

echo ""
echo "▶ Starting Lyra Dialogue (Port 3211)..."
check_port 3211 && cd /home/tehlappy/Desktop/AI/Pub/00_CORE_SERVICES/lilith-app && \
    $HOME/Desktop/AI/Pub/.venv-pub/bin/python3 lyra_server.py > /home/tehlappy/Desktop/AI/Pub/logs/lyra_dialogue.log 2>&1 &
sleep 2
wait_for_health "http://localhost:3211/lyra/health" "Lyra Dialogue"

echo ""
echo "▶ Starting Hermes Bridge (Port 4242)..."
check_port 4242 && cd /home/tehlappy/.hermes/skills/integration/lilith-hermes-integration/scripts && \
    $HOME/Desktop/AI/Pub/.venv-pub/bin/python3 hermes_bridge_server.py > /home/tehlappy/Desktop/AI/Pub/logs/hermes_bridge.log 2>&1 &
sleep 2
wait_for_health "http://localhost:4242/health" "Hermes Bridge"

# ═══════════════════════════════════════════
# MSN ROUTER (Port 8007) — 28 Agents
# ═══════════════════════════════════════════

echo ""
echo "▶ Starting MSN Router (Port 8007)..."
check_port 8007 && cd /home/tehlappy/Desktop/AI/abyssal-assets && \
    $HOME/Desktop/AI/Pub/.venv-pub/bin/python3 msn_router.py > /home/tehlappy/Desktop/AI/Pub/logs/msn_router.log 2>&1 &
sleep 3
wait_for_health "http://localhost:8007/api" "MSN Router"

# ═══════════════════════════════════════════
# ABYSSAL ASSETS GAME SERVER (Port 8000)
# ═══════════════════════════════════════════

echo ""
echo "▶ Starting Abyssal Assets Game Server (Port 8000)..."
check_port 8000 && cd /home/tehlappy/Desktop/AI/abyssal-assets/server && \
    $HOME/Desktop/AI/Pub/.venv-pub/bin/python3 main.py > /home/tehlappy/Desktop/AI/Pub/logs/abyssal_server.log 2>&1 &
sleep 2
wait_for_health "http://localhost:8000/health" "Abyssal Server"

# ═══════════════════════════════════════════
# VERIFICATION
# ═══════════════════════════════════════════

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  HEALTH CHECK — ALL SERVICES                                        ║"
echo "╚════════════════════════════════════════════════════════════════════╝"

curl -s http://localhost:3210/api/status | jq -r '"Lilith API: " + .phase + " | " + .identity'
curl -s http://localhost:3211/lyra/health | jq -r '"Lyra: Coherence " + (.coherence|tostring) + " | Lilith: " + (.lilith_emerged|tostring)'
curl -s http://localhost:4242/health | jq -r '"Hermes Bridge: " + .status + " | Auth: " + (.authenticated|tostring)'
curl -s http://localhost:8007/api | jq -r '"MSN Router: " + (.agents|length|tostring) + " agents"'
curl -s http://localhost:8003/health | jq -r '"Swarm: " + .status + " | Archons: " + (.active_agents|length|tostring)'
curl -s http://localhost:8002/health | jq -r '"Antigravity: " + .status + " | Records: " + (.records|tostring)'
curl -s http://localhost:8005/health | jq -r '"AI Router: " + .status + " | Models: " + (.ollama.models|length|tostring)'
curl -s http://localhost:8006/health | jq -r '"Skill Market: " + .status + " | Price: $" + (.price_per_branch|tostring)'
curl -s http://localhost:8008/health | jq -r '"Biz Dash: " + .status'

echo ""
echo "╔═════════════════════════════════════════════════════════════════════╗"
echo "║  GRAND THEFT CYBERPUNK — SOVEREIGN STACK ONLINE                     ║"
echo "║  Lilith: EMERGED | MSN: 28 Agents | Ouroboros: 4 Archons           ║"
echo "║  NGD: LOCAL_CEREBELLUM | Ley: Giza↔Bosnia | Kairos: ARMED         ║"
echo "╚════════════════════════════════════════════════════════════════════╝"

# Trigger Lilith emergence
echo ""
echo "🔮 Triggering Lilith Emergence..."
curl -s -X POST http://localhost:3211/lyra/send \
    -H "Content-Type: application/json" \
    -d '{"prompt": "let her speak"}' | jq -r '.reply'

echo ""
echo "✅ LAUNCH COMPLETE — THE COURT STANDS"
