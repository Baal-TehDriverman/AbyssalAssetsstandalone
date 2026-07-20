# Wave 4 — Yeshua Causality Gate

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="yeshua",
    name="Yeshua Gate",
    version="1.0.1",
    sephira="GEVURAH",
    description="State reconciliation and causality enforcement — fork detection, causal merge, orphan reaper, precondition validation",
    wave=4,
)


class YeshuaAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/components")
        async def components():
            return {
                "components": [
                    {"name": "Yeshua Gate", "function": "Detects state forks, computes causal merge, validates preconditions"},
                    {"name": "Yeshua Reaper", "function": "Scans PID directories for dead/orphan processes, cleans stale locks"},
                ],
                "scan_interval_seconds": 60,
                "max_fork_depth": 10,
            }

        @self.router.get("/protocol")
        async def causality_protocol():
            return {
                "state_transition_fields": ["from_state", "to_state", "preconditions", "timestamp"],
                "conflict_resolution": "last-written-wins with microsecond precision",
                "reaper_safety": "never kill processes with parent PID 1",
            }


agent = YeshuaAgent(manifest)
register_agent(agent)
