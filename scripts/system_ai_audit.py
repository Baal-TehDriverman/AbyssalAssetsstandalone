#!/usr/bin/env python3
"""Collect a local AI/PC audit for repeatable improvement passes."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SYSTEM_AI_AUDIT.json"


def run(cmd: list[str], timeout: int = 15) -> dict:
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def maybe(cmd: list[str], timeout: int = 15) -> dict:
    if shutil.which(cmd[0]) is None:
        return {"cmd": cmd, "returncode": 127, "stdout": "", "stderr": f"{cmd[0]} not found"}
    try:
        return run(cmd, timeout)
    except Exception as exc:
        return {"cmd": cmd, "returncode": 1, "stdout": "", "stderr": str(exc)}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def parse_free(text: str) -> dict:
    lines = [line.split() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return {}
    mem = lines[1]
    swap = lines[2] if len(lines) > 2 else []
    return {
        "memory_total": mem[1] if len(mem) > 1 else "",
        "memory_used": mem[2] if len(mem) > 2 else "",
        "memory_available": mem[6] if len(mem) > 6 else "",
        "swap_total": swap[1] if len(swap) > 1 else "",
        "swap_used": swap[2] if len(swap) > 2 else "",
    }


def parse_lscpu(text: str) -> dict:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in {"Model name", "CPU(s)", "Core(s) per socket", "Thread(s) per core", "CPU max MHz"}:
            out[key.lower().replace(" ", "_").replace("(s)", "s")] = value
    return out


def parse_lsblk_unmounted(text: str) -> list[str]:
    devices = []
    for line in text.splitlines():
        if "disk" in line and "Samsung SSD 990 EVO" in line and "/" not in line:
            devices.append(line.strip())
    return devices


def parse_json_stdout(result: dict) -> dict:
    try:
        return json.loads(result.get("stdout", ""))
    except Exception:
        return {}


def parse_running_service_count(text: str) -> int:
    return len([line for line in text.splitlines() if ".service" in line and " loaded active running " in line])


def build_summary(audit: dict) -> dict:
    commands = audit.get("commands", {})
    gpu_policy = parse_json_stdout(commands.get("gpu_vram_policy", {})).get("policy", {})
    ollama_guard = parse_json_stdout(commands.get("ollama_vram_guard", {}))
    service_gate = parse_json_stdout(commands.get("ai_service_health_gate", {}))
    endpoint_gate = parse_json_stdout(commands.get("ai_endpoint_health_gate", {}))
    gtc_verify = parse_json_stdout(commands.get("gtc_cerebellum_verify", {}))

    findings: list[str] = []
    recommendations: list[str] = []

    if gpu_policy:
        status = gpu_policy.get("status")
        findings.append(
            "GPU VRAM policy is "
            f"{status}: {gpu_policy.get('free_mb')} MiB free, "
            f"{gpu_policy.get('free_after_reserve_mb')} MiB after Cyberpunk/desktop reserve."
        )
        if status == "red":
            recommendations.append("Unload or downshift Ollama before launching Cyberpunk or another GPU-heavy local model.")
        elif status == "yellow":
            recommendations.append("Keep one quantized local model loaded and avoid raising context/concurrency.")
    if service_gate:
        findings.append(
            f"AI service gate: {service_gate.get('running_count', 0)}/"
            f"{service_gate.get('expected_count', 0)} expected services running."
        )
    if endpoint_gate:
        findings.append(
            f"Endpoint gate: {endpoint_gate.get('endpoint_count', 0)} endpoints checked; "
            f"required failures={endpoint_gate.get('required_failure_count', 0)}."
        )
    if gtc_verify:
        findings.append(f"GTC cerebellum verification ok={gtc_verify.get('ok')}; ram_available={gtc_verify.get('ram_available')}.")

    unmounted = parse_lsblk_unmounted(commands.get("lsblk", {}).get("stdout", ""))
    if unmounted:
        findings.append("Samsung 990 EVO 2TB appears present but unmounted.")
        recommendations.append("Mount the Samsung 990 EVO as a large asset/model workspace after deciding mountpoint and filesystem policy.")

    if ollama_guard.get("loaded_models"):
        names = ", ".join(model.get("name", "?") for model in ollama_guard["loaded_models"])
        findings.append(f"Ollama loaded models: {names}.")

    if not recommendations:
        recommendations.append("No urgent local action found; keep running gates before deployment or launch work.")

    return {
        "system": {
            "platform": audit.get("platform"),
            "kernel": commands.get("uname", {}).get("stdout", ""),
            "cpu": parse_lscpu(commands.get("lscpu", {}).get("stdout", "")),
            "memory": parse_free(commands.get("free", {}).get("stdout", "")),
            "running_user_services": parse_running_service_count(commands.get("user_services", {}).get("stdout", "")),
        },
        "gpu_policy": gpu_policy,
        "ai_service_gate": {
            "ok": service_gate.get("ok"),
            "running_count": service_gate.get("running_count"),
            "expected_count": service_gate.get("expected_count"),
            "inactive_count": service_gate.get("inactive_count"),
            "missing_count": service_gate.get("missing_count"),
        } if service_gate else {},
        "endpoint_gate": {
            "ok": endpoint_gate.get("ok"),
            "endpoint_count": endpoint_gate.get("endpoint_count"),
            "required_failure_count": endpoint_gate.get("required_failure_count"),
            "optional_failure_count": endpoint_gate.get("optional_failure_count"),
        } if endpoint_gate else {},
        "gtc_cerebellum": {
            "ok": gtc_verify.get("ok"),
            "ram_available": gtc_verify.get("ram_available"),
            "ram_root": gtc_verify.get("ram_root"),
            "fallback_root": gtc_verify.get("fallback_root"),
        } if gtc_verify else {},
        "himalaya": {
            "version": commands.get("himalaya_version", {}).get("stdout", ""),
            "doctor_ok": commands.get("himalaya_doctor", {}).get("returncode") == 0,
        },
        "unmounted_large_devices": unmounted,
        "findings": findings,
        "recommendations": recommendations,
    }


def main() -> int:
    audit = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "env": {
            "cwd": str(Path.cwd()),
            "home": str(Path.home()),
        },
        "os_release": read_text(Path("/etc/os-release")),
        "commands": {
            "uname": maybe(["uname", "-a"]),
            "free": maybe(["free", "-h"]),
            "lscpu": maybe(["lscpu"]),
            "df": maybe(["df", "-hT"]),
            "lsblk": maybe(["lsblk", "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL"]),
            "nvidia_smi": maybe(["nvidia-smi"]),
            "himalaya_version": maybe(["himalaya", "--version"]),
            "himalaya_doctor": maybe(["himalaya", "account", "doctor"], timeout=30),
        },
        "repo_artifacts": {
            "gtc_context": (ROOT / "GTC_CONTEXT.md").exists(),
            "gtc_context_index": (ROOT / "GTC_CONTEXT_INDEX.json").exists(),
            "gtc_deployment_plan": (ROOT / "GTC_DEPLOYMENT_PLAN.json").exists(),
            "gtc_verify": (ROOT / "scripts/verify_gtc_cerebellum.py").exists(),
        },
    }

    if (ROOT / "scripts/verify_gtc_cerebellum.py").exists():
        audit["commands"]["gtc_cerebellum_verify"] = maybe([str(ROOT / "scripts/verify_gtc_cerebellum.py")], timeout=30)
    if (ROOT / "scripts/gpu_vram_policy.py").exists():
        audit["commands"]["gpu_vram_policy"] = maybe([str(ROOT / "scripts/gpu_vram_policy.py")], timeout=30)
    if (ROOT / "scripts/ai_service_health_gate.py").exists():
        audit["commands"]["ai_service_health_gate"] = maybe([str(ROOT / "scripts/ai_service_health_gate.py")], timeout=30)
    if (ROOT / "scripts/ai_endpoint_health_gate.py").exists():
        audit["commands"]["ai_endpoint_health_gate"] = maybe([str(ROOT / "scripts/ai_endpoint_health_gate.py")], timeout=30)
    if (ROOT / "scripts/ai_failure_triage.py").exists():
        audit["commands"]["ai_failure_triage"] = maybe([str(ROOT / "scripts/ai_failure_triage.py")], timeout=30)
    if (ROOT / "scripts/ollama_vram_guard.py").exists():
        audit["commands"]["ollama_vram_guard"] = maybe([str(ROOT / "scripts/ollama_vram_guard.py")], timeout=30)

    # Avoid requiring elevated service access from the script. If the caller runs
    # it in a real user session, this captures services; in a sandbox, it records
    # the failure for the report.
    audit["commands"]["user_services"] = maybe([
        "systemctl",
        "--user",
        "--no-pager",
        "--state=running",
        "--type=service",
    ])

    audit["summary"] = build_summary(audit)

    OUT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
