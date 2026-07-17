#!/usr/bin/env python3
"""Render SYSTEM_AI_AUDIT.json into a concise operational Markdown report."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "SYSTEM_AI_AUDIT.json"
OUT = ROOT / "SYSTEM_AI_AUDIT_SUMMARY.md"


def load_audit() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def bullet(lines: list[str], items: list[str]) -> None:
    for item in items:
        lines.append(f"- {item}")


def main() -> int:
    audit = load_audit()
    summary = audit.get("summary", {})
    system = summary.get("system", {})
    memory = system.get("memory", {})
    cpu = system.get("cpu", {})
    gpu = summary.get("gpu_policy", {})
    services = summary.get("ai_service_gate", {})
    endpoints = summary.get("endpoint_gate", {})
    gtc = summary.get("gtc_cerebellum", {})
    triage = audit.get("commands", {}).get("ai_failure_triage", {})
    triage_payload = {}
    try:
        triage_payload = json.loads(triage.get("stdout", ""))
    except Exception:
        triage_payload = {}

    lines = [
        "# System AI Audit Summary",
        "",
        f"- Generated: `{audit.get('generated_at', 'unknown')}`",
        f"- Host: `{audit.get('host', 'unknown')}`",
        f"- Platform: `{system.get('platform', audit.get('platform', 'unknown'))}`",
        f"- CPU: `{cpu.get('model_name', 'unknown')}`",
        f"- RAM: `{memory.get('memory_total', 'unknown')}` total, `{memory.get('memory_available', 'unknown')}` available",
        f"- Swap: `{memory.get('swap_total', 'unknown')}` total, `{memory.get('swap_used', 'unknown')}` used",
        f"- Running user services: `{system.get('running_user_services', 'unknown')}`",
        "",
        "## Current Gates",
        "",
        f"- GPU/VRAM policy: `{gpu.get('status', 'unknown')}`; free `{gpu.get('free_mb', 'unknown')}` MiB; after reserve `{gpu.get('free_after_reserve_mb', 'unknown')}` MiB",
        f"- AI services: ok=`{services.get('ok', 'unknown')}`, running `{services.get('running_count', 'unknown')}/{services.get('expected_count', 'unknown')}`",
        f"- Endpoints: ok=`{endpoints.get('ok', 'unknown')}`, required failures `{endpoints.get('required_failure_count', 'unknown')}`, optional failures `{endpoints.get('optional_failure_count', 'unknown')}`",
        f"- Failure triage: ok=`{triage_payload.get('ok', 'unknown')}`, unhealthy services `{triage_payload.get('unhealthy_count', 'unknown')}`, optional endpoint failures `{triage_payload.get('optional_endpoint_failure_count', 'unknown')}`",
        f"- GTC cerebellum: ok=`{gtc.get('ok', 'unknown')}`, RAM available=`{gtc.get('ram_available', 'unknown')}`",
        "",
        "## Findings",
        "",
    ]
    bullet(lines, summary.get("findings", ["No findings recorded."]))
    lines.extend(["", "## Recommendations", ""])
    bullet(lines, summary.get("recommendations", ["No recommendations recorded."]))
    lines.extend([
        "",
        "## Source Artifacts",
        "",
        "- JSON audit: `SYSTEM_AI_AUDIT.json`",
        "- GTC context: `GTC_CONTEXT_INDEX.json`",
        "- GTC deployment plan: `GTC_DEPLOYMENT_PLAN.md`",
        "- Persistent local cerebellum: `runtime/gtc_cerebellum/AGENT_README.md`",
        "",
    ])

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
