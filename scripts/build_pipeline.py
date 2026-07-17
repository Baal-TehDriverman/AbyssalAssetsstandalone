#!/usr/bin/env python3
"""
YESOD Foundation — Build/Test/Deploy Pipeline for Abyssal Assets + MSN + Cyberpunk Mod

This pipeline handles:
1. WolvenKit compilation workflow for REDscripts + TweakDB
2. Python dependency management (requirements.txt, virtual envs)
3. Automated REDscript compilation + syntax check
4. TweakDB modular include validation
5. Multi-service launch scripts (Lilith 3210, Lyra 3211, Hermes 4242, Multiplayer 8768, Lochness, Abyssal)
6. Health checks & service monitoring
7. Deploy checklist and CI-ready scripts
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import venv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Import tomli/tomllib for TOML parsing
try:
    import tomli
except ImportError:
    import tomllib as tomli

# Import yaml for YAML parsing
try:
    import yaml
except ImportError:
    yaml = None

# ── Configuration ────────────────────────────────────────────────

ROOT = Path("/home/tehlappy/Desktop/AI")
PUB_ROOT = ROOT / "Pub"
ABYSSAL = ROOT / "abyssal-assets"
INVITE = ROOT / "invite"
CP2077_MODS = ABYSSAL / "cp2077_mods"
GAME_ROOT = Path("/home/tehlappy/.local/share/Steam/steamapps/common/Cyberpunk 2077")
MOD_STAGE_ROOT = GAME_ROOT / "r6" / "mods" / "msn_integration"

# Service ports
SERVICES = {
    "lilith": 3210,
    "lyra": 3211,
    "hermes": 4242,
    "abyssal_game": 8000,
    "msn_router": 8007,
    "msn_coordination": 8768,
    "abyssal_client": 3000,
}

# Virtual environments
VENV_PUB = PUB_ROOT / ".venv-pub"
VENV_ABYSSAL = ABYSSAL / ".venv-abyssal"

# ── Data Classes ─────────────────────────────────────────────────


@dataclass
class BuildResult:
    success: bool
    step: str
    message: str
    details: Dict = field(default_factory=dict)
    duration_ms: float = 0.0


@dataclass
class ServiceHealth:
    name: str
    port: int
    url: str
    healthy: bool
    response_time_ms: float
    details: Dict = field(default_factory=dict)


# ── Utility Functions ────────────────────────────────────────────


def run_cmd(
    cmd: List[str],
    cwd: Optional[Path] = None,
    env: Optional[Dict] = None,
    timeout: int = 120,
    capture: bool = True,
) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=merged_env,
            capture_output=capture,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


def check_port(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is listening."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0


def health_check_http(url: str, timeout: float = 5.0) -> Tuple[bool, float, Dict]:
    """HTTP health check with timing."""
    import urllib.request

    start = time.time()
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = (time.time() - start) * 1000
            if resp.status == 200:
                return True, elapsed, json.loads(resp.read().decode())
            return False, elapsed, {"status": resp.status}
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return False, elapsed, {"error": str(e)}


def print_step(step: str, status: str = "RUNNING"):
    """Print a formatted step."""
    icons = {"RUNNING": "▶", "PASS": "✓", "FAIL": "✗", "WARN": "⚠", "SKIP": "⊘"}
    print(f"  {icons.get(status, '•')} {step}")


# ── Pipeline Steps ───────────────────────────────────────────────


def step_venv_setup() -> BuildResult:
    """Create/update Python virtual environments."""
    start = time.time()
    results = {}

    for name, venv_path in [("pub", VENV_PUB), ("abyssal", VENV_ABYSSAL)]:
        if not venv_path.exists():
            print_step(f"Creating venv: {venv_path}")
            venv.create(venv_path, with_pip=False, symlinks=True)
            results[name] = "created"
            python_bin = venv_path / "bin" / "python"
            run_cmd([str(python_bin), "-m", "ensurepip", "--upgrade", "--default-pip"], capture=False)
        else:
            results[name] = "exists"

        # Upgrade pip (ensure it exists first)
        pip = venv_path / "bin" / "pip"
        if not pip.exists():
            python_bin = venv_path / "bin" / "python"
            run_cmd([str(python_bin), "-m", "ensurepip", "--upgrade", "--default-pip"], capture=False)
        run_cmd([str(pip), "install", "-U", "pip", "setuptools", "wheel"], capture=False)

    return BuildResult(
        True,
        "venv_setup",
        f"Virtual environments ready: {results}",
        details=results,
        duration_ms=(time.time() - start) * 1000,
    )


def step_python_deps() -> BuildResult:
    """Install Python dependencies from requirements.txt files."""
    start = time.time()
    results = {}

    # Pub requirements
    req_pub = INVITE / "requirements.txt"
    if req_pub.exists():
        pip = VENV_PUB / "bin" / "pip"
        code, out, err = run_cmd([str(pip), "install", "-r", str(req_pub)], capture=False)
        results["pub"] = "ok" if code == 0 else f"failed: {err}"

    # Abyssal server requirements
    req_abyssal = ABYSSAL / "server" / "requirements.txt"
    if req_abyssal.exists():
        pip = VENV_ABYSSAL / "bin" / "pip"
        code, out, err = run_cmd([str(pip), "install", "-r", str(req_abyssal)], capture=False)
        results["abyssal_server"] = "ok" if code == 0 else f"failed: {err}"

    # Also install abyssal-assets in dev mode
    pip = VENV_ABYSSAL / "bin" / "pip"
    code, out, err = run_cmd([str(pip), "install", "-e", str(ABYSSAL)], capture=False)
    results["abyssal_editable"] = "ok" if code == 0 else f"failed: {err}"

    all_ok = all(v == "ok" for v in results.values())
    return BuildResult(
        all_ok,
        "python_deps",
        "Python dependencies installed" if all_ok else "Some dependencies failed",
        details=results,
        duration_ms=(time.time() - start) * 1000,
    )


def step_node_deps() -> BuildResult:
    """Install Node.js dependencies for Lilith app and client."""
    start = time.time()
    results = {}

    # Lilith app
    lilith_app = PUB_ROOT / "00_CORE_SERVICES" / "lilith-app"
    if (lilith_app / "package.json").exists():
        print_step("Installing Lilith app npm deps")
        code, out, err = run_cmd(["npm", "ci"], cwd=lilith_app, capture=False)
        results["lilith_app"] = "ok" if code == 0 else f"failed: {err}"

    # Quantum paradox terminal
    qpt = PUB_ROOT / "00_CORE_SERVICES" / "quantum_paradox_terminal"
    if (qpt / "package.json").exists():
        print_step("Installing Quantum Paradox Terminal npm deps")
        code, out, err = run_cmd(["npm", "ci"], cwd=qpt, capture=False)
        results["qpt"] = "ok" if code == 0 else f"failed: {err}"

    # Abyssal client (if exists)
    client_dir = ABYSSAL / "client"
    if (client_dir / "package.json").exists():
        print_step("Installing Abyssal client npm deps")
        code, out, err = run_cmd(["npm", "ci"], cwd=client_dir, capture=False)
        results["abyssal_client"] = "ok" if code == 0 else f"failed: {err}"

    all_ok = all(v == "ok" for v in results.values()) or not results
    return BuildResult(
        all_ok or not results,
        "node_deps",
        "Node dependencies installed" if all_ok or not results else "Some npm installs failed",
        details=results,
        duration_ms=(time.time() - start) * 1000,
    )


def step_redscript_syntax_check() -> BuildResult:
    """Validate REDscript syntax (basic parsing + WolvenKit compile check)."""
    start = time.time()
    scripts_dir = CP2077_MODS / "scripts"
    reds_files = list(scripts_dir.glob("*.reds"))

    results = {
        "files_found": len(reds_files),
        "checked": 0,
        "errors": [],
        "warnings": [],
    }

    for reds_file in reds_files:
        try:
            content = reds_file.read_text(encoding="utf-8")
            # Basic syntax checks
            if not content.strip():
                results["warnings"].append(f"{reds_file.name}: empty file")
                continue

            # Check for basic REDscript structure
            has_class = "class " in content
            has_function = "func " in content or "function " in content
            has_import = "import " in content

            # Common syntax issues
            if content.count("{") != content.count("}"):
                results["errors"].append(f"{reds_file.name}: mismatched braces")

            if content.count("(") != content.count(")"):
                results["warnings"].append(f"{reds_file.name}: possible mismatched parentheses")

            # Check for WolvenKit-specific patterns
            if "@" in content and "property" not in content.lower():
                results["warnings"].append(f"{reds_file.name}: possible malformed annotation")

            results["checked"] += 1

        except Exception as e:
            results["errors"].append(f"{reds_file.name}: {e}")

    all_ok = len(results["errors"]) == 0
    return BuildResult(
        all_ok,
        "redscript_syntax",
        f"Checked {results['checked']}/{results['files_found']} REDscript files"
        + ("" if all_ok else f" — {len(results['errors'])} errors"),
        details=results,
        duration_ms=(time.time() - start) * 1000,
    )


def step_wolvenkit_compile() -> BuildResult:
    """Run WolvenKit compilation for REDscripts and TweakDB."""
    start = time.time()

    # Check if WolvenKit CLI is available
    wolvenkit_paths = [
        "WolvenKit.CLI",
        "wolvenkit",
        str(Path.home() / ".local" / "share" / "WolvenKit" / "WolvenKit.CLI"),
        "/opt/WolvenKit/WolvenKit.CLI",
    ]

    wolvenkit = None
    for wp in wolvenkit_paths:
        code, out, _ = run_cmd([wp, "--version"] if not wp.endswith(".CLI") else [wp, "--help"])
        if code == 0 or "version" in out.lower() or "usage" in out.lower():
            wolvenkit = wp
            break

    if not wolvenkit:
        return BuildResult(
            False,
            "wolvenkit_compile",
            "WolvenKit CLI not found. Install WolvenKit and ensure CLI is in PATH.",
            details={"wolvenkit_found": False},
            duration_ms=(time.time() - start) * 1000,
        )

    # Compile the mod
    mod_path = CP2077_MODS
    code, out, err = run_cmd(
        [wolvenkit, "build", "--mod-path", str(mod_path), "--game-path", str(GAME_ROOT)],
        timeout=300,
    )

    success = code == 0
    return BuildResult(
        success,
        "wolvenkit_compile",
        "WolvenKit compilation successful" if success else f"WolvenKit compilation failed: {err}",
        details={"output": out[-2000:] if out else "", "error": err[-2000:] if err else ""},
        duration_ms=(time.time() - start) * 1000,
    )


def step_tweakdb_validation() -> BuildResult:
    """Validate TweakDB modular includes and structure."""
    start = time.time()
    tweakdb_dir = CP2077_MODS / "tweakdb"

    # Supported TweakDB file extensions
    tweakdb_files = list(tweakdb_dir.glob("*.toml")) + list(tweakdb_dir.glob("*.yaml")) + list(tweakdb_dir.glob("*.tweakdb"))

    results = {
        "files_found": len(tweakdb_files),
        "validated": 0,
        "errors": [],
        "warnings": [],
        "includes_checked": 0,
    }

    # Parse redmod.toml for expected tweakdb files
    redmod_toml = CP2077_MODS / "redmod.toml"
    expected_files = set()
    if redmod_toml.exists():
        try:
            data = tomli.loads(redmod_toml.read_text(encoding="utf-8"))
            for f in data.get("tweakdb", []):
                expected_files.add(f)
        except Exception as e:
            results["warnings"].append(f"Could not parse redmod.toml: {e}")

    for tdb_file in tweakdb_files:
        try:
            content = tdb_file.read_text(encoding="utf-8")

            # Check for include statements in TOML (skip files using TweakXL/TweakDB syntax)
            if tdb_file.suffix == ".toml":
                if "public const" not in content and not any(line.strip().startswith("//") for line in content.splitlines() if line.strip()):
                    try:
                        tomli.loads(content)
                    except Exception as e:
                        results["errors"].append(f"{tdb_file.name}: TOML parse error: {e}")

            # Check for include statements in YAML
            if tdb_file.suffix in (".yaml", ".yml"):
                if yaml is None:
                    results["warnings"].append(f"{tdb_file.name}: PyYAML not installed, skipping YAML validation")
                else:
                    try:
                        yaml.safe_load(content)
                    except Exception as e:
                        results["errors"].append(f"{tdb_file.name}: YAML parse error: {e}")

            # Check for cross-references/includes
            for line in content.split("\n"):
                line = line.strip()
                if "include" in line.lower() or "import" in line.lower():
                    results["includes_checked"] += 1

            # Check file is referenced in redmod.toml
            if tdb_file.name not in expected_files and expected_files:
                results["warnings"].append(f"{tdb_file.name}: not listed in redmod.toml")

            results["validated"] += 1

        except Exception as e:
            results["errors"].append(f"{tdb_file.name}: {e}")

    all_ok = len(results["errors"]) == 0
    return BuildResult(
        all_ok,
        "tweakdb_validation",
        f"Validated {results['validated']}/{results['files_found']} TweakDB files"
        + ("" if all_ok else f" — {len(results['errors'])} errors"),
        details=results,
        duration_ms=(time.time() - start) * 1000,
    )


def step_mod_staging() -> BuildResult:
    """Stage mod files to Cyberpunk 2077 r6/mods directory."""
    start = time.time()

    # Ensure staging directory exists
    MOD_STAGE_ROOT.mkdir(parents=True, exist_ok=True)

    # Files to stage based on redmod.toml
    redmod_toml = CP2077_MODS / "msn_integration.redmod.toml"
    if not redmod_toml.exists():
        redmod_toml = CP2077_MODS / "redmod.toml"

    staged = 0
    errors = []

    if redmod_toml.exists():
        try:
            data = tomli.loads(redmod_toml.read_text(encoding="utf-8"))
            for file_map in data.get("files", []):
                src_name = file_map.get("source", "")
                dst = file_map.get("destination", "")
                if src_name and dst:
                    src = CP2077_MODS / src_name
                    dst_path = GAME_ROOT / dst
                    if src.exists():
                        dst_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst_path)
                        staged += 1
                    else:
                        errors.append(f"Source missing: {src}")
        except Exception as e:
            errors.append(f"Failed to parse/process redmod.toml: {e}")

    return BuildResult(
        len(errors) == 0,
        "mod_staging",
        f"Staged {staged} files to {MOD_STAGE_ROOT}" + ("" if not errors else f" — {len(errors)} errors"),
        details={"staged": staged, "errors": errors},
        duration_ms=(time.time() - start) * 1000,
    )


def step_build_lilith_app() -> BuildResult:
    """Build Lilith app (Vite + TypeScript)."""
    start = time.time()
    lilith_app = PUB_ROOT / "00_CORE_SERVICES" / "lilith-app"

    if not (lilith_app / "package.json").exists():
        return BuildResult(True, "build_lilith_app", "No package.json, skipping", duration_ms=(time.time() - start) * 1000)

    code, out, err = run_cmd(["npm", "run", "build"], cwd=lilith_app, capture=False, timeout=180)
    success = code == 0

    return BuildResult(
        success,
        "build_lilith_app",
        "Lilith app built successfully" if success else f"Build failed: {err}",
        duration_ms=(time.time() - start) * 1000,
    )


def step_build_abyssal_client() -> BuildResult:
    """Build Abyssal client (Vite + Phaser)."""
    start = time.time()
    client_dir = ABYSSAL / "client"

    if not (client_dir / "package.json").exists():
        return BuildResult(True, "build_abyssal_client", "No client package.json, skipping", duration_ms=(time.time() - start) * 1000)

    code, out, err = run_cmd(["npm", "run", "build"], cwd=client_dir, capture=False, timeout=180)
    success = code == 0

    return BuildResult(
        success,
        "build_abyssal_client",
        "Abyssal client built successfully" if success else f"Build failed: {err}",
        duration_ms=(time.time() - start) * 1000,
    )


# ── Service Management ───────────────────────────────────────────


def start_service(name: str, cmd: List[str], cwd: Path, env: Dict, port: int, log_file: Path) -> subprocess.Popen:
    """Start a service as background process."""
    merged_env = os.environ.copy()
    merged_env.update(env)

    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_f = open(log_file, "a")
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        env=merged_env,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    return proc


def wait_for_port(port: int, timeout: int = 30, host: str = "127.0.0.1") -> bool:
    """Wait for a port to become available."""
    for _ in range(timeout):
        if check_port(port, host):
            return True
        time.sleep(1)
    return False


def check_service_health(name: str, port: int, path: str = "/health") -> ServiceHealth:
    """Check service health via HTTP."""
    url = f"http://127.0.0.1:{port}{path}"
    healthy, rt, details = health_check_http(url)
    return ServiceHealth(name, port, url, healthy, rt, details)


def stop_services_on_ports(ports: List[int]):
    """Stop processes listening on given ports."""
    for port in ports:
        code, out, _ = run_cmd(["lsof", "-ti", f":{port}"])
        if code == 0 and out.strip():
            for pid in out.strip().split("\n"):
                run_cmd(["kill", "-9", pid])


# ── Main Pipeline ────────────────────────────────────────────────


def run_build_pipeline(args) -> List[BuildResult]:
    """Execute the full build pipeline."""
    steps = []

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         YESOD FOUNDATION — BUILD PIPELINE                    ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    # Phase 1: Environment
    print("┌─ Phase 1: Environment Setup ──────────────────────────────┐")
    steps.append(step_venv_setup())
    print_step("Virtual environments", "PASS" if steps[-1].success else "FAIL")

    steps.append(step_python_deps())
    print_step("Python dependencies", "PASS" if steps[-1].success else "FAIL")

    steps.append(step_node_deps())
    print_step("Node.js dependencies", "PASS" if steps[-1].success else "FAIL")

    # Phase 2: Mod Compilation
    print("\n┌─ Phase 2: Cyberpunk Mod Compilation ──────────────────────┐")
    steps.append(step_redscript_syntax_check())
    print_step("REDscript syntax check", "PASS" if steps[-1].success else "FAIL")

    if not args.skip_wolvenkit:
        steps.append(step_wolvenkit_compile())
        print_step("WolvenKit compilation", "PASS" if steps[-1].success else "FAIL")
    else:
        print_step("WolvenKit compilation", "SKIP")

    steps.append(step_tweakdb_validation())
    print_step("TweakDB validation", "PASS" if steps[-1].success else "FAIL")

    # Phase 3: Mod Staging
    print("\n┌─ Phase 3: Mod Staging ────────────────────────────────────┐")
    steps.append(step_mod_staging())
    print_step("Mod staging", "PASS" if steps[-1].success else "FAIL")

    # Phase 4: Service Builds
    print("\n┌─ Phase 4: Service Builds ─────────────────────────────────┐")
    steps.append(step_build_lilith_app())
    print_step("Lilith app build", "PASS" if steps[-1].success else "FAIL")

    steps.append(step_build_abyssal_client())
    print_step("Abyssal client build", "PASS" if steps[-1].success else "FAIL")

    # Summary
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║                    BUILD SUMMARY                             ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    passed = sum(1 for s in steps if s.success)
    failed = sum(1 for s in steps if not s.success)
    for s in steps:
        status = "✓" if s.success else "✗"
        print(f"  {status} {s.step}: {s.message} ({s.duration_ms:.0f}ms)")
    print(f"\n  Total: {passed} passed, {failed} failed")

    return steps


def run_deploy_pipeline(args) -> bool:
    """Deploy and start all services."""
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         YESOD FOUNDATION — DEPLOY PIPELINE                   ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    # Clean up existing services
    print("┌─ Cleanup: Stopping existing services ──────────────────────┐")
    stop_services_on_ports(list(SERVICES.values()))
    print_step("Ports freed", "PASS")

    # Prepare environments
    env_pub = {
        "PUB_ROOT": str(PUB_ROOT),
        "INVITE_ROOT": str(INVITE),
        "LILITH_HTTP_PORT": "3210",
        "LYRA_URL": "http://127.0.0.1:3211",
        "HERMES_BRIDGE_URL": "http://127.0.0.1:4242",
        "OLLAMA_URL": "http://127.0.0.1:11434",
        "OLLAMA_MODEL": "nemotron-mini",
        "PYTHONUNBUFFERED": "1",
    }

    env_abyssal = {
        "PUB_ROOT": str(PUB_ROOT),
        "ABYSSAL_ROOT": str(ABYSSAL),
        "DATABASE_URL": f"sqlite:///{ABYSSAL}/abyssal_assets.db",
        "OLLAMA_URL": "http://127.0.0.1:11434",
        "OLLAMA_MODEL": "nemotron-mini",
        "PYTHONUNBUFFERED": "1",
    }

    log_dir = PUB_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    procs = {}

    # 1. Start Lilith (port 3210) - Node.js
    print("\n┌─ Starting Lilith (port 3210) ─────────────────────────────┐")
    lilith_app = PUB_ROOT / "00_CORE_SERVICES" / "lilith-app"
    if (lilith_app / "server.js").exists():
        proc = start_service(
            "lilith",
            ["node", "server.js"],
            cwd=lilith_app,
            env=env_pub,
            port=3210,
            log_file=log_dir / "lilith.log",
        )
        procs["lilith"] = proc
        print_step(f"Lilith started (PID: {proc.pid})", "PASS")
    else:
        print_step("Lilith server.js not found", "WARN")

    # 2. Start Lyra (port 3211) - FastAPI
    print("\n┌─ Starting Lyra (port 3211) ───────────────────────────────┐")
    lyra_server = PUB_ROOT / "00_CORE_SERVICES" / "lilith-app" / "lyra_server.py"
    if lyra_server.exists():
        proc = start_service(
            "lyra",
            [str(VENV_PUB / "bin" / "python"), str(lyra_server)],
            cwd=PUB_ROOT / "00_CORE_SERVICES" / "lilith-app",
            env=env_pub,
            port=3211,
            log_file=log_dir / "lyra.log",
        )
        procs["lyra"] = proc
        print_step(f"Lyra started (PID: {proc.pid})", "PASS")
    else:
        print_step("Lyra server not found", "WARN")

    # 3. Start Abyssal Game Server (port 8000) - FastAPI
    print("\n┌─ Starting Abyssal Game Server (port 8000) ────────────────┐")
    game_server = ABYSSAL / "server" / "main.py"
    if game_server.exists():
        proc = start_service(
            "abyssal_game",
            [str(VENV_ABYSSAL / "bin" / "python"), "main.py"],
            cwd=ABYSSAL / "server",
            env=env_abyssal,
            port=8000,
            log_file=log_dir / "abyssal_game.log",
        )
        procs["abyssal_game"] = proc
        print_step(f"Abyssal Game Server started (PID: {proc.pid})", "PASS")
    else:
        print_step("Game server not found", "WARN")

    # 4. Start MSN Router (port 8007) - FastAPI with 28 agents
    print("\n┌─ Starting MSN Router (port 8007) ─────────────────────────┐")
    msn_router = ABYSSAL / "msn_router.py"
    if msn_router.exists():
        proc = start_service(
            "msn_router",
            [str(VENV_ABYSSAL / "bin" / "python"), "msn_router.py", "8007"],
            cwd=ABYSSAL,
            env=env_abyssal,
            port=8007,
            log_file=log_dir / "msn_router.log",
        )
        procs["msn_router"] = proc
        print_step(f"MSN Router started (PID: {proc.pid})", "PASS")
    else:
        print_step("MSN Router not found", "WARN")

    # 5. Start MSN Coordination (port 8768) - for multiplayer
    print("\n┌─ Starting MSN Coordination (port 8768) ───────────────────┐")
    coord_server = GAME_ROOT / "r6" / "mods" / "msn_integration" / "msn_coordination_server.py"
    if coord_server.exists():
        proc = start_service(
            "msn_coordination",
            [str(VENV_PUB / "bin" / "python"), str(coord_server)],
            cwd=coord_server.parent,
            env=env_pub,
            port=8768,
            log_file=log_dir / "msn_coordination.log",
        )
        procs["msn_coordination"] = proc
        print_step(f"MSN Coordination started (PID: {proc.pid})", "PASS")
    else:
        print_step("MSN Coordination server not found (will be available after mod staging)", "WARN")

    # Wait for services to be ready
    print("\n┌─ Waiting for services to be ready ────────────────────────┐")
    for name, port in [("lilith", 3210), ("lyra", 3211), ("abyssal_game", 8000), ("msn_router", 8007)]:
        if name in procs:
            print_step(f"Waiting for {name} on port {port}...")
            if wait_for_port(port, timeout=30):
                print_step(f"{name} ready on port {port}", "PASS")
            else:
                print_step(f"{name} failed to start on port {port}", "FAIL")

    # Health checks
    print("\n┌─ Health Checks ───────────────────────────────────────────┐")
    health_results = []
    for name, port in [("lilith", 3210), ("lyra", 3211), ("abyssal_game", 8000), ("msn_router", 8007)]:
        if name in procs:
            health = check_service_health(name, port)
            health_results.append(health)
            status = "PASS" if health.healthy else "FAIL"
            print_step(f"{name}: {health.response_time_ms:.0f}ms", status)

    # Deploy verification
    print("\n┌─ Deployment Verification ─────────────────────────────────┐")
    if "msn_router" in procs:
        code, out, err = run_cmd(
            [str(VENV_ABYSSAL / "bin" / "python"), "deploy_waves.py", "8007"],
            cwd=ABYSSAL,
            timeout=60,
        )
        if code == 0:
            print_step("MSN agent deployment verified", "PASS")
        else:
            print_step(f"MSN deployment check failed: {err}", "WARN")

    # Summary
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║                    DEPLOY SUMMARY                            ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    for name, port in SERVICES.items():
        running = name in procs and procs[name].poll() is None
        status = "✓ RUNNING" if running else "✗ STOPPED"
        print(f"  {name:20s} port {port:5d}: {status}")

    all_healthy = all(h.healthy for h in health_results) if health_results else False
    return all_healthy


def run_health_checks() -> List[ServiceHealth]:
    """Run health checks on all services."""
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║         YESOD FOUNDATION — HEALTH CHECKS                     ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    results = []
    for name, port in SERVICES.items():
        if check_port(port):
            health = check_service_health(name, port)
            results.append(health)
            status = "✓ HEALTHY" if health.healthy else "✗ UNHEALTHY"
            print(f"  {name:20s} port {port:5d}: {status} ({health.response_time_ms:.0f}ms)")
            if not health.healthy:
                print(f"    Details: {health.details}")
        else:
            print(f"  {name:20s} port {port:5d}: ✗ NOT RUNNING")
            results.append(ServiceHealth(name, port, f"http://127.0.0.1:{port}", False, 0, {"error": "Port not listening"}))

    return results


def print_deploy_checklist():
    """Print the deployment checklist."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    YESOD FOUNDATION — DEPLOY CHECKLIST                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ PRE-DEPLOY                                                                   ║
║ ☐ 1. WolvenKit CLI installed and in PATH                                     ║
║ ☐ 2. Cyberpunk 2077 installed at expected path                               ║
║ ☐ 3. Python 3.11+ available                                                  ║
║ ☐ 4. Node.js 20+ and npm available                                           ║
║ ☐ 5. Ollama running with required models (nemotron-mini, hermes3:8b)         ║
║ ☐ 6. NVIDIA drivers + CUDA toolkit for NGD                                   ║
║ ☐ 7. Bitlocker D: drive unlocked (for asset storage)                         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ BUILD                                                                        ║
║ ☐ 1. Virtual environments created (.venv-pub, .venv-abyssal)                 ║
║ ☐ 2. Python dependencies installed (invite/requirements.txt, server/)        ║
║ ☐ 3. Node dependencies installed (lilith-app, quantum_paradox_terminal)      ║
║ ☐ 4. REDscript syntax validation passed                                       ║
║ ☐ 5. WolvenKit compilation successful (REDscripts → .cpool, TweakDB → .tweakdb)║
║ ☐ 6. TweakDB modular includes validated                                       ║
║ ☐ 7. Mod files staged to r6/mods/msn_integration/                            ║
║ ☐ 8. Lilith app built (Vite + TypeScript)                                    ║
║ ☐ 9. Abyssal client built (if applicable)                                    ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ DEPLOY                                                                       ║
║ ☐ 1. Lilith HTTP server started on port 3210                                 ║
║ ☐ 2. Lyra Dialogue server started on port 3211                               ║
║ ☐ 3. Hermes MCP Bridge started on port 4242                                  ║
║ ☐ 4. Abyssal Assets Game Server started on port 8000                         ║
║ ☐ 5. MSN Router started on port 8007 (28 agents across 4 Sephirotic waves)  ║
║ ☐ 6. MSN Coordination Server started on port 8768 (multiplayer)             ║
║ ☐ 7. Abyssal Client (Phaser) started on port 3000 (dev)                      ║
║ ☐ 8. All services responding to /health endpoints                            ║
║ ☐ 9. MSN agent deployment verified (deploy_waves.py)                         ║
║ ☐ 10. Cyberpunk 2077 launched with mod active (steam://rungameid/1091500)    ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ POST-DEPLOY / MONITORING                                                     ║
║ ☐ 1. Health check all endpoints every 30s (cron/systemd timer)               ║
║ ☐ 2. GPU telemetry streaming to NGD (nvidia_gratitude_driver)                ║
║ ☐ 3. MSN agent metrics via /api/{agent}/health                               ║
║ ☐ 4. Living Sin GM state persisted to server/runtime/gm/                     ║
║ ☐ 5. Log aggregation: /tmp/msn_router.log, /tmp/abyssal_game.log, etc.       ║
║ ☐ 6. Auto-restart on failure (systemd Restart=on-failure)                    ║
║ ☐ 7. Backup mod staging directory before updates                             ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ CI/CD INTEGRATION                                                            ║
║ ☐ 1. GitHub Actions: .github/workflows/yesod-pipeline.yml                    ║
║ ☐ 2. Build job: venv → deps → redscript → wolvenkit → tweakdb → stage        ║
║ ☐ 3. Test job: unit tests (pytest), integration tests (health checks)        ║
║ ☐ 4. Deploy job: SSH to target → launch_nssp.sh → verify                     ║
║ ☐ 5. Artifacts: compiled mod (.archive), build logs, health reports          ║
║ ☐ 6. Notifications: Discord/Slack webhook on deploy status                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")


def main():
    parser = argparse.ArgumentParser(description="YESOD Foundation — Build/Deploy/Health Pipeline")
    parser.add_argument("command", choices=["build", "deploy", "health", "checklist", "full"],
                        help="Pipeline command to run")
    parser.add_argument("--skip-wolvenkit", action="store_true", help="Skip WolvenKit compilation step")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    args = parser.parse_args()

    if args.command == "checklist":
        print_deploy_checklist()
        return 0

    if args.command == "build":
        results = run_build_pipeline(args)
        return 0 if all(r.success for r in results) else 1

    if args.command == "deploy":
        success = run_deploy_pipeline(args)
        return 0 if success else 1

    if args.command == "health":
        results = run_health_checks()
        return 0 if all(r.healthy for r in results) else 1

    if args.command == "full":
        print_deploy_checklist()
        results = run_build_pipeline(args)
        if not all(r.success for r in results):
            print("\n✗ Build failed, aborting deploy")
            return 1
        success = run_deploy_pipeline(args)
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())