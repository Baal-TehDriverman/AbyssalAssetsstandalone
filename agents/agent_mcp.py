# Wave 4 — Hermes MCP Bridge

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="hermes-mcp",
    name="Hermes MCP Bridge",
    version="1.0.1",
    sephira="HOD",
    description="MCP protocol bridge — skill_discover, skill_inject, swarm_status, memdir_read/write, telemetry_push, nvidia-smi query",
    wave=4,
)


class HermesMCPAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/tools")
        async def list_tools():
            return {
                "tools": [
                    "skill_discover",
                    "skill_inject",
                    "swarm_status",
                    "orchestrate_task",
                    "memdir_read",
                    "memdir_write",
                    "telemetry_push",
                    "nvidia_smi_query",
                ],
                "protocol": "JSON-RPC 2.0 over MCP",
            }

        @self.router.get("/skills/discover")
        async def skill_discover(tag: str = ""):
            from pathlib import Path
            skills_dir = Path(__file__).parent.parent / ".opencode" / "skills"
            skills = sorted(d.name for d in skills_dir.iterdir() if d.is_dir())
            return {"skills": skills, "count": len(skills)}


agent = HermesMCPAgent(manifest)
register_agent(agent)
