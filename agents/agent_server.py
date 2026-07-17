# Wave 1 — Binah: Game Server

from agents import SubAgent, AgentManifest, register_agent
from pathlib import Path
import sys

manifest = AgentManifest(
    id="server",
    name="Game Server",
    version="1.0.1",
    sephira="BINAH",
    description="FastAPI game server — 7 DB models, auth, WebSocket, CLOB, dredge, Living Sin GM, boss combat",
    wave=1,
)


def _server_dir():
    return str(Path(__file__).parent.parent / "server")


def _import_gm():
    sd = _server_dir()
    if sd not in sys.path:
        sys.path.insert(0, sd)
    import game_master
    return game_master


class ServerAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/routes")
        async def list_routes():
            sd = _server_dir()
            if sd not in sys.path:
                sys.path.insert(0, sd)
            from main import app
            routes = []
            for r in app.routes:
                if hasattr(r, "path") and hasattr(r, "methods"):
                    for m in r.methods:
                        routes.append({"method": m, "path": r.path})
            return {"routes": routes, "count": len(routes)}

        @self.router.get("/models")
        async def list_models():
            return {
                "models": ["User", "Hat", "InventoryItem", "Order", "MarketListing", "Trade", "DredgeLog"],
                "count": 7,
            }

        @self.router.get("/gm/status")
        async def gm_status():
            return _import_gm().get_living_sin().get_state()


agent = ServerAgent(manifest)
register_agent(agent)
