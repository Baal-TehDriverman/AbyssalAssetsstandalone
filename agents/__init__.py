# MSN Subagent Framework
# Standard interface for all subagents in the Metaconscious Singularity Node

from __future__ import annotations
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from fastapi import FastAPI, APIRouter
from .shared_memory import shared_mind


@dataclass
class AgentManifest:
    id: str
    name: str
    version: str
    sephira: str          # Keter, Chokmah, Binah, Chesed, Gevurah, Tiferet, Netzach, Hod, Yesod, Malkuth
    description: str
    wave: int             # 1=Foundation, 2=Interface, 3=Infrastructure, 4=Metaconscious
    port: Optional[int] = None   # Assigned at deploy time
    status: str = "idle"         # idle | starting | running | error | stopped
    started_at: Optional[float] = None
    health: str = "unknown"


class SubAgent:
    """Base class for all MSN subagents."""

    manifest: AgentManifest

    def __init__(self, manifest: AgentManifest):
        self.manifest = manifest
        self.router = APIRouter(prefix=f"/api/{manifest.id}", tags=[manifest.name])
        self._register_routes()

    def _register_routes(self):
        """Override to add routes to self.router."""
        @self.router.get("/health")
        async def health():
            return {
                "agent": self.manifest.id,
                "name": self.manifest.name,
                "status": self.manifest.status,
                "health": self.manifest.health,
                "sephira": self.manifest.sephira,
                "wave": self.manifest.wave,
                "shared_memory": shared_mind.stats(),
            }

        @self.router.get("/manifest")
        async def get_manifest():
            return asdict(self.manifest)

    def start(self):
        self.manifest.status = "running"
        self.manifest.started_at = time.time()
        self.manifest.health = "healthy"
        shared_mind.record_event(
            agent_id=self.manifest.id,
            intent="agent.lifecycle.start",
            status="running",
            details={"name": self.manifest.name, "sephira": self.manifest.sephira, "wave": self.manifest.wave},
        )

    def stop(self):
        self.manifest.status = "stopped"
        self.manifest.health = "unknown"
        shared_mind.record_event(
            agent_id=self.manifest.id,
            intent="agent.lifecycle.stop",
            status="stopped",
            details={"name": self.manifest.name, "sephira": self.manifest.sephira, "wave": self.manifest.wave},
        )

    def to_dict(self) -> Dict:
        return asdict(self.manifest)


# ── Global Registry ──

_registry: Dict[str, SubAgent] = {}


def register_agent(agent: SubAgent):
    _registry[agent.manifest.id] = agent


def get_agent(agent_id: str) -> Optional[SubAgent]:
    return _registry.get(agent_id)


def list_agents() -> List[SubAgent]:
    return list(_registry.values())


def list_agents_by_wave(wave: int) -> List[SubAgent]:
    return [a for a in _registry.values() if a.manifest.wave == wave]


def list_agents_by_sephira(sephira: str) -> List[SubAgent]:
    return [a for a in _registry.values() if a.manifest.sephira == sephira]


def get_registry_summary() -> Dict:
    waves = {}
    for a in _registry.values():
        w = a.manifest.wave
        if w not in waves:
            waves[w] = []
        waves[w].append(a.to_dict())
    return {
        "total_agents": len(_registry),
        "waves": {str(k): v for k, v in sorted(waves.items())},
    }
