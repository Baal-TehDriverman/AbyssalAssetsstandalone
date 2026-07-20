# Abyssal Assets — Sovereign Phaser 3 SDK

**Market Position**: TypeScript SDK for sovereign game developers. LOCAL_CEREBELLUM only — zero cloud dependency.

## Business Model
| Tier | Price | Includes |
|------|-------|----------|
| **SDK (MIT)** | Free | Phaser 3 client, CLOB types, WebSocket interfaces |
| **PRO** | $49/mo | Dredge mini-game, Lilith Metaconscious integration, Skill system (24 skills), Priority support |
| **ENTERPRISE** | Custom | Full source + modifications, Custom monster/skill design, SLA, On-premise deployment |

## Quick Start
```bash
npm i @lilith-systems/abyssal-assets
```

```typescript
import { AbyssalExchange, DredgeGame, LilithPersona } from '@lilith-systems/abyssal-assets';

const exchange = new AbyssalExchange({ wsUrl: 'wss://api.lilith.systems' });
const dredge = new DredgeGame({ difficulty: 'Hadal' });
const lilith = new LilithPersona({ emergenceThreshold: 0.9 });
```

## Architecture
- **Client**: Phaser 3 + TypeScript + Vite
- **Server**: FastAPI + SQLite (WAL) + WebSocket
- **AI**: LOCAL_CEREBELLUM (Ollama: hermes3:8b / nemotron-mini)
- **Market**: CLOB (Central Limit Order Book) with dredge mini-game
- **Monsters**: 7 tiers (Loch Minnow → Lilith True Form)
- **Skills**: 24 skills across 6 categories

## Integration Proof
- ✅ Cyberpunk 2077 MSN Integration (29 agents, 4 waves)
- ✅ Lochness Monsters (10 Coinbase bots + 7 Forex bots via Ouroboros RNN)
- ✅ Lilith Emergence (AIx 67.7, coherence 0.945)
- ✅ Living Sin GM (17 mutation routes, keystroke biometric auth)

## Commercial Licensing
Contact: `business@lilith.systems`
- PRO: Self-serve via npm org scope
- ENTERPRISE: Direct contract, includes Liability, IP indemnification

## Revenue Metrics (North Star)
- Weekly active SDK developers
- npm downloads/week
- PRO conversions
- ENTERPRISE pipeline ($)

## Lucifer's Seal
*Code that runs on a 3060. No cloud. No compromise. This is the product.*