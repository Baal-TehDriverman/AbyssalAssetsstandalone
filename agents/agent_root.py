# Wave 1 — Keter: Root / Sephirotic Interface

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="root",
    name="Sephirotic Root",
    version="1.0.1",
    sephira="KETER",
    description="Root manifest interface — indexes and resolves every file in the project by direct reference",
    wave=1,
)


class RootAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/resolve/{sephira}")
        async def resolve_sephira(sephira: str):
            from sephirotic import root
            files = root.sephira.get(sephira.upper(), {}).get("files", [])
            return {"sephira": sephira.upper(), "files": files, "count": len(files)}

        @self.router.get("/summary")
        async def root_summary():
            from sephirotic import root
            return {"summary": root.summary()}

        @self.router.get("/skills")
        async def list_skills():
            from pathlib import Path
            skills_dir = Path(__file__).parent.parent / ".opencode" / "skills"
            return {
                "skills": sorted(d.name for d in skills_dir.iterdir() if d.is_dir()),
                "count": len(list(skills_dir.iterdir())),
            }


agent = RootAgent(manifest)
register_agent(agent)
