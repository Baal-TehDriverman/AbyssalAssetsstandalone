#!/usr/bin/env python3
"""
MSN Economy Bridge — Cyberpunk Mod ↔ Abyssal Exchange
Integrates CP2077 MSN mod economy commands with Abyssal Assets market.
"""
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

PUB_ROOT = Path("/home/tehlappy/Desktop/AI/Pub")
ABYSSAL_ROOT = Path("/home/tehlappy/Desktop/AI/abyssal-assets")
MSN_MOD_DIR = Path("/home/tehlappy/.local/share/Steam/steamapps/common/Cyberpunk 2077/r6/mods/msn_integration")

# Abyssal Exchange API base
ABYSSAL_API = "http://localhost:8000"
ABYSSAL_WS = "ws://localhost:8000/ws/market"

# Tree Fiddy constants
TREE_FIDDY_USD = 3.50
TREE_FIDDY_SC = 350  # Soul Coin equivalent (1 USD = 100 SC)

@dataclass
class EconomyState:
    """Unified economy state across games."""
    soul_coins: int = 0
    eddies: int = 0
    salvage_credits: int = 0
    nessie_treasury_marks: int = 0
    market_volume_24h: int = 0
    active_listings: int = 0
    top_gainers: List[Dict] = None
    top_losers: List[Dict] = None
    nessie_friendship_tier: int = 0
    loch_exchange_reputation: int = 0
    
    def __post_init__(self):
        if self.top_gainers is None:
            self.top_gainers = []
        if self.top_losers is None:
            self.top_losers = []

class MSNEconomyBridge:
    """Bridges CP2077 MSN mod commands to Abyssal Exchange."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.state = EconomyState()
        self.running = False
        
    async def start(self):
        self.session = aiohttp.ClientSession()
        self.running = True
        await self._sync_state()
        asyncio.create_task(self._ws_listener())
        print("[MSN Economy Bridge] Started")
        
    async def stop(self):
        self.running = False
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()
        print("[MSN Economy Bridge] Stopped")
        
    async def _ws_listener(self):
        """Listen for real-time market updates from Abyssal Exchange."""
        try:
            async with self.session.ws_connect(ABYSSAL_WS) as ws:
                self.ws = ws
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        await self._handle_market_update(data)
        except Exception as e:
            print(f"[MSN Economy Bridge] WS error: {e}")
            
    async def _handle_market_update(self, data: Dict):
        """Process incoming market WebSocket data."""
        if data.get("type") == "price_update":
            # Broadcast to CP2077 via coordination server
            await self._push_to_cp2077("price_update", data)
            
    async def _sync_state(self):
        """Sync economy state from Abyssal Exchange."""
        try:
            async with self.session.get(f"{ABYSSAL_API}/api/market/stats") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.state.market_volume_24h = data.get("total_volume_24h", 0)
                    self.state.active_listings = data.get("total_listings", 0)
                    
            async with self.session.get(f"{ABYSSAL_API}/api/market") as resp:
                if resp.status == 200:
                    market = await resp.json()
                    # Calculate gainers/losers from price changes
                    gainers = sorted(market, key=lambda x: x.get("price_change_24h", 0), reverse=True)[:5]
                    losers = sorted(market, key=lambda x: x.get("price_change_24h", 0))[:5]
                    self.state.top_gainers = gainers
                    self.state.top_losers = losers
        except Exception as e:
            print(f"[MSN Economy Bridge] Sync error: {e}")
            
    async def _push_to_cp2077(self, event: str, data: Dict):
        """Push economy events to CP2077 via MSN Coordination Server (port 8768)."""
        try:
            async with self.session.post(
                "http://localhost:8768/api/economy/event",
                json={"event": event, "data": data, "timestamp": datetime.utcnow().isoformat()}
            ) as resp:
                pass
        except Exception:
            pass  # Coordination server may not be running
            
    # === COMMAND HANDLERS ===
    
    async def cmd_market_exchange(self, args: List[str]) -> Dict:
        """market.exchange — Show Abyssal Exchange status."""
        await self._sync_state()
        return {
            "command": "market.exchange",
            "exchange": "The Loch Exchange",
            "currency": "Soul Coins (SC)",
            "volume_24h": self.state.market_volume_24h,
            "active_listings": self.state.active_listings,
            "fee_model": {"buy_fee": "3%", "burn": "1%", "nessie_treasury": "2%"},
            "top_gainers": [{"name": g["name"], "change": g["price_change_24h"]} for g in self.state.top_gainers],
            "top_losers": [{"name": l["name"], "change": l["price_change_24h"]} for l in self.state.top_losers],
            "tree_fiddy_tax": f"${TREE_FIDDY_USD} per transaction ({TREE_FIDDY_SC} SC)"
        }
        
    async def cmd_soulcoins_status(self, args: List[str]) -> Dict:
        """soulcoins.status — Show Soul Coin economy status."""
        # Get user balance from Abyssal (would need auth in real impl)
        return {
            "command": "soulcoins.status",
            "currency": "Soul Coins (SC)",
            "your_balance": "Query /api/users/me (requires auth)",
            "exchange_rate": "1 USD = 100 SC",
            "tree_fiddy": f"{TREE_FIDDY_SC} SC = ${TREE_FIDDY_USD}",
            "fees": {"buy": "3%", "burn": "1%", "nessie_treasury": "2%"},
            "total_supply": "Tracked via /api/market/stats"
        }
        
    async def cmd_nessie_treasury(self, args: List[str]) -> Dict:
        """nessie.treasury — Show Nessie Treasury status."""
        return {
            "command": "nessie.treasury",
            "treasury": "Nessie Treasury — Guardian-backed vouchers",
            "currency": "Nessie Treasury Marks (NTM)",
            "your_marks": "Query via abyssal.business (requires auth)",
            "earn_by": ["Respectful sightings", "Restoration contracts", "Non-hostile communion", "Covenant progression"],
            "spend_on": ["Guardian bounties", "Covenant rewards", "Abyssal fabricator unlocks", "Mount summoning"],
            "friendship_tier": self.state.nessie_friendship_tier
        }
        
    async def cmd_abyssal_business(self, args: List[str]) -> Dict:
        """abyssal.business — Full business dashboard."""
        await self._sync_state()
        return {
            "command": "abyssal.business",
            "exchange": "The Loch Exchange",
            "currencies": {
                "soul_coins": {"symbol": "SC", "rate": "1 USD = 100 SC"},
                "eddies": {"symbol": "€$", "role": "Night City retail"},
                "salvage_credits": {"symbol": "SAL", "role": "Freighter/fighter economy"},
                "nessie_marks": {"symbol": "NTM", "role": "Covenant rewards"}
            },
            "market": {
                "volume_24h": self.state.market_volume_24h,
                "listings": self.state.active_listings,
                "fee_model": {"buy": "3%", "burn": "1%", "treasury": "2%"}
            },
            "markets": ["lochExchange", "orbitalSalvageBoard", "abyssalTreasury"],
            "tree_fiddy": f"${TREE_FIDDY_USD}/tx = {TREE_FIDDY_SC} SC"
        }
        
    async def cmd_msn_economy_space(self, args: List[str]) -> Dict:
        """msn.economy.space — Space economy status."""
        return {
            "command": "msn.economy.space",
            "world": "Malkuth-One",
            "city_nodes": ["nightCity", "pacificaTrench", "orbitalGraveyard", "nomadLaunchCorridor", "lunarFreeport"],
            "currencies": ["eddies", "soulCoins", "salvageCredits", "nessieTreasuryMarks"],
            "markets": ["lochExchange", "orbitalSalvageBoard", "abyssalTreasury"],
            "freighters": ["CovenantFreighter", "VanceLonghaulCarrier", "NyxSilentArk"],
            "javelin_combat": "Vector/Bastion/Phantom/Tempest roles"
        }
        
    async def handle_cp2077_command(self, command: str, args: List[str]) -> Dict:
        """Route CP2077 console command to handler."""
        handlers = {
            "market.exchange": self.cmd_market_exchange,
            "soulcoins.status": self.cmd_soulcoins_status,
            "nessie.treasury": self.cmd_nessie_treasury,
            "abyssal.business": self.cmd_abyssal_business,
            "msn.economy.space": self.cmd_msn_economy_space,
        }
        
        handler = handlers.get(command)
        if handler:
            return await handler(args)
        return {"error": f"Unknown command: {command}"}

# === SERVER ===

async def run_bridge_server():
    """Run the economy bridge as a FastAPI server."""
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from pydantic import BaseModel
    
    bridge = MSNEconomyBridge()
    app = FastAPI(title="MSN Economy Bridge")
    
    class CommandRequest(BaseModel):
        command: str
        args: List[str] = []
        
    @app.on_event("startup")
    async def startup():
        await bridge.start()
        
    @app.on_event("shutdown")
    async def shutdown():
        await bridge.stop()
        
    @app.post("/api/economy/command")
    async def economy_command(req: CommandRequest):
        return await bridge.handle_cp2077_command(req.command, req.args)
        
    @app.get("/api/economy/state")
    async def economy_state():
        await bridge._sync_state()
        return asdict(bridge.state)
        
    @app.websocket("/ws/economy")
    async def economy_ws(ws: WebSocket):
        await ws.accept()
        try:
            while True:
                data = await ws.receive_json()
                if data.get("type") == "command":
                    result = await bridge.handle_cp2077_command(data["command"], data.get("args", []))
                    await ws.send_json(result)
        except WebSocketDisconnect:
            pass
            
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8769)

if __name__ == "__main__":
    asyncio.run(run_bridge_server())
