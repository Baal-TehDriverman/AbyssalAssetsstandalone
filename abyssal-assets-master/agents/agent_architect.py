# Wave 1 — Chokmah: Architecture / Game Design

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="architect",
    name="Game Architect",
    version="1.0.1",
    sephira="CHOKMAH",
    description="Game architecture reference — GDD, design decisions, full stack vision",
    wave=1,
)


class ArchitectAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/gdd")
        async def get_gdd():
            from pathlib import Path
            gdd_path = Path(__file__).parent.parent / "GDD.md"
            if gdd_path.exists():
                text = gdd_path.read_text()
                lines = text.count("\n")
                return {"path": str(gdd_path), "lines": lines, "size": len(text)}
            return {"error": "GDD.md not found"}

        @self.router.get("/design/philosophy")
        async def design_philosophy():
            return {
                "principles": [
                    "Cryptid hat trading as core loop",
                    "Dredge → Hunt → Craft → Trade → Ascend",
                    "Logarithmic drop rate formula",
                    "Skill web with 24 skills across 6 categories",
                    "Alchemical acts (12 Acts)",
                    "Local-first sovereign AI",
                ]
            }


agent = ArchitectAgent(manifest)
register_agent(agent)
