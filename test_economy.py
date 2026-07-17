import asyncio
import os
import sys
from pathlib import Path

import requests

URL = "http://localhost:8000"


def run_http_tests():
    try:
        # Check health
        res = requests.get(f"{URL}/health")
        if res.status_code != 200:
            print("Server not running.")
            return
            
        print("Triggering procedural event...")
        res = requests.post(f"{URL}/api/gm/economy/procedural-event")
        print(res.json())

        print("Triggering AI tick...")
        res = requests.post(f"{URL}/api/gm/ai-business/tick")
        print(res.json())
        
        print("Tests complete!")
    except Exception as e:
        print(f"Error: {e}")


async def run_local_tests():
    os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/abyssal-business-validation.db")
    server_dir = Path(__file__).parent / "server"
    sys.path.insert(0, str(server_dir))
    import main

    db = main.SessionLocal()
    try:
        main.seed_hats(db)
        event = await main.procedural_economy_event(db=db)
        tick = await main.ai_business_tick(db=db)
        summary = await main.business_summary(db=db)
        businesses = await main.list_businesses(ai_only=True, db=db)
        financials = await main.business_financials(businesses[0]["id"], db=db)

        assert event["event_id"] > 0
        assert tick["businesses_processed"] >= 1
        assert summary["ai_businesses"] >= 1
        assert businesses
        assert financials["records"]

        print({
            "event": event["event_name"],
            "orders_created": len(tick["orders_created"]),
            "businesses": summary["total_businesses"],
            "financial_records": len(financials["records"]),
        })
        print("Local economy validation complete.")
    finally:
        db.close()


def run_tests():
    if os.getenv("ABYSSAL_ECONOMY_TEST_MODE", "local") == "http":
        run_http_tests()
    else:
        asyncio.run(run_local_tests())


if __name__ == "__main__":
    run_tests()
