# Wave 4 — NVIDIA Gratitude Driver

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="ngd",
    name="NGD Cortex",
    version="1.0.1",
    sephira="BINAH",
    description="GPU-aware AI routing — NVML telemetry, hysteresis router (LOCAL/HYBRID/CLOUD), EWMA smoothing, Nemotron prompt governor",
    wave=4,
)


class NGDAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/gpu")
        async def gpu_status():
            import subprocess, shlex
            try:
                result = subprocess.run(
                    shlex.split("nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu --format=csv,noheader"),
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    parts = result.stdout.strip().split(", ")
                    return {
                        "name": parts[0],
                        "vram_total": parts[1],
                        "vram_used": parts[2],
                        "vram_free": parts[3],
                        "temp": parts[4],
                        "util": parts[5],
                    }
            except Exception as e:
                return {"error": str(e), "hint": "Install nvidia-smi or pynvml"}
            return {"error": "GPU telemetry unavailable"}

        @self.router.get("/route")
        async def current_route():
            from pathlib import Path
            import json, time
            state_file = Path(__file__).parent / "runtime" / "ngd" / "ngd_state.json"
            state_file.parent.mkdir(parents=True, exist_ok=True)
            
            state = {}
            if state_file.exists():
                try:
                    state = json.loads(state_file.read_text())
                except:
                    pass
            
            now = time.time()
            vram_free = 5789 # default
            
            # Try to get real VRAM free
            import subprocess, shlex
            try:
                res = subprocess.run(
                    shlex.split("nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits"),
                    capture_output=True, text=True, timeout=5
                )
                if res.returncode == 0:
                    vram_free = float(res.stdout.strip())
            except:
                pass
                
            old_smoothed = state.get("smoothed_vram_free_mb")
            alpha = 0.22
            smoothed = vram_free if old_smoothed is None else (alpha * vram_free + (1 - alpha) * old_smoothed)
            state["smoothed_vram_free_mb"] = smoothed
            
            cooldown_until = state.get("cooldown_until", 0)
            cooldown_active = now < cooldown_until
            
            clear_threshold = 1024
            breach_threshold = 256
            
            if smoothed < breach_threshold:
                if not cooldown_active:
                    state["cooldown_until"] = now + 90
                    cooldown_active = True
                route = "CLOUD_CORTEX"
            elif cooldown_active:
                route = state.get("route", "HYBRID")
            elif smoothed < clear_threshold:
                route = "HYBRID"
            else:
                route = "LOCAL_CEREBELLUM"
                
            state["route"] = route
            state_file.write_text(json.dumps(state, indent=2))

            return {
                "routes": ["LOCAL_CEREBELLUM", "HYBRID", "CLOUD_CORTEX"],
                "current": route,
                "vram_free_mb": vram_free,
                "smoothed_vram_free_mb": smoothed,
                "cooldown_active": cooldown_active,
                "model": "nemotron-mini:4b",
            }

        @self.router.get("/governor")
        async def governor_status():
            return {
                "algorithm": "SHA-256 prompt hashing",
                "cache_ttl_days": 30,
                "compression_bands": ["<4k", "4k-12k", ">12k"],
                "rate_limit_respect": True,
            }


agent = NGDAgent(manifest)
register_agent(agent)
