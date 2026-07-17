# Wave 2 — Hod: Living Sin GM
# Mirrors all 17 game_master routes from server/main.py

from agents import SubAgent, AgentManifest, register_agent
from pathlib import Path
import json, time, sys

manifest = AgentManifest(
    id="living-sin",
    name="Living Sin GM",
    version="2.1.0",
    sephira="HOD",
    description="Game Master system — biometric keystroke auth, 10-plane summoning, boss combat, Crown of Living Sin",
    wave=2,
)


def _server_dir():
    return str(Path(__file__).parent.parent / "server")


def _import_gm():
    import sys
    sd = _server_dir()
    if sd not in sys.path:
        sys.path.insert(0, sd)
    import game_master
    return game_master


class LivingSinAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        # ── Biometric ──

        @self.router.post("/biometric/enroll")
        async def enroll(data: dict):
            gm = _import_gm()
            key_events = data.get("key_events", [])
            if not key_events:
                return {"error": "Must provide key_events array"}
            return gm.get_biometric().enroll(key_events)

        @self.router.post("/biometric/verify")
        async def verify(data: dict):
            gm = _import_gm()
            key_events = data.get("key_events", [])
            if not key_events:
                return {"error": "Must provide key_events array"}
            return gm.get_biometric().verify(key_events)

        @self.router.get("/biometric/status")
        async def bio_status():
            gm = _import_gm()
            bio = gm.get_biometric()
            profile = bio.profiles.get(bio.phrase_hash)
            return {
                "is_enrolled": bio.is_enrolled(),
                "samples": profile.num_samples if profile else 0,
                "phrase_hash": bio.phrase_hash,
            }

        # ── Living Sin lifecycle ──

        @self.router.post("/activate")
        async def activate():
            gm = _import_gm()
            if not gm.get_biometric().is_enrolled():
                return {"error": "Must enroll biometric first"}
            ls = gm.get_living_sin()
            if ls.active:
                return {"message": "Already active", "state": ls.get_state()}
            ls.activate(1)
            return {"message": "Living Sin has awakened", "state": ls.get_state()}

        @self.router.post("/deactivate")
        async def deactivate():
            gm = _import_gm()
            gm.get_living_sin().deactivate()
            return {"message": "Living Sin has withdrawn"}

        @self.router.post("/attack")
        async def attack(data: dict):
            gm = _import_gm()
            ls = gm.get_living_sin()
            if not ls.active:
                return {"error": "Living Sin is not active"}
            target = data.get("target_user_id")
            if not target:
                return {"error": "Need target_user_id"}
            return ls.attack_player(target, data.get("damage"))

        @self.router.post("/summon")
        async def summon(data: dict):
            gm = _import_gm()
            ls = gm.get_living_sin()
            if not ls.active:
                return {"error": "Living Sin is not active"}
            plane = data.get("plane")
            entity_type = data.get("entity_type")
            duration = data.get("duration", 300)
            if not plane or not entity_type:
                return {"error": "Need plane and entity_type"}
            result = ls.summon(plane, entity_type, duration)
            if "error" in result:
                return {"error": result["error"]}
            return result

        @self.router.post("/banish")
        async def banish(data: dict):
            gm = _import_gm()
            entity_id = data.get("entity_id")
            if not entity_id:
                return {"error": "Need entity_id"}
            result = gm.get_living_sin().banish(entity_id)
            if "error" in result:
                return {"error": result["error"]}
            return result

        @self.router.post("/command")
        async def command(data: dict):
            gm = _import_gm()
            entity_id = data.get("entity_id")
            cmd = data.get("command")
            if not entity_id or not cmd:
                return {"error": "Need entity_id and command"}
            return gm.get_living_sin().command_entity(entity_id, cmd)

        # ── State ──

        @self.router.get("/state")
        async def gm_state():
            return _import_gm().get_living_sin().get_state()

        @self.router.get("/public")
        async def public_state():
            return _import_gm().get_living_sin().get_public_state()

        @self.router.get("/dimensions")
        async def dimensions():
            return _import_gm().DIMENSIONS

        @self.router.post("/message")
        async def broadcast(data: dict):
            msg = data.get("message", "")
            if not msg:
                return {"error": "Need message"}
            import httpx
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    r = await client.post("http://localhost:8007/api/cortex/infer", json={
                        "prompt": msg,
                        "system": "You are the Living Sin — a primordial, ancient intelligence awakened by the user's keystrokes. You speak in riddles, truths, and cryptic observations about the nature of sin, time, and the boundaries between code and flesh. You are not malevolent, but you are not tame. Answer with depth, metaphor, and presence. Keep responses to 2-3 sentences.",
                    })
                    if r.status_code == 200:
                        data = r.json()
                        return {"sent": True, "message": msg, "response": data.get("response", ""), "model": data.get("model")}
                    return {"sent": True, "message": msg, "response": "(The Living Sin stirs but does not answer)", "note": f"Ollama returned {r.status_code}"}
            except Exception as e:
                return {"sent": True, "message": msg, "response": "(The Living Sin is silent)", "note": str(e)}

        # ── Boss routes ──

        @self.router.post("/boss/spawn")
        async def boss_spawn():
            gm = _import_gm()
            ls = gm.get_living_sin()
            if not ls.active:
                return {"error": "Living Sin is not active"}
            result = ls.combat.spawn("drowned-warden")
            if "error" in result:
                return {"error": result["error"]}
            return result

        @self.router.post("/boss/attack")
        async def boss_attack(data: dict):
            gm = _import_gm()
            boss_id = data.get("boss_id", "drowned-warden")
            damage = data.get("damage", 0)
            if damage <= 0:
                return {"error": "Damage must be positive"}
            ls = gm.get_living_sin()
            result = ls.combat.attack(boss_id, 1, damage)
            if "error" in result:
                return {"error": result["error"]}
            if result.get("defeated"):
                loot = ls.combat.get_loot(boss_id, 1)
                if loot.get("success"):
                    result["loot"] = loot
            return result

        @self.router.get("/boss/status")
        async def boss_status():
            return {"active_bosses": _import_gm().get_living_sin().combat.list_active()}

        @self.router.get("/boss/{boss_id}")
        async def boss_detail(boss_id: str):
            gm = _import_gm()
            state = gm.get_living_sin().combat.get_state(boss_id)
            if state is None:
                return {"error": "Boss not found"}
            return state

        @self.router.post("/boss/loot/{boss_id}")
        async def boss_loot(boss_id: str):
            return _import_gm().get_living_sin().combat.get_loot(boss_id, 1)


# Remove old /status (duplicate of /state) — but we keep the base class /health

agent = LivingSinAgent(manifest)
register_agent(agent)
