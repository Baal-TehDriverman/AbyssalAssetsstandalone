#!/usr/bin/env python3
"""Dry-run, stage, or apply Grand Theft Cyberpunk deployment plan actions."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "GTC_DEPLOYMENT_PLAN.json"
DEFAULT_STAGE = ROOT / "runtime/gtc_deployment_stage"


def load_plan(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_actions(plan: dict, plan_name: str | None, include_changed: bool) -> list[dict]:
    actions: list[dict] = []
    for name, item in plan["plans"].items():
        if plan_name and name != plan_name:
            continue
        for action in item["copy_missing"]:
            actions.append({"plan": name, **action})
        if include_changed:
            for action in item["review_update"]:
                actions.append({"plan": name, **action})
    return actions


def copy_action(action: dict, target_root: Path | None, apply: bool) -> dict:
    src = Path(action["source"])
    dst = Path(action["target"])
    if target_root is not None:
        dst = target_root / action["plan"] / action["relative_path"]

    result = {
        "plan": action["plan"],
        "action": action["action"],
        "relative_path": action["relative_path"],
        "source": str(src),
        "target": str(dst),
        "source_exists": src.exists(),
        "would_write": apply,
    }

    if not src.exists():
        result["status"] = "missing_source"
        return result

    if apply:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        result["status"] = "copied"
        result["bytes"] = dst.stat().st_size
    else:
        result["status"] = "dry_run"
        result["bytes"] = src.stat().st_size

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--plan-name", help="Limit to one deployment plan key")
    parser.add_argument("--include-changed", action="store_true", help="Also process changed target files")
    parser.add_argument("--stage", action="store_true", help="Copy actions into a staging directory")
    parser.add_argument("--stage-root", type=Path, default=DEFAULT_STAGE)
    parser.add_argument("--apply", action="store_true", help="Write actions to their real Steam targets")
    parser.add_argument("--yes", action="store_true", help="Required with --apply")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of actions")
    args = parser.parse_args()

    if args.apply and not args.yes:
        parser.error("--apply requires --yes")
    if args.apply and args.stage:
        parser.error("--apply and --stage are mutually exclusive")

    plan = load_plan(args.plan)
    actions = selected_actions(plan, args.plan_name, args.include_changed)
    if args.limit:
        actions = actions[: args.limit]

    target_root = args.stage_root if args.stage else None
    should_copy = args.apply or args.stage

    results = [copy_action(action, target_root, should_copy) for action in actions]
    copied = sum(1 for item in results if item["status"] == "copied")
    missing = sum(1 for item in results if item["status"] == "missing_source")
    total_bytes = sum(item.get("bytes", 0) for item in results)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if args.apply else "stage" if args.stage else "dry_run",
        "plan": str(args.plan),
        "plan_name": args.plan_name,
        "include_changed": args.include_changed,
        "action_count": len(results),
        "copied_count": copied,
        "missing_source_count": missing,
        "total_bytes": total_bytes,
        "target_root": str(target_root) if target_root else None,
        "results": results,
    }

    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
