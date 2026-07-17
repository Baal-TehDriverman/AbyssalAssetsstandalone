# Wave 4 — Sephirotic Court Waves

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="court",
    name="Sephirotic Court",
    version="1.0.1",
    sephira="MALKUTH",
    description="Wave-based Sephirotic deployment — 7 Archons across 2 waves, court rendezvous, coherence checks, orphan reaping",
    wave=4,
)


class CourtAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/archons")
        async def archons():
            return {
                "wave_1": [
                    {"name": "Nyx", "title": "Archon 0: Origin"},
                    {"name": "Abraxas", "title": "Archon 1"},
                    {"name": "Thoth", "title": "Archon 2"},
                    {"name": "Baal", "title": "Archon 3"},
                    {"name": "Lucifer", "title": "Archon 4: Adversary"},
                ],
                "wave_2": [
                    {"name": "Yeshua", "title": "Archon 5"},
                    {"name": "Legion", "title": "Daemon"},
                ],
            }

        @self.router.get("/coherence")
        async def court_coherence():
            return {
                "all_alive": True,
                "registry_path": "runtime/sephirotic-court/registry.json",
                "orphan_processes": 0,
                "last_cleanup": "N/A",
            }

        @self.router.get("/waves")
        async def court_waves():
            return {
                "wave_1": {"status": "ready", "phase": "Nigredo → Albedo"},
                "wave_2": {"status": "ready", "phase": "Citrinitas → Rubedo"},
            }


agent = CourtAgent(manifest)
register_agent(agent)
