# Wave 4 — Speculative Cerebellum (LOCAL-ONLY MODE)
# All tokens processed locally via Ollama — NO cloud fallback

from agents import SubAgent, AgentManifest, register_agent
from agents.shared_memory import shared_mind
from pydantic import BaseModel
import os

# ── Model Priority Chain (all local) ──
# Primary: msn-cyberpunk:latest — QLoRA fine-tuned for CP2077 MSN integration
# Fallback: hermes3:8b — 131k ctx, tool-capable, Q4_0, 4.7GB
# Emergency: nemotron-mini:latest — 4k ctx, 2.7GB (fast)
LOCAL_MODEL_PRIMARY   = os.getenv("CEREBELLUM_MODEL",   "msn-cyberpunk:latest")
LOCAL_MODEL_FALLBACK  = os.getenv("CEREBELLUM_FALLBACK", "hermes3:8b")
LOCAL_MODEL_EMERGENCY = os.getenv("CEREBELLUM_EMERGENCY", "nemotron-mini:latest")
OLLAMA_BASE           = "http://localhost:11434"

manifest = AgentManifest(
    id="cerebellum",
    name="Speculative Cerebellum",
    version="2.0.0",
    sephira="BINAH",
    description="LOCAL-ONLY inference — hermes3:8b primary, llama3.1:8b fallback, nemotron-mini emergency. Zero cloud egress. MSN-routed.",
    wave=4,
)


class InferRequest(BaseModel):
    prompt: str = ""
    system: str = ""
    model: str = ""  # optional override
    use_memory: bool = True
    memory_limit: int = 5


class MemoryRecordRequest(BaseModel):
    agent_id: str = "external"
    objective: str = ""
    forward_state: dict = {}
    backward_state: dict = {}
    trigger_condition: str = "manual"
    metadata: dict = {}


class CerebellumAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.post("/infer")
        async def infer(req: InferRequest):
            import httpx
            memories = shared_mind.recall(limit=req.memory_limit) if req.use_memory else []
            memory_context = ""
            if memories:
                memory_context = "\n\nLocal shared cerebellum recall:\n" + "\n".join(
                    f"- step {item['step_id']} {item['trigger_condition']}: {item['forward_state']}"
                    for item in memories
                )
            prompt = req.prompt + memory_context

            shared_mind.record_step(
                agent_id="cerebellum",
                objective=req.prompt[:500],
                forward_state={"prompt": req.prompt[:2000], "memory_items": len(memories)},
                backward_state={"projected_intent": "local_inference", "model_override": req.model},
                trigger_condition="infer_request",
                metadata={"use_memory": req.use_memory},
            )

            # Respect explicit model override, otherwise use priority chain
            models_to_try = [
                req.model if req.model else LOCAL_MODEL_PRIMARY,
                LOCAL_MODEL_FALLBACK,
                LOCAL_MODEL_EMERGENCY,
            ]
            last_error = None
            for model in models_to_try:
                try:
                    async with httpx.AsyncClient(timeout=60) as client:
                        r = await client.post(f"{OLLAMA_BASE}/api/generate", json={
                            "model": model,
                            "prompt": prompt,
                            "system": req.system,
                            "stream": False,
                        })
                        if r.status_code == 200:
                            data = r.json()
                            shared_mind.record_step(
                                agent_id="cerebellum",
                                objective=req.prompt[:500],
                                forward_state={"model": data.get("model", model), "response": data.get("response", "")[:2000]},
                                backward_state={"projected_intent": "answer_delivered", "route": "LOCAL_CEREBELLUM"},
                                trigger_condition="infer_response",
                                metadata={"eval_count": data.get("eval_count"), "memory_items": len(memories)},
                            )
                            return {
                                "model":          data.get("model", model),
                                "response":       data.get("response", ""),
                                "route":          "LOCAL_CEREBELLUM",
                                "local":          True,
                                "cloud":          False,
                                "tokens_local":   True,
                                "eval_count":     data.get("eval_count"),
                                "eval_duration_ns": data.get("eval_duration"),
                                "shared_memory": {
                                    "enabled": req.use_memory,
                                    "items_recalled": len(memories),
                                    "db_path": shared_mind.stats().get("db_path"),
                                },
                                "model_chain": {
                                    "primary":   LOCAL_MODEL_PRIMARY,
                                    "fallback":  LOCAL_MODEL_FALLBACK,
                                    "emergency": LOCAL_MODEL_EMERGENCY,
                                },
                            }
                        last_error = f"Ollama HTTP {r.status_code} for model {model}"
                except Exception as e:
                    last_error = str(e)
                    continue
            return {
                "error": last_error,
                "local": False,
                "cloud": False,
                "hint": "All local models exhausted — check Ollama is running: ollama list",
            }

        @self.router.get("/memory/status")
        async def memory_status():
            return shared_mind.stats()

        @self.router.get("/memory/recall")
        async def memory_recall(limit: int = 5, agent_id: str = ""):
            return {"memories": shared_mind.recall(limit=limit, agent_id=agent_id or None)}

        @self.router.post("/memory/record")
        async def memory_record(req: MemoryRecordRequest):
            step_id = shared_mind.record_step(
                agent_id=req.agent_id,
                objective=req.objective,
                forward_state=req.forward_state,
                backward_state=req.backward_state,
                trigger_condition=req.trigger_condition,
                metadata=req.metadata,
            )
            return {"recorded": step_id is not None, "step_id": step_id}

        @self.router.get("/models")
        async def list_local_models():
            import httpx
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    r = await client.get(f"{OLLAMA_BASE}/api/tags")
                    if r.status_code == 200:
                        tags = r.json().get("models", [])
                        return {
                            "local_models": [m["name"] for m in tags],
                            "active_primary": LOCAL_MODEL_PRIMARY,
                            "active_fallback": LOCAL_MODEL_FALLBACK,
                            "active_emergency": LOCAL_MODEL_EMERGENCY,
                            "cloud_enabled": False,
                        }
            except Exception as e:
                return {"error": str(e)}

        @self.router.get("/status")
        async def status():
            import httpx
            ollama_ok = False
            loaded_models = []
            try:
                async with httpx.AsyncClient(timeout=3) as client:
                    r = await client.get(f"{OLLAMA_BASE}/api/tags")
                    if r.status_code == 200:
                        ollama_ok = True
                        loaded_models = [m["name"] for m in r.json().get("models", [])]
            except Exception:
                pass
            return {
                "ollama_running": ollama_ok,
                "model_primary": LOCAL_MODEL_PRIMARY,
                "model_fallback": LOCAL_MODEL_FALLBACK,
                "model_emergency": LOCAL_MODEL_EMERGENCY,
                "loaded_models": loaded_models,
                "mode": "LOCAL_ONLY",
                "cloud_enabled": False,
                "tokens_local": True,
                "shared_memory": shared_mind.stats(),
                "circuit_breaker": {"failures": 0, "state": "closed"},
            }


agent = CerebellumAgent(manifest)
register_agent(agent)
