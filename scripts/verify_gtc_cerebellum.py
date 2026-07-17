#!/usr/bin/env python3
"""Verify Grand Theft Cyberpunk local cerebellum readiness."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAM_ROOT = Path("/dev/shm/gtc_cerebellum")
FALLBACK_ROOT = ROOT / "runtime/gtc_cerebellum"

REQUIRED_ROOT_FILES = [
    ROOT / "GTC_CONTEXT.md",
    ROOT / "GTC_CONTEXT_INDEX.json",
    ROOT / "GTC_DEPLOYMENT_PLAN.json",
    ROOT / "GTC_DEPLOYMENT_PLAN.md",
    ROOT / "scripts/bootstrap_gtc_cerebellum.sh",
    ROOT / "scripts/gtc_context_lookup.sh",
    ROOT / "scripts/index_gtc_context.py",
    ROOT / "scripts/prime_gtc_ram_context.sh",
    ROOT / "scripts/reconcile_gtc_deployment.py",
]

REQUIRED_FALLBACK_FILES = [
    FALLBACK_ROOT / "AGENT_README.md",
    FALLBACK_ROOT / "GTC_CONTEXT.md",
    FALLBACK_ROOT / "GTC_CONTEXT_INDEX.json",
    FALLBACK_ROOT / "GTC_DEPLOYMENT_PLAN.json",
    FALLBACK_ROOT / "GTC_DEPLOYMENT_PLAN.md",
    FALLBACK_ROOT / "manifest.tsv",
    FALLBACK_ROOT / "index/files.tsv",
    FALLBACK_ROOT / "index/extra_files.tsv",
    FALLBACK_ROOT / "index/steam_cyberpunk_files.tsv",
]

REQUIRED_RAM_FILES = [
    RAM_ROOT / "AGENT_README.md",
    RAM_ROOT / "GTC_CONTEXT_INDEX.json",
    RAM_ROOT / "GTC_DEPLOYMENT_PLAN.json",
    RAM_ROOT / "index/files.tsv",
    RAM_ROOT / "index/extra_files.tsv",
    RAM_ROOT / "index/hot_terms.rg",
    RAM_ROOT / "index/extra_hot_terms.rg",
    RAM_ROOT / "index/steam_cyberpunk_files.tsv",
]


def check_file(path: Path, label: str, required: bool = True) -> tuple[bool, dict]:
    exists = path.exists() and path.is_file()
    ok = exists or not required
    return ok, {"label": label, "path": str(path), "exists": exists, "bytes": path.stat().st_size if exists else 0}


def check_json(path: Path, keys: set[str]) -> tuple[bool, dict]:
    if not path.exists():
        return False, {"path": str(path), "error": "missing"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, {"path": str(path), "error": str(exc)}
    missing = sorted(keys - set(data))
    return not missing, {"path": str(path), "missing_keys": missing, "keys": sorted(data.keys())}


def check_reconcile_dry_run() -> tuple[bool, dict]:
    cmd = [
        sys.executable,
        str(ROOT / "scripts/reconcile_gtc_deployment.py"),
        "--plan-name",
        "primary_mod_source_to_installed_msn_integration",
        "--limit",
        "1",
    ]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    detail = {"returncode": proc.returncode, "stderr": proc.stderr.strip()}
    if proc.returncode != 0:
        return False, detail
    try:
        payload = json.loads(proc.stdout)
    except Exception as exc:
        detail["error"] = str(exc)
        return False, detail
    detail.update({
        "mode": payload.get("mode"),
        "action_count": payload.get("action_count"),
        "copied_count": payload.get("copied_count"),
        "missing_source_count": payload.get("missing_source_count"),
    })
    ok = (
        payload.get("mode") == "dry_run"
        and payload.get("action_count", 0) >= 1
        and payload.get("copied_count") == 0
        and payload.get("missing_source_count") == 0
    )
    return ok, detail


def main() -> int:
    checks: list[tuple[str, bool, dict]] = []

    for path in REQUIRED_ROOT_FILES:
        ok, detail = check_file(path, "root")
        checks.append(("root_file", ok, detail))

    for path in REQUIRED_FALLBACK_FILES:
        ok, detail = check_file(path, "fallback")
        checks.append(("fallback_file", ok, detail))

    ram_available = RAM_ROOT.exists()
    for path in REQUIRED_RAM_FILES:
        ok, detail = check_file(path, "ram", required=ram_available)
        checks.append(("ram_file", ok, detail))

    ok, detail = check_json(ROOT / "GTC_CONTEXT_INDEX.json", {"source_roots", "installed_roots", "deployment_comparison", "priority_read_order"})
    checks.append(("context_json", ok, detail))

    ok, detail = check_json(ROOT / "GTC_DEPLOYMENT_PLAN.json", {"plans", "safety", "purpose"})
    checks.append(("deployment_plan_json", ok, detail))

    ok, detail = check_reconcile_dry_run()
    checks.append(("reconcile_dry_run", ok, detail))

    failures = [item for item in checks if not item[1]]
    report = {
        "ok": not failures,
        "root": str(ROOT),
        "ram_root": str(RAM_ROOT),
        "ram_available": ram_available,
        "fallback_root": str(FALLBACK_ROOT),
        "checks": [{"name": name, "ok": ok, **detail} for name, ok, detail in checks],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
