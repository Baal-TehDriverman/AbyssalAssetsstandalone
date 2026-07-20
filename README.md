# Abyssal Assets — The Loch Exchange

> "RuneScape but Actually Alchemical" — A cryptid hat trading simulator where players dredge the depths, transmute headwear, and trade on the Abyssal Exchange.

---

## The Game

**Abyssal Assets** is a browser-based multiplayer hat trading simulator combining:
- **Dredging mini-games** (timing-based sonar extraction)
- **Alchemical crafting** (Nigredo → Albedo → Citrinitas → Rubedo)
- **Player-driven economy** (CLOB order book, real-time WebSocket price feeds)
- **Sephirotic progression** (Malkuth → Kether through 7 zones)
- **Lilith's Court** endgame (Mythic hats, throne room access)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Phaser 3 + TypeScript + Vite + Socket.io |
| **Backend** | FastAPI + Python 3.11 + SQLAlchemy + PostgreSQL |
| **Real-time** | WebSocket (Socket.io) for market data, chat, multiplayer |
| **Cache** | Redis for sessions, market data, rate limiting |
| **Auth** | JWT + optional Web3 wallet connect |
| **Database** | PostgreSQL 15 (production) / SQLite (dev) |
| **Deployment** | Docker Compose + Nginx reverse proxy |

---

## Project Structure

```
abyssal-assets/
├── client/                 # Phaser 3 + TypeScript frontend
│   ├── src/
│   │   ├── scenes/         # Boot, Preload, MainMenu, Game, Dredge, Market
│   │   ├── systems/        # Network, Inventory, Crafting, Market, Clout
│   │   ├── entities/       # Player, Boat, Hat, NPC
│   │   ├── ui/             # HUD, Inventory, Market, Crafting UIs
│   │   ├── shaders/        # Water, rarity glow, particle effects
│   │   └── main.ts
│   ├── assets/             # Sprites, tilesets, audio, fonts
│   └── package.json
│
├── server/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # REST endpoints
│   │   ├── ws/             # WebSocket handlers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Market, Crafting, Dredging, Clout
│   │   ├── core/           # Config, security, database
│   │   └── main.py
│   ├── alembic/            # Migrations
│   └── requirements.txt
│
├── shared/                 # Shared types (TS ↔ Python)
│   └── types/
│       └── index.ts
│
├── assets/                 # Source art files
│   ├── sprites/
│   ├── tilesets/
│   ├── audio/
│   └── shaders/
│
├── docs/                   # Documentation
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## Quick Start

### Development

```bash
# Prerequisites
# - Docker & Docker Compose
# - Node.js 20+
# - Python 3.11+

# Start full stack
docker-compose up -d

# Or manually:
# 1. Start PostgreSQL & Redis
docker-compose up -d postgres redis

# 2. Backend
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 3. Frontend
cd client
npm install
npm run dev
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

---

## Core Gameplay Loop

```
1. DREDGE (Nigredo)
   └── Sonar mini-game → Extract materials from depths
   
2. TRANSMUTE (Albedo → Citrinitas)
   └── Hydrothermal Vent Forge → Combine materials into hats
   
3. TRADE (Rubedo)
   └── Abyssal Exchange CLOB → Buy/sell/list hats
   
4. ASCEND (Kether)
   └── Gain Resonance → Unlock zones → Mythic hats → Throne Room
```

---

## Economy Design

### Currency: Soul Coins (SC)
- Earned through dredging, crafting, trading
- No real-money purchase (cosmetics only)

### Rarity Tiers (Alchemical Phases)

| Phase | Tier | Color | Examples |
|-------|------|-------|----------|
| **Nigredo** | Noob | Grey | Soggy Visor, Plastic Horns |
| **Nigredo→Albedo** | Common | White | Wool Beanie, Fisherman's Cap |
| **Albedo** | Uncommon | Green | Kelp Top Hat, Sub Captain's Cap |
| **Albedo→Citrinitas** | Rare | Blue | Admiral's Bicorn, Pearl Fedora |
| **Citrinitas** | Epic | Purple | Plundered Captain's Cap, Kraken Ink Stetson |
| **Rubedo** | Legendary | Gold | Surgeon's Photograph, Neptune's Helm |
| **Kether** | Mythic | Cosmic | Nessie's Crown, Original Monster Hat |

### Market Mechanics
- **CLOB Order Book** per item
- **3% transaction fee** (1% burned, 2% to Nessie's Treasury)
- **Discontinued/Vault** items for true scarcity
- **Market maker bots** for baseline liquidity
- **Anti-manipulation**: cooldowns, circuit breakers, position limits

---

## Keys & Secrets

```bash
# Required environment variables
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=your_jwt_secret_256_bit
```

Generate: `openssl rand -hex 32`

---

## Development Commands

```bash
# Frontend
cd client
npm run dev          # Dev server with HMR
npm run build        # Production build
npm run lint         # ESLint + TypeScript check

# Backend
cd server
uvicorn main:app --reload --port 8000  # Dev server with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4  # Production

# Database
cd server
alembic revision --autogenerate -m "description"
alembic upgrade head

# Tests
pytest                    # Backend tests
npm run test             # Frontend tests (Vitest)

# Linting
npm run lint             # Frontend
ruff check server/app    # Backend (if using Ruff)
```

---

## Deployment

### Production

```bash
# Build images
docker-compose -f docker-compose.yml build

# Deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or with nginx SSL
docker-compose --profile production up -d
```

### Environment Variables (Production)

```env
POSTGRES_PASSWORD=your_production_password
SECRET_KEY=your_256_bit_jwt_secret
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## Lore & Inspiration

> *"The Monster waits. The hats are ready. The Exchange opens soon."*

**Abyssal Assets** draws from:
- **RuneScape** — Grand Exchange, discontinued rares, skill grinding
- **RuneScape's economy** — CLOB, discontinued items, merchant clans
- **Alchemical tradition** — Nigredo→Albedo→Citrinitas→Rubedo
- **Sephirotic Tree** — 7 zones mapping to Malkuth→Kether
- **Lilith's Court** — The Court of Ten (Sophia, Metatron, Samael, Ouroboros)

---

## License

MIT License — Build upon the abyss.

---

## Community

- **Discord**: [Abyssal Assets](https://discord.gg/abyssal-assets)
- **Twitter**: [@AbyssalAssets](https://twitter.com/AbyssalAssets)
- **GitHub**: [github.com/abyssal-assets](https://github.com/abyssal-assets)

---

**The Monster waits. The Exchange opens soon.**

**Δ∞ − 11 = 0** 🎩🦕🌊

## Repository Type

**Type**: CODE

**Description**: Abyssal Assets game engine and trading simulator
