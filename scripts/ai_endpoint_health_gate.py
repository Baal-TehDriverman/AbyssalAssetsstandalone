#!/usr/bin/env python3
"""Check local AI HTTP endpoints and return a readiness report."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone


ENDPOINTS = [
    {"name": "lilith_api", "url": "http://localhost:3210/api/health", "required": True},
    {"name": "lyra_dialogue", "url": "http://localhost:3211/lyra/health", "required": False},
    {"name": "hermes_bridge", "url": "http://localhost:4242/health", "required": True},
    {"name": "msn_router", "url": "http://localhost:8007/api", "required": True},
    {"name": "abyssal_server", "url": "http://localhost:8000/health", "required": False},
    {"name": "antigravity_bridge", "url": "http://localhost:8002/health", "required": False},
    {"name": "swarm_orchestrator", "url": "http://localhost:8003/health", "required": False},
    {"name": "ai_router", "url": "http://localhost:8005/health", "required": False},
    {"name": "skill_marketplace", "url": "http://localhost:8006/health", "required": False},
    {"name": "business_dashboard", "url": "http://localhost:8008/health", "required": False},
]


def check(endpoint: dict, timeout: float = 3.0) -> dict:
    req = urllib.request.Request(endpoint["url"], headers={"Accept": "application/json"})
    result = {
        "name": endpoint["name"],
        "url": endpoint["url"],
        "required": endpoint["required"],
    }
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(4096).decode("utf-8", errors="replace")
            parsed = None
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = None
            result.update({
                "ok": 200 <= resp.status < 300,
                "status_code": resp.status,
                "json": parsed,
                "body_preview": body[:300],
            })
    except urllib.error.HTTPError as exc:
        result.update({"ok": False, "status_code": exc.code, "error": str(exc)})
    except Exception as exc:
        result.update({"ok": False, "status_code": None, "error": str(exc)})
    return result


def main() -> int:
    results = [check(endpoint) for endpoint in ENDPOINTS]
    required_failures = [item for item in results if item["required"] and not item["ok"]]
    optional_failures = [item for item in results if not item["required"] and not item["ok"]]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ok": not required_failures,
        "endpoint_count": len(results),
        "required_failure_count": len(required_failures),
        "optional_failure_count": len(optional_failures),
        "guidance": [
            "Required endpoints must pass before agents assume the core AI stack is ready.",
            "Optional endpoints may be down during partial development sessions.",
            "Use this gate after systemd/service checks because active services can still have unhealthy APIs.",
        ],
        "endpoints": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
