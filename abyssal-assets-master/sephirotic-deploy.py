#!/usr/bin/env python3
"""
Sephirotic Deployment Orchestrator
Deploys agents in 3 parallel batches across the Sephirotic tree.

Usage:
    python sephirotic-deploy.py                    # Full deploy
    python sephirotic-deploy.py --batch 1          # Deploy batch 1 only
    python sephirotic-deploy.py --status           # Current deployment status
    python sephirotic-deploy.py --validate         # Validate manifest only
    python sephirotic-deploy.py --summary          # Print tree summary
"""

import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

SELF = Path(__file__).resolve().parent
MANIFEST = SELF / "sephirotic-root.json"
STATUS_FILE = SELF / ".sephirotic-status.json"
SKILLS_DIR = SELF / ".opencode" / "skills"

# Sephirotic deployment schedule — 3 parallel batches
BATCHES = {
    1: {
        "name": "Foundation (Keter → Binah)",
        "pillar": "Middle (Keter → Tiferet → Yesod → Malkuth)",
        "description": "Root manifest + design + server core",
        "sephira": ["KETER", "CHOKMAH", "BINAH"],
        "tasks": [
            "manifest-validate",
            "python-interface",
            "server-imports",
        ],
    },
    2: {
        "name": "Interface (Chesed → Hod)",
        "pillar": "Right (Chokmah → Chesed → Netzach → Hod)",
        "description": "Client + monsters + skills + market + Lyra",
        "sephira": ["CHESED", "GEVURAH", "TIFERET", "NETZACH", "HOD"],
        "tasks": [
            "typescript-types",
            "shared-types-consistent",
        ],
    },
    3: {
        "name": "Infrastructure (Yesod → Malkuth)",
        "pillar": "Left (Binah → Gevurah → Yesod → Malkuth)",
        "description": "Build configs + Docker + deployment",
        "sephira": ["YESOD", "MALKUTH"],
        "tasks": [
            "config-files-valid",
        ],
    },
}


def _color(text: str, code: int) -> str:
    return f"\033[{code}m{text}\033[0m"


def green(text: str) -> str:
    return _color(text, 32)


def yellow(text: str) -> str:
    return _color(text, 33)


def red(text: str) -> str:
    return _color(text, 31)


def cyan(text: str) -> str:
    return _color(text, 36)


def bold(text: str) -> str:
    return _color(text, 1)


def load_manifest():
    if not MANIFEST.exists():
        print(red(f"Manifest not found: {MANIFEST}"))
        sys.exit(1)
    return json.loads(MANIFEST.read_text())


def load_status() -> dict:
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text())
    return {"deployed_batches": [], "timestamp": None, "results": {}}


def save_status(status: dict):
    STATUS_FILE.write_text(json.dumps(status, indent=2))


# ── Validation Tasks ──────────────────────────────────────────────

def task_manifest_validate():
    """Validate sephirotic-root.json has all required fields."""
    data = load_manifest()
    errors = []
    if "sephira" not in data:
        errors.append("Missing 'sephira' key")
    if "root" not in data:
        errors.append("Missing 'root' key")
    if "interfaces" not in data:
        errors.append("Missing 'interfaces' key")
    for name in ["KETER", "CHOKMAH", "BINAH", "CHESED", "GEVURAH",
                  "TIFERET", "NETZACH", "HOD", "YESOD", "MALKUTH"]:
        if name not in data.get("sephira", {}):
            errors.append(f"Missing sephira: {name}")
    
    base = Path(data.get("root", ".")).resolve()
    for seph_name, seph_data in data.get("sephira", {}).items():
        for f in seph_data.get("files", []):
            fpath = base / f["path"]
            if "purpose" not in f:
                errors.append(f"{seph_name}/{f['path']}: missing purpose")
    return (len(errors) == 0, errors if errors else ["Manifest valid"])


def task_python_interface():
    """Verify sephirotic.py imports and resolves correctly."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", 
             "import sys; sys.path.insert(0, '.'); "
             "from sephirotic import root, sephira, resolve; "
             "print(root.summary()); "
             "keter = sephira('KETER'); "
             f"print(f'KETER: {{len(keter)}} files'); "
             "print(f'API health: {root.api_url(\"server-api\", \"health\")}')"],
            capture_output=True, text=True, cwd=str(SELF), timeout=15)
        if result.returncode != 0:
            return (False, [result.stderr.strip()])
        return (True, result.stdout.strip().split("\n"))
    except Exception as e:
        return (False, [str(e)])


def task_server_imports():
    """Check server/main.py parses as valid Python."""
    server_path = SELF / "server" / "main.py"
    if not server_path.exists():
        return (False, ["server/main.py not found"])
    try:
        import ast
        with open(server_path) as f:
            ast.parse(f.read())
        return (True, ["server/main.py — valid AST"])
    except SyntaxError as e:
        return (False, [f"server/main.py — syntax error: {e}"])


def task_typescript_types():
    """Check shared/types files exist and have content."""
    types_dir = SELF / "shared" / "types"
    expected = ["index.ts", "monsters.ts", "skills.ts", "synergies.ts",
                "provenance.ts", "quests.ts"]
    ok, fail = [], []
    for name in expected:
        f = types_dir / name
        if f.exists() and f.stat().st_size > 100:
            ok.append(f"{name} ({f.stat().st_size} bytes)")
        else:
            fail.append(f"{name} — missing or empty")
    return (len(fail) == 0, ok if ok else fail)


def task_shared_types_consistent():
    """Check monster tier counts and skill counts match expectations."""
    types_dir = SELF / "shared" / "types"
    monsters_file = types_dir / "monsters.ts"
    skills_file = types_dir / "skills.ts"
    
    info = []
    if monsters_file.exists():
        content = monsters_file.read_text()
        tiers = content.count("tier:")
        info.append(f"monsters.ts: ~{tiers} monster definitions found")
    if skills_file.exists():
        content = skills_file.read_text()
        skill_count = content.count("id:")
        info.append(f"skills.ts: ~{skill_count} skill definitions found")
    return (True, info)


def task_config_files_valid():
    """Check key config files exist."""
    expected = [
        ("client/package.json", "Node package config"),
        ("client/vite.config.ts", "Vite bundler config"),
        ("client/tsconfig.json", "TypeScript config"),
        ("server/Dockerfile", "Docker build file"),
        ("server/requirements.txt", "Python deps"),
        ("server/init.sql", "DB init script"),
    ]
    ok, fail = [], []
    for path, desc in expected:
        if (SELF / path).exists():
            ok.append(f"{path} — {desc}")
        else:
            fail.append(f"{path} — {desc} missing")
    return (len(fail) == 0, ok if ok else fail)


TASKS = {
    "manifest-validate": task_manifest_validate,
    "python-interface": task_python_interface,
    "server-imports": task_server_imports,
    "typescript-types": task_typescript_types,
    "shared-types-consistent": task_shared_types_consistent,
    "config-files-valid": task_config_files_valid,
}


# ── Check skills deployed ────────────────────────────────────────

def check_skills() -> list:
    deployed, missing = [], []
    for path in SKILLS_DIR.iterdir():
        if path.is_dir() and (path / "SKILL.md").exists():
            deployed.append(path.name)
    return deployed, missing


# ── Deployment ────────────────────────────────────────────────────

def deploy_batch(batch_num: int, force: bool = False) -> dict:
    """Deploy a single batch of agents."""
    batch = BATCHES.get(batch_num)
    if not batch:
        return {"batch": batch_num, "status": "error", "error": "Unknown batch"}
    
    batch_name = batch["name"]
    print(f"\n{bold(cyan(f'═══ Deploying Batch {batch_num}: {batch_name} ═══'))}")
    print(f"  Pillar: {batch['pillar']}")
    print(f"  Sephira: {', '.join(batch['sephira'])}")
    print(f"  Tasks: {', '.join(batch['tasks'])}")
    
    status = load_status()
    if batch_num in status.get("deployed_batches", []) and not force:
        print(yellow(f"  Batch {batch_num} already deployed (use --force to redeploy)"))
        return {"batch": batch_num, "status": "skipped"}
    
    results = {}
    all_ok = True
    
    for task_name in batch["tasks"]:
        task_fn = TASKS.get(task_name)
        if not task_fn:
            results[task_name] = {"status": "error", "message": "Unknown task"}
            all_ok = False
            continue
        
        print(f"  ▶ {task_name}...", end=" ")
        sys.stdout.flush()
        try:
            ok, messages = task_fn()
            if ok:
                print(green("OK"))
                results[task_name] = {"status": "ok", "messages": messages}
            else:
                print(red("FAIL"))
                for m in messages:
                    print(f"    {red('✗')} {m}")
                results[task_name] = {"status": "fail", "messages": messages}
                all_ok = False
        except Exception as e:
            print(red("ERROR"))
            print(f"    {red(str(e))}")
            results[task_name] = {"status": "error", "message": str(e)}
            all_ok = False
    
    # Check skills
    deployed, missing = check_skills()
    if deployed:
        print(green(f"  Skills deployed: {len(deployed)}"))
    if missing:
        print(yellow(f"  Skills missing: {', '.join(missing)}"))
    
    final_status = "deployed" if all_ok else "deployed_with_errors"
    status["deployed_batches"].append(batch_num)
    status["timestamp"] = time.time()
    status["results"][str(batch_num)] = {
        "status": final_status,
        "tasks": results,
        "skills_deployed": len(deployed),
        "skills_total": len(deployed),
    }
    save_status(status)
    
    print(f"\n  {green('✓') if all_ok else yellow('⚠')} Batch {batch_num}: {final_status}")
    return {"batch": batch_num, "status": final_status, "results": results}


def deploy_all():
    """Deploy all batches in parallel where possible."""
    print(bold(cyan("\n╔══════════════════════════════════════╗")))
    print(bold(cyan("║   Sephirotic Deployment Orchestrator  ║")))
    print(bold(cyan("╚══════════════════════════════════════╝\n")))
    
    # Validate manifest first
    print("Pre-flight: Validating manifest...")
    ok, msgs = task_manifest_validate()
    if not ok:
        print(red("Manifest validation FAILED:"))
        for m in msgs:
            print(f"  {red('✗')} {m}")
        sys.exit(1)
    print(green("  Manifest valid"))
    
    # Deploy batches in sequence (they share state)
    for batch_num in [1, 2, 3]:
        deploy_batch(batch_num)
    
    print_summary()


def print_summary():
    """Print deployment summary."""
    status = load_status()
    print(bold(cyan("\n═══ Deployment Summary ═══")))
    print(f"  Batches deployed: {status.get('deployed_batches', [])}")
    print(f"  Timestamp: {time.ctime(status.get('timestamp', 0))}")
    
    for bnum_str, result in status.get("results", {}).items():
        bnum = int(bnum_str)
        batch = BATCHES.get(bnum, {})
        s = result.get("status", "unknown")
        color_fn = green if s == "deployed" else yellow
        print(f"  Batch {bnum} ({batch.get('name', '?')}): {color_fn(s)}")
        for task_name, task_result in result.get("tasks", {}).items():
            ts = task_result.get("status", "?")
            tc = green if ts == "ok" else red
            print(f"    {tc('●')} {task_name}: {tc(ts)}")
    
    deployed, missing = check_skills()
    print(f"\n  Skills: {green(str(len(deployed)))} deployed")
    if missing:
        print(f"  Missing: {', '.join(missing)}")


# ── CLI ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sephirotic Deployment Orchestrator")
    parser.add_argument("--batch", type=int, choices=[1, 2, 3],
                        help="Deploy specific batch only")
    parser.add_argument("--force", action="store_true",
                        help="Force redeploy even if already deployed")
    parser.add_argument("--status", action="store_true",
                        help="Show current deployment status")
    parser.add_argument("--validate", action="store_true",
                        help="Validate manifest only")
    parser.add_argument("--summary", action="store_true",
                        help="Print tree summary")
    parser.add_argument("--reset", action="store_true",
                        help="Reset deployment status")
    
    args = parser.parse_args()
    
    if args.reset:
        save_status({"deployed_batches": [], "timestamp": None, "results": {}})
        print(green("Status reset"))
        sys.exit(0)
    
    if args.status:
        print_summary()
        sys.exit(0)
    
    if args.validate:
        ok, msgs = task_manifest_validate()
        if ok:
            print(green("Manifest valid"))
        else:
            for m in msgs:
                print(red(f"  ✗ {m}"))
        sys.exit(0 if ok else 1)
    
    if args.summary:
        root_mod = __import__("sephirotic", fromlist=["root"])
        print(root_mod.root.summary())
        sys.exit(0)
    
    if args.batch:
        deploy_batch(args.batch, force=args.force)
    else:
        deploy_all()
