---
name: abyssal-architecture
description: Use when working on game architecture, tech stack decisions, project structure, or the core loop. Covers the full stack: FastAPI server at server/main.py (852 lines), Phaser 3/TypeScript client at client/src/, and shared types at shared/types/.
---

# Abyssal Assets — Architecture

## Core Loop
Dredge → Hunt → Craft → Quest → Trade → Ascend

## Tech Stack
- **Server**: FastAPI (Python) at `server/main.py` — single file, 852 lines, needs modularization
- **Client**: Phaser 3 (TypeScript) at `client/src/` — Vite bundler, :3000 dev server
- **Database**: SQLite dev (`sqlite:///./abyssal_assets.db`), PostgreSQL prod via `docker-compose.yml`
- **Auth**: JWT (python-jose), bcrypt via passlib
- **Real-time**: WebSocket connections at `/ws/market` and `/ws/user/{id}`
- **Shared types**: `shared/types/` — 6 files (monsters.ts 621 lines, skills.ts 635 lines, quests.ts, synergies.ts, provenance.ts, index.ts)

## Key Files
| File | Lines | Purpose |
|------|-------|---------|
| `server/main.py` | 852 | All server code — models, routes, auth, WebSocket manager, seed data |
| `client/src/` | ~3000 | Phaser 3 scenes, market CLOB (1539 lines), dredge mini-game (838 lines) |
| `shared/types/monsters.ts` | 621 | 7 monster tiers, 6 defined monsters, full type system |
| `shared/types/skills.ts` | 635 | 24 skills across 6 categories, XP curves, synergies |
| `GDD.md` | 583 | Full game design — quest Acts, skill web, drop rates |

## Database Models (in `server/main.py`)
- `User` — username, email, soul_coins, clout, boat_level, zone
- `Hat` — 17 seeded hats across 7 rarity tiers
- `InventoryItem` — user inventory with quantity, serial_number, equipped
- `Order` — CLOB buy/sell orders with price, quantity, fill tracking
- `MarketListing` — seller listings with expiry
- `Trade` — executed trades with buyer/seller/fee
- `DredgeLog` — dredge attempt records

## Linux Migration Notes
- Server runs with `python main.py` via uvicorn on :8000
- Client runs with `npm run dev` via vite on :3000
- No .bat/.ps1 files exist for this project (already Linux-native)
- GDD mentions NSSM at deployment section — use systemd instead
- `docker-compose.yml` for PostgreSQL production deployment
