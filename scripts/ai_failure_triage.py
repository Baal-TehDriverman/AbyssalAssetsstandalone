#!/usr/bin/env python3
"""Collect read-only triage details for unhealthy local AI services/endpoints."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ai_service_health_gate import EXPECTED_SERVICES, service_state


ROOT = Path(__file__).resolve().parents[1]
ENDPOINT_GATE = ROOT / "scripts/ai_endpoint_health_gate.py"


def run(cmd: list[str], timeout: int = 15) -> dict:
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def recent_journal(service: str, lines: int) -> dict:
    return run([
        "journalctl",
        "--user",
        "-u",
        service,
        "--no-pager",
        "-n",
        str(lines),
    ])


def endpoint_report() -> dict:
    if not ENDPOINT_GATE.exists():
        return {"available": False, "error": f"missing {ENDPOINT_GATE}"}
    result = run([str(ENDPOINT_GATE)], timeout=30)
    try:
        payload = json.loads(result["stdout"])
    except Exception:
        payload = {}
    return {"available": True, "gate": result, "parsed": payload}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--journal-lines", type=int, default=80)
    parser.add_argument("--all", action="store_true", help="Include journals for healthy services too")
    parser.add_argument("--skip-endpoints", action="store_true")
    args = parser.parse_args()

    services = [service_state(service) for service in EXPECTED_SERVICES]
    unhealthy = [
        service for service in services
        if service["load_state"] in {"not-found", "unknown"} or service["active_state"] != "active"
    ]
    restart_attention = [
        service for service in services
        if service.get("restarts", "0").isdigit() and int(service["restarts"]) > 0
    ]

    journal_targets = services if args.all else unhealthy
    journals = {
        item["service"]: recent_journal(item["service"], args.journal_lines)
        for item in journal_targets
    }

    endpoints = None if args.skip_endpoints else endpoint_report()
    optional_endpoint_failures = []
    required_endpoint_failures = []
    if endpoints and endpoints.get("parsed"):
        for endpoint in endpoints["parsed"].get("endpoints", []):
            if endpoint.get("ok"):
                continue
            if endpoint.get("required"):
                required_endpoint_failures.append(endpoint)
            else:
                optional_endpoint_failures.append(endpoint)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "all_services" if args.all else "unhealthy_only",
        "service_count": len(services),
        "unhealthy_count": len(unhealthy),
        "restart_attention_count": len(restart_attention),
        "required_endpoint_failure_count": len(required_endpoint_failures),
        "optional_endpoint_failure_count": len(optional_endpoint_failures),
        "ok": not unhealthy and not required_endpoint_failures,
        "guidance": [
            "Read journals before restarting anything.",
            "Restart only the specific failed service, not the whole AI stack.",
            "Optional endpoint failures are degraded mode unless the current task needs that endpoint.",
            "If GPU/VRAM policy is red, inspect Ollama before blaming HTTP services.",
        ],
        "unhealthy_services": unhealthy,
        "services_with_restarts": restart_attention,
        "required_endpoint_failures": required_endpoint_failures,
        "optional_endpoint_failures": optional_endpoint_failures,
        "journals": journals,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
