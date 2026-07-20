#!/usr/bin/env python3
"""Inspect and optionally unload Ollama models to protect Cyberpunk VRAM."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GPU_POLICY = ROOT / "scripts/gpu_vram_policy.py"


def run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def parse_ollama_ps(text: str) -> list[dict]:
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) <= 1:
        return []
    models = []
    for line in lines[1:]:
        parts = line.split()
        if not parts:
            continue
        models.append({
            "name": parts[0],
            "raw": line,
        })
    return models


def gpu_policy() -> dict:
    proc = subprocess.run([str(GPU_POLICY)], text=True, capture_output=True)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {}
    payload["_returncode"] = proc.returncode
    payload["_stderr"] = proc.stderr.strip()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stop", metavar="MODEL", help="Stop one named Ollama model")
    parser.add_argument("--stop-all", action="store_true", help="Stop all models shown by ollama ps")
    parser.add_argument("--restart-service", action="store_true", help="Restart user ollama.service as a last resort")
    parser.add_argument("--yes", action="store_true", help="Required for --stop, --stop-all, or --restart-service")
    args = parser.parse_args()

    mutating = bool(args.stop or args.stop_all or args.restart_service)
    if mutating and not args.yes:
        parser.error("mutating actions require --yes")

    ps = run(["ollama", "ps"])
    models = parse_ollama_ps(ps["stdout"]) if ps["returncode"] == 0 else []
    policy_before = gpu_policy()
    actions = []

    if args.stop:
        actions.append(run(["ollama", "stop", args.stop]))

    if args.stop_all:
        for model in models:
            actions.append(run(["ollama", "stop", model["name"]]))

    if args.restart_service:
        actions.append(run(["systemctl", "--user", "restart", "ollama.service"]))

    policy_after = gpu_policy() if actions else None
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "mutating" if mutating else "inspect",
        "ollama_ps": ps,
        "loaded_models": models,
        "gpu_policy_before": policy_before,
        "actions": actions,
        "gpu_policy_after": policy_after,
        "guidance": [
            "Use inspect mode first.",
            "Prefer `ollama stop MODEL --yes` via this helper before restarting the service.",
            "Use --restart-service --yes only when nvidia-smi still shows llama-server VRAM pressure but ollama ps is empty.",
            "Do not unload models during active agent work unless Cyberpunk/game VRAM needs priority.",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))

    status = policy_after or policy_before
    policy = status.get("policy", {})
    return 0 if policy.get("status") in {"green", "yellow"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
