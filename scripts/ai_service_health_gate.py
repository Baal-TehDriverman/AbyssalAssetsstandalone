#!/usr/bin/env python3
"""Check local AI service health before starting or restarting the stack."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone


EXPECTED_SERVICES = [
    "antigravity-bridge.service",
    "cyberpunk-ngd.service",
    "god-engine.service",
    "hermes-bridge.service",
    "hermes-gateway.service",
    "lilith-api.service",
    "lyra-api.service",
    "msn-router.service",
    "ngd-cerebellum.service",
    "ngd.service",
    "quantum-terminal.service",
    "swarm-orchestrator.service",
]


def service_state(service: str) -> dict:
    proc = subprocess.run(
        ["systemctl", "--user", "show", service, "--property=LoadState,ActiveState,SubState,MainPID,NRestarts"],
        text=True,
        capture_output=True,
    )
    fields: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key] = value
    return {
        "service": service,
        "returncode": proc.returncode,
        "load_state": fields.get("LoadState", "unknown"),
        "active_state": fields.get("ActiveState", "unknown"),
        "sub_state": fields.get("SubState", "unknown"),
        "main_pid": fields.get("MainPID", "0"),
        "restarts": fields.get("NRestarts", "0"),
        "stderr": proc.stderr.strip(),
    }


def main() -> int:
    services = [service_state(service) for service in EXPECTED_SERVICES]
    missing = [s for s in services if s["load_state"] in {"not-found", "unknown"}]
    inactive = [s for s in services if s["active_state"] != "active"]
    running = [s for s in services if s["active_state"] == "active"]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "expected_count": len(EXPECTED_SERVICES),
        "running_count": len(running),
        "missing_count": len(missing),
        "inactive_count": len(inactive),
        "ok": not missing and not inactive,
        "action": "status_only",
        "guidance": [
            "If a service is already active, do not start a duplicate foreground process.",
            "Restart only the specific failed service after reading its journal.",
            "Use this gate before launch scripts that start Lilith/Hermes/MSN/NGD services.",
        ],
        "services": services,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
