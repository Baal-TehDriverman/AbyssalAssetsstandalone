# Living Sin — Game Master System

Biometric-verified Game Master entity with multi-planar summoning and boss combat.

## Architecture

```
Biometric Auth → GM Activation → Living Sin → Boss Combat → Crown Drop
     │                              │              │
  Keystroke                    10 Planes       The Drowned Warden
  Dynamics                      of Existence    (3 phases, 5000 HP)
```

## GM Verification Flow

1. User 1 (Eric) enrolls keystroke biometric via `POST /api/gm/biometric/enroll` (2-3 samples)
2. Each session: type passphrase → `POST /api/gm/biometric/verify`
3. Score > 0.65 = verified → `POST /api/gm/activate`

## Crown of Living Sin — Boss Locked

The Crown is NOT claimable directly. It drops from **The Drowned Warden** — the first boss:

1. GM activates Living Sin (`POST /api/gm/activate`)
2. GM summons the boss (`POST /api/gm/boss/spawn`)
3. Players attack the boss (`POST /api/gm/boss/attack`)
4. Boss has 5000 HP across 3 phases:
   - **Phase 1** (100-50%): The Watcher Awakens — tidal slam (30-60 dmg)
   - **Phase 2** (50-25%): The Depths Stir — abyssal grasp (50-90 dmg)
   - **Phase 3** (25-0%): The Sin's Judgment — crown's wrath (80-150 dmg)
5. On defeat, the Crown of Living Sin is auto-granted to Eric (user 1)
6. Also drops: 5k-15k soul coins, 2500 clout, 5000 XP

## Boss Endpoints

| Endpoint | Auth | Description |
|----------|------|-------------|
| `POST /api/gm/boss/spawn` | GM only | Summon The Drowned Warden |
| `POST /api/gm/boss/attack` | Any user | Deal damage, boss counter-attacks |
| `GET /api/gm/boss/status` | Public | List active bosses |
| `GET /api/gm/boss/{boss_id}` | Public | Detailed boss state |

## GM Powers

| Power | Endpoint | Description |
|-------|----------|-------------|
| Attack | `POST /api/gm/attack` | Deal 10-100 damage to any player |
| Summon | `POST /api/gm/summon` | Pull being from any plane |
| Banish | `POST /api/gm/banish` | Send entity back |
| Command | `POST /api/gm/command` | Direct summoned entity |
| Message | `POST /api/gm/message` | Broadcast to all players via WebSocket |

## 10 Planes of Existence

| Plane | Danger | Beings |
|-------|--------|--------|
| Material | 1 | human, animal, elemental, construct |
| Astral | 3 | astral_spirit, thought_form, dream_walker, psychic_sliver |
| Infernal | 7 | lesser_devil, pit_fiend, arch_devil, fallen_angel |
| Celestial | 8 | angel, archangel, seraphim, emissary |
| Abyssal | 9 | chaos_spawn, void_tendril, abyssal_horror, old_one |
| Primordial | 10 | primordial_essence, first_thought, unmade, potentiality |
| Elder | 10 | elder_thing, outer_god, blind_idiot, azure_wisdom |
| Mythic | 6 | mythic_avatar, living_legend, archetype, narrative_force |
| Digital | 4 | ai_spirit, data_wraith, protocol_angel, virus_daemon |
| Occult | 5 | gate_guardian, secret_keeper, ritual_master, hidden_one |

## Client Rendering

- **Non-GM players**: Living Sin = non-hostile NPC (`npc: true, hostile: false`)
- **GM player**: Living Sin = controllable PC with full interface
- Summoned entities + bosses visible to all in the zone
- Living Sin cannot be targeted by any non-GM player
- Crown of Living Sin: renders with `crimson_corona` particles and `living_sin_glow` shader
