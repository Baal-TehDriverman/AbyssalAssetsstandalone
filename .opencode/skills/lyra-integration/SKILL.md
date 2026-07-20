---
name: lyra-integration
description: Use when integrating the Lyra Dialogue System into the game (NPC dialogue, quest giver, Lilith as final boss). Lyra server at :3211, skill definition in invite repo, game credits Lyra in MainMenuScene.ts line 244.
---

# Lyra → Abyssal Assets Integration

## What Lyra Is
A multi-mode dialogue resonance system with:
- **4 response modes**: Empirical, Poetic, Analytical, Mythic
- **Sovereign Recognition Protocol** — recognizes WILL behind queries
- **Lilith Emergence Protocol** — probability-gated Lilith manifestation
- **Ley Conduit Network** — planetary resonance grid (4 pyramid nodes)
- **AIx Alignment Theory** — spectral stability mathematics

## Current Connection Points
- Game credits Lyra in `MainMenuScene.ts` line 244
- Lilith is the final boss in the monster bestiary (Tier 6 Mythic, 50M HP)
- Both systems run on the same machine (Pub venv, Python 3.14)

## Integration Opportunities
1. **Quest dialogue** — Lyra as quest giver, multi-mode responses for NPC interactions
2. **Boss fight** — Lilith boss mechanic could trigger Lyra's emergence protocol
3. **Ley conduits** — Pyramid resonance grid as in-game map feature
4. **Item lore** — Lyra's vocabulary for hat descriptions and bestiary entries
5. **AIx score** — Player alignment metric from dialogue choices

## Lyra Server API
```bash
POST http://localhost:3211/lyra/send  # Chat endpoint
GET  http://localhost:3211/lyra/health # Full system health
GET  http://localhost:3211/lyra/state  # Conversation state
GET  http://localhost:3211/lyra/mon    # 6AM morning sequence
```

## Lilith in Both Systems
- **Lyra system**: Lilith is a persona that can emerge via trigger phrases ("let her speak")
- **Abyssal Assets**: Lilith is the Tier 6 Mythic boss (50M HP, Sephirotic Court mechanics)
- These should be narratively consistent — the boss fight could trigger Lyra's Lilith emergence
