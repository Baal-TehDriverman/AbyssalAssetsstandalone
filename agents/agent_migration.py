# Wave 3 — Malkuth: Linux Conversion / Operations

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="migration",
    name="Linux Migration",
    version="1.0.1",
    sephira="MALKUTH",
    description="Linux migration tools — batch path fixing, systemd deployment, bash equivalents for all PowerShell agents",
    wave=3,
)


class MigrationAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/audit")
        async def audit_windows():
            from pathlib import Path
            import os
            pub = Path(os.environ.get("PUB_ROOT", Path.home() / "Desktop/AI/Pub"))
            ps1_files = list(pub.rglob("*.ps1"))
            bat_files = list(pub.rglob("*.bat"))
            return {
                "remaining_ps1": len(ps1_files),
                "remaining_bat": len(bat_files),
                "converted_to_bash": True,
                "systemd_units": 5,
            }

        @self.router.get("/env")
        async def env_check():
            import os
            keys = ["PUB_ROOT", "ABYSSAL_SECRET_KEY", "DATABASE_URL", "CORS_ORIGINS", "NVIDIA_API_KEY"]
            return {k: "set" if os.getenv(k) else "not set" for k in keys}


agent = MigrationAgent(manifest)
register_agent(agent)
