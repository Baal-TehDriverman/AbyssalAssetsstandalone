#!/usr/bin/env python3
"""Report RTX/VRAM readiness for local AI plus Cyberpunk workloads."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone


VRAM_TOTAL_MB_FALLBACK = 6144
CYBERPUNK_HEADROOM_MB = 1536
DESKTOP_HEADROOM_MB = 512
LOCAL_AI_MIN_FREE_MB = 1024


def nvidia_query() -> dict:
    cmd = [
        "nvidia-smi",
        "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu,power.draw,power.limit",
        "--format=csv,noheader,nounits",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        return {
            "available": False,
            "returncode": proc.returncode,
            "stderr": proc.stderr.strip(),
        }

    row = proc.stdout.strip().splitlines()[0]
    parts = [part.strip() for part in row.split(",")]
    name, total, used, free, util, temp, power_draw, power_limit = parts
    def maybe_float(value: str) -> float | None:
        if value in {"[Not Supported]", "[N/A]", "N/A", ""}:
            return None
        return float(value)

    return {
        "available": True,
        "name": name,
        "memory_total_mb": int(float(total)),
        "memory_used_mb": int(float(used)),
        "memory_free_mb": int(float(free)),
        "gpu_util_percent": int(float(util)),
        "temperature_c": int(float(temp)),
        "power_draw_w": maybe_float(power_draw),
        "power_limit_w": maybe_float(power_limit),
    }


def process_query() -> list[dict]:
    cmd = [
        "nvidia-smi",
        "--query-compute-apps=pid,process_name,used_memory",
        "--format=csv,noheader,nounits",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        return []
    rows = []
    for line in proc.stdout.strip().splitlines():
        if not line.strip():
            continue
        pid, name, used = [part.strip() for part in line.split(",", 2)]
        rows.append({"pid": int(pid), "process_name": name, "used_memory_mb": int(float(used))})
    return rows


def decide(gpu: dict, processes: list[dict]) -> dict:
    if not gpu.get("available"):
        return {
            "status": "unknown",
            "local_ai_ok": False,
            "cyberpunk_ok": False,
            "reason": "nvidia-smi unavailable; use CPU/RAM fallback or run outside sandbox",
        }

    total = gpu.get("memory_total_mb") or VRAM_TOTAL_MB_FALLBACK
    free = gpu["memory_free_mb"]
    used = gpu["memory_used_mb"]
    ollama_mb = sum(p["used_memory_mb"] for p in processes if "ollama" in p["process_name"] or "llama" in p["process_name"])
    reserved = CYBERPUNK_HEADROOM_MB + DESKTOP_HEADROOM_MB
    free_after_reserve = free - reserved

    status = "green"
    reason = "enough VRAM headroom for local AI and desktop/game reserve"
    if free_after_reserve < 0:
        status = "red"
        reason = "VRAM reserve for Cyberpunk/desktop is already exceeded"
    elif free_after_reserve < LOCAL_AI_MIN_FREE_MB:
        status = "yellow"
        reason = "local AI can run, but avoid increasing context/concurrency"

    return {
        "status": status,
        "reason": reason,
        "local_ai_ok": free_after_reserve >= 0,
        "cyberpunk_ok": free >= reserved,
        "total_mb": total,
        "used_mb": used,
        "free_mb": free,
        "ollama_compute_mb": ollama_mb,
        "reserved_for_cyberpunk_and_desktop_mb": reserved,
        "free_after_reserve_mb": free_after_reserve,
        "recommendations": [
            "Keep one GPU-heavy Ollama model loaded at a time on 6 GiB VRAM.",
            "Prefer Q4/K quantized 7B-8B models for local coding/cerebellum work.",
            "Reduce context or unload Ollama before launching Cyberpunk if status is red/yellow.",
            "Use CPU/RAM fallback for indexing, search, and deployment planning.",
        ],
    }


def main() -> int:
    gpu = nvidia_query()
    processes = process_query() if gpu.get("available") else []
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gpu": gpu,
        "compute_processes": processes,
        "policy": decide(gpu, processes),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["policy"]["status"] in {"green", "yellow"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
