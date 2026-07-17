# Grand Theft Cyberpunk Deployment Plan

Generated from `GTC_CONTEXT_INDEX.json`.

This is a review plan, not an automatic deployment script.

## primary_mod_source_to_installed_msn_integration

- Source: `/home/tehlappy/Desktop/Lilith/Core_Systems/AI/abyssal-assets/cp2077_mods`
- Target: `/mnt/d/Games/steamapps/common/Cyberpunk 2077/r6/mods/msn_integration`
- Copy missing: `208`
- Review changed: `86`
- Review installed-only: `53`

### First missing files

- `BUSINESS.md`
- `DESIGN_DOCS/PITCH_DECK.md`
- `DESIGN_DOCS/book_1_ground.md`
- `DESIGN_DOCS/book_2_water.md`
- `DESIGN_DOCS/book_3_fire.md`
- `DESIGN_DOCS/book_4_wind.md`
- `DESIGN_DOCS/book_5_void.md`
- `DESIGN_DOCS/file_manifest.md`
- `DESIGN_DOCS/metrics.md`
- `DESIGN_DOCS/pipeline.md`
- `DESIGN_DOCS/pitch_deck.md`
- `DESIGN_DOCS/space_quests.md`
- `README.md`
- `append_tweakdb.py`
- `archive/benchmark_results.json`
- `balance_tweakdb.py`
- `bench_cerebellum.py`
- `benchmark_results.json`
- `compile_wolvenkit.sh`
- `data/cyberpunk_skill_trees.json`

### Changed files

- `assets/models/model_production_manifest.yaml`
- `character/lilith_character.yaml`
- `hell_campaign.cpmodproj`
- `info.json`
- `localization/en.stringlist`
- `msn_integration.cpmodproj`
- `msn_integration.redmod.toml`
- `msn_integration.toml`
- `msn_magic_starwars.cpmodproj`
- `msn_multiplayer.toml`
- `msn_tweakdb.toml`
- `ngd_rnn_optimization.redmod.toml`
- `quests/abyssal_skill_tree_quests.yaml`
- `quests/guild/msn_guild_quests.toml`
- `quests/guild/msn_guild_quests.yaml`
- `quests/msn_narrative_arc.yaml`
- `redmod.toml`
- `scripts/abyssal_lyra_integration.reds`
- `scripts/cyberpunk_ngd_bridge.reds`
- `scripts/cyberpunk_ngd_integration.reds`

### Installed-only files

- `.deploy_manifest.json`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `build_msn.py`
- `msn_abyssal_crafting.reds`
- `msn_abyssal_skills.reds`
- `msn_business_management.reds`
- `msn_crafting_overhaul.reds`
- `msn_crime_syndicate.reds`
- `msn_crypto_wallet.reds`
- `msn_cyberpsychosis_ui.reds`
- `msn_drone_swarms.reds`
- `msn_five_rings_quest.reds`
- `msn_freighter_business.reds`
- `msn_gang_bases.reds`
- `msn_gang_management.reds`
- `msn_guilds_expansion.reds`
- `msn_horsemen_audio.reds`

## total_rebuild_source_to_installed_gtc_total_rebuild

- Source: `/home/tehlappy/Desktop/Lilith/Core_Systems/AI/gtc_rebuild`
- Target: `/mnt/d/Games/steamapps/common/Cyberpunk 2077/r6/mods/gtc_total_rebuild`
- Copy missing: `13`
- Review changed: `7`
- Review installed-only: `13`

### First missing files

- `scripts/cyberpunk_ngd_integration.reds`
- `scripts/lilith_campaign.reds`
- `scripts/lilith_easter_eggs.reds`
- `scripts/livingsin_time_blade.reds`
- `scripts/msn_cerebellum.reds`
- `scripts/msn_cortex_link.reds`
- `scripts/msn_five_rings_quest.reds`
- `scripts/msn_lyra_dialogue.reds`
- `scripts/msn_main_quest_the_void.reds`
- `scripts/msn_npc_ai.reds`
- `scripts/msn_ouroboros.reds`
- `scripts/msn_sephirotic_quests.reds`
- `scripts/nssp_bridge.reds`

### Changed files

- `redmod.toml`
- `tweakdb/gtc_easter_eggs.yaml`
- `tweakdb/gtc_items.yaml`
- `tweakdb/gtc_nessie_hats.yaml`
- `tweakdb/gtc_quests.yaml`
- `tweakdb/gtc_space_systems.yaml`
- `tweakdb/lilith_campaign_tweakdb.yaml`

### Installed-only files

- `redscripts/cyberpunk_ngd_integration.reds`
- `redscripts/lilith_campaign.reds`
- `redscripts/lilith_easter_eggs.reds`
- `redscripts/livingsin_time_blade.reds`
- `redscripts/msn_cerebellum.reds`
- `redscripts/msn_cortex_link.reds`
- `redscripts/msn_five_rings_quest.reds`
- `redscripts/msn_lyra_dialogue.reds`
- `redscripts/msn_main_quest_the_void.reds`
- `redscripts/msn_npc_ai.reds`
- `redscripts/msn_ouroboros.reds`
- `redscripts/msn_sephirotic_quests.reds`
- `redscripts/nssp_bridge.reds`

