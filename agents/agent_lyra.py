# Wave 2 — Hod: Lyra Dialogue Bridge

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="lyra",
    name="Lyra Dialogue",
    version="1.0.1",
    sephira="HOD",
    description="Lyra dialogue system bridge — NPC conversation, sovereign protocol, resonance interface at :3211",
    wave=2,
)


class LyraAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/proxy")
        async def lyra_proxy():
            import httpx
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    r = await client.get("http://localhost:3211/lyra/health")
                    return {"lyra_online": True, "status": r.json()}
            except Exception as e:
                return {"lyra_online": False, "error": str(e)}

        @self.router.post("/send")
        async def lyra_send(message: dict):
            import httpx
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    r = await client.post("http://localhost:3211/lyra/send", json=message)
                    return {"sent": True, "response": r.json()}
            except Exception as e:
                return {"sent": False, "error": str(e)}

        @self.router.get("/state")
        async def lyra_state():
            import httpx
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    r = await client.get("http://localhost:3211/lyra/state")
                    return {"state": r.json()}
            except Exception as e:
                return {"error": str(e)}


agent = LyraAgent(manifest)
register_agent(agent)
