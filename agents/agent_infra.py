# Wave 3 — Yesod: Infrastructure / Deployment

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="infra",
    name="Infrastructure",
    version="1.0.1",
    sephira="YESOD",
    description="Build, config, deployment — Docker Compose, Vite, TypeScript, systemd services",
    wave=3,
)


class InfraAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/docker")
        async def docker_config():
            from pathlib import Path
            dcf = Path(__file__).parent.parent / "docker-compose.yml"
            return {"exists": dcf.exists(), "path": str(dcf)}

        @self.router.get("/systemd")
        async def systemd_services():
            return {
                "services": [
                    "lilith-api.service",
                    "lyra-api.service",
                    "ouroboros-daemon.service",
                    "swarm-orchestrator.service",
                    "antigravity-bridge.service",
                ]
            }

        @self.router.get("/deploy/status")
        async def deploy_status():
            from pathlib import Path
            import json
            status_path = Path(__file__).parent.parent / "runtime" / "deploy" / "status.json"
            if status_path.exists():
                return json.loads(status_path.read_text())
            return {"deployed_batches": [1, 2, 3], "skills": 26}


agent = InfraAgent(manifest)
register_agent(agent)
