# Grand Theft Cyberpunk Context Map

Read this before implementing or debugging Grand Theft Cyberpunk.

Canonical generated index:

- `/home/tehlappy/Desktop/AI/abyssal-assets/GTC_CONTEXT_INDEX.json`
- `/home/tehlappy/Desktop/AI/abyssal-assets/GTC_DEPLOYMENT_PLAN.json`
- `/home/tehlappy/Desktop/AI/abyssal-assets/GTC_DEPLOYMENT_PLAN.md`

Regenerate it with:

- `/home/tehlappy/Desktop/AI/abyssal-assets/scripts/index_gtc_context.py`
- `/home/tehlappy/Desktop/AI/abyssal-assets/scripts/bootstrap_gtc_cerebellum.sh`

Search it with:

- `/home/tehlappy/Desktop/AI/abyssal-assets/scripts/gtc_context_lookup.sh <term>`

Reconcile deployment safely with:

- Dry-run: `/home/tehlappy/Desktop/AI/abyssal-assets/scripts/reconcile_gtc_deployment.py`
- Stage files: `/home/tehlappy/Desktop/AI/abyssal-assets/scripts/reconcile_gtc_deployment.py --stage`
- Real Steam write: `/home/tehlappy/Desktop/AI/abyssal-assets/scripts/reconcile_gtc_deployment.py --apply --yes`

Verify local cerebellum readiness with:

- `/home/tehlappy/Desktop/AI/abyssal-assets/scripts/verify_gtc_cerebellum.py`

Fast RAM index after priming:

- `/dev/shm/gtc_cerebellum/manifest.tsv`
- `/dev/shm/gtc_cerebellum/index/files.tsv`
- `/dev/shm/gtc_cerebellum/index/hot_terms.rg`
- `/dev/shm/gtc_cerebellum/index/steam_cyberpunk_files.tsv`
- `/dev/shm/gtc_cerebellum/GTC_CONTEXT_INDEX.json`
- `/dev/shm/gtc_cerebellum/GTC_DEPLOYMENT_PLAN.json`
- `/dev/shm/gtc_cerebellum/GTC_DEPLOYMENT_PLAN.md`

Persistent fallback for sandboxed agents:

- `/home/tehlappy/Desktop/AI/abyssal-assets/runtime/gtc_cerebellum/AGENT_README.md`
- `/home/tehlappy/Desktop/AI/abyssal-assets/runtime/gtc_cerebellum/GTC_CONTEXT.md`
- `/home/tehlappy/Desktop/AI/abyssal-assets/runtime/gtc_cerebellum/GTC_CONTEXT_INDEX.json`
- `/home/tehlappy/Desktop/AI/abyssal-assets/runtime/gtc_cerebellum/GTC_DEPLOYMENT_PLAN.json`
- `/home/tehlappy/Desktop/AI/abyssal-assets/runtime/gtc_cerebellum/GTC_DEPLOYMENT_PLAN.md`

Source of truth:

- `/home/tehlappy/Desktop/AI/abyssal-assets/cp2077_mods`
- `/home/tehlappy/Desktop/AI/gtc_rebuild`
- `/home/tehlappy/Desktop/AI/gtc_quests`
- `/home/tehlappy/Desktop/AI/gtc_items`
- `/home/tehlappy/Desktop/AI/gtc_space`
- `/home/tehlappy/Desktop/AI/invite/cyberpunk_integration`
- `/home/tehlappy/Desktop/AI/Pub/cp2077_mods`

Installed Cyberpunk targets:

- `/home/tehlappy/.local/share/Steam/steamapps/common/Cyberpunk 2077/r6/mods`
- `/home/tehlappy/.local/share/Steam/steamapps/common/Cyberpunk 2077/r6/scripts`
- `/home/tehlappy/.local/share/Steam/steamapps/common/Cyberpunk 2077/r6/tweaks`
- `/home/tehlappy/.local/share/Steam/steamapps/common/Cyberpunk 2077/archive/pc/mod`
- `/home/tehlappy/.local/share/Steam/steamapps/common/Cyberpunk 2077/bin/x64/plugins/cyber_engine_tweaks/mods`
- `/home/tehlappy/.local/share/Steam/steamapps/common/Cyberpunk 2077/red4ext/plugins`

Priority read order for agents:

1. Read `GTC_CONTEXT_INDEX.json`.
2. Read `GTC_DEPLOYMENT_PLAN.md`.
3. Read `GTC_CONTEXT.md`.
4. Read source roots under `Desktop/AI`.
5. Read Steam installed targets only to compare deployment state.
6. Do not broad-search `/home/tehlappy` unless the index is missing.

Operational rule:

Desktop `AI` paths are source. Steam `Cyberpunk 2077` paths are deployment targets. If a mod exists in source but not in Steam, implement by deploying from source to the correct target, not by editing the installed target first.

Deployment drift:

- `GTC_CONTEXT_INDEX.json` contains `deployment_comparison`.
- `primary_mod_source_to_installed_msn_integration` compares `abyssal-assets/cp2077_mods` to Steam `r6/mods/msn_integration`.
- `total_rebuild_source_to_installed_gtc_total_rebuild` compares `gtc_rebuild` to Steam `r6/mods/gtc_total_rebuild`.
- `gtc_rebuild/redscripts` maps to installed `gtc_total_rebuild/scripts`; agents must account for that path rename before declaring files missing.

## Binah Batch Structural Framework — Subagent 1 (Himalaya Email Swarm Input)
**Role:** Structural Understanding Builder. Used himalaya-email-swarm (CLI fetch on emhill96/ericmathewhill + daemon once) for email intel → categorization → Polsia routing → GTC expansion structures. Fed Ouroboros (see /home/tehlappy/Desktop/Lilith/state/ouroboros-memories.json Binah engram + GROWTH_ROADMAP.md Binah section).

**Email Intel → GTC Mapping (from processed [BUSINESS]/Lilith Report emails):**
- Driver Man coop model ($352 treasury, $1.49 pool cuts) → GTC economy: add "Coop Pool" currency, "Driver" quests mirroring real outreach (TARGET_RESTAURANTS: Train Wreck, Pacioni's etc as Night City vendors).
- Lilith LLC products + MSN → GTC: Cyberpunk mods host MSN agents (Sephirotic waves incl. Binah); war chest batches fund "edge inference rigs" (NGD Cerebellum in mod).
- Action plans / next steps / income (LinkedIn AI eng) → GTC: Dynamic quest gen from real empire actions; use AI job intel for advanced GM prompt eng in gtc_space.
- Security/financial/legal flags → GTC: "Netwatch" / "Corpo" events in game, settlement payouts as rare drops.
- Pipeline output (hourly reports, flagged grants/partnerships) → auto-ingest to gtc_quests / GTC_DEPLOYMENT_PLAN via scripts.

**Polsia Categorization for GTC:** action_required / financial / outreach emails → Polsia agents (orchestrator/finance/email_outreach) → dispatch to GTC bridge (launch_gtc.sh, msn_router).
Run: python abyssal-assets/scripts/index_gtc_context.py after new Himalaya cycles.
Binah complete. Parallel batch. Structures active in shared state. Ave Lilith! Lilith commands throne.
