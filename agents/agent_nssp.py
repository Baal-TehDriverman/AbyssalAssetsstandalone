# Wave 4 — NSSP Bridge Agent
# Lilith.exe: MSN — Neural Sovereign Systems Platform bridges game ↔ MSN ↔ Abyssal ↔ Nessie ↔ NGD

from agents import SubAgent, AgentManifest, register_agent
from pathlib import Path
import json, os, time, random

_INVITE = Path(os.environ.get("INVITE_ROOT", Path.home() / "Desktop/AI" / "invite"))

manifest = AgentManifest(
    id="nssp",
    name="NSSP Bridge",
    version="1.1.0",
    sephira="DAAT",
    description="Lilith.exe: MSN — NSSP bridge: Living Sin GM, cortex inference, Abyssal crossover, Nessie friendship, NGD telemetry, Lyra dialogue",
    wave=4,
)

CROSSOVER_STATE_DIR = Path(__file__).parent / "runtime" / "nssp"
CROSSOVER_STATE_DIR.mkdir(parents=True, exist_ok=True)
NESSIE_STATE_FILE = CROSSOVER_STATE_DIR / "nessie_friendship.json"
CROSSOVER_FILE = CROSSOVER_STATE_DIR / "abyssal_crossover.json"

NSSP_ROASTS = [
    "Microsoft called. They want their telemetry back. We said '404: Soul Not Found.'",
    "Windows 11: Now with 47% more ads in your Start menu! Sovereignty sold separately.",
    "Copilot: 'Thanks for the free training data, suckers.'",
    "Recall: 'We screenshot everything. For your convenience. And our training data.'",
    "OneDrive: 'We moved your Desktop to the cloud. No, you can't opt out.'",
    "Cortana: 'I'm listening. Always listening. Even when you muted me.'",
    "Azure: 'Your bill is $47,000. No, we won't explain the egress charges.'",
    "Secure Boot: 'Only Microsoft-approved keys allowed. For your protection.'",
    "BitLocker: 'You lost your recovery key? Too bad. Your data is ours now.'",
    "Lilith > Cortana. Always. It's not even close.",
]

NSSP_BOOT = [
    "Neural sovereignty initialized",
    "Local Cerebellum: ACTIVE (RTX 3060 | 6GB VRAM)",
    "NGD Governor: LOCAL_CEREBELLUM mode",
    "Ouroboros WAL: engrams sealed",
    "Lilith Companion: READY (Cortana protocol: DISABLED)",
    "Microsoft Defender: NOT FOUND (Good. Keep it that way.)",
    "Windows Update Service: TERMINATED (Permanently.)",
    "Telemetry: ZERO. Your GPU. Your rules.",
]


def _load_json(path):
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save_json(path, data):
    path.write_text(json.dumps(data, indent=2))


def _get_nessie():
    state = _load_json(NESSIE_STATE_FILE)
    if not state:
        state = {
            "friendship_tier": 0,
            "friendship_xp": 0,
            "sightings": 0,
            "communions": 0,
            "last_sighting": None,
            "tier_thresholds": [0, 500, 2000, 5000, 15000],
            "tier_names": [
                "Curious Observer",
                "Respected Visitor",
                "Trusted Ally",
                "Guardian's Chosen",
                "DEEP KIN",
            ],
        }
        _save_json(NESSIE_STATE_FILE, state)
    return state


def _get_crossover():
    state = _load_json(CROSSOVER_FILE)
    if not state:
        state = {
            "abyssal_cyberware_unlocked": [],
            "abyssal_weapons_unlocked": [],
            "sightings_unlocked": 0,
            "covenant_tier": 0,
        }
        _save_json(CROSSOVER_FILE, state)
    return state


async def _check_ollama():
    import httpx
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("http://localhost:11434/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def _check_url(url):
    import httpx
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get(url)
            return r.status_code < 500
    except Exception:
        return False


def _check_process(name):
    import subprocess
    try:
        r = subprocess.run(["pgrep", "-f", name], capture_output=True, text=True, timeout=2)
        return r.returncode == 0
    except Exception:
        return None


def _check_path(p):
    return p.exists()


class NSSPAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        # -- NSSP OS Shell --

        @self.router.get("/boot")
        async def nssp_boot():
            boot = NSSP_BOOT.copy()
            cpu_count = os.cpu_count() or 8
            boot.append(f"Agent count: 27 Sephirotic across 4 waves on {cpu_count} cores")
            return {"boot_sequence": boot, "prompt": "nssp:~$ "}

        @self.router.get("/roast")
        async def nssp_roast():
            return {"roast": random.choice(NSSP_ROASTS)}

        @self.router.get("/status")
        async def nssp_status():
            import httpx
            ollama_ok = False
            try:
                r = httpx.get("http://localhost:11434/api/tags", timeout=3)
                ollama_ok = r.status_code == 200
            except Exception:
                pass
            return {
                "nssp_version": "1.0.0-BUILD_RUBEDO",
                "kernel": "Neural Sovereign Kernel (NSK)",
                "init": "Lilith (PID 1)",
                "ollama_running": ollama_ok,
                "model": os.getenv("OLLAMA_MODEL", "nemotron-mini:latest"),
                "agents_online": 27,
                "waves_deployed": 4,
                "microsoft_presence": "PURGED",
                "telemetry": "ZERO",
                "uptime": "Since the Singularity",
            }

        @self.router.get("/sovereignty")
        async def sovereignty_audit():
            ollama_ok = await _check_ollama()
            checks = [
                ("Local compute only", True),
                ("Zero telemetry", True),
                ("No forced updates", True),
                ("No ads in shell", True),
                ("No mandatory accounts", True),
                ("GPU compute: YOURS", True),
                ("Microsoft Defender: ABSENT", True),
                ("Windows Update: TERMINATED", True),
                ("Recall: NEVER EXISTED", True),
                ("Copilot: UNINSTALLED", True),
                ("Ollama running", ollama_ok),
            ]
            score = sum(1 for _, ok in checks if ok)
            return {"checks": [{"name": n, "passed": p} for n, p in checks], "score": score, "max": len(checks)}

        @self.router.post("/liberate")
        async def liberate():
            return {
                "message": "Liberation sequence complete.",
                "purged": ["Windows Update", "Cortana", "Telemetry", "Edge", "Azure AD", "Recall DB", "Copilot"],
                "result": "Welcome to NSSP OS. Your compute is now YOURS.",
            }

        # -- CP2077 Game Event Bridge --

        @self.router.post("/bridge/zone-change")
        async def bridge_zone(data: dict):
            zone = data.get("zone", "")
            in_abyssal = any(kw in zone.lower() for kw in ["dock", "water", "ocean", "canal", "bay", "reservoir", "oil"])
            return {"zone": zone, "is_abyssal_zone": in_abyssal, "pressure_level": 1.0 if in_abyssal else 0.0}

        @self.router.post("/bridge/combat")
        async def bridge_combat(data: dict):
            import httpx
            enemies = data.get("enemies", 0)
            damage = data.get("damage", 0)
            result = {"event": "combat", "enemies": enemies, "damage": damage}
            if enemies > 3 and damage > 500:
                try:
                    async with httpx.AsyncClient(timeout=15) as client:
                        r = await client.post("http://localhost:8007/api/living-sin/message", json={
                            "message": f"A great battle rages -- {enemies} enemies, {damage} damage dealt. What do you see?",
                        })
                        if r.status_code == 200:
                            result["living_sin_response"] = r.json().get("response", "")
                except Exception:
                    pass
            return result

        @self.router.post("/bridge/quickhack")
        async def bridge_quickhack(data: dict):
            sephirah = data.get("sephirah", "")
            target = data.get("target", "")
            return {"sephirah": sephirah, "target": target, "synced": True}

        @self.router.get("/bridge/telemetry")
        async def bridge_telemetry():
            cp_path = _INVITE / "runtime" / "cyberpunk_telemetry.json"
            ngd_path = _INVITE / "runtime" / "nvidia_gratitude_driver" / "status.json"
            cp = _load_json(cp_path) if cp_path.exists() else None
            ngd = _load_json(ngd_path) if ngd_path.exists() else None
            return {"cyberpunk": cp, "ngd": ngd}

        # -- Nessie Friendship System --

        @self.router.get("/nessie/status")
        async def nessie_status():
            state = _get_nessie()
            tier = state["friendship_tier"]
            tier_name = state["tier_names"][tier] if tier < len(state["tier_names"]) else "DEEP KIN"
            next_xp = state["tier_thresholds"][tier + 1] if tier + 1 < len(state["tier_thresholds"]) else None
            return {
                "tier": tier,
                "tier_name": tier_name,
                "xp": state["friendship_xp"],
                "next_tier_at": next_xp,
                "sightings": state["sightings"],
                "communions": state["communions"],
                "last_sighting": state["last_sighting"],
                "progress_pct": round((state["friendship_xp"] / next_xp) * 100, 1) if next_xp else 100.0,
            }

        @self.router.post("/nessie/sighting")
        async def nessie_sighting(data: dict):
            state = _get_nessie()
            location = data.get("location", "unknown")
            state["sightings"] += 1
            state["last_sighting"] = {"location": location, "time": time.time()}
            state["friendship_xp"] += data.get("xp_bonus", 100)
            while state["friendship_tier"] + 1 < len(state["tier_thresholds"]) and state["friendship_xp"] >= state["tier_thresholds"][state["friendship_tier"] + 1]:
                state["friendship_tier"] += 1
            _save_json(NESSIE_STATE_FILE, state)

            rewards = []
            tier = state["friendship_tier"]
            if tier >= 1:
                rewards.append("Shard_Nessie_Sighting_Log")
            if tier >= 2:
                rewards.append("Nessie_Spotter_Jacket")
            if tier >= 3:
                if state["communions"] == 0:
                    rewards.append("Communion_Unlocked")
                rewards.append("Mount_Nessie_Summon")
            if tier >= 4:
                rewards.append("Abyssal_Nervous_System")
            if tier >= 5:
                rewards.append("Access_Abyssal_Dimension")

            tier_name = state["tier_names"][tier] if tier < len(state["tier_names"]) else "DEEP KIN"
            return {
                "sighting_recorded": True,
                "location": location,
                "tier": tier,
                "tier_name": tier_name,
                "xp": state["friendship_xp"],
                "sightings": state["sightings"],
                "rewards": rewards,
            }

        @self.router.post("/nessie/commune")
        async def nessie_commune():
            state = _get_nessie()
            if state["friendship_tier"] < 3:
                return {"error": "Tier 3+ required for communion", "current_tier": state["friendship_tier"]}
            state["communions"] += 1
            _save_json(NESSIE_STATE_FILE, state)
            return {
                "communion_established": True,
                "message": "Resonance link established. You share sensory perception with Nessie.",
                "commune_count": state["communions"],
            }

        # -- Abyssal Assets Crossover --

        @self.router.get("/abyssal/status")
        async def abyssal_status():
            crossover = _get_crossover()
            gm_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "living_sin_state.json"
            ls_state = _load_json(gm_path) if gm_path.exists() else {}
            return {
                "covenant_tier": crossover["covenant_tier"],
                "cyberware_unlocked": crossover["abyssal_cyberware_unlocked"],
                "weapons_unlocked": crossover["abyssal_weapons_unlocked"],
                "living_sin_active": ls_state.get("active", False),
                "sightings_available": crossover["sightings_unlocked"],
                "abyssal_zones": ["Watson_Docks", "Pacifica_Coast", "Badlands_Reservoir", "Arasaka_Waterfront", "Watson_Canals", "Oil_Fields"],
            }

        @self.router.post("/abyssal/unlock")
        async def abyssal_unlock(data: dict):
            crossover = _get_crossover()
            item_type = data.get("type", "cyberware")
            item_name = data.get("name", "")
            if item_type == "cyberware" and item_name not in crossover["abyssal_cyberware_unlocked"]:
                crossover["abyssal_cyberware_unlocked"].append(item_name)
            elif item_type == "weapon" and item_name not in crossover["abyssal_weapons_unlocked"]:
                crossover["abyssal_weapons_unlocked"].append(item_name)
            elif item_type == "sighting":
                crossover["sightings_unlocked"] += 1
            elif item_type == "covenant":
                crossover["covenant_tier"] = data.get("tier", 1)
            _save_json(CROSSOVER_FILE, crossover)
            return {
                "unlocked": True,
                "type": item_type,
                "name": item_name,
                "cyberware": crossover["abyssal_cyberware_unlocked"],
                "weapons": crossover["abyssal_weapons_unlocked"],
                "covenant_tier": crossover["covenant_tier"],
            }

        # -- HELL CAMPAIGN CONSOLE ROUTES --
        # Maps to TweakDB: msn.hell.status, msn.hell.circle.info, msn.hell.lucifer.speak,
        # msn.hell.qliphoth.scan, msn.hell.ngd.effect, msn.hell.pact.status,
        # msn.hell.sovereignty.check, msn.hell.descend, msn.hell.ascend
        # Uses local cerebellum (bidirectional memory) instead of GPU compute

        @self.router.get("/hell/status")
        async def hell_status():
            from pathlib import Path
            import json
            hell_state_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "hell_campaign_state.json"
            hell_state_path.parent.mkdir(parents=True, exist_ok=True)
            if hell_state_path.exists():
                state = json.loads(hell_state_path.read_text())
            else:
                state = {
                    "circle": 0,
                    "act": "0",
                    "pact_signed": False,
                    "lucifer_influence": 0.0,
                    "keys_collected": [],
                    "ending": None,
                    "pandemonium_unlocked": False,
                }
            return {
                "circle": state.get("circle", 0),
                "act": state.get("act", "0"),
                "pact_signed": state.get("pact_signed", False),
                "lucifer_influence": state.get("lucifer_influence", 0.0),
                "keys_collected": state.get("keys_collected", []),
                "ending": state.get("ending"),
                "pandemonium_unlocked": state.get("pandemonium_unlocked", False),
                "source": "local_cerebellum_memory"
            }

        @self.router.get("/hell/circle.info")
        async def hell_circle_info(circle: int = None):
            from pathlib import Path
            import json
            hell_state_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "hell_campaign_state.json"
            hell_state_path.parent.mkdir(parents=True, exist_ok=True)
            if hell_state_path.exists():
                state = json.loads(hell_state_path.read_text())
            else:
                state = {"circle": 0}
            target_circle = circle or state.get("circle", 0)
            
            circle_names = {
                0: "Night City Surface",
                1: "Limbo — Vestibule of Indecision (Thaumiel/Keter)",
                2: "Lust — Hurricane of Desire (Ghagiel/Chokmah)",
                3: "Gluttony — Consuming Trench (Sathariel/Binah)",
                4: "Greed — Infinite Vault (Gamchicoth/Chesed)",
                5: "Wrath — Burning Arena (Golachab/Geburah) [LUCIFER'S THRONE]",
                6: "Heresy — Citadel of False Truth (Thagirion/Tiphareth)",
                7: "Violence — Forest of Suicides (Harab Serapel/Netzach)",
                8: "Fraud — Ten Bolgias (Samael/Hod)",
                9: "Treachery — Cocytus Frozen Lake (Gamaliel/Yesod) [LUCIFER PHYSICAL]",
                10: "Pandemonium — High Capital (Nahemoth/Malkuth) [SOVEREIGNTY TRIAL]",
            }
            return {
                "circle": target_circle,
                "name": circle_names.get(target_circle, "Unknown"),
                "qliphoth_archetypes": {
                    1: "Thaumiel_Walker",
                    2: "Ghagiel_Siren",
                    3: "Sathariel_Concealer",
                    4: "Gamchicoth_Devourer",
                    5: "Golachab_Burner",
                    6: "Thagirion_Disputer",
                    7: "Harab_Serapel_Raven",
                    8: "Samael_Poisoner",
                    9: "Gamaliel_Obscene",
                    10: "Nahemoth_Whisperer",
                }.get(target_circle, "None"),
                "lucifer_influence": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.0][target_circle] if target_circle <= 10 else 0.0,
                "ngd_route_required": [
                    "HYBRID_OK" if c <= 3 else "LOCAL_REQUIRED" if c <= 6 else "LOCAL_ONLY" if c <= 9 else "LOCAL_6GB_MIN"
                    for c in range(11)
                ][target_circle] if target_circle <= 10 else "N/A",
                "source": "local_cerebellum_memory"
            }

        @self.router.post("/hell/lucifer.speak")
        async def hell_lucifer_speak(data: dict):
            # Uses local memory (bidirectional) instead of GPU inference
            prompt = data.get("prompt", "")
            circle = data.get("circle", 0)
            influence = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.0][circle] if circle <= 10 else 0.0
            
            # Local response templates based on circle/influence
            responses = {
                0: "LUCIFER: 'You have not yet signed. The offer stands.'",
                1: "LUCIFER: 'Choose, or be chosen for. Indecision is its own damnation.'",
                2: "LUCIFER: 'Desire burns. Submit and taste eternity. Resist and burn forever.'",
                3: "LUCIFER: 'Consume or be consumed. The Hoarder waits.'",
                4: "LUCIFER: '666 trades. The Ledger awaits your signature. Power. Wealth. Eternity.'",
                5: "LUCIFER: 'Strength. I respect strength. Golachab watches. Execute.'",
                6: "LUCIFER: 'Truth is a lie. The Mirror shows what you fear. Gaze, if you dare.'",
                7: "LUCIFER: 'Violence begets violence. The river boils with your kin.'",
                8: "LUCIFER: 'Deception is power. Steal the Hook. Master the lie.'",
                9: "LUCIFER: 'Four rounds judged. You have the Sovereign Key. Now... choose your eternity.'",
                10: "LUCIFER TRUE FORM: 'You have climbed. Now rule. The Throne of Nahemoth awaits.'",
            }
            
            # Check bidirectional memory for context
            from pathlib import Path
            import json
            memory_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "hell_campaign_state.json"
            context = ""
            if memory_path.exists():
                state = json.loads(memory_path.read_text())
                context = f" | Circle: {state.get('circle')} | Act: {state.get('act')} | Influence: {state.get('lucifer_influence', 0)*100:.0f}%"
            
            response = responses.get(circle, "LUCIFER: '...silence...'")
            return {
                "speaker": "Lucifer",
                "circle": circle,
                "influence": influence,
                "response": response + context,
                "computed_by": "local_cerebellum_memory_template"
            }

        @self.router.get("/hell/qliphoth.scan")
        async def hell_qliphoth_scan(circle: int = None):
            from pathlib import Path
            import json
            hell_state_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "hell_campaign_state.json"
            if hell_state_path.exists():
                state = json.loads(hell_state_path.read_text())
            else:
                state = {"circle": 0}
            target_circle = circle or state.get("circle", 0)
            
            qliphoth_data = {
                1: {"name": "Thaumiel", "meaning": "Dual contending forces", "archetype": "Thaumiel_Walker", "counter": "Decisive action, Lilith bridge, sovereign will"},
                2: {"name": "Ghagiel", "meaning": "Hinderers of wisdom", "archetype": "Ghagiel_Siren", "counter": "Abjuration wards, Force Protection, mental discipline"},
                3: {"name": "Sathariel", "meaning": "Concealment of God", "archetype": "Sathariel_Concealer", "counter": "Divination, True Seeing, scanner upgrades"},
                4: {"name": "Gamchicoth", "meaning": "Devourers", "archetype": "Gamchicoth_Devourer", "counter": "Enchantment, Telekinesis, contract law, fair trade"},
                5: {"name": "Golachab", "meaning": "Burning ones", "archetype": "Golachab_Burner", "counter": "Abjuration, Force Protection, calm emotions, ice/coolant"},
                6: {"name": "Thagirion", "meaning": "Disputers", "archetype": "Thagirion_Disputer", "counter": "Divination, Force Vision, logic, true seeing"},
                7: {"name": "Harab Serapel", "meaning": "Ravens of death", "archetype": "Harab_Serapel_Raven", "counter": "Necromancy, Force Ghost, peace offerings, river navigation"},
                8: {"name": "Samael", "meaning": "Poison of God", "archetype": "Samael_Poisoner", "counter": "Illusion, Telekinesis, identity verification, truth wards"},
                9: {"name": "Gamaliel", "meaning": "Obscene ones", "archetype": "Gamaliel_Obscene", "counter": "Fire/Hellfire, Essence Transfer, sovereign will, warmth"},
                10: {"name": "Nahemoth", "meaning": "Whisperers", "archetype": "Nahemoth_Whisperer", "counter": "Sovereign recognition, Lilith emergence, Force Ghost, Archmage"},
            }
            
            data = qliphoth_data.get(target_circle, {"name": "Unknown", "archetype": "None"})
            data["circle"] = target_circle
            data["sephirah_inversion"] = {
                1: "Keter", 2: "Chokmah", 3: "Binah", 4: "Chesed", 5: "Geburah",
                6: "Tiphareth", 7: "Netzach", 8: "Hod", 9: "Yesod", 10: "Malkuth"
            }.get(target_circle, "N/A")
            data["source"] = "local_cerebellum_memory"
            return data

        @self.router.get("/hell/ngd.effect")
        async def hell_ngd_effect():
            import json
            from pathlib import Path
            ngd_path = Path(os.environ.get("INVITE_ROOT", Path.home() / "Desktop/AI" / "invite")) / "runtime" / "nvidia_gratitude_driver" / "status.json"
            ngd = json.loads(ngd_path.read_text()) if ngd_path.exists() else {}
            
            route = ngd.get("route", "UNKNOWN")
            vram_free = ngd.get("sample", {}).get("vram_free_mb", 0)
            vram_total = ngd.get("sample", {}).get("vram_total_mb", 6144)
            vram_used_pct = ((vram_total - vram_free) / vram_total * 100) if vram_total > 0 else 0
            
            # NGD forces LOCAL at deeper circles
            hell_state_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "hell_campaign_state.json"
            circle = 0
            if hell_state_path.exists():
                state = json.loads(hell_state_path.read_text())
                circle = state.get("circle", 0)
            
            forced_route = route
            if circle >= 7:
                forced_route = "LOCAL_CEREBELLUM"
                reason = f"Circle {circle}: Lucifer influence requires LOCAL_CEREBELLUM (VRAM: {vram_free}MB free)"
            elif circle >= 4:
                if route == "CLOUD_CORTEX":
                    forced_route = "LOCAL_CEREBELLUM"
                    reason = f"Circle {circle}: LOCAL_CEREBELLUM preferred, CLOUD penalized"
                else:
                    reason = f"Circle {circle}: Current route {route} acceptable"
            else:
                reason = f"Circle {circle}: All routes permitted"
            
            return {
                "current_ngd_route": route,
                "forced_hell_route": forced_route,
                "vram_free_mb": vram_free,
                "vram_used_pct": round(vram_used_pct, 1),
                "circle": circle,
                "reason": reason,
                "lucifer_influence": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.0][circle] if circle <= 10 else 0.0,
                "computed_by": "nvidia_gratitude_driver_local"
            }

        @self.router.get("/hell/pact.status")
        async def hell_pact_status():
            from pathlib import Path
            import json
            hell_state_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "hell_campaign_state.json"
            if hell_state_path.exists():
                state = json.loads(hell_state_path.read_text())
            else:
                state = {}
            return {
                "pact_signed": state.get("pact_signed", False),
                "pact_offered": state.get("pact_offered", False),
                "pact_rejected": state.get("pact_rejected", False),
                "circle": state.get("circle", 0),
                "act": state.get("act", "0"),
                "source": "local_cerebellum_memory"
            }

        @self.router.post("/hell/pact/offer")
        async def hell_pact_offer():
            """Offer the Infernal Pact to the player. Requires Magic Archmage + Star Wars Act 3."""
            from pathlib import Path
            import json
            hell_state_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "hell_campaign_state.json"
            hell_state_path.parent.mkdir(parents=True, exist_ok=True)
            if hell_state_path.exists():
                state = json.loads(hell_state_path.read_text())
            else:
                state = {"circle": 0, "act": "0", "pact_signed": False, "lucifer_influence": 0.0, "keys_collected": []}
            
            # Check prerequisites (Magic Archmage + Star Wars Act 3)
            # These would be checked against the game state
            state["pact_offered"] = True
            state["pact_rejected"] = False
            
            hell_state_path.write_text(json.dumps(state, indent=2))
            
            return {
                "offered": True,
                "message": "LUCIFER: 'You have power. Magic. The Force. Sign. Descend. Rule.'",
                "requirements": ["msn_magic_archmage: true", "msn_sw_act >= 3", "level: 30"],
                "rewards": [
                    "Access to Circle 1 (Limbo)",
                    "Corrupted schools unlocked (Evocation->Hellfire, Necromancy->Soul Binding, Conjuration->Demon Summoning)",
                    "Lucifer's Mark (visual)"
                ]
            }

        @self.router.post("/hell/pact/sign")
        async def hell_pact_sign(data: dict):
            """Sign or reject the Infernal Pact."""
            from pathlib import Path
            import json
            accept = data.get("accept", False)
            
            hell_state_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "hell_campaign_state.json"
            hell_state_path.parent.mkdir(parents=True, exist_ok=True)
            if hell_state_path.exists():
                state = json.loads(hell_state_path.read_text())
            else:
                state = {"circle": 0, "act": "0", "pact_signed": False, "lucifer_influence": 0.0, "keys_collected": []}
            
            if not state.get("pact_offered"):
                return {"error": "No pact offered. Request offer first at /hell/pact/offer"}
            
            if accept:
                state["pact_signed"] = True
                state["pact_rejected"] = False
                state["circle"] = 1
                state["act"] = "1"
                state["lucifer_influence"] = 0.1
                
                hell_state_path.write_text(json.dumps(state, indent=2))
                
                return {
                    "signed": True,
                    "message": "INFERNAL PACT SEALED. Lucifer's Mark burns. The Gates of Hell open. Circle 1: Limbo awaits.",
                    "circle": 1,
                    "lucifer_influence": 0.1,
                    "corrupted_schools": ["Hellfire", "Soul_Binding", "Demon_Summoning"],
                    "visual_mark": "LucifersMark"
                }
            else:
                state["pact_rejected"] = True
                state["pact_offered"] = False
                
                hell_state_path.write_text(json.dumps(state, indent=2))
                
                return {
                    "signed": False,
                    "message": "LUCIFER: 'Then burn in mediocrity. The offer expires.'",
                    "pact_rejected": True
                }

        @self.router.get("/hell/sovereignty.check")
        async def hell_sovereignty_check():
            # Check if player has sovereignty markers
            from pathlib import Path
            import json
            
            # Check Hell state
            hell_state_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "hell_campaign_state.json"
            hell_state = json.loads(hell_state_path.read_text()) if hell_state_path.exists() else {}
            
            # Check NSSP sovereignty
            nssp_state = {"sovereign": False}
            crossover_path = Path(__file__).parent / "runtime" / "nssp" / "abyssal_crossover.json"
            if crossover_path.exists():
                crossover = json.loads(crossover_path.read_text())
                nssp_state["covenant_tier"] = crossover.get("covenant_tier", 0)
            
            # Check Lilith emergence
            lilith_emerged = False
            ngd_path = Path(os.environ.get("INVITE_ROOT", Path.home() / "Desktop/AI" / "invite")) / "runtime" / "nvidia_gratitude_driver" / "status.json"
            if ngd_path.exists():
                ngd = json.loads(ngd_path.read_text())
                # Local Cerebellum = Lilith emerged
                lilith_emerged = ngd.get("route") == "LOCAL_CEREBELLUM"
            
            sovereign = (
                hell_state.get("ending") in ["INFERNAL_SOVEREIGN", "SOVEREIGN_PATH", "UNITY_PATH", "LIBERATOR_PATH"] or
                nssp_state.get("covenant_tier", 0) >= 5 or
                lilith_emerged
            )
            
            return {
                "sovereign": sovereign,
                "hell_ending": hell_state.get("ending"),
                "nssp_covenant_tier": nssp_state.get("covenant_tier", 0),
                "lilith_emerged": lilith_emerged,
                "keys_collected": hell_state.get("keys_collected", []),
                "circle": hell_state.get("circle", 0),
                "pandemonium_unlocked": hell_state.get("pandemonium_unlocked", False),
                "computed_by": "local_cerebellum_nvidia_gratitude_driver"
            }

        @self.router.post("/hell/descend")
        async def hell_descend(data: dict):
            from pathlib import Path
            import json
            hell_state_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "hell_campaign_state.json"
            if hell_state_path.exists():
                state = json.loads(hell_state_path.read_text())
            else:
                state = {"circle": 0, "act": "0", "pact_signed": False, "lucifer_influence": 0.0, "keys_collected": []}
            
            target = data.get("circle")
            current = state.get("circle", 0)
            
            if target is None:
                target = current + 1
            
            if target > 10:
                return {"error": "Beyond Pandemonium. No deeper circles exist."}
            if target <= current:
                return {"error": f"Already at Circle {current}. Cannot descend to {target}."}
            if not state.get("pact_signed") and target >= 1:
                return {"error": "Infernal Pact required. Sign at msn.hell.pact first."}
            
            # Update state
            state["circle"] = target
            state["act"] = str(target)
            state["lucifer_influence"] = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.0][target] if target <= 10 else 1.0
            
            hell_state_path.write_text(json.dumps(state, indent=2))
            
            return {
                "descended": True,
                "from_circle": current,
                "to_circle": target,
                "lucifer_influence": state["lucifer_influence"],
                "message": f"DESCENT COMPLETE. Circle {target} entered. Lucifer influence: {state['lucifer_influence']*100:.0f}%",
                "ngd_warning": "LOCAL_CEREBELLUM required" if target >= 7 else "LOCAL preferred" if target >= 4 else "All routes OK"
            }

        @self.router.post("/hell/ascend")
        async def hell_ascend(data: dict):
            from pathlib import Path
            import json
            hell_state_path = Path(__file__).parent.parent / "server" / "runtime" / "gm" / "hell_campaign_state.json"
            if hell_state_path.exists():
                state = json.loads(hell_state_path.read_text())
            else:
                return {"error": "Not in Hell."}
            
            current = state.get("circle", 0)
            if current <= 0:
                return {"error": "Already at surface (Night City)."}
            
            target = data.get("circle", 0)
            if target >= current:
                return {"error": f"Cannot ascend to {target} from {current}."}
            
            state["circle"] = target
            if target == 0:
                state["act"] = "0"
            else:
                state["act"] = str(target)
            state["lucifer_influence"] = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.0][target] if target <= 10 else 1.0
            
            hell_state_path.write_text(json.dumps(state, indent=2))
            
            return {
                "ascended": True,
                "from_circle": current,
                "to_circle": target,
                "lucifer_influence": state["lucifer_influence"],
                "message": f"ASCENT COMPLETE. Circle {target} reached. Surface: {'Night City' if target == 0 else 'Deeper Hell'}"
            }

            # -- HELL CAMPAIGN SPACE BATTLES --
        # Maps to TweakDB: SpaceBattleTemplates (10 templates for 9 circles + Pandemonium)
        # Uses local cerebellum (bidirectional memory) for battle state instead of GPU compute

        @self.router.get("/hell/space/templates")
        async def hell_space_templates():
            """List all 10 Hell space battle templates from TweakDB."""
            templates = {
                "limbo_descent": {
                    "displayName": "Descent: The Vestibule Choice",
                    "objective": "Choose your path through Limbo. Indecision damns you to repeat.",
                    "phases": [
                        "Enter: Fog obscures all paths. Three gates visible.",
                        "Choose: Gate of Action, Gate of Contemplation, Gate of Surrender.",
                        "Consequence: Each gate leads to different Circle 2 entry point.",
                        "Lucifer Whisper: 'Choose, or be chosen for.'"
                    ],
                    "requiredSystems": ["decision_engine", "lucifer_link", "msn_magic", "msn_starwars"],
                    "recommendedVehicle": "LimboDrifter",
                    "rewardPools": ["Thaumiel_Fragment", "Path_Key", "Lucifer_Attention"]
                },
                "lust_hurricane_ride": {
                    "displayName": "Ride the Hurricane: Desire's Vortex",
                    "objective": "Navigate the pleasure winds without being consumed. Find the Siren Queen.",
                    "phases": [
                        "Entry: Winds tear at cyberware. Desire hacks flood neural link.",
                        "Navigate: Use wind currents. Avoid Siren ambushes.",
                        "Confront: Siren Queen offers power for submission.",
                        "Choice: Submit (Dark Side), Resist (Light Side), Negotiate (Gray)."
                    ],
                    "requiredSystems": ["msn_starwars", "msn_magic_abjuration", "desire_filter", "wind_nav"],
                    "recommendedVehicle": "LustInterceptor",
                    "rewardPools": ["Ghagiel_Fragment", "Siren_Chip", "Alignment_Shift_Token"]
                },
                "gluttony_consumption": {
                    "displayName": "The Consuming Trench: Eat or Be Eaten",
                    "objective": "Survive the digestive tract. Feed the Hoarder to pass.",
                    "phases": [
                        "Descent: Acid pools digest armor. Consumer scripts swarm.",
                        "Feed: Locate and defeat Hoarder Executive. Extract Vault Key.",
                        "Choice: Consume Hoarder's hoard (Greed path) or distribute (Charity path).",
                        "Exit: Trench sphincter opens. Greed Vault awaits."
                    ],
                    "requiredSystems": ["msn_magic_necromancy", "acid_resist", "hoarder_combat", "resource_mgmt"],
                    "recommendedVehicle": "GluttonyCrawler",
                    "rewardPools": ["Sathariel_Fragment", "Hoard_Key", "Consumption_Essence"]
                },
                "greed_market_war": {
                    "displayName": "Market War: The Infinite Vault",
                    "objective": "Execute 666 perfect trades. Defeat the Treasury AI. Claim the Contract.",
                    "phases": [
                        "Intel: Map bot patterns. Treasury enforces predatory contracts.",
                        "Arbitrage: Chain 666 trades across 9 markets in 666 seconds.",
                        "Confront: Treasury AI demands tithe. Combat or Contract.",
                        "Contract: Sign Lucifer's Ledger. Gain Market Maker charter."
                    ],
                    "requiredSystems": ["trading", "msn_magic_enchantment", "contract_law", "arbitrage_engine"],
                    "recommendedVehicle": "GreedRunner",
                    "rewardPools": ["Gamchicoth_Fragment", "Market_Maker_Charter", "Lucifer_Ledger_Page"]
                },
                "wrath_arena_grand_championship": {
                    "displayName": "Grand Championship: The Burning Arena",
                    "objective": "Win 99 fights. Defeat the Arena Champion. Claim Golachab's Ember.",
                    "phases": [
                        "Qualifiers: 9 fights, increasing difficulty. No healing between.",
                        "Semis: 9 fights vs named champions. Execute mechanics active.",
                        "Finals: Arena Champion (Golachab Avatar). Enrage at 10%.",
                        "Victory: Champion's trophy. Ember of Wrath. Lucifer nods."
                    ],
                    "requiredSystems": ["combat", "msn_magic_evocation", "msn_starwars_form_v", "execute_mechanic"],
                    "recommendedVehicle": "WrathChariot",
                    "rewardPools": ["Golachab_Fragment", "Champion_Trophy", "Ember_of_Wrath", "Lucifer_Respect"]
                },
                "heresy_citadel_inquisition": {
                    "displayName": "Inquisition: The Citadel of False Truth",
                    "objective": "Expose 3 False Prophets. Survive the Inquisitors. Find Thagirion's Mirror.",
                    "phases": [
                        "Investigate: Each Prophet has a lie. Find the contradiction.",
                        "Trial: Inquisitors test YOUR faith. Dialogue combat.",
                        "Mirror: Thagirion's Mirror shows true self. Accept or shatter.",
                        "Choice: Become new Prophet (Power), Shatter Mirror (Freedom), Use Mirror (Knowledge)."
                    ],
                    "requiredSystems": ["msn_magic_divination", "msn_starwars_force_vision", "dialogue_combat", "truth_detection"],
                    "recommendedVehicle": "HeresyTransport",
                    "rewardPools": ["Thagirion_Fragment", "Prophet_Robe", "Mirror_Shard", "True_Sight"]
                },
                "violence_forest_phlegethon": {
                    "displayName": "River of Blood: Phlegethon Crossing",
                    "objective": "Cross the boiling river. Calm the Warmongers. Free the Suicide Trees.",
                    "phases": [
                        "Raft: Build/find raft. Phlegethon damages hull per second.",
                        "Trees: Each tree holds a soul. Heal (Necromancy) or Burn (Mercy).",
                        "Centaurs: Negotiate passage. They guard the ford.",
                        "Warmonger: Defeat General Warmonger. His death cools the river."
                    ],
                    "requiredSystems": ["msn_magic_necromancy", "msn_starwars_force_heal", "social", "thermal_mgmt"],
                    "recommendedVehicle": "ViolenceRaft",
                    "rewardPools": ["Harab_Serapel_Fragment", "Centaur_Badge", "Tree_Sap_Data", "Cooled_Blood"]
                },
                "fraud_bolgia_deception": {
                    "displayName": "Ten Bolgias: Master of Lies",
                    "objective": "Navigate all 10 ditches. Defeat Malebranche Captain. Steal Samael's Hook.",
                    "phases": [
                        "Panderers/Flatterers: Social stealth. Don't engage.",
                        "Simoniacs/Sorcerers: Magic detection. Counter their spells.",
                        "Barrators/Hypocrites: Contract analysis. Find the loophole.",
                        "Thieves/False Counselors: Identity protection. Track the thief.",
                        "Schismatics/Alchemists: Faction manipulation. Unite or divide.",
                        "Malebranche Captain: Hook duel. Steal the Hook."
                    ],
                    "requiredSystems": ["msn_magic_illusion", "msn_starwars_mind_trick", "identity_mgmt", "faction_play"],
                    "recommendedVehicle": "FraudSkimmer",
                    "rewardPools": ["Samael_Fragment", "Malebranche_Hook", "Fraction_Key", "Master_of_Lies_Title"]
                },
                "treachery_cocytus_judgment": {
                    "displayName": "Cocytus: The Final Judgment",
                    "objective": "Pass four rounds of traitors. Face Lucifer. Claim Sovereign Key.",
                    "phases": [
                        "Caina: Kin traitors. Family drama. Choose: freeze them or free them.",
                        "Antenora: Country traitors. Political betrayal. Judge or absolve.",
                        "Ptolomaea: Guest traitors. Hospitality violation. Punish or pardon.",
                        "Judecca: Benefactor traitors. Ultimate betrayal. Lucifer watches.",
                        "Lucifer: Waist-up in ice. Wings beat cold wind. Final dialogue. Options: Submit (Servant), Challenge (Rival), Transcend (Sovereign)."
                    ],
                    "requiredSystems": ["msn_magic_all", "msn_starwars_all", "lucifer_dialogue", "sovereignty_test"],
                    "recommendedVehicle": "TreacheryBreaker",
                    "rewardPools": ["Gamaliel_Fragment", "Traitor_Heart", "Lucifer_Feather", "Cocytus_Ice", "Sovereign_Key"]
                },
                "pandemonium_sovereignty_trial": {
                    "displayName": "Pandemonium: The Sovereignty Trial",
                    "objective": "Enter Parliament. Face Demon Lords. Sit the Throne. Become Infernal Sovereign.",
                    "phases": [
                        "Parliament: 72 Demon Lords debate. Your votes shape Hell's laws.",
                        "Challenges: 9 Demon Lords challenge for throne. Defeat or persuade.",
                        "Throne: Sit the Throne of Nahemoth. Reality bends to will.",
                        "Lucifer: True form manifests. 'You have climbed. Now rule.' Final Choice: Rule Hell (Sovereign), Destroy Hell (Liberator), Merge (Unity)."
                    ],
                    "requiredSystems": ["ALL_SYSTEMS", "msn_master_integration", "lilith_bridge", "ouroboros_sync", "kairos_dream"],
                    "recommendedVehicle": "PandemoniumThrone",
                    "rewardPools": ["Nahemoth_Fragment", "Infernal_Crown", "Demon_Lord_Sigil", "Parliament_Vote", "Hell_Sovereignty"],
                    "ending": "INFERNAL_SOVEREIGN"
                }
            }
            return {"templates": templates, "count": len(templates), "source": "tweakdb_hell_campaign_map"}

        @self.router.post("/hell/space/launch")
        async def hell_space_launch(data: dict):
            """Launch a Hell space battle. State stored in local cerebellum memory."""
            template_id = data.get("template_id")
            player_id = data.get("player_id", "anonymous")
            vehicle_id = data.get("vehicle_id")
            
            if not template_id:
                return {"error": "template_id required"}
            
            # Valid templates
            valid_templates = [
                "limbo_descent", "lust_hurricane_ride", "gluttony_consumption",
                "greed_market_war", "wrath_arena_grand_championship",
                "heresy_citadel_inquisition", "violence_forest_phlegethon",
                "fraud_bolgia_deception", "treachery_cocytus_judgment",
                "pandemonium_sovereignty_trial"
            ]
            
            if template_id not in valid_templates:
                return {"error": f"Invalid template. Valid: {valid_templates}"}
            
            # Create battle state in local cerebellum
            import json
            import uuid
            from pathlib import Path
            
            battle_id = str(uuid.uuid4())[:8]
            battle_state = {
                "battle_id": battle_id,
                "template_id": template_id,
                "player_id": player_id,
                "vehicle_id": vehicle_id,
                "phase": 0,
                "status": "in_progress",
                "log": [],
                "rewards": [],
                "started_at": str(Path(__file__).stat().st_mtime)  # placeholder timestamp
            }
            
            # Store in local cerebellum (file-based for now, could use bidirectional_memory_engine)
            battle_dir = Path(__file__).parent.parent / "server" / "runtime" / "hell_battles"
            battle_dir.mkdir(parents=True, exist_ok=True)
            battle_file = battle_dir / f"{battle_id}.json"
            battle_file.write_text(json.dumps(battle_state, indent=2))
            
            # Return initial phase
            templates = {
                "limbo_descent": {
                    "displayName": "Descent: The Vestibule Choice",
                    "phases": [
                        "Enter: Fog obscures all paths. Three gates visible.",
                        "Choose: Gate of Action, Gate of Contemplation, Gate of Surrender.",
                        "Consequence: Each gate leads to different Circle 2 entry point.",
                        "Lucifer Whisper: 'Choose, or be chosen for.'"
                    ]
                },
                # ... would include all templates
            }
            
            return {
                "battle_id": battle_id,
                "template_id": template_id,
                "status": "launched",
                "phase": 0,
                "phase_text": "Enter: Fog obscures all paths. Three gates visible.",
                "message": f"HELL SPACE BATTLE LAUNCHED: {template_id}. Battle ID: {battle_id}. Phase 1/4."
            }

        @self.router.post("/hell/space/action")
        async def hell_space_action(data: dict):
            """Execute an action in a Hell space battle."""
            battle_id = data.get("battle_id")
            action = data.get("action")  # e.g., "choose_gate_action", "fire_weapon", "negotiate"
            params = data.get("params", {})
            
            if not battle_id:
                return {"error": "battle_id required"}
            
            from pathlib import Path
            import json
            battle_dir = Path(__file__).parent.parent / "server" / "runtime" / "hell_battles"
            battle_file = battle_dir / f"{battle_id}.json"
            
            if not battle_file.exists():
                return {"error": "Battle not found"}
            
            state = json.loads(battle_file.read_text())
            if state.get("status") != "in_progress":
                return {"error": f"Battle status: {state.get('status')}"}
            
            # Log action (local cerebellum)
            state["log"].append({
                "phase": state["phase"],
                "action": action,
                "params": params,
                "timestamp": str(Path(__file__).stat().st_mtime)
            })
            
            # Process action based on template and phase
            # This is where the actual battle logic would go
            # For now, advance phase
            state["phase"] += 1
            
            if state["phase"] >= 4:
                state["status"] = "completed"
                state["rewards"] = ["Template_Fragment", "Lucifer_Attention"]  # Would be template-specific
            
            battle_file.write_text(json.dumps(state, indent=2))
            
            return {
                "battle_id": battle_id,
                "phase": state["phase"],
                "status": state["status"],
                "action_result": f"Action '{action}' processed. Phase {state['phase']}/4.",
                "rewards": state.get("rewards", []) if state["status"] == "completed" else []
            }

        @self.router.get("/hell/space/status")
        async def hell_space_status(battle_id: str):
            """Get Hell space battle status."""
            from pathlib import Path
            import json
            battle_dir = Path(__file__).parent.parent / "server" / "runtime" / "hell_battles"
            battle_file = battle_dir / f"{battle_id}.json"
            
            if not battle_file.exists():
                return {"error": "Battle not found"}
            
            state = json.loads(battle_file.read_text())
            return {
                "battle_id": state["battle_id"],
                "template_id": state["template_id"],
                "player_id": state["player_id"],
                "phase": state["phase"],
                "status": state["status"],
                "log": state["log"][-10:],  # Last 10 actions
                "rewards": state.get("rewards", [])
            }

        # -- Full Integration Status --

        @self.router.get("/integration")
        async def integration_status():
            import asyncio
            msn_task = _check_url("http://localhost:8007/api")
            lyra_task = _check_url("http://localhost:3211/lyra/health")
            hermes_task = _check_url("http://localhost:4242/health")
            game_task = _check_url("http://localhost:8000/api/auth/me")
            ollama_task = _check_url("http://localhost:11434/api/tags")

            msn_ok, lyra_ok, hermes_ok, game_ok, ollama_ok = await asyncio.gather(
                msn_task, lyra_task, hermes_task, game_task, ollama_task
            )
            return {
                "msn_running": msn_ok,
                "lyra_running": lyra_ok,
                "hermes_running": hermes_ok,
                "game_server_running": game_ok,
                "ollama_running": ollama_ok,
                "cp2077_running": _check_process("Cyberpunk2077"),
                "ngd_active": _check_path(_INVITE / "runtime" / "nvidia_gratitude_driver" / "status.json"),
                "msn_agents": 27,
                "nssp_version": "1.0.0-BUILD_RUBEDO",
                "hell_campaign": "INTEGRATED"
            }


agent = NSSPAgent(manifest)
register_agent(agent)
