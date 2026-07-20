#!/usr/bin/env python3
"""
NSSP Token Bridge — Lochness Monster × Abyssal Assets × Cyberpunk
Exposes BTC price, chaos pulses, and token ledger sync for in-game NSSP economy.
Port 8010 (local-only, zero telemetry)
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import httpx
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    httpx = None  # type: ignore
    FastAPI = None  # type: ignore

LOCHNESS_DIR = Path("/home/tehlappy/Desktop/Lilith/Core_Systems/AI/abyssal-agents")
LEDGER_PATH = LOCHNESS_DIR / "nssp_token_ledger.json"
COINBASE_TICKER = "https://api.coinbase.com/api/v3/brokerage/market/products/BTC-USD/ticker"
COINBASE_PUBLIC = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

# Exchange rates (match tweakdb/nssp_token_economy.yaml)
RATES = {
    "soul_to_chaos": 13,
    "chaos_to_lilith": 3,
    "soul_to_btc_sats": 350,  # per 100 SC
    "tree_fiddy_usd": 3.50,
}

DEFAULT_LEDGER = {
    "soul_coins": 350,
    "chaos_tokens": 13,
    "lilith_tokens": 3,
    "btc_sats": 0,
    "btc_usd": 0.0,
    "lochness_online": False,
    "last_sync": None,
    "sync_count": 0,
}


def load_ledger() -> dict[str, Any]:
    if LEDGER_PATH.exists():
        try:
            return {**DEFAULT_LEDGER, **json.loads(LEDGER_PATH.read_text())}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_LEDGER)


def save_ledger(ledger: dict[str, Any]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2))


def check_lochness_status() -> bool:
    pid_path = LOCHNESS_DIR / "lochness.pid"
    if not pid_path.exists():
        return False
    try:
        pid = int(pid_path.read_text().strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def fetch_btc_price() -> float:
    if httpx is None:
        return 0.0
    try:
        resp = httpx.get(COINBASE_PUBLIC, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            return float(data["data"]["amount"])
    except Exception:
        pass
    try:
        resp = httpx.get(COINBASE_TICKER, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            trades = data.get("trades", [])
            if trades:
                return float(trades[0].get("price", 0))
            price = data.get("price")
            if price:
                return float(price)
    except Exception:
        pass
    return 0.0


def compute_sync_grants(btc_usd: float, lochness_online: bool) -> dict[str, int]:
    """Compute in-game grants from live market telemetry."""
    grants = {"btc_sats_grant": 0, "chaos_pulse": 0, "soul_coin_bonus": 0}
    if btc_usd <= 0:
        return grants

    # Tree Fiddy subsidized: $3.50 worth of sats at current price
    sats_per_btc = 100_000_000
    tree_fiddy_sats = int((RATES["tree_fiddy_usd"] / btc_usd) * sats_per_btc)
    grants["btc_sats_grant"] = max(1, tree_fiddy_sats // 1000)  # scaled for in-game

    if lochness_online:
        grants["chaos_pulse"] = 1 + int(btc_usd % 13)  # Baal 1.3% theme
        grants["soul_coin_bonus"] = 7  # Nessie covenant drip

    return grants


def create_app() -> "FastAPI":
    app = FastAPI(title="NSSP Token Bridge", version="1.0.0")

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "service": "nssp_token_bridge", "port": 8010}

    @app.get("/api/tokens/status")
    def token_status() -> dict[str, Any]:
        ledger = load_ledger()
        btc_usd = fetch_btc_price()
        lochness_online = check_lochness_status()
        grants = compute_sync_grants(btc_usd, lochness_online)

        ledger["btc_usd"] = btc_usd
        ledger["lochness_online"] = lochness_online
        ledger["last_sync"] = datetime.now(timezone.utc).isoformat()
        ledger["sync_count"] = ledger.get("sync_count", 0) + 1
        save_ledger(ledger)

        return {
            **ledger,
            **grants,
            "rates": RATES,
            "nssp": "Neural Sovereign Systems Platform",
            "integrations": ["Abyssal Assets", "Lochness Monster", "Cyberpunk 2077"],
        }

    @app.post("/api/tokens/sync")
    def token_sync() -> dict[str, Any]:
        return token_status()

    @app.post("/api/tokens/exchange")
    def token_exchange(payload: dict[str, Any]) -> dict[str, Any]:
        ledger = load_ledger()
        from_type = str(payload.get("from", "soul")).lower()
        to_type = str(payload.get("to", "chaos")).lower()
        amount = int(payload.get("amount", 0))

        if amount <= 0:
            raise HTTPException(400, "amount must be positive")

        key_map = {
            "soul": "soul_coins", "sc": "soul_coins",
            "chaos": "chaos_tokens",
            "lilith": "lilith_tokens",
            "btc": "btc_sats", "sat": "btc_sats", "sats": "btc_sats",
        }
        from_key = key_map.get(from_type)
        to_key = key_map.get(to_type)
        if not from_key or not to_key:
            raise HTTPException(400, f"unknown token type: {from_type} -> {to_type}")

        if ledger.get(from_key, 0) < amount:
            raise HTTPException(400, f"insufficient {from_type} balance")

        # Convert via soul coin equivalent
        def to_sc(key: str, amt: int) -> float:
            if key == "soul_coins":
                return float(amt)
            if key == "chaos_tokens":
                return amt * RATES["soul_to_chaos"]
            if key == "lilith_tokens":
                return amt * RATES["soul_to_chaos"] * RATES["chaos_to_lilith"]
            if key == "btc_sats":
                return amt * 100.0 / RATES["soul_to_btc_sats"]
            return 0.0

        def from_sc(key: str, sc: float) -> int:
            if key == "soul_coins":
                return int(sc)
            if key == "chaos_tokens":
                return int(sc / RATES["soul_to_chaos"])
            if key == "lilith_tokens":
                return int(sc / (RATES["soul_to_chaos"] * RATES["chaos_to_lilith"]))
            if key == "btc_sats":
                return int(sc * RATES["soul_to_btc_sats"] / 100.0)
            return 0

        sc_equiv = to_sc(from_key, amount)
        received = from_sc(to_key, sc_equiv)
        if received <= 0:
            raise HTTPException(400, "exchange yields zero — increase amount")

        ledger[from_key] = ledger.get(from_key, 0) - amount
        ledger[to_key] = ledger.get(to_key, 0) + received
        save_ledger(ledger)

        return {
            "exchanged": amount,
            "from": from_type,
            "to": to_type,
            "received": received,
            "ledger": ledger,
        }

    @app.get("/api/tokens/btc/price")
    def btc_price() -> dict[str, Any]:
        price = fetch_btc_price()
        return {
            "pair": "BTC-USD",
            "price": price,
            "source": "Coinbase",
            "lochness_online": check_lochness_status(),
            "tree_fiddy_sats": compute_sync_grants(price, True)["btc_sats_grant"],
        }

    return app


def main() -> None:
    if FastAPI is None:
        # CLI fallback without FastAPI
        import sys
        action = sys.argv[1] if len(sys.argv) > 1 else "status"
        if action == "status":
            btc = fetch_btc_price()
            loch = check_lochness_status()
            grants = compute_sync_grants(btc, loch)
            print(json.dumps({
                "btc_usd": btc,
                "lochness_online": loch,
                **grants,
                "ledger": load_ledger(),
            }, indent=2))
        return

    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8010, log_level="info")


if __name__ == "__main__":
    main()