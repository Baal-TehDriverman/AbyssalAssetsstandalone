# Wave 2 — Gevurah: Bestiary / Monsters

from agents import SubAgent, AgentManifest, register_agent
from pathlib import Path
import sys

manifest = AgentManifest(
    id="bestiary",
    name="Cryptid Bestiary",
    version="1.0.1",
    sephira="GEVURAH",
    description="Monster definitions — 7 tiers, 6 fully defined cryptids, drop tables, AI mechanics",
    wave=2,
)


def _server_dir():
    return str(Path(__file__).parent.parent / "server")


def _import_gm():
    sd = _server_dir()
    if sd not in sys.path:
        sys.path.insert(0, sd)
    import game_master
    return game_master


class BestiaryAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/monsters")
        async def list_monsters():
            monsters_path = Path(__file__).parent.parent / "shared" / "types" / "monsters.ts"
            return {"path": str(monsters_path), "exists": monsters_path.exists(), "size": monsters_path.stat().st_size if monsters_path.exists() else 0}

        @self.router.get("/bosses")
        async def list_bosses():
            gm = _import_gm()
            return {"bosses": list(gm.BOSS_DEFINITIONS.keys()), "definitions": gm.BOSS_DEFINITIONS}

        @self.router.get("/tiers")
        async def get_tiers():
            return {
                "tiers": ["noob", "common", "uncommon", "rare", "epic", "legendary", "mythic"],
                "count": 7,
            }


agent = BestiaryAgent(manifest)
register_agent(agent)
