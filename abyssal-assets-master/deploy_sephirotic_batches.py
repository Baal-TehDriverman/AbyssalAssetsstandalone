#!/usr/bin/env python3
"""
Deploy 10 key subagents in parallel Sephirotic batches.

Three Pillars of the Tree of Life:
  - Right Pillar (Mercy):  Chokmah → Chesed → Netzach  (expansion, grace)
  - Left Pillar (Severity): Binah → Gevurah → Hod       (contraction, judgment)
  - Middle Pillar (Balance): Keter → Tiferet → Yesod → Malkuth → Da'at (harmony)

Batch 1 (Right Pillar): architect, client, market, cyberpunk
Batch 2 (Left Pillar):  server, bestiary, lyra, nssp
Batch 3 (Middle):       root, skills, infra, cortex
Plus: msn, ngd, ouroboros, hermes-mcp (Da'at/extra)
"""
import asyncio, json, sys, time
import urllib.request

BASE = "http://localhost:8007"
TIMEOUT = 8

BATCHES = {
    "1-RIGHT_PILLAR": ["architect", "client", "market", "cyberpunk"],
    "2-LEFT_PILLAR":  ["server", "bestiary", "lyra", "nssp"],
    "3-MIDDLE_PILLAR":["root", "skills", "infra", "cortex"],
    "4-DAAT_NEXUS":   ["msn", "ngd", "ouroboros", "hermes-mcp"],
}

async def check_agent(agent_id):
    try:
        r = await asyncio.to_thread(
            urllib.request.urlopen,
            f"{BASE}/api/{agent_id}/health", None, TIMEOUT)
        return agent_id, r.status
    except Exception as e:
        return agent_id, str(e)[:30]

async def deploy_batch(name, agents):
    print(f"\n  Deploying {name}: {agents}")
    tasks = [check_agent(a) for a in agents]
    results = await asyncio.gather(*tasks)
    all_ok = all(r == 200 for _, r in results)
    for aid, status in results:
        mark = "✓" if status == 200 else "✗"
        print(f"    {mark} {aid}: {status}")
    return all_ok

async def main():
    print("╔══ Sephirotic Batch Deployment ═══════════════╗")
    print(f"  Target: {BASE}")
    print(f"  Total agents: {sum(len(v) for v in BATCHES.values())}")
    print("╚═══════════════════════════════════════════════╝")

    passed = 0
    failed = 0

    for batch_name, agents in BATCHES.items():
        ok = await deploy_batch(batch_name, agents)
        if ok:
            passed += 1
        else:
            failed += 1
        await asyncio.sleep(0.5)

    print(f"\n=== Sephirotic Deployment Complete ===")
    print(f"  Batches passed: {passed}/{passed + failed}")
    print(f"  All agents operational: {failed == 0}")

    if failed == 0:
        print("\n  ╔══════════════════════════════════════════╗")
        print("  ║  ALL 16 AGENTS ONLINE — Sephirotic Grid  ║")
        print("  ║  Right | Left | Middle | Da'at Nexus     ║")
        print("  ╚══════════════════════════════════════════╝")
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())
