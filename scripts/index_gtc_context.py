#!/usr/bin/env python3
"""Build a canonical Grand Theft Cyberpunk context map for local agents."""

from __future__ import annotations

import hashlib
import json
import os
import filecmp
from datetime import datetime, timezone
from pathlib import Path


HOME = Path.home()
AI_ROOT = Path(os.environ.get("AI_ROOT", HOME / "Desktop/AI")).expanduser()
STEAM_ROOT = Path(
    os.environ.get(
        "STEAM_CYBERPUNK_ROOT",
        HOME / ".local/share/Steam/steamapps/common/Cyberpunk 2077",
    )
).expanduser()
OUT = Path(__file__).resolve().parents[1] / "GTC_CONTEXT_INDEX.json"
DEPLOYMENT_PLAN_OUT = Path(__file__).resolve().parents[1] / "GTC_DEPLOYMENT_PLAN.json"
DEPLOYMENT_PLAN_MD = Path(__file__).resolve().parents[1] / "GTC_DEPLOYMENT_PLAN.md"

SOURCE_ROOTS = {
    "primary_mod_source": AI_ROOT / "abyssal-assets/cp2077_mods",
    "total_rebuild_source": AI_ROOT / "gtc_rebuild",
    "quest_source_data": AI_ROOT / "gtc_quests",
    "item_source_data": AI_ROOT / "gtc_items",
    "space_source_data": AI_ROOT / "gtc_space",
    "ngd_cyberpunk_integration": AI_ROOT / "invite/cyberpunk_integration",
    "pub_gtc_scripts": AI_ROOT / "Pub/scripts",
    "desktop_gtc_app": HOME / "Desktop/GrandTheftCyberpunk",
    "abyssal_gtc_webapp": AI_ROOT / "abyssal-assets/server/static/gtc",
    "gta_bridge_mods": AI_ROOT / "abyssal-assets/gta_mods",
}

INSTALLED_ROOTS = {
    "installed_redmod_mods": STEAM_ROOT / "r6/mods",
    "installed_redscripts": STEAM_ROOT / "r6/scripts",
    "installed_tweaks": STEAM_ROOT / "r6/tweaks",
    "installed_archives": STEAM_ROOT / "archive/pc/mod",
    "installed_cet_mods": STEAM_ROOT / "bin/x64/plugins/cyber_engine_tweaks/mods",
    "red4ext_plugins": STEAM_ROOT / "red4ext/plugins",
}

DEPLOYMENT_PAIRS = {
    "primary_mod_source_to_installed_msn_integration": (
        SOURCE_ROOTS["primary_mod_source"],
        STEAM_ROOT / "r6/mods/msn_integration",
        {},
    ),
    "total_rebuild_source_to_installed_gtc_total_rebuild": (
        SOURCE_ROOTS["total_rebuild_source"],
        STEAM_ROOT / "r6/mods/gtc_total_rebuild",
        {"redscripts/": "scripts/"},
    ),
}

EXTENSIONS = {
    ".reds",
    ".yaml",
    ".yml",
    ".toml",
    ".json",
    ".archive",
    ".xl",
    ".lua",
    ".cpmodproj",
    ".stringlist",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".tsx",
    ".py",
    ".sh",
    ".md",
    ".txt",
}

SKIP_DIRS = {".git", ".venv", ".venv-abyssal", ".venv-ngd", "venv", "__pycache__", "node_modules", "runtime"}


def sha256_prefix(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def iter_files(root: Path):
    if not root.exists():
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in EXTENSIONS or path.name in {"redmod.toml", "info.json"}:
            yield path


def summarize_root(root: Path) -> dict:
    files = list(iter_files(root) or [])
    by_ext: dict[str, int] = {}
    manifests: list[str] = []
    key_files: list[dict] = []

    for path in files:
        by_ext[path.suffix.lower() or path.name] = by_ext.get(path.suffix.lower() or path.name, 0) + 1
        if path.name in {"redmod.toml", "info.json"} or path.suffix.lower() == ".cpmodproj":
            manifests.append(str(path))
        if any(token in path.name.lower() for token in ("cerebellum", "cortex", "ngd", "gtc", "msn", "hell", "space")):
            key_files.append({"path": str(path), "size": path.stat().st_size})

    return {
        "path": str(root),
        "exists": root.exists(),
        "file_count": len(files),
        "by_extension": dict(sorted(by_ext.items())),
        "manifests": sorted(manifests),
        "key_files": sorted(key_files, key=lambda item: item["path"])[:200],
    }


def discover_git_repos(root: Path) -> list[dict]:
    repos: list[dict] = []
    if not root.exists():
        return repos

    for git_dir in sorted(root.glob("**/.git")):
        repo = git_dir.parent
        if any(part in SKIP_DIRS for part in repo.parts):
            continue
        if len(repo.relative_to(root).parts) > 4:
            continue

        branch = "unknown"
        commit = "unknown"
        try:
            branch = os.popen(f"git -C {repo!s} rev-parse --abbrev-ref HEAD 2>/dev/null").read().strip() or branch
            commit = os.popen(f"git -C {repo!s} rev-parse --short HEAD 2>/dev/null").read().strip() or commit
        except Exception:
            pass

        tags: list[str] = []
        repo_text = repo.as_posix().lower()
        if "gtc" in repo_text or "grand" in repo_text:
            tags.append("gtc")
        if "cyberpunk" in repo_text or "cp2077" in repo_text:
            tags.append("cyberpunk")
        if "abyssal-assets" in repo_text:
            tags.append("primary")

        repos.append({
            "name": repo.name,
            "path": str(repo),
            "branch": branch,
            "commit": commit,
            "tags": tags,
        })
    return repos


def normalize_relative_path(rel: str, path_map: dict[str, str]) -> str:
    for source_prefix, target_prefix in path_map.items():
        if rel.startswith(source_prefix):
            return target_prefix + rel[len(source_prefix):]
    return rel


def comparable_files(root: Path, path_map: dict[str, str] | None = None) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in iter_files(root) or []:
        rel = path.relative_to(root).as_posix()
        if path_map:
            rel = normalize_relative_path(rel, path_map)
        files[rel] = path
    return files


def compare_deployment(source: Path, target: Path, path_map: dict[str, str] | None = None) -> dict:
    source_files = comparable_files(source, path_map)
    target_files = comparable_files(target)
    missing = sorted(set(source_files) - set(target_files))
    extra = sorted(set(target_files) - set(source_files))
    common = sorted(set(source_files) & set(target_files))
    changed = []

    for rel in common:
        src = source_files[rel]
        dst = target_files[rel]
        if src.stat().st_size != dst.stat().st_size or not filecmp.cmp(src, dst, shallow=False):
            changed.append(rel)

    return {
        "source": str(source),
        "target": str(target),
        "source_to_target_path_map": path_map or {},
        "source_exists": source.exists(),
        "target_exists": target.exists(),
        "source_file_count": len(source_files),
        "target_file_count": len(target_files),
        "missing_in_target": missing[:500],
        "extra_in_target": extra[:500],
        "changed_in_target": changed[:500],
        "missing_count": len(missing),
        "extra_count": len(extra),
        "changed_count": len(changed),
    }


def denormalize_source_rel(target_rel: str, path_map: dict[str, str]) -> str:
    for source_prefix, target_prefix in path_map.items():
        if target_rel.startswith(target_prefix):
            return source_prefix + target_rel[len(target_prefix):]
    return target_rel


def build_deployment_plan(deployment: dict) -> dict:
    plan: dict[str, dict] = {}

    for name, cmp in deployment.items():
        source = Path(cmp["source"])
        target = Path(cmp["target"])
        path_map = cmp.get("source_to_target_path_map", {})

        copy_actions = []
        for rel in cmp["missing_in_target"]:
            source_rel = denormalize_source_rel(rel, path_map)
            copy_actions.append({
                "action": "copy_missing_source_to_target",
                "relative_path": rel,
                "source": str(source / source_rel),
                "target": str(target / rel),
            })

        update_actions = []
        for rel in cmp["changed_in_target"]:
            source_rel = denormalize_source_rel(rel, path_map)
            update_actions.append({
                "action": "review_then_update_changed_target",
                "relative_path": rel,
                "source": str(source / source_rel),
                "target": str(target / rel),
            })

        review_actions = []
        for rel in cmp["extra_in_target"]:
            review_actions.append({
                "action": "review_installed_only_file",
                "relative_path": rel,
                "target": str(target / rel),
            })

        plan[name] = {
            "source": cmp["source"],
            "target": cmp["target"],
            "path_map": path_map,
            "summary": {
                "copy_missing_count": cmp["missing_count"],
                "review_update_count": cmp["changed_count"],
                "review_installed_only_count": cmp["extra_count"],
            },
            "copy_missing": copy_actions,
            "review_update": update_actions,
            "review_installed_only": review_actions,
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Action plan for reconciling Grand Theft Cyberpunk source mods with installed Cyberpunk 2077 targets.",
        "safety": [
            "This file is a plan only; it does not copy or delete files.",
            "Copy missing source files only after confirming they belong in the target mod.",
            "Never delete installed-only files until they are classified as obsolete or generated output.",
            "Changed files require review because installed files may contain local deployment edits.",
        ],
        "plans": plan,
    }


def write_deployment_plan_markdown(plan: dict) -> None:
    lines = [
        "# Grand Theft Cyberpunk Deployment Plan",
        "",
        "Generated from `GTC_CONTEXT_INDEX.json`.",
        "",
        "This is a review plan, not an automatic deployment script.",
        "",
    ]

    for name, item in plan["plans"].items():
        summary = item["summary"]
        lines.extend([
            f"## {name}",
            "",
            f"- Source: `{item['source']}`",
            f"- Target: `{item['target']}`",
            f"- Copy missing: `{summary['copy_missing_count']}`",
            f"- Review changed: `{summary['review_update_count']}`",
            f"- Review installed-only: `{summary['review_installed_only_count']}`",
            "",
        ])

        for label, key in [
            ("First missing files", "copy_missing"),
            ("Changed files", "review_update"),
            ("Installed-only files", "review_installed_only"),
        ]:
            actions = item[key][:20]
            if not actions:
                continue
            lines.append(f"### {label}")
            lines.append("")
            for action in actions:
                lines.append(f"- `{action['relative_path']}`")
            lines.append("")

    DEPLOYMENT_PLAN_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    source = {name: summarize_root(path) for name, path in SOURCE_ROOTS.items()}
    installed = {name: summarize_root(path) for name, path in INSTALLED_ROOTS.items()}
    deployment = {
        name: compare_deployment(src, dst, path_map)
        for name, (src, dst, path_map) in DEPLOYMENT_PAIRS.items()
    }

    priority_read_order = [
        str(OUT),
        str(AI_ROOT / "abyssal-assets/GTC_CONTEXT.md"),
        str(AI_ROOT / "abyssal-assets/cp2077_mods"),
        str(HOME / "Desktop/GrandTheftCyberpunk"),
        str(AI_ROOT / "gtc_rebuild/redmod.toml"),
        str(AI_ROOT / "gtc_rebuild/redscripts"),
        str(AI_ROOT / "gtc_rebuild/tweakdb"),
        str(AI_ROOT / "gtc_quests/master_index.json"),
        str(AI_ROOT / "gtc_items/master_index.json"),
        str(AI_ROOT / "gtc_space/master_index.json"),
        str(STEAM_ROOT / "r6/mods/gtc_total_rebuild"),
        str(STEAM_ROOT / "r6/mods/msn_integration"),
        str(STEAM_ROOT / "r6/scripts/msn_integration"),
        str(STEAM_ROOT / "r6/tweaks/msn_integration"),
    ]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Canonical locator for Grand Theft Cyberpunk local AI context and Cyberpunk 2077 mod deployment.",
        "ai_root": str(AI_ROOT),
        "steam_cyberpunk_root": str(STEAM_ROOT),
        "priority_read_order": priority_read_order,
        "source_roots": source,
        "installed_roots": installed,
        "local_git_repos": discover_git_repos(AI_ROOT),
        "deployment_comparison": deployment,
        "notes": [
            "Treat Desktop/AI source roots as editable source of truth.",
            "Treat Steam Cyberpunk roots as installed deployment targets.",
            "Desktop/GrandTheftCyberpunk is the standalone local GTC web surface.",
            "Do not broad-search home when implementing GTC; read this index first.",
            "Run scripts/prime_gtc_ram_context.sh before agent work to expose RAM indexes under /dev/shm/gtc_cerebellum.",
        ],
    }
    deployment_plan = build_deployment_plan(deployment)

    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    DEPLOYMENT_PLAN_OUT.write_text(json.dumps(deployment_plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_deployment_plan_markdown(deployment_plan)
    print(f"Wrote {OUT}")
    print(f"Wrote {DEPLOYMENT_PLAN_OUT}")
    print(f"Wrote {DEPLOYMENT_PLAN_MD}")
    print(f"Source roots: {len(source)}")
    print(f"Installed roots: {len(installed)}")


if __name__ == "__main__":
    main()
