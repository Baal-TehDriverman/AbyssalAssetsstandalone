#!/usr/bin/env python3
"""
Final verification: Run bots for 30 seconds and verify all data types reach bridge
"""

import asyncio
import time
import sys
sys.path.insert(0, '/home/tehlappy/Desktop/AI/abyssal-agents')

from deploy_public_bots import (
    PublicLochnessOrchestrator, AbyssalExchangeBridge, verify_bridge
)

async def main():
    print("=" * 60)
    print("FINAL VERIFICATION: 7 PUBLIC LOCHNESS BOTS + BRIDGE")
    print("=" * 60)

    bridge = AbyssalExchangeBridge("http://localhost:8000")
    orchestrator = PublicLochnessOrchestrator(data_callback=bridge.on_market_data)

    # Start all bots
    bot_task = asyncio.create_task(orchestrator.start_all())
    await asyncio.sleep(5)  # Let connections establish

    print("\n--- Bot Stats After 5s ---")
    for stat in orchestrator.get_all_stats():
        print(f"  {stat['sephira']:>12} ({stat['name']}): {stat['messages_processed']} msgs, {stat['errors']} errors")

    # Run for 30 seconds, checking bridge every 10s
    for i in range(3):
        await asyncio.sleep(10)
        print(f"\n--- Bridge Check at {10*(i+1)}s ---")
        summary = bridge.get_market_summary()
        if summary:
            for product, bots_data in summary.items():
                print(f"  Product: {product}")
                for bot_name, data in bots_data.items():
                    dt = data.get('type', 'unknown')
                    age = time.time() - data.get('timestamp', 0)
                    filtered = {k: v for k, v in data.get('data', {}).items() if k not in ['bids', 'asks']}
                    print(f"    {bot_name}: {dt} (age={age:.1f}s) {filtered}")

    # Final stats
    await asyncio.sleep(5)
    print("\n--- Final Bot Stats ---")
    for stat in orchestrator.get_all_stats():
        print(f"  {stat['sephira']:>12}: {stat['messages_processed']} msgs, {stat['errors']} errors, {stat['uptime_seconds']:.1f}s")

    # Test Abyssal health
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://localhost:8000/health")
        print(f"\n✓ Abyssal Exchange Health: {resp.json()}")

    await orchestrator.stop_all()
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass
    print("\n✓ All done!")

if __name__ == "__main__":
    asyncio.run(main())