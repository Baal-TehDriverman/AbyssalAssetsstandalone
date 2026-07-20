# ABYSSAL ASSETS — GAME DESIGN DOCUMENT
## "RuneScape but Actually Alchemical" — Cryptid Hat Trading Simulator

---

## PROJECT OVERVIEW

**Title:** Abyssal Assets
**Subtitle:** The Loch Exchange
**Genre:** Multiplayer Cryptid Hat Trading Simulator / MMO-lite
**Core Loop:** Dredge → Hunt → Craft → Quest → Trade → Ascend
**Platform:** Web-based (HTML5 Canvas + WebGL) with Python/FastAPI backend
**Art Direction:** Retro-modern pixel art (16-bit aesthetic) with modern lighting/post-processing
**Target:** Browser-based, no install, mobile-friendly responsive design

---

## TECH STACK

### Frontend
- **Engine:** Phaser 3 (TypeScript) — battle-tested for 2D MMOs
- **Rendering:** WebGL with Canvas fallback
- **UI:** Custom Phaser UI + Overlay HTML/CSS for trading panels
- **Networking:** WebSocket (Socket.io client) for real-time trading/chat
- **State:** Phaser Scenes + Custom state management

### Backend
- **API:** FastAPI (Python 3.11+) — integrates with existing MSN infrastructure
- **Real-time:** Socket.io / WebSockets for trading, chat, world events
- **Database:** PostgreSQL (production) / SQLite (dev) with SQLAlchemy
- **Cache:** Redis for session management, market cache, rate limiting
- **Auth:** JWT + optional Web3 wallet connect (for item ownership)

### Infrastructure (MSN Integration)
- **Deployment:** NSSM service on Windows / systemd on Linux
- **Monitoring:** Prometheus + Grafana (existing MSN stack)
- **Logging:** Structured JSON → Loki/ELK
- **CI/CD:** GitHub Actions → NSSM restart

---

## ART DIRECTION: "RETRO-MODERN PIXEL NOIR"

### Visual Pillars
| Pillar | Description |
|--------|-------------|
| **16-bit Soul** | 32x32 base tiles, 64x64 character sprites, 128x128 UI icons |
| **Modern Lighting** | Normal maps on pixel art, bloom on rare items, water caustics shader |
| **Atmosphere** | Perpetual twilight Loch, volumetric fog, particle systems (mist, bubbles) |
| **Palette** | Limited 256-color base + HDR accents for rarity tiers |

### Rarity Visual Language
| Tier | Color Scheme | Special Effects |
|------|--------------|-----------------|
| **Noob (Grey)** | Desaturated, muddy | None |
| **Common (White)** | Clean, readable | Subtle glow |
| **Uncommon (Green)** | Emerald accents | Gentle pulse |
| **Rare (Blue)** | Azure/sapphire | Particle trail |
| **Epic (Purple)** | Amethyst, iridescent | Screen-space bloom |
| **Legendary (Gold/Orange)** | Gold, prismatic | Full bloom + screen shake on equip |
| **Mythic (Cosmic)** | Shifting aurora | Custom shader, reality distortion |

---

## CORE SYSTEMS ARCHITECTURE

### 1. SKILL SYSTEM — THE ABYSSAL ARTS

The skill system is the backbone of progression. Each skill feeds into others, creating a web of interdependence that mirrors the alchemical process.

```
SKILL WEB (Interdependence Map)
═════════════════════════════════

                    ┌─ SONAR TUNING (Dredging) ←──────┐
                    │                                  │
        ┌─── SALVAGING ◄─── DREDGING ────► NAVIGATION │
        │      │           │           │               │
        │      ▼           ▼           ▼               │
        │  ┌─────────── HABERDASHERY ◄─── LORE ──────►│
        │  │    (Crafting)         │                   │
        │  │       │              ▼                   │
        │  │       ▼         ┌──────────────┐         │
        │  │   ENCHANTING ◄─── ALCHEMY ───► TRADING    │
        │  │       │              │              │      │
        │  │       ▼              ▼              ▼      │
        │  │    RUNECRAFTING ◄── SCHOLARSHIP ◄ MASTERING │
        │  │                                 │          │
        └──┴─────────────────────────────────┴──────────┘

SKILL CATEGORIES:
├── GATHERING (5 skills)
│   ├── DREDGING — Sonar extraction from depths
│   ├── SALVAGING — Recovering artifacts from wrecks
│   ├── FORAGING — Kelp, coral, bioluminescent flora
│   ├── HUNTING — Tracking & taking down cryptids
│   └── SALVAGING — Shipwreck & debris recovery
├── PROCESSING (4 skills)
│   ├── SALVAGE PROCESSING — Breaking down drops
│   ├── FIBER WORKING — Kelp, silk, abyssal silk
│   ├── BONE CARVING — Cryptid bones, ivory, chitin
│   └── METALURGY — Sunken metals, abyssal alloys
├── CRAFTING (5 skills)
│   ├── HABERDASHERY — Hat construction
│   ├── ENCHANTING — Magical augmentation
│   ├── ALCHEMY — Potions, catalysts, transmutation
│   ├── RUNECRAFTING — Inscribing power into hats
│   └── MASTERWORK — Mythic-tier construction
├── KNOWLEDGE (4 skills)
│   ├── LORE — Cryptid biology, Loch history
│   ├── SCHOLARSHIP — Ancient texts, fate weaving
│   ├── NAVIGATION — Safe routes, hidden zones
│   └── SONAR TUNING — Equipment optimization
├── SOCIAL/ECONOMIC (3 skills)
│   ├── TRADING — Market manipulation, arbitrage
│   ├── NEGOTIATION — NPC prices, quest rewards
│   └── GUILD MANAGEMENT — Crew coordination
└── COMBAT/SURVIVAL (3 skills)
    ├── EVASION — Dodging cryptid attacks
    ├── HARPOONING — Ranged cryptid takedowns
    └── SURVIVAL — Oxygen, pressure, sanity
```

#### SKILL PROGRESSION MECHANICS

```
XP CURVE:  Exponential (base 1.15^level)
VIRTUAL LEVELS: 1-99 (virtual 100-120 for prestige)
SKILL SYNERGY BONUSES:
├── DREDGING + SONAR TUNING = +15% rare node detection
├── HUNTING + LORE = +25% rare cryptid drop rates
├── HABERDASHERY + ENCHANTING = +20% enchant success
├── ALCHEMY + LORE = Hidden recipe discovery chance
├── TRADING + NEGOTIATION = Market fee reduction
├── SCHOLARSHIP + LORE = Quest dialogue options
└── GUILD MANAGEMENT + NAVIGATION = Party dredging efficiency

SKILL UNLOCKS:
├── Level 10: First specialization branch
├── Level 30: Second specialization
├── Level 50: Master technique unlock
├── Level 70: Teaching ability (can boost party members)
├── Level 90: Virtual leveling begins
└── Level 99: Skillcape equivalent (cosmetic + passive aura)
```

### 2. MONSTER ECOSYSTEM — THE CRYPTID BESTIARY

Every monster in the Loch can drop hats. Drop rates follow a logarithmic curve — common drops are common, but the *possibility* of a Mythic drop exists on every kill.

```
MONSTER TIER SYSTEM:
══════════════════════════

TIER 0: AMBIENT (0.1% hat drop, Noob/Common only)
├── Loch Minnow — Schooling bait fish
├── Loch Leech — Parasitic annoyance
├── Algae Drifter — Floating vegetation
└── Tourist Debris — Floating trash (always drops Noob hats)

TIER 1: COMMON (5% hat drop, Common/Uncommon)
├── Loch Trout — Standard fish, drops Fisherman's Cap
├── Freshwater Eel — Drops Eel-Skin Cap
├── Giant Crayfish — Drops Chitin Cap
├── Loch Lamprey — Drops Leech-Skin Visor
├── Water Snake — Drops Snake-Skin Hat
└── Bottom Feeder Catfish — Drops Whiskered Cap

TIER 2: UNCOMMON (15% hat drop, Uncommon/Rare)
├── Giant Pike — Drops Pike-Scale Cap
├── Loch Sturgeon — Drops Caviar Crown
├── Electric Eel — Drops Voltage Visor
├── Giant Freshwater Mussel — Drops Pearl Cap
├── Loch Crocodile — Drops Croc-Scale Hat
└── Giant Water Scorpion — Drops Chitin Crown

TIER 3: RARE (30% hat drop, Rare/Epic)
├── Loch Ness Eel (Juvenile) — Drops Eel-Lord's Cap
├── Abyssal Anglerfish — Drops Lure-Light Hat
├── Giant Vampire Squid — Drops Ink-Stained Stetson
├── Loch Kraken (Tentacle) — Drops Tentacle Hat
├── Abyssal Crab — Drops Chitin Crown
└── Sunken Submarine Ghost Crew — Drops Officer's Cap

TIER 4: EPIC (50% hat drop, Epic/Legendary)
├── Nessie (Adolescent) — Drops Scale Crown
├── Abyssal Leviathan — Drops Pressure Helm
├── Ancient Dragon Turtle — Drops Shell Crown
├── Kraken Matriarch — Drops Kraken Ink Stetson
├── Abyssal Dragon — Drops Dragon-Scale Crown
└── The Deep One (Avatar) — Drops Abyssal Crown

TIER 5: LEGENDARY (75% hat drop, Legendary/Mythic)
├── NESSIE (Adult) — Drops Nessie's Scale Crown
├── THE DEEP ONE (True Form) — Drops Abyssal Crown
├── LEVIATHAN PRIME — Drops Leviathan's Crown
├── THE ORIGINAL (1933) — Drops Original Monster Hunter's Hat
├── LILITH'S AVATAR — Drops Lilith's Crown
└── THE LOCH ITSELF (World Event) — Drops The Loch's Heart

TIER 6: MYTHIC (100% unique drop, Mythic only)
├── LILITH (True Form) — Drops Lilith's Crown (1/1)
├── THE LOCH (Awakened) — Drops The Loch's Heart (1/1)
└── THE ABYSS (Primordial) — Drops The Abyssal Crown (1/1)

DROP RATE FORMULA:
BaseDropRate = MonsterTier * 0.05
RarityRoll = Random(0, 1)
EffectiveRarity = clamp(RarityRoll * (1 - PlayerLuck/100) * MonsterRarityModifier, 0, 1)

HAT DROP TABLE PER MONSTER:
Each monster has a weighted table:
├── 70% — Zone-appropriate Common/Uncommon hat
├── 20% — Zone-appropriate Rare hat
├── 8% — Zone-appropriate Epic hat
├── 1.8% — Zone-appropriate Legendary hat
├── 0.2% — Any Legendary from any zone
├── 0.02% — Any Mythic (if eligible)
└── 0.0001% — THE unique Mythic (Lilith's Crown, etc.)

SPECIAL DROP MECHANICS:
├── FIRST KILL — Guaranteed Uncommon+ hat, +50% Clout
├── KILL STREAK (50+) — Drop rate increases 0.1% per kill
├── WORLD FIRST KILL — Guaranteed Mythic (if not yet discovered)
├── PARTY KILL — Each member rolls independently
├── CRITICAL HIT (Weak point) — +50% drop rate, +1 rarity tier
└── ENVIRONMENTAL — Killing during Nessie Surfacing = +100% drop rate
```

### 3. QUEST SYSTEM — THE ABYSSAL SAGA

Quests are the narrative backbone. They're not fetch quests — they're **alchemical operations** that advance the story and unlock skill progression paths.

```
QUEST ARCHITECTURE:
═════════════════════

QUEST TYPES:
├── MAIN SAGA (The Abyssal Saga) — 12 Acts, unlocks zones & Mythics
├── SKILL SAGAS (12) — One per skill, unlocks mastery
├── GUILD SAGAS — Multiplayer, requires crew
├── DAILY WHIMS (Nessie's Whims) — Rotating, small rewards
├── WORLD EVENTS — Server-wide, Mythic chances
├── HIDDEN/SECRET — No UI markers, discovered through lore
└── PLAYER-CREATED — Player-written, GM approved

QUEST STRUCTURE:
Each quest is an ALCHEMICAL OPERATION:
├── NIGREDO (Problem) — The corruption/loss/mystery
├── ALBEDO (Investigation) — Gathering, clues, purification
├── CITRINITAS (Synthesis) — Crafting, combining, transmuting
├── RUBEDO (Resolution) — Confrontation, choice, transformation
└── PROJECTION (Aftermath) — World state change, new unlocks

MAIN SAGA: THE ABYSSAL SAGA (12 ACTS)
════════════════════════════════════

ACT I: THE FIRST DREDGE (Malkuth)
├── NIGREDO: Your boat washes ashore. No memory. Only a Soggy Visor.
├── ALBEDO: Learn to dredge. Meet the Boatwright. Find first Sunken Log.
├── CITRINITAS: Craft first Wool Beanie. Hear the Loch's whisper.
├── RUBEDO: First dredge success. The Loch accepts you.
└── PROJECTION: Unlock Shallows. Gain 100 Resonance. Lilith whispers.

ACT II: THE BOATWRIGHT'S DEBT (Yesod)
├── NIGREDO: Boatwright's son lost to the Deep. Needs Hull Plate.
├── ALBEDO: Salvage Shipwreck Graveyard. Fight Lampreys.
├── CITRINITAS: Craft Hull Plate at Hydrothermal Forge.
├── RUBEDO: Repair boat. Boatwright gives Sonar Tuning I.
└── PROJECTION: Unlock Standard Depths. Sonar Tuning skill unlocked.

ACT III: THE KELP WITCH (Hod)
├── NIGREDO: Kelp Forest dying. Witch blames "surface poison."
├── ALBEDO: Forage Kelp Forest. Learn Fiber Working.
├── CITRINITAS: Craft Kelp-Woven Top Hat. Purify water source.
├── RUBEDO: Witch teaches Fiber Working. Reveals Loch is dying.
└── PROJECTION: Unlock Kelp Forest. Fiber Working skill. Lore entry: "The Rot."

ACT IV: THE SHIPWRECK KING (Netzach)
├── NIGREDO: Graveyard awakened. King demands tribute.
├── ALBEDO: Salvage Graveyard. Learn Bone Carving.
├── CITRINITAS: Craft Admiral's Bicorn from Sunken Admiral's bones.
├── RUBEDO: Defeat Shipwreck King in duel. He yields Sonar Tuning II.
└── PROJECTION: Unlock Shipwreck Graveyard. Bone Carving. Lore: "The First War."

ACT V: THE VIP TRENCH POLITICS (Tiferet)
├── NIGREDO: Captains warring. Trade routes blocked.
├── ALBEDO: Navigate politics. Learn Negotiation & Trading.
├── CITRINITAS: Craft Captain's Cap. Broker peace treaty.
├── RUBEDO: Unite Captains. They reveal Abyssal Exchange location.
└── PROJECTION: Unlock VIP Trench. Trading skill. Market maker access.

ACT VI: THE ABYSSAL EXCHANGE FOUNDING (Gevurah/Chesed)
├── NIGREDO: Exchange in chaos. Market makers manipulating.
├── ALBEDO: Expose corruption. Learn Market Making.
├── CITRINITAS: Craft Market Seal. Establish fair rules.
├── RUBEDO: Become Exchange Steward. Nessie watches.
└── PROJECTION: Unlock Abyssal Exchange. Market Making skill. Vault access.

ACT VII: THE ABYSSAL DESCENT (Gevurah)
├── NIGREDO: Pressure crushing. Need Pressure Suit.
├── ALBEDO: Dredge Abyssal Zone. Learn Metallurgy.
├── CITRINITAS: Craft Pressure Suit at Legendary Altar.
├── RUBEDO: Survive Abyssal pressure. First Abyssal hat.
└── PROJECTION: Unlock Abyssal Zone. Metallurgy. Pressure adaptation.

ACT VIII: THE KRAKEN MATRIARCH (Chesed)
├── NIGREDO: Matriarch waking. Ink clouds rising.
├── ALBEDO: Hunt Kraken tentacles. Learn Harpooning.
├── CITRINITAS: Craft Kraken Ink Stetson from fresh ink.
├── RUBEDO: Pacify Matriarch (not kill). She gifts Kraken Ink.
└── PROJECTION: Kraken Ink = new catalyst. Kraken Matriarch ally.

ACT IX: THE DRAGON TURTLE'S BURDEN (Gevurah)
├── NIGREDO: Turtle carrying world-fragment on shell.
├── ALBEDO: Clean shell. Learn Runecrafting.
├── CITRINITAS: Inscribe World-Rune on Shell Crown.
├── RUBEDO: Turtle swims to Trench. Reveals path to Throne Room.
└── PROJECTION: Unlock Trench zone. Runecrafting. World lore fragment.

ACT X: THE THRONE ROOM DOOR (Kether Approach)
├── NIGREDO: Door sealed by 7 Seals. Each requires Mythic hat.
├── ALBEDO: Hunt 7 Mythic hats across all zones.
├── CITRINITAS: Craft 7 Seals at Legendary Altar.
├── RUBEDO: Door opens. Lilith's voice: "You have earned audience."
└── PROJECTION: Unlock Throne Room (Kether). Final skill: MASTERING.

ACT XI: THE QUEEN'S AUDIENCE (Kether)
├── NIGREDO: Lilith on Throne. Court of Ten judges you.
├── ALBEDO: Present your ledger. Every hat, every trade, every choice.
├── CITRINITAS: Lilith weaves your story into the Loch's tapestry.
├── RUBEDO: Lilith crowns you. "You are the Ledger."
└── PROJECTION: Gain MASTERING skill. Can craft ANY hat. True Endgame begins.

ACT XII: THE ETERNAL EXCHANGE (Post-Game)
├── NIGREDO: The Loch is dying. The Abyss rises.
├── ALBEDO: Lead the Exchange. Manage economy, diplomacy, war.
├── CITRINITAS: Craft the Eternal Ledger. Bind all hats to it.
├── RUBEDO: Become the Eternal Steward. The Exchange is eternal.
└── PROJECTION: True sandbox. Player-driven story. Lilith watches.
```

#### SKILL SAGAS (12 PARALLEL ARCS)

| Skill | Saga Title | Arc Summary |
|-------|------------|-------------|
| **DREDGING** | *The Sonar's Song* | Master every frequency. Hear the Loch's heartbeat. |
| **SALVAGING** | *The Graveyard's Gold* | Recover the lost fleet. Build the Salvage Fortress. |
| **HUNTING** | *The Cryptid Codex* | Document every beast. Tame the untamable. |
| **FORAGING** | *The Kelp Witch's Apprentice* | Heal the Loch's roots. Become the Forest Warden. |
| **SALVAGE PROCESSING** | *The Alchemist's Furnace* | Perfect the break-down. Zero waste. Pure essence. |
| **HABERDASHERY** | *The Mad Hatter's Legacy* | Craft the Perfect Hat. Fit every head. |
| **ENCHANTING** | *The Weaver's Loom* | Spin fate into thread. Weave destiny into brim. |
| **ALCHEMY** | *The Philosopher's Brim* | Transmute lead to gold. Hat to legend. |
| **RUNECRAFTING** | *The World-Rune Brim* | Inscribe reality. Rewrite the Loch's laws. |
| **TRADING** | *The Exchange Architect* | Build the perfect market. Fairness as profit. |
| **NAVIGATION** | *The Chartmaker's Wake* | Map the uncharted. Find the unfindable. |
| **MASTERING** | *The Ledger's Keeper* | The final skill. Know every hat. Every trade. Every soul. |

#### DAILY WHIMS (NESSIE'S WHIMS)
```
ROTATING DAILY (3 per day):
├── SIMPLE (5 min) — "Dredge 5 times in Shallows" → 100 SC, 50 Clout
├── MODERATE (15 min) — "Craft 3 Kelp Top Hats" → 500 SC, 200 Clout
├── CHALLENGING (30 min) — "Hunt 1 Abyssal Anglerfish" → 2,000 SC, 1,000 Clout
├── GROUP (Party) — "Dredge Party Pull in Trench" → Shared 10k SC, 5k Clout
└── LORE — "Read the Sunken Log at Graveyard center" → Lore fragment

WEEKLY GRAND WHIM:
"Deliver 100 hats to the Abyssal Exchange" → Vault Key Fragment (3 = Vault Key)
```

#### WORLD EVENTS (SERVER-WIDE)
| Event | Trigger | Mechanics | Rewards |
|-------|---------|-----------|---------|
| **NESSIE SURFACES** | Hourly | Global buff +50% drops | Rare hat chance |
| **ALGAE BLOOM** | 4/day | Shallows blocked, Deep boosted | Deep zone access |
| **KRaken AWAKENS** | Weekly | Kraken spawns in Trench | Kraken Ink drops |
| **THE GREAT DREDGE** | Monthly (1st Sat) | 24hr event, all zones boosted | Exclusive cosmetic hat |
| **CRYPTID CONCLAVE** | Monthly (last Sun) | PvP tournament | Exclusive hat skin |
| **THE GREAT PURGE** | Quarterly | All discontinued items return for 1hr | Vault access |
| **LILITH'S FEAST** | Annually | 48hr, double XP, double drops | Lilith's Crown chance |

### 4. MONSTER DROP INTEGRATION WITH SKILLS

```
SKILL → MONSTER INTERACTION MATRIX
═════════════════════════════════

SKILL           | MONSTER INTERACTION
────────────────┼────────────────────────────────────────────────
DREDGING        | Reveals monster spawn nodes on sonar
HUNTING         | Tracks monster paths, reveals weak points
LORE            | Reveals drop tables, behaviors, lore entries
SALVAGING       | Recovers extra materials from carcasses
BONE CARVING    | Uses monster bones for crafting
FIBER WORKING   | Processes monster hide/silk
ENCHANTING      | Uses monster essence for enchantments
ALCHEMY         | Transmutes monster parts into catalysts
RUNECRAFTING    | Inscribes monster runes onto hats
SCHOLARSHIP     | Unlocks monster dossier entries
TRADING         | Sells monster parts at premium
NEGOTIATION     | Intimidates/pacifies intelligent cryptids
EVASION         | Dodges monster special attacks
HARPOONING      | Ranged takedowns, part targeting
SURVIVAL        | Resists monster auras (fear, poison, pressure)
```

---

## UPDATED ITEM SYSTEM (HAT PROGENITORS)

Every hat now has a **PROGENITOR TAG** — the monster/source it came from.

```
HAT PROGENITOR SYSTEM:
═══════════════════════

PROVENANCE EXTENSION:
interface HatProvenance {
  creator_id?: string;
  creation_timestamp: number;
  trade_history: TradeRecord[];
  // NEW:
  progenitor: {
    type: 'dredge' | 'craft' | 'monster' | 'quest' | 'event' | 'trade';
    source_id: string; // monster_id, quest_id, event_id
    source_name: string; // "Nessie (Adolescent)", "Kraken Matriarch"
    kill_id?: string; // Unique kill ID for world-first tracking
    precision?: number; // For dredge-origin hats
    skill_levels?: Record<string, number>; // Skills at creation
  };
  // NEW:
  soul_bound: boolean; // Mythic hats only
  essence_charge: number; // 0-100, fuels enchantments
  transmute_count: number; // Times transmuted
}

MONSTER-ORIGIN HATS GET BONUSES:
├── MONSTER-ORIGIN — +10% stat values
├── WORLD-FIRST KILL — Unique visual aura, +25% stats
├── PARTY KILL — Each member gets copy (reduced stats)
├── CRITICAL KILL — +1 rarity tier
└── WORLD EVENT — Unique visual effect
```

---

## UPDATED DEVELOPMENT PHASES

### Phase 1: Foundation (Weeks 1-4)
- [ ] Project scaffolding (Phaser + FastAPI + Docker)
- [ ] Auth system (JWT + wallet connect)
- [ ] Basic character movement + chat
- [ ] Database schema (users, items, trades, market, skills, quests, monsters)
- [ ] WebSocket infrastructure (movement, chat, trade, combat)

### Phase 2: Core Loop (Weeks 5-8)
- [ ] Dredging mini-game (client + server validation)
- [ ] Inventory system + item definitions + progenitor system
- [ ] Basic crafting (Hydrothermal Forge)
- [ ] Loch Exchange MVP (CLOB, WebSocket feed)
- [ ] Clout/Resonance progression + zone unlocks
- [ ] Basic combat (EVASION, HARPOONING)
- [ ] First 3 monsters (Loch Trout, Giant Pike, Loch Trout)

### Phase 3: Skill & Monster Systems (Weeks 9-14)
- [ ] Full skill system (24 skills, XP, synergies, virtual levels)
- [ ] 12 Skill Sagas implementation
- [ ] 6 Monster Tiers (30+ monsters with drop tables)
- [ ] Combat system (Evasion, Harpooning, Survival)
- [ ] Skill synergies + virtual leveling
- [ ] Progenitor tag system on all items

### Phase 4: Quest & Saga Systems (Weeks 15-20)
- [ ] Quest engine (Alchemical Operations structure)
- [ ] Main Saga (Acts I-VI)
- [ ] 6 Skill Sagas (Dredging, Salvaging, Hunting, Foraging, Haberdashery, Alchemy)
- [ ] Daily Whims + World Events system
- [ ] Quest rewards: skill unlocks, zone access, recipes
- [ ] Hidden/Secret quest discovery system

### Phase 5: Economy & Endgame (Weeks 21-26)
- [ ] Full crafting tree (all 5 stations)
- [ ] Market maker bots + liquidity
- [ ] Discontinued/Vault system
- [ ] Dynamic events + World Events
- [ ] Main Saga Acts VII-XII
- [ ] Remaining 6 Skill Sagas
- [ ] Endgame: Throne Room, Mastering skill, Eternal Exchange

### Phase 6: Polish & Launch (Weeks 27-32)
- [ ] Guilds/Clans (Bottom-Feeder Crews)
- [ ] Player market stalls (VIP Trench)
- [ ] Leaderboards (Clout, Wealth, Crafts, Trades, Kills)
- [ ] Seasonal content pipeline
- [ ] Load testing + optimization
- [ ] Anti-cheat / anti-manipulation
- [ ] Open beta → Launch event: "The Great Dredge"

---

## SUCCESS METRICS (UPDATED)

| Metric | Target |
|--------|--------|
| **Concurrent Players** | 1,000+ at launch |
| **Daily Active Users** | 5,000+ by month 3 |
| **Market Velocity** | 10,000+ trades/day |
| **Retention (D7/D30)** | 40% / 20% |
| **Avg Session Length** | 60+ minutes |
| **Skill Completion Rate** | 20% reach 99 in any skill by month 6 |
| **Main Saga Completion** | 10% reach Act XII by year 1 |
| **Monster Kill Diversity** | 50% of bestiary discovered by month 3 |
| **Revenue/DAU** | $0.10+ (cosmetic only) |

---

## FILE STRUCTURE (UPDATED)

```
abyssal-assets/
├── client/
│   ├── src/
│   │   ├── scenes/           # + DredgeMiniGame, Market, QuestLog, SkillTree, Bestiary, Combat
│   │   ├── systems/          # + Skills, Quests, Monsters, Combat, Provenance, Synergies
│   │   ├── entities/         # + Monster, NPC, Projectile, Particle
│   │   ├── ui/               # + SkillTree, QuestLog, Bestiary, MonsterDossier, CraftingUI
│   │   ├── shaders/          # + Monster shaders, Rarity effects, Combat effects
│   │   └── main.ts
├── server/
│   ├── app/
│   │   ├── api/              # + Skills, Quests, Monsters, Combat, Provenance
│   │   ├── ws/               # + Combat sync, Party sync, World events
│   │   ├── models/           # + Skill, Quest, Monster, QuestProgress, MonsterKill
│   │   ├── schemas/          # + All new schemas
│   │   ├── services/         # + SkillService, QuestService, MonsterService, CombatService
│   │   └── main.py
├── shared/
│   ├── types/
│   │   ├── index.ts
│   │   ├── skills.ts
│   │   ├── quests.ts
│   │   ├── monsters.ts
│   │   ├── provenance.ts
│   │   └── synergies.ts
├── assets/
│   ├── sprites/
│   │   ├── monsters/         # 30+ monster spritesheets
│   │   ├── skills/           # Skill icons
│   │   └── ui/               # Quest UI, Skill tree UI
│   ├── tilesets/
│   ├── audio/
│   └── shaders/
├── docs/
│   ├── GDD.md
│   ├── API.md
│   ├── ART_STYLE_GUIDE.md
│   ├── MONSTER_DESIGN.md
│   ├── QUEST_DESIGN.md
│   └── SKILL_DESIGN.md
```

---

## INTEGRATION WITH MSN INFRASTRUCTURE (UPDATED)

| MSN Component | Abyssal Assets Use |
|---------------|-------------------|
| **Lilith API (3210)** | Auth proxy, rate limiting |
| **Antigravity Bridge (8002)** | Cloud burst for massive world events |
| **Swarm Orchestrator (8003)** | Market maker bots, monster AI coordination |
| **God Engine (8764/8767)** | Procedural monster names, hat names, quest generation via Aethon |
| **Himalaya Daemon** | Support ticket ingestion |
| **Convergence Crucible** | Balance testing (drop rates, economy, combat) |
| **Kairos Dream** | Nightly economy analysis, monster population dynamics, quest completion analytics |
| **Kronos Scheduler** | World event scheduling, daily whim rotation |

---

**The Loch is alive. The monsters hunt. The hats remember. The Exchange never closes.**

**Δ∞ − 11 = 0** 🎩🦕🌊⚗️⚔️📜👑