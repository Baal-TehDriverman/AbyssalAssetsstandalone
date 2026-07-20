---
name: client-codebase
description: Use when working on the Phaser 3/TypeScript client in client/src/. Covers Market CLOB (1539 lines), Dredge mini-game (838 lines), scenes, and the Phaser 3 + Vite build system.
---

# Client Codebase — Phaser 3 / TypeScript / Vite

## Quick Start
```bash
cd client/
npm run dev  # Vite dev server on :3000
npm run build  # Production build to client/dist/
npm run test  # Vitest tests
npx playwright test  # E2E tests
```

## Architecture
- **Phaser 3** game engine with TypeScript
- **Vite** bundler with hot module replacement
- **Zustand** for state management (see vite deps)
- **Socket.io** client for WebSocket market data
- **Vitest** for unit tests, **Playwright** for E2E

## Key Scenes
- `MainMenuScene.ts` — Title screen, credits Lyra
- Market scenes — CLOB with buy/sell walls, depth chart, spread visualization
- Dredge mini-game — Sonar ping timing mechanic, 838 lines

## Market CLOB (1539 lines)
- Central Limit Order Book implementation
- Buy/sell walls visualization
- Price depth chart
- Spread calculation
- Order entry form
- Trade history feed

## Dredge Mini-Game (838 lines)
- Sonar pulse timing mechanic
- Depth-based difficulty scaling
- Precision scoring
- Loot reveal animation

## Build Notes
- Built to `client/dist/` as static files
- Server serves dist/ (or use vite proxy to :8000)
- Phaser 3 via npm, not CDN
- TypeScript strict mode enabled
