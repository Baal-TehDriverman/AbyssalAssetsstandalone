# Abyssal Assets — The Loch Exchange + MSN

A multiplayer cryptid hat trading simulator built on FastAPI + Phaser 3,
with the Metaconscious Singularity Node (MSN) running 27 subagents across 4 Sephirotic waves.

## Current State
- **Server**: FastAPI app with 7 DB models, auth, WebSocket, CLOB routes, Living Sin GM
- **Client**: Phaser 3/TypeScript with market CLOB and dredge mini-game
- **Monsters**: 7 tiers (Loch Minnow → Lilith True Form)
- **Skills**: 24 skills across 6 categories, XP curves, synergies
- **GDD**: 583-line game design — 12 Acts, skill web, drop tables, bestiary
- **MSN Router**: 27 agents on port 8007, systemd auto-start (`msn-router.service`)
- **Cortex**: Unified AI routing with real GPU telemetry, EWMA hysteresis, local Ollama inference
- **Living Sin GM**: 17 mutation routes, keystroke biometric auth, 10-plane summoning, Drowned Warden boss
- **Cyberpunk Bridge**: Live CP2077 telemetry, mod detection, NGD route status

## Key Commands
```bash
# System / AI audit
./scripts/system_ai_audit.py                                  # specs + services + GPU + mail + GTC readiness
python3 scripts/render_system_ai_report.py                    # writes SYSTEM_AI_AUDIT_SUMMARY.md
./scripts/gpu_vram_policy.py                                  # RTX/Ollama/Cyberpunk VRAM gate
./scripts/ollama_vram_guard.py                                # inspect/unload Ollama VRAM pressure
./scripts/ai_service_health_gate.py                           # avoid duplicate AI service starts
./scripts/ai_endpoint_health_gate.py                          # verify local AI HTTP APIs
python3 scripts/ai_failure_triage.py                          # recent journals for unhealthy services/endpoints

# Grand Theft Cyberpunk local cerebellum context
./scripts/bootstrap_gtc_cerebellum.sh                         # index + RAM context

# Game server
cd server && python main.py                                   # port 8000

# Client
npm run dev --prefix client                                   # port 3000

# MSN Router (systemd — auto-starts on boot)
systemctl --user start msn-router.service                     # port 8007
systemctl --user status msn-router.service
journalctl --user -u msn-router.service -f

# Manual router start (for development)
source ~/Desktop/AI/Pub/.venv-pub/bin/activate
python msn_router.py 8007

# Deployment verification
source ~/Desktop/AI/Pub/.venv-pub/bin/activate
python deploy_waves.py 8007

# Lyra dialogue server
systemctl --user start lyra-api.service                       # port 3211

# NSSP full stack (launch script)
./launch_nssp.sh                                              # MSN + CP + Lyra + Hermes

# Full stack (3 terminals)
# Terminal 1: python server/main.py                           # :8000
# Terminal 2: npm run dev --prefix client                     # :3000
# Terminal 3: python msn_router.py 8007                       # :8007
```

## Grand Theft Cyberpunk Context
- Before launch/deploy work, read `SYSTEM_AI_AUDIT_SUMMARY.md` for current host, service, endpoint, and VRAM state.
- If service or endpoint gates fail, run `python3 scripts/ai_failure_triage.py` before restarting anything.
- Before GTC/Cyberpunk mod work, read `GTC_CONTEXT_INDEX.json` then `GTC_CONTEXT.md`.
- Read `GTC_DEPLOYMENT_PLAN.md` before copying source files into Steam Cyberpunk targets.
- Run `./scripts/bootstrap_gtc_cerebellum.sh` to refresh the source/deploy index and RAM context under `/dev/shm/gtc_cerebellum`.
- Use `./scripts/gtc_context_lookup.sh <term>` for fast RAM-first lookup across GTC source, deployment plans, and installed Cyberpunk files.
- Use `./scripts/reconcile_gtc_deployment.py` for dry-run/staged deployment reconciliation; real Steam writes require `--apply --yes`.
- Use `./scripts/verify_gtc_cerebellum.py` as the pass/fail readiness check after bootstrap.
- Treat `~/Desktop/AI` paths as source of truth and Steam `Cyberpunk 2077` paths as deployment targets.
- Use `deployment_comparison` in `GTC_CONTEXT_INDEX.json` before deciding a mod is missing or stale.

## MSN Agent Map (29 agents, 4 waves)
| Wave | Sephirot | Agents |
|------|----------|--------|
| 1 — Foundation | Keter → Chokmah → Binah | root, architect, server |
| 2 — Interface | Chesed → Gevurah → Tiferet → Netzach → Hod | client, bestiary, skills, market, lyra, living-sin |
| 3 — Infrastructure | Yesod → Malkuth | infra, migration |
| 4 — Metaconscious | Da'at → Binah → Hod → Tiferet → Malkuth → Netzach → Gevurah → Chokmah | msn, ngd, cerebellum, ouroboros, hermes-mcp, kairos, swarm, court, himalaya, antigravity, yeshua, scribe, analytics, worker, cortex, cyberpunk, nssp, **grokdata** |

## Key Architecture Decisions
- **NSSP Bridge Agent** (Da'at) — NSSP OS shell (status, roast, sovereignty, liberate), Nessie friendship (5 tiers, 6 Night City sighting locations, communion), Abyssal Assets crossover, CP2077 game event bridge, full integration health status
- **Cortex** replaces NGD/Cerebellum/Worker triad — unified EWMA-smoothed GPU telemetry with hysteresis routing (LOCAL/HYBRID/CLOUD)
- **Living Sin** persists to `server/runtime/gm/living_sin_state.json` — file-based IPC between game (:8000) and MSN (:8007)
- **Messages from living-sin** route through cortex for real nemotron-mini inference (no hardcoded responses)
- Cyberpunk telemetry reads live from `/home/tehlappy/Desktop/AI/invite/runtime/cyberpunk_telemetry.json`

## Environment
- System: Garuda Linux (Arch-based), RTX 3060 6GB, 62GB RAM
- Python: 3.14, venv at ~/Desktop/AI/Pub/.venv-pub/ (198 packages)
- Ollama: nemotron-mini (4.2B) for local inference, hermes3:8b + llama3.1:8b available
- Lyra: dialogue server at localhost:3211
- D: drive (Samsung 990 EVO 2TB): BitLocker encrypted — needs recovery key
