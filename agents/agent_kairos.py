# Wave 4 — Kairos Dream System

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="kairos",
    name="Kairos Dream",
    version="1.0.1",
    sephira="HOD",
    description="Dream/time state processor — hypnagogic/hypnopompic capture, kairos timing, resonance-gated injection, memory storage",
    wave=4,
)


class KairosAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/pipeline")
        async def dream_pipeline():
            return {
                "stages": ["Dream Capture", "Pattern Extraction", "Kairos Stamping", "Memory Injection"],
                "states": ["Hypnagogic", "REM", "Hypnopompic", "Lucid"],
                "capture_methods": ["passive", "active", "detected"],
            }

        @self.router.get("/kairotic")
        async def kairotic_window():
            return {
                "context_resonance_min": 0.7,
                "min_conversation_depth": 5,
                "max_queue": 10,
                "kairos_window_seconds": 3600,
            }

        @self.router.get("/queue")
        async def dream_queue():
            from pathlib import Path
            import json, os
            queue_path = Path(os.environ.get("PUB_ROOT", Path.home() / "Desktop/AI/Pub")) / "golem_diary.db"
            return {"queue_size": 0, "delivered": 0, "pending": 0, "db_present": queue_path.exists()}


agent = KairosAgent(manifest)
register_agent(agent)
