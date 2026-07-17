#!/usr/bin/env python3
"""
Sephirotic Wave Deployment — launches MSN subagents in waves
  Wave 1 (Foundation):  root, architect, server        → Keter → Binah
  Wave 2 (Interface):    client, bestiary, skills, market, lyra, living_sin  → Chesed → Hod
  Wave 3 (Infrastructure): infra, migration             → Yesod → Malkuth
  Wave 4 (Metaconscious): msn, ngd, cerebellum, ouroboros, mcp, kairos,
                          swarm, court, himalaya, bridge, yeshua, scribe,
                          analytics, worker             → DAAT → Malkuth
"""

import sys
import time
import json
import httpx
import asyncio
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).parent
WAVES = {
    1: {
        "name": "Foundation",
        "sephirot": "Keter → Chokmah → Binah",
        "agents": ["root", "architect", "server"],
    },
    2: {
        "name": "Interface",
        "sephirot": "Chesed → Gevurah → Tiferet → Netzach → Hod",
        "agents": ["client", "bestiary", "skills", "market", "lyra", "living-sin"],
    },
    3: {
        "name": "Infrastructure",
        "sephirot": "Yesod → Malkuth",
        "agents": ["infra", "migration"],
    },
    4: {
        "name": "Metaconscious",
        "sephirot": "DAAT → Binah → Hod → Tiferet → Malkuth → Netzach → Gevurah → Chokmah",
        "agents": [
            "msn", "ngd", "cerebellum", "ouroboros",
            "hermes-mcp", "kairos", "swarm", "court",
            "himalaya", "antigravity", "yeshua", "scribe",
            "analytics", "worker", "cortex", "cyberpunk", "nssp", "grokdata",
        ],
    },
}


def print_banner(text: str):
    width = 60
    print()
    print("=" * width)
    print(f"  {text}")
    print("=" * width)


async def check_agent_health(url: str, agent_id: str, retries: int = 3) -> bool:
    async with httpx.AsyncClient(timeout=5) as client:
        for attempt in range(1, retries + 1):
            try:
                r = await client.get(f"{url}/api/{agent_id}/health")
                if r.status_code == 200:
                    data = r.json()
                    if data.get("health") == "healthy":
                        return True
                    print(f"    [{agent_id}] status={data.get('status')}, health={data.get('health')}")
                else:
                    print(f"    [{agent_id}] HTTP {r.status_code}")
            except Exception as e:
                if attempt < retries:
                    print(f"    [{agent_id}] attempt {attempt}/{retries}: {e}")
                    await asyncio.sleep(1)
                else:
                    print(f"    [{agent_id}] FAILED after {retries} retries: {e}")
    return False


async def deploy_wave(wave_num: int, router_url: str) -> bool:
    wave = WAVES[wave_num]
    print_banner(f"Wave {wave_num}: {wave['name']} ({wave['sephirot']})")
    print(f"  Agents: {', '.join(wave['agents'])}")
    print()

    # Agents are already loaded when msn_router starts — we just health-check
    results = []
    for agent_id in wave["agents"]:
        healthy = await check_agent_health(router_url, agent_id)
        results.append((agent_id, healthy))
        status_icon = "✓" if healthy else "✗"
        print(f"  {status_icon} {agent_id} — {'healthy' if healthy else 'UNHEALTHY'}")

    all_ok = all(h for _, h in results)
    print()
    if all_ok:
        print(f"  Wave {wave_num} ALL HEALTHY")
    else:
        failed = [a for a, h in results if not h]
        print(f"  Wave {wave_num} PARTIAL — {len(failed)} unhealthy: {', '.join(failed)}")

    print()
    return all_ok


async def main():
    router_port = 8007
    if len(sys.argv) > 1:
        router_port = int(sys.argv[1])

    router_url = f"http://localhost:{router_port}"
    print_banner("SEPHIROTIC WAVE DEPLOYMENT")
    print(f"  MSN Router: {router_url}")
    print(f"  Waves: {len(WAVES)}")
    print()

    # Ensure router is running
    print("Checking MSN Router...")
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            r = await client.get(f"{router_url}/")
            if r.status_code == 200:
                data = r.json()
                print(f"  MSN Router online — {data.get('agents_online', '?')} agents loaded")
            else:
                print(f"  MSN Router returned HTTP {r.status_code}")
                print(f"  Start with: python msn_router.py {router_port}")
                return
        except Exception as e:
            print(f"  Cannot reach MSN Router at {router_url}: {e}")
            print(f"  Start with: python msn_router.py {router_port}")
            return

    print()

    # Deploy each wave
    results = {}
    for w in sorted(WAVES.keys()):
        ok = await deploy_wave(w, router_url)
        results[w] = ok
        if w < max(WAVES.keys()):
            print("  Inter-wave pause (1s)...")
            await asyncio.sleep(1)

    # Summary
    print_banner("DEPLOYMENT SUMMARY")
    all_ok = True
    for w, ok in sorted(results.items()):
        icon = "✓" if ok else "✗"
        name = WAVES[w]["name"]
        print(f"  Wave {w} ({name}): {icon}")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("  ALL WAVES DEPLOYED SUCCESSFULLY")
        print(f"  Router: {router_url}")
        print(f"  Agents: {router_url}/api")
    else:
        print("  Some waves have unhealthy agents — check logs above")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
