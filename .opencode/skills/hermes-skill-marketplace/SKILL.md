# Hermes Skill Marketplace

A self-hosted skill packaging, registry, and runtime discovery system synthesized from `skill_marketplace/registry/*.json`, `frontier_skill_injector.py`, and `set_codex_skill_mode.ps1`.

## Skill Packaging (.hermes-skill)

Each skill is a JSON file with:
- `skill_name` — unique identifier
- `codex_mode` — `"Performance"` or `"All"`
- `hermes_mode` — legacy Hermes bridge mode
- `path` — origin path
- `tags` — categorization labels
- `version` — semver string
- `integrity` — sha256 hash of file content

## Registry Structure

All skills live in `00_CORE_SERVICES/skill_marketplace/registry/`. The unified manifest at `runtime/skill-audit/skill-manifest.json` indexes all ~184 entries.

## Mode Switching

Use `set_codex_skill_mode.ps1` to toggle:
- **Performance mode**: only 43 explicit marketplace skills active
- **All mode**: all ~184 manifest entries discoverable

## Skill Injection Pipeline

`frontier_skill_injector.py`:
1. Scans registry for new/updated skills
2. Discovers Hermes skills by glob
3. Updates God Engine schema
4. Injects skill metadata into golem_diary.db
5. Pushes telemetry to NGD status

## Runtime Discovery

A Lilith endpoint scans `skill_marketplace/registry/*.json` at startup. Skills tagged with matching user intent context are loaded into active capabilities.
