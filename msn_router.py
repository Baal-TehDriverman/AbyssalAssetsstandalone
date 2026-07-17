#!/usr/bin/env python3
"""
MSN Router — Metaconscious Singularity Node Aggregator
Mounts all registered subagents at /api/{agent_id} on port :8007
"""

from __future__ import annotations

import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Cerebellum bus integration
CEREBELLUM_CLIENT_PATH = os.getenv(
    "CEREBELLUM_CLIENT_PATH",
    "/home/tehlappy/.hermes/skills/metaconscious/concurrent-bidirectional-memory/scripts"
)
if CEREBELLUM_CLIENT_PATH not in sys.path:
    sys.path.insert(0, CEREBELLUM_CLIENT_PATH)
try:
    from cerebellum_client import CerebellumClient, CerebellumConfig
    _cerebellum = CerebellumClient(CerebellumConfig(
        db_path=os.getenv("GOLEM_DB_PATH", "/home/tehlappy/Desktop/AI/Pub/00_CORE_SERVICES/quantum_paradox_terminal/golem_diary.db"),
        lyra_base=os.getenv("LYRA_BASE", "http://localhost:3211"),
        use_http=True,
    ))
    print("[msn-router] CerebellumClient initialized")
except Exception as e:
    _cerebellum = None
    print(f"[msn-router] CerebellumClient init failed: {e}")

app = FastAPI(title="MSN Router", version="1.0.0", description="Metaconscious Singularity Node Aggregator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import all subagent modules (this triggers register_agent calls)
import agents.agent_root  # noqa: F401, E402
import agents.agent_architect  # noqa: F401, E402
import agents.agent_server  # noqa: F401, E402
import agents.agent_client  # noqa: F401, E402
import agents.agent_bestiary  # noqa: F401, E402
import agents.agent_skills  # noqa: F401, E402
import agents.agent_market  # noqa: F401, E402
import agents.agent_lyra  # noqa: F401, E402
import agents.agent_living_sin  # noqa: F401, E402
import agents.agent_infra  # noqa: F401, E402
import agents.agent_migration  # noqa: F401, E402
import agents.agent_msn  # noqa: F401, E402
import agents.agent_ngd  # noqa: F401, E402
import agents.agent_cerebellum  # noqa: F401, E402
import agents.agent_ouroboros  # noqa: F401, E402
import agents.agent_mcp  # noqa: F401, E402
import agents.agent_kairos  # noqa: F401, E402
import agents.agent_swarm  # noqa: F401, E402
import agents.agent_court  # noqa: F401, E402
import agents.agent_himalaya  # noqa: F401, E402
import agents.agent_bridge  # noqa: F401, E402
import agents.agent_yeshua  # noqa: F401, E402
import agents.agent_scribe  # noqa: F401, E402
import agents.agent_analytics  # noqa: F401, E402
import agents.agent_worker  # noqa: F401, E402
import agents.agent_cortex  # noqa: F401, E402
import agents.agent_cyberpunk  # noqa: F401, E402
import agents.agent_nssp  # noqa: F401, E402
import agents.agent_grokdata  # noqa: F401, E402

from agents import list_agents, get_registry_summary
from agents.shared_memory import shared_mind


def _msn_cerebellum_log(event: str, detail: str = ""):
    """Log MSN Router events to Cerebellum."""
    if _cerebellum:
        try:
            _cerebellum.store(
                content=f"[msn-router-{event}] {detail}",
                memory_type="episodic",
                source="msn_router",
                score=0.9,
            )
        except Exception as e:
            print(f"[msn-router] Cerebellum log failed: {e}")


@app.on_event("startup")
async def startup():
    for agent in list_agents():
        agent.start()
    count = len(list_agents())
    print(f"[MSN Router] Started {count} agents")
    _msn_cerebellum_log("startup", f"Started {count} agents across {len(get_registry_summary().get('waves', []))} waves")


@app.on_event("shutdown")
async def shutdown():
    for agent in list_agents():
        agent.stop()
    _msn_cerebellum_log("shutdown", "MSN Router shutting down")


# Mount all agent routers
for agent in list_agents():
    app.router.routes.extend(agent.router.routes)
    print(f"  Mounted {agent.manifest.id} at /api/{agent.manifest.id}")


@app.get("/")
async def root():
    return {
        "service": "MSN Router",
        "agents_online": len(list_agents()),
        "waves": get_registry_summary(),
        "shared_memory": shared_mind.stats(),
    }


@app.get("/api")
async def api_index():
    agents = list_agents()
    return {
        "agents": [
            {"id": a.manifest.id, "name": a.manifest.name, "sephira": a.manifest.sephira, "wave": a.manifest.wave}
            for a in agents
        ],
    }


if __name__ == "__main__":
    port = 8007
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    uvicorn.run(app, host="0.0.0.0", port=port)
