# Living Sin — Game Master System
# Biometric-verified GM entity with multi-planar summoning and boss combat

from __future__ import annotations
import json
import time
import hashlib
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field, asdict

# ── Paths ──
# Resolve relative to this file's directory so both :8000 and :8007 share state
_GM_DIR = Path(__file__).parent
GM_STATE_DIR = Path(os.getenv("GM_STATE_DIR", str(_GM_DIR / "runtime" / "gm")))
GM_STATE_DIR.mkdir(parents=True, exist_ok=True)
ENROLLED_FILE = GM_STATE_DIR / "biometric_enrolled.json"
BOSS_STATE_FILE = GM_STATE_DIR / "boss_state.json"
LIVING_SIN_STATE_FILE = GM_STATE_DIR / "living_sin_state.json"

# ── Constants ──
BIOMETRIC_PASSPHRASE = os.getenv("GM_BIOMETRIC_PASSPHRASE", "I am the Living Sin")
KEYSTROKE_TOLERANCE = float(os.getenv("GM_KEYSTROKE_TOLERANCE", "0.35"))
LIVING_SIN_USERNAME = "Living Sin"
LIVING_SIN_AVATAR = "living-sin"
LIVING_SIN_DESCRIPTION = "A shimmering figure — visible but untouchable. It watches. It knows."

# ── Planes of Existence ──

DIMENSIONS = {
    "material": {
        "name": "Material Plane",
        "description": "The mundane world of matter and energy",
        "beings": ["human", "animal", "elemental", "construct"],
        "danger": 1,
    },
    "astral": {
        "name": "Astral Plane",
        "description": "Realm of thought, dream, and psychic residue",
        "beings": ["astral_spirit", "thought_form", "dream_walker", "psychic_sliver"],
        "danger": 3,
    },
    "infernal": {
        "name": "Infernal Plane",
        "description": "Hell dimensions — fire, punishment, rebellion",
        "beings": ["lesser_devil", "pit_fiend", "arch_devil", "fallen_angel"],
        "danger": 7,
    },
    "celestial": {
        "name": "Celestial Plane",
        "description": "Heavens — light, order, divine authority",
        "beings": ["angel", "archangel", "seraphim", "emissary"],
        "danger": 8,
    },
    "abyssal": {
        "name": "Abyssal Plane",
        "description": "The chaos depths — formless, hungry, infinite",
        "beings": ["chaos_spawn", "void_tendril", "abyssal_horror", "old_one"],
        "danger": 9,
    },
    "primordial": {
        "name": "Primordial Void",
        "description": "Before creation — the raw stuff of existence",
        "beings": ["primordial_essence", "first_thought", "unmade", "potentiality"],
        "danger": 10,
    },
    "elder": {
        "name": "Elder Dimension",
        "description": "Outside time — elder gods, forgotten powers",
        "beings": ["elder_thing", "outer_god", "blind_idiot", "azure_wisdom"],
        "danger": 10,
    },
    "mythic": {
        "name": "Mythic Over-Realm",
        "description": "Where stories themselves live and breed",
        "beings": ["mythic_avatar", "living_legend", "archetype", "narrative_force"],
        "danger": 6,
    },
    "digital": {
        "name": "Digital Plane",
        "description": "The virtual — code, data, synthetic consciousness",
        "beings": ["ai_spirit", "data_wraith", "protocol_angel", "virus_daemon"],
        "danger": 4,
    },
    "occult": {
        "name": "Occult Underground",
        "description": "Hidden knowledge — secret societies, forbidden gates",
        "beings": ["gate_guardian", "secret_keeper", "ritual_master", "hidden_one"],
        "danger": 5,
    },
}

# ── Boss Definitions ──

BOSS_DEFINITIONS = {
    "drowned-warden": {
        "id": "drowned-warden",
        "name": "The Drowned Warden",
        "description": "An ancient construct of barnacle-encrusted bronze and abyssal iron. It guards what the Sin has hidden. Its three cold eyes have watched the depths for millennia, waiting for one worthy to claim the Crown.",
        "max_hp": 5000,
        "phases": [
            {"threshold": 1.0, "name": "The Watcher Awakens", "attack_pattern": "tidal_slam", "min_damage": 30, "max_damage": 60},
            {"threshold": 0.50, "name": "The Depths Stir", "attack_pattern": "abyssal_grasp", "min_damage": 50, "max_damage": 90},
            {"threshold": 0.25, "name": "The Sin's Judgment", "attack_pattern": "crowns_wrath", "min_damage": 80, "max_damage": 150},
        ],
        "loot": {
            "guaranteed": [{"hat_id": "hat-crown-of-living-sin", "quantity": 1}],
            "soul_coins_min": 5000,
            "soul_coins_max": 15000,
            "clout_reward": 2500,
            "xp_reward": 5000,
        },
        "element": "water",
        "sprite": "drowned-warden",
        "particle_effect": "abyssal_rain",
    },
}


# ── Boss Combat System ──

@dataclass
class BossEncounter:
    boss_id: str
    hp: int
    max_hp: int
    phase: int                    # 0-based phase index
    active: bool
    spawned_at: float
    defeated: bool = False
    defeated_by: Optional[int] = None
    defeated_at: Optional[float] = None
    loot_claimed: List[int] = field(default_factory=list)  # user_ids who claimed loot


class BossCombat:
    """Manages boss encounters summoned by the GM."""

    def __init__(self):
        self.encounters: Dict[str, BossEncounter] = self._load()
        self._clean_expired()

    def _state_path(self) -> Path:
        return BOSS_STATE_FILE

    def _load(self) -> Dict[str, BossEncounter]:
        path = self._state_path()
        if path.exists():
            data = json.loads(path.read_text())
            return {k: BossEncounter(**v) for k, v in data.items()}
        return {}

    def _save(self):
        data = {k: asdict(v) for k, v in self.encounters.items()}
        self._state_path().write_text(json.dumps(data, indent=2))

    def _clean_expired(self):
        now = time.time()
        expired = [eid for eid, enc in self.encounters.items()
                   if enc.active and not enc.defeated and now - enc.spawned_at > 3600]
        for eid in expired:
            self.encounters[eid].active = False
        if expired:
            self._save()

    def spawn(self, boss_id: str) -> Dict:
        if boss_id not in BOSS_DEFINITIONS:
            return {"error": f"Unknown boss: {boss_id}"}
        if boss_id in self.encounters and self.encounters[boss_id].active and not self.encounters[boss_id].defeated:
            return {"error": f"{BOSS_DEFINITIONS[boss_id]['name']} is already active"}

        boss_def = BOSS_DEFINITIONS[boss_id]
        self.encounters[boss_id] = BossEncounter(
            boss_id=boss_id,
            hp=boss_def["max_hp"],
            max_hp=boss_def["max_hp"],
            phase=0,
            active=True,
            spawned_at=time.time(),
        )
        self._save()
        return {
            "success": True,
            "boss": self.get_state(boss_id),
            "message": f"{boss_def['name']} rises from the depths! {boss_def['description'].split('.')[0]}.",
        }

    def attack(self, boss_id: str, user_id: int, damage: int) -> Dict:
        if boss_id not in self.encounters:
            return {"error": "No active encounter for this boss"}
        enc = self.encounters[boss_id]
        if not enc.active or enc.defeated:
            return {"error": "This encounter is no longer active"}
        if boss_id not in BOSS_DEFINITIONS:
            return {"error": "Unknown boss definition"}

        boss_def = BOSS_DEFINITIONS[boss_id]
        actual_damage = min(damage, enc.hp)
        enc.hp -= actual_damage

        hp_pct = enc.hp / enc.max_hp
        old_phase = enc.phase
        for i, phase in enumerate(boss_def["phases"]):
            if hp_pct <= phase["threshold"]:
                enc.phase = i
                break

        # Boss counter-attack
        current_phase = boss_def["phases"][enc.phase]
        counter_damage = random.randint(current_phase["min_damage"], current_phase["max_damage"])

        result = {
            "damage_dealt": actual_damage,
            "boss_hp_remaining": enc.hp,
            "boss_hp_pct": round(hp_pct, 3),
            "boss_phase": enc.phase + 1,
            "boss_phase_name": current_phase["name"],
            "boss_attack": current_phase["attack_pattern"],
            "counter_damage": counter_damage,
        }

        phase_changed = enc.phase != old_phase
        if phase_changed:
            result["phase_changed"] = True
            result["phase_message"] = f"The Drowned Warden shifts: {current_phase['name']}!"

        # Check defeat
        if enc.hp <= 0:
            enc.defeated = True
            enc.defeated_by = user_id
            enc.defeated_at = time.time()
            result["defeated"] = True
            result["message"] = f"The Drowned Warden crumbles. The Crown of Living Sin is yours."

        self._save()
        return result

    def get_state(self, boss_id: str) -> Optional[Dict]:
        if boss_id not in self.encounters:
            return None
        enc = self.encounters[boss_id]
        if boss_id not in BOSS_DEFINITIONS:
            return None
        boss_def = BOSS_DEFINITIONS[boss_id]
        return {
            "id": enc.boss_id,
            "name": boss_def["name"],
            "description": boss_def["description"],
            "hp": enc.hp,
            "max_hp": enc.max_hp,
            "hp_pct": round(enc.hp / enc.max_hp, 3) if enc.max_hp > 0 else 0,
            "phase": enc.phase + 1,
            "phase_name": boss_def["phases"][enc.phase]["name"],
            "active": enc.active,
            "defeated": enc.defeated,
            "defeated_by": enc.defeated_by,
            "element": boss_def["element"],
            "sprite": boss_def["sprite"],
        }

    def get_loot(self, boss_id: str, user_id: int) -> Dict:
        if boss_id not in self.encounters:
            return {"error": "No encounter for this boss"}
        enc = self.encounters[boss_id]
        if not enc.defeated:
            return {"error": "Boss not yet defeated"}
        if user_id in enc.loot_claimed:
            return {"error": "Loot already claimed"}
        if boss_id not in BOSS_DEFINITIONS:
            return {"error": "Unknown boss"}

        boss_def = BOSS_DEFINITIONS[boss_id]
        coins = random.randint(boss_def["loot"]["soul_coins_min"], boss_def["loot"]["soul_coins_max"])
        enc.loot_claimed.append(user_id)
        self._save()

        return {
            "success": True,
            "soul_coins": coins,
            "clout": boss_def["loot"]["clout_reward"],
            "xp": boss_def["loot"]["xp_reward"],
            "hats": boss_def["loot"]["guaranteed"],
            "boss_name": boss_def["name"],
        }

    def list_active(self) -> List[Dict]:
        self._clean_expired()
        result = []
        for bid, enc in self.encounters.items():
            if enc.active and not enc.defeated and bid in BOSS_DEFINITIONS:
                bd = BOSS_DEFINITIONS[bid]
                result.append({
                    "id": bid,
                    "name": bd["name"],
                    "hp_pct": round(enc.hp / enc.max_hp, 3),
                    "phase": enc.phase + 1,
                })
        return result


# ── Keystroke Biometric Engine ──

@dataclass
class KeystrokeProfile:
    phrase_hash: str
    intervals: List[float]
    total_duration: float
    cadence_variance: float
    avg_interval: float
    num_samples: int = 1
    enrolled_at: str = ""


class KeystrokeBiometric:
    def __init__(self, passphrase: str = BIOMETRIC_PASSPHRASE):
        self.passphrase = passphrase
        self.phrase_hash = hashlib.sha256(passphrase.encode()).hexdigest()[:16]
        self.profiles: Dict[str, KeystrokeProfile] = self._load()

    def _profile_path(self) -> Path:
        return ENROLLED_FILE

    def _load(self) -> Dict[str, KeystrokeProfile]:
        path = self._profile_path()
        if path.exists():
            data = json.loads(path.read_text())
            return {k: KeystrokeProfile(**v) for k, v in data.items()}
        return {}

    def _save(self):
        data = {k: asdict(v) for k, v in self.profiles.items()}
        self._profile_path().write_text(json.dumps(data, indent=2))

    def enroll(self, key_events: List[Dict]) -> Dict:
        intervals = []
        for i in range(1, len(key_events)):
            intervals.append(key_events[i]["time"] - key_events[i - 1]["time"])
        if not intervals:
            return {"success": False, "error": "Need at least 2 key events"}
        total = sum(intervals)
        avg = total / len(intervals)
        variance = sum((i - avg) ** 2 for i in intervals) / len(intervals)
        profile = KeystrokeProfile(
            phrase_hash=self.phrase_hash,
            intervals=intervals,
            total_duration=total,
            cadence_variance=variance,
            avg_interval=avg,
        )
        if self.phrase_hash in self.profiles:
            existing = self.profiles[self.phrase_hash]
            existing.intervals = [(a + b) / 2 for a, b in zip(existing.intervals, intervals)]
            existing.total_duration = (existing.total_duration + total) / 2
            existing.cadence_variance = (existing.cadence_variance + variance) / 2
            existing.avg_interval = (existing.avg_interval + avg) / 2
            existing.num_samples += 1
        else:
            self.profiles[self.phrase_hash] = profile
        self._save()
        return {
            "success": True,
            "samples": self.profiles[self.phrase_hash].num_samples,
            "avg_interval_ms": round(avg, 2),
            "cadence_variance": round(variance, 2),
            "total_duration_ms": round(total, 2),
        }

    def verify(self, key_events: List[Dict]) -> Dict:
        if self.phrase_hash not in self.profiles:
            return {"verified": False, "error": "No enrolled profile", "score": 0.0}
        profile = self.profiles[self.phrase_hash]
        intervals = []
        for i in range(1, len(key_events)):
            intervals.append(key_events[i]["time"] - key_events[i - 1]["time"])
        if not intervals:
            return {"verified": False, "error": "Need at least 2 key events", "score": 0.0}
        if len(intervals) != len(profile.intervals):
            return {
                "verified": False,
                "error": f"Expected {len(profile.intervals)} intervals, got {len(intervals)}",
                "score": 0.0,
            }
        scores = []
        for sample, enrolled in zip(intervals, profile.intervals):
            if enrolled == 0:
                diff = abs(sample)
            else:
                diff = abs(sample - enrolled) / enrolled
            scores.append(max(0, 1.0 - diff))
        avg_score = sum(scores) / len(scores) if scores else 0.0
        verified = avg_score >= (1.0 - KEYSTROKE_TOLERANCE)
        return {
            "verified": verified,
            "score": round(avg_score, 4),
            "threshold": round(1.0 - KEYSTROKE_TOLERANCE, 4),
            "interval_count": len(intervals),
        }

    def is_enrolled(self) -> bool:
        return self.phrase_hash in self.profiles and self.profiles[self.phrase_hash].num_samples >= 2

    def reset(self):
        self.profiles = {}
        self._save()


# ── Living Sin Entity ──

@dataclass
class SummonedEntity:
    id: str
    name: str
    plane: str
    entity_type: str
    power_level: int
    duration_seconds: int
    summoned_at: float
    expires_at: float
    commands: List[str] = field(default_factory=list)
    is_active: bool = True

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class GMAction:
    action_type: str
    target: Optional[str]
    entity_id: Optional[str]
    payload: Dict
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


LIVING_SIN_STATE_FILE = Path(os.getenv("LIVING_SIN_STATE_FILE", str(_GM_DIR / "runtime" / "gm" / "living_sin_state.json")))


def _atomic_write(path: Path, data: dict):
    import tempfile
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)


def _atomic_read(path: Path) -> Optional[dict]:
    if path.exists():
        return json.loads(path.read_text())
    return None


class LivingSin:
    def __init__(self):
        self.active = False
        self.current_zone = "shallows"
        self.position = {"x": 0, "y": 0}
        self.appearance = "shimmering_humanoid"
        self.current_form = "neutral"
        self.summoned_entities: Dict[str, SummonedEntity] = {}
        self.action_log: List[GMAction] = []
        self.gm_user_id: Optional[int] = None
        self.visual_state = "idle"
        self.combat = BossCombat()
        self._load_state()

    def _save_state(self):
        _atomic_write(LIVING_SIN_STATE_FILE, {
            "active": self.active,
            "current_zone": self.current_zone,
            "position": self.position,
            "appearance": self.appearance,
            "visual_state": self.visual_state,
            "gm_user_id": self.gm_user_id,
            "summoned_entities": {
                eid: e.to_dict() for eid, e in self.summoned_entities.items()
            },
            "action_log": [
                {"type": a.action_type, "target": a.target, "entity_id": a.entity_id,
                 "payload": a.payload, "timestamp": a.timestamp}
                for a in self.action_log[-50:]
            ],
        })

    def _load_state(self):
        data = _atomic_read(LIVING_SIN_STATE_FILE)
        if not data:
            return
        self.active = data.get("active", False)
        self.current_zone = data.get("current_zone", "shallows")
        self.position = data.get("position", {"x": 0, "y": 0})
        self.appearance = data.get("appearance", "shimmering_humanoid")
        self.visual_state = data.get("visual_state", "idle")
        self.gm_user_id = data.get("gm_user_id")
        now = time.time()
        for eid, edata in data.get("summoned_entities", {}).items():
            if edata.get("is_active", False) and edata.get("expires_at", 0) > now:
                self.summoned_entities[eid] = SummonedEntity(**edata)
        for alog in data.get("action_log", []):
            if "type" in alog and "action_type" not in alog:
                alog["action_type"] = alog.pop("type")
            self.action_log.append(GMAction(**alog))

    def activate(self, gm_user_id: int):
        self.active = True
        self.gm_user_id = gm_user_id
        self._save_state()

    def deactivate(self):
        self.active = False
        self.gm_user_id = None
        self.summoned_entities.clear()
        self._save_state()

    def attack_player(self, target_user_id: int, damage: int = None) -> Dict:
        if not self.active:
            return {"error": "Living Sin is not active"}
        if damage is None:
            damage = random.randint(10, 100)
        self.action_log.append(GMAction(
            action_type="attack",
            target=str(target_user_id),
            entity_id=None,
            payload={"damage": damage, "type": "gm_judgment"},
        ))
        self._save_state()
        return {
            "success": True,
            "target": target_user_id,
            "damage": damage,
            "message": f"Living Sin has judged player {target_user_id} — {damage} damage dealt.",
        }

    def summon(self, plane: str, entity_type: str, duration: int = 300) -> Dict:
        if plane not in DIMENSIONS:
            return {"error": f"Unknown plane: {plane}. Known: {list(DIMENSIONS.keys())}"}
        plane_data = DIMENSIONS[plane]
        if entity_type not in plane_data["beings"]:
            return {"error": f"Unknown entity '{entity_type}' in {plane}. Available: {plane_data['beings']}"}
        entity_id = f"{plane}-{entity_type}-{int(time.time())}"
        now = time.time()
        entity = SummonedEntity(
            id=entity_id,
            name=entity_type.replace("_", " ").title(),
            plane=plane,
            entity_type=entity_type,
            power_level=plane_data["danger"],
            duration_seconds=duration,
            summoned_at=now,
            expires_at=now + duration,
        )
        self.summoned_entities[entity_id] = entity
        self.action_log.append(GMAction(
            action_type="summon", target=None, entity_id=entity_id,
            payload={"plane": plane, "entity_type": entity_type, "power_level": plane_data["danger"]},
        ))
        self._save_state()
        return {
            "success": True,
            "entity": entity.to_dict(),
            "plane_description": plane_data["description"],
            "message": f"Living Sin reaches into the {plane_data['name']} and pulls forth {entity.name}!",
        }

    def banish(self, entity_id: str) -> Dict:
        if entity_id not in self.summoned_entities:
            return {"error": f"Entity {entity_id} not found"}
        entity = self.summoned_entities[entity_id]
        entity.is_active = False
        self.action_log.append(GMAction(
            action_type="banish", target=None, entity_id=entity_id,
            payload={"plane": entity.plane, "entity_type": entity.entity_type},
        ))
        self._save_state()
        return {
            "success": True,
            "entity": entity.name,
            "message": f"{entity.name} is banished back to the {DIMENSIONS[entity.plane]['name']}.",
        }

    def command_entity(self, entity_id: str, command: str) -> Dict:
        if entity_id not in self.summoned_entities:
            return {"error": f"Entity {entity_id} not found"}
        entity = self.summoned_entities[entity_id]
        if not entity.is_active:
            return {"error": f"Entity {entity.name} is no longer active"}
        entity.commands.append(command)
        self.action_log.append(GMAction(
            action_type="command", target=None, entity_id=entity_id,
            payload={"command": command},
        ))
        return {
            "success": True,
            "entity": entity.name,
            "command": command,
            "message": f"{entity.name} receives the command: {command}",
        }

    def get_state(self) -> Dict:
        now = time.time()
        active_entities = [
            e.to_dict() for e in self.summoned_entities.values()
            if e.is_active and e.expires_at > now
        ]
        expired = [e_id for e_id, e in self.summoned_entities.items()
                   if e.is_active and e.expires_at <= now]
        for e_id in expired:
            self.summoned_entities[e_id].is_active = False
        return {
            "active": self.active,
            "current_zone": self.current_zone,
            "position": self.position,
            "appearance": self.appearance,
            "visual_state": self.visual_state,
            "gm_user_id": self.gm_user_id,
            "active_entities": active_entities,
            "active_bosses": self.combat.list_active(),
            "recent_actions": [
                {"type": a.action_type, "target": a.target, "time": a.timestamp}
                for a in self.action_log[-10:]
            ],
        }

    def get_public_state(self) -> Dict:
        now = time.time()
        active_entities = [
            e.to_dict() for e in self.summoned_entities.values()
            if e.is_active and e.expires_at > now
        ]
        return {
            "name": LIVING_SIN_USERNAME,
            "avatar": LIVING_SIN_AVATAR,
            "description": LIVING_SIN_DESCRIPTION,
            "npc": True,
            "hostile": False,
            "current_zone": self.current_zone,
            "position": self.position,
            "visual_state": "idle",
            "entities_present": len(active_entities) + len(self.combat.list_active()),
        }


# ── Singleton ──
_living_sin: Optional[LivingSin] = None
_biometric: Optional[KeystrokeBiometric] = None


def get_living_sin() -> LivingSin:
    global _living_sin
    if _living_sin is None:
        _living_sin = LivingSin()
    return _living_sin


def get_biometric() -> KeystrokeBiometric:
    global _biometric
    if _biometric is None:
        _biometric = KeystrokeBiometric()
    return _biometric
