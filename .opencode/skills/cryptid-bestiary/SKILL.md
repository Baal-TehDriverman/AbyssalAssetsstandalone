---
name: cryptid-bestiary
description: Use when designing or implementing monsters, drop tables, boss mechanics, spawning, or the 7-tier cryptid ecosystem. Types defined in shared/types/monsters.ts (621 lines). 6 monsters defined, 24+ more needed.
---

# Cryptid Bestiary

## Monster Tier System (shared/types/monsters.ts)

| Tier | Drop Rate | Rarity Weights | Example |
|------|-----------|----------------|---------|
| 0 Ambient | 0.1% | Noob 90%, Common 10% | Loch Minnow |
| 1 Common | 5% | Common 70%, Uncommon 30% | Loch Trout |
| 2 Uncommon | 15% | Uncommon 70%, Rare 20%, Epic 10% | Giant Pike |
| 3 Rare | 30% | Rare 60%, Epic 30%, Legendary 10% | Abyssal Anglerfish |
| 4 Epic | 50% | Epic 60%, Legendary 30%, Mythic 10% | Kraken Matriarch |
| 5 Legendary | 75% | Legendary 70%, Mythic 30% | Nessie (Adult) |
| 6 Mythic | 100% | Mythic 100% | Lilith (True Form) |

## Currently Defined Monsters
| ID | Tier | Health | Zone | Special |
|----|------|--------|------|---------|
| loch_minnow | ambient | 10 | shallows | Passive, 100 population |
| loch_trout | common | 150 | shallows/standard | Dash attack mechanic |
| giant_pike | uncommon | 800 | standard/deep | Ambush strike + tail whip |
| abyssal_anglerfish | rare | 3000 | deep/abyssal | Hypnotic lure + ink cloud |
| kraken_matriarch | epic | 500K | trench | 4 phases, weekly boss |
| nessie_adult | legendary | 2M | trench | Monthly world boss |
| lilith_true | mythic | 50M | throne_room | Yearly, Sephirotic Court |

## Drop Rate Formula (from GDD.md line 206)
```
BaseDropRate = MonsterTier * 0.05
RarityRoll = Random(0, 1)
EffectiveRarity = clamp(RarityRoll * (1 - PlayerLuck/100) * MonsterRarityModifier, 0, 1)
```

## Hat Drop Table Per Monster
- 70% — Zone-appropriate Common/Uncommon
- 20% — Zone-appropriate Rare
- 8% — Zone-appropriate Epic
- 1.8% — Zone-appropriate Legendary
- 0.2% — Any Legendary from any zone
- 0.02% — Any Mythic (if eligible)
- 0.0001% — Unique Mythic (1/1 world drop)

## Monster Interfaces (monsters.ts)
Key interfaces: Monster, MonsterStats, MonsterAI, MonsterLootTable, MonsterDrop, MonsterMechanic, SpawnCondition, LevelScaling. Use MONSTER_DEFINITIONS record for adding new monsters.

## Adding a New Monster
1. Add entry to `MONSTER_DEFINITIONS` in `shared/types/monsters.ts`
2. Fill all required fields: stats, AI, loot_table, spawn config, visual, audio, lore
3. Add hat drops to server seed data in `server/main.py` if new hats needed
4. Create sprite/animation assets in client (or use placeholder)
5. Register in bestiary system
