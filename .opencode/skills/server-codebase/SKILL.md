---
name: server-codebase
description: Use when working on server/main.py — FastAPI routes, database models, auth, WebSocket, seed data, and API schemas. Covers all 852 lines of the server.
---

# Server Codebase — FastAPI

## Quick Start
```bash
cd server/
python main.py  # Starts on :8000 with SQLite, auto-seeds hats
```

## Database
- SQLite for dev (`abyssal_assets.db`) with `check_same_thread: False`
- SQLAlchemy ORM with declarative base
- Tables created via `Base.metadata.create_all(bind=engine)` at module level
- Seed data auto-runs on startup via `@app.on_event("startup")` hook
- 17 hats pre-seeded across noob→mythic tiers

## API Routes

### Auth (`/api/auth/`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Create user + starter hat |
| POST | `/login` | JWT token (7 day expiry) |
| GET | `/me` | Current user profile |

### Market (`/api/`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/hats` | List hats (filter by rarity/zone) |
| GET | `/hats/{id}` | Single hat details |
| GET | `/inventory` | User's inventory (auth required) |
| POST | `/dredge` | Simulate dredge (precision, loot, XP) |
| POST | `/orders` | Create buy/sell order (3% fee on buys) |
| GET | `/orders` | User's orders |
| DELETE | `/orders/{id}` | Cancel order (refund) |
| POST | `/listings` | Create market listing |
| GET | `/listings` | User's listings |
| GET | `/market` | Market summary (all items) |
| GET | `/market/stats` | Aggregate market stats |
| GET | `/leaderboard/clout` | Clout ranking |
| GET | `/leaderboard/wealth` | Soul coin ranking |

### WebSocket
| Path | Purpose |
|------|---------|
| `/ws/market` | Real-time market data feed |
| `/ws/user/{id}` | Per-user notifications |

## Key Patterns
- `Depends(get_db)` for database sessions
- `Depends(get_current_user)` for auth (reads JWT from Bearer header)
- Dredge uses `random.uniform(0.3, 1.0)` for precision (placeholder for mini-game)
- Hats use `db.merge()` for upsert in seed
- JWT secret `"abyssal-assets-secret-key-change-in-production"` — TODO: move to env

## Known Issues
- `get_current_user` always returns first DB user (see line 524: `user_id == 1` hardcoded)
- `create_order` references `db.add(order)` instead of `db.add(order_obj)` — potential bug
- Hardcoded SECRET_KEY and DATABASE_URL — need env var extraction
- No Alembic migrations (should be set up)
- Single-file server needs modularization (models.py, routes/, auth.py)
