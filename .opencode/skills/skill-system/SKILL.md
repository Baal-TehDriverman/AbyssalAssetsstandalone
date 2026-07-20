---
name: skill-system
description: Use when working on the 24-skill progression system. Types in shared/types/skills.ts (635 lines). Covers XP curves (1.15^level), skill synergies, specializations, and unlocks for all 6 categories.
---

# Skill System — The Abyssal Arts

## 24 Skills Across 6 Categories

### Gathering (5)
- **Dredging** — Sonar extraction, XP:100, curve:1.15 — synergy: Sonar Tuning +15% XP
- **Salvaging** — Wreck recovery, XP:120, curve:1.14 — synergy: Salvage Processing +20%
- **Foraging** — Flora harvest, XP:90, curve:1.16 — synergy: Fiber Working +20%
- **Hunting** — Cryptid tracking, XP:150, curve:1.13 — synergy: Lore +25% drop rate
- **Navigation** — Charting, XP:80, curve:1.17 — synergy: Dredging +10%

### Processing (4)
- Salvage Processing, Fiber Working, Bone Carving, Metallurgy

### Crafting (5)
- **Haberdashery** — Hat construction, 2 specializations (Master Hatter)
- Enchanting, Alchemy, Runecrafting, Masterwork

### Knowledge (4)
- Lore, Sonar Tuning, Scholarship (+ Navigation from gathering)

### Social/Economic (3)
- Trading, Negotiation, Guild Management

### Combat/Survival (3)
- Evasion, Harpooning, Survival

## XP Curve
```
xp_for_level(n) = base_xp * (1.15 ^ (n-1))
total_xp_for_level(99) = base_xp * (1.15^99 - 1) / (1.15 - 1)
```

## Skill Synergies
Synergies defined in SKILL_DEFAULTS record. Key pattern:
```typescript
{ skill_id: 'sonar_tuning', bonus_type: 'xp_boost', value: 15, condition: 'both_above_50' }
```
Bonus types: xp_boost, drop_rate, success_rate, speed, quality, efficiency, fee_reduction, discovery.

## Specializations
Only Dredging (Deep Delver / Sonar Savant), Hunting (Cryptid Tracker / Trophy Collector), and Haberdashery (Master Hatter) have specialization branches defined. 21 more skills need specialization design.

## Skill Progress
```typescript
interface SkillProgress {
  skill_id: SkillId; level: number; xp: number;
  virtual_level: number; virtual_xp: number; total_xp: number;
}
```

## Adding Skills
1. Add `SkillId` to the union type
2. Add entry to `SKILL_DEFAULTS` with all fields
3. Add to `ALL_SKILL_IDS` and `SKILLS_BY_CATEGORY`
4. Create server model and API routes for XP tracking
