"""
Lochness Monster ↔ Abyssal Assets Integration Bridge
Ingests Coinbase telemetry from 10 Sephirotic bots and drives:
- Loch Exchange order book overlays
- Whale → rare hat drop events
- Funding/basis → crafting cost modifiers
- BTC/Chaos token sync to NSSP ledger (port 8010)
"""
from __future__ import annotations

import json
import time
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Optional

import httpx

TOKEN_BRIDGE_URL = "http://localhost:8010"
WHALE_THRESHOLD_USD = 100_000
MAX_EVENTS = 200


@dataclass
class LochnessEvent:
    event_type: str
    product_id: str
    source_bot: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "product_id": self.product_id,
            "source_bot": self.source_bot,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "iso": datetime.fromtimestamp(self.timestamp, tz=timezone.utc).isoformat(),
        }


class LochnessBridgeStore:
    """In-memory Lochness telemetry store for Abyssal Assets API."""

    def __init__(self) -> None:
        self.started_at = time.time()
        self.btc_usd: float = 0.0
        self.best_bid: float = 0.0
        self.best_ask: float = 0.0
        self.spread_bps: float = 0.0
        self.sentiment: str = "neutral"
        self.sentiment_score: float = 0.0
        self.funding_basis_pct: float = 0.0
        self.rsi: float = 50.0
        self.macd: float = 0.0
        self.lochness_online: bool = False
        self.bots_seen: Dict[str, float] = {}
        self.order_book: Dict[str, List] = {"bids": [], "asks": []}
        self.events: Deque[LochnessEvent] = deque(maxlen=MAX_EVENTS)
        self.whale_alerts: Deque[Dict[str, Any]] = deque(maxlen=50)
        self.crafting_modifier: float = 1.0
        self.chaos_pulse: int = 0
        self._last_token_sync: float = 0.0

    def _touch_bot(self, bot_name: str) -> None:
        self.bots_seen[bot_name] = time.time()
        cutoff = time.time() - 120
        self.lochness_online = any(ts > cutoff for ts in self.bots_seen.values())

    def _push_event(self, event_type: str, product_id: str, source_bot: str, payload: Dict[str, Any]) -> LochnessEvent:
        ev = LochnessEvent(event_type, product_id, source_bot, payload)
        self.events.appendleft(ev)
        return ev

    def ingest_depth(self, product_id: str, bids: List, asks: List, source_bot: str = "Nessie-Prime") -> Dict[str, Any]:
        self._touch_bot(source_bot)
        self.order_book = {"bids": bids[:20], "asks": asks[:20]}
        if bids and asks:
            try:
                self.best_bid = float(bids[0][0] if isinstance(bids[0], (list, tuple)) else bids[0].get("price", 0))
                self.best_ask = float(asks[0][0] if isinstance(asks[0], (list, tuple)) else asks[0].get("price", 0))
                if self.best_bid > 0:
                    self.spread_bps = ((self.best_ask - self.best_bid) / self.best_bid) * 10000
                    self.btc_usd = (self.best_bid + self.best_ask) / 2
            except (IndexError, TypeError, ValueError):
                pass
        ev = self._push_event("market_depth", product_id, source_bot, {"bids": len(bids), "asks": len(asks)})
        return ev.to_dict()

    def ingest_ticker(self, product_id: str, bid: float, ask: float, spread_bps: float, source_bot: str = "Nessie-Arbitrage") -> Dict[str, Any]:
        self._touch_bot(source_bot)
        self.best_bid = bid
        self.best_ask = ask
        self.spread_bps = spread_bps
        self.btc_usd = (bid + ask) / 2 if bid and ask else self.btc_usd
        ev = self._push_event("book_ticker", product_id, source_bot, {"bid": bid, "ask": ask, "spread_bps": spread_bps})
        return ev.to_dict()

    def ingest_whale(self, product_id: str, notional: float, side: str, source_bot: str = "Nessie-Whale") -> Dict[str, Any]:
        self._touch_bot(source_bot)
        alert = {
            "product_id": product_id,
            "notional_usd": notional,
            "side": side,
            "timestamp": time.time(),
            "rare_hat_drop": notional >= WHALE_THRESHOLD_USD,
            "drop_tier": "mythic" if notional >= 500_000 else "legendary" if notional >= 250_000 else "epic",
        }
        self.whale_alerts.appendleft(alert)
        self.chaos_pulse += 1
        ev = self._push_event("whale_trade", product_id, source_bot, alert)
        return {"event": ev.to_dict(), "whale_alert": alert, "hat_drop_triggered": alert["rare_hat_drop"]}

    def ingest_basis(self, product_id: str, basis_pct: float, annualized: float, source_bot: str = "Nessie-Funding") -> Dict[str, Any]:
        self._touch_bot(source_bot)
        self.funding_basis_pct = basis_pct
        # High basis → expensive crafting (funding squeeze)
        self.crafting_modifier = max(0.7, min(1.5, 1.0 + basis_pct / 100.0))
        ev = self._push_event("futures_basis", product_id, source_bot, {
            "basis_pct": basis_pct,
            "annualized_pct": annualized,
            "crafting_modifier": self.crafting_modifier,
        })
        return ev.to_dict()

    def ingest_technical(self, product_id: str, rsi: float, macd: float, signals: List[str], source_bot: str = "Nessie-Technical") -> Dict[str, Any]:
        self._touch_bot(source_bot)
        self.rsi = rsi
        self.macd = macd
        ev = self._push_event("technical_analysis", product_id, source_bot, {
            "rsi": rsi, "macd": macd, "signals": signals,
        })
        return ev.to_dict()

    def ingest_sentiment(self, product_id: str, sentiment: str, score: float, source_bot: str = "Nessie-Sentiment") -> Dict[str, Any]:
        self._touch_bot(source_bot)
        self.sentiment = sentiment
        self.sentiment_score = score
        ev = self._push_event("sentiment", product_id, source_bot, {"sentiment": sentiment, "score": score})
        return ev.to_dict()

    def ingest_generic(self, data: Dict[str, Any], source_bot: str = "Lochness") -> Dict[str, Any]:
        """Route any Lochness payload by type field."""
        event_type = data.get("type", "unknown")
        product_id = data.get("product_id", "BTC-USD")

        if event_type == "market_depth":
            return self.ingest_depth(product_id, data.get("bids", []), data.get("asks", []), source_bot)
        if event_type == "book_ticker":
            return self.ingest_ticker(product_id, data.get("bid", 0), data.get("ask", 0), data.get("spread_bps", 0), source_bot)
        if event_type == "whale_trade":
            return self.ingest_whale(product_id, data.get("notional", 0), data.get("side", "unknown"), source_bot)
        if event_type == "futures_basis":
            return self.ingest_basis(product_id, data.get("basis_pct", 0), data.get("annualized_pct", 0), source_bot)
        if event_type == "technical_analysis":
            return self.ingest_technical(product_id, data.get("rsi", 50), data.get("macd", 0), data.get("signals", []), source_bot)
        if event_type in ("sentiment", "sentiment_public"):
            return self.ingest_sentiment(product_id, data.get("sentiment", "neutral"), data.get("sentiment_score", 0), source_bot)

        self._touch_bot(source_bot)
        ev = self._push_event(event_type, product_id, source_bot, data)
        return ev.to_dict()

    def sync_tokens(self) -> Dict[str, Any]:
        """Push Lochness state to NSSP token bridge."""
        now = time.time()
        if now - self._last_token_sync < 30:
            return {"skipped": True, "reason": "throttled"}
        self._last_token_sync = now
        try:
            resp = httpx.post(f"{TOKEN_BRIDGE_URL}/api/tokens/sync", timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            return {"error": str(e)}
        return {"error": "token bridge unreachable"}

    def get_summary(self) -> Dict[str, Any]:
        return {
            "service": "lochness_bridge",
            "lochness_online": self.lochness_online,
            "bots_active": len([b for b, ts in self.bots_seen.items() if ts > time.time() - 120]),
            "bots_seen": list(self.bots_seen.keys()),
            "btc_usd": round(self.btc_usd, 2),
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "spread_bps": round(self.spread_bps, 2),
            "sentiment": self.sentiment,
            "sentiment_score": round(self.sentiment_score, 4),
            "funding_basis_pct": round(self.funding_basis_pct, 4),
            "crafting_modifier": round(self.crafting_modifier, 4),
            "rsi": round(self.rsi, 2),
            "macd": round(self.macd, 4),
            "chaos_pulse": self.chaos_pulse,
            "whale_alerts_24h": len(self.whale_alerts),
            "recent_whales": list(self.whale_alerts)[:5],
            "order_book_depth": {"bids": len(self.order_book["bids"]), "asks": len(self.order_book["asks"])},
            "events_buffered": len(self.events),
            "uptime_seconds": int(time.time() - self.started_at),
            "integrations": ["Abyssal Exchange", "NSSP Token Bridge", "Cyberpunk 2077"],
        }

    def get_feed(self, limit: int = 25) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in list(self.events)[:limit]]


# Singleton
_store: Optional[LochnessBridgeStore] = None


def get_lochness_store() -> LochnessBridgeStore:
    global _store
    if _store is None:
        _store = LochnessBridgeStore()
    return _store