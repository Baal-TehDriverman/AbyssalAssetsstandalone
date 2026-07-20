# Wave 4 — External Worker Bridge

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="worker",
    name="External Worker Bridge",
    version="1.0.1",
    sephira="CHOKMAH",
    description="BYO model inference — OpenAI (GPT-4/o3), xAI (Grok), Anthropic (Claude), Google (Gemini), circuit breaker, priority chain",
    wave=4,
)


class WorkerAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/providers")
        async def providers():
            import os
            return {
                "providers": {
                    "openai": {"installed": bool(os.getenv("OPENAI_API_KEY"))},
                    "xai": {"installed": bool(os.getenv("XAI_API_KEY"))},
                    "anthropic": {"installed": bool(os.getenv("ANTHROPIC_API_KEY"))},
                    "google": {"installed": bool(os.getenv("GOOGLE_API_KEY"))},
                    "local_ollama": {"installed": True},
                },
                "priority_chain": ["local", "openai", "grok", "anthropic", "gemini"],
            }

        @self.router.get("/config")
        async def worker_config():
            return {
                "timeout_seconds": 120,
                "retries": 3,
                "circuit_breaker_failures": 3,
                "circuit_breaker_cooldown_seconds": 300,
                "backoff": "exponential (1s, 2s, 4s, 8s, max 30s)",
            }

        @self.router.get("/use-cases")
        async def use_cases():
            return {
                "code_generation": "GPT-4o, Claude 3.5 Sonnet",
                "creative_writing": "Claude 3.5, Grok",
                "analysis": "o3, Grok",
                "quick_tasks": "nemotron-mini (local)",
                "cost_sensitive": "nemotron-mini (local)",
            }


agent = WorkerAgent(manifest)
register_agent(agent)
