# Wave 2 — Chesed: Client / Phaser 3

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="client",
    name="Game Client",
    version="1.0.1",
    sephira="CHESED",
    description="Phaser 3 TypeScript client — MainMenu, Market CLOB, Dredge mini-game, GameScene",
    wave=2,
)


class ClientAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/scenes")
        async def list_scenes():
            from pathlib import Path
            scenes_dir = Path(__file__).parent.parent / "client" / "src" / "scenes"
            scenes = sorted(f.stem for f in scenes_dir.glob("*.ts") if f.is_file())
            return {"scenes": scenes, "count": len(scenes)}

        @self.router.get("/services")
        async def list_services():
            from pathlib import Path
            services_dir = Path(__file__).parent.parent / "client" / "src" / "services"
            if services_dir.exists():
                services = sorted(f.stem for f in services_dir.glob("*.ts") if f.is_file())
                return {"services": services, "count": len(services)}
            return {"services": [], "count": 0}

        @self.router.get("/config")
        async def client_config():
            from pathlib import Path
            pkg = Path(__file__).parent.parent / "client" / "package.json"
            vite = Path(__file__).parent.parent / "client" / "vite.config.ts"
            return {
                "package_json": pkg.exists(),
                "vite_config": vite.exists(),
            }


agent = ClientAgent(manifest)
register_agent(agent)
