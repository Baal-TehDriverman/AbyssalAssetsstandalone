# Lochness Monsters - Coinbase Advanced Trade WebSocket Monitoring Bots
# =====================================================================
# 10 Sephiroth-aligned bots monitoring Coinbase streams
# Updated from Binance to Coinbase Advanced Trade API
#
# Existing (7):
# - Keter:      Nessie-Prime      → level2/heartbeats   → Market Depth
# - Chokmah:    Nessie-Arbitrage  → ticker              → Best Bid/Ask
# - Binah:      Nessie-Liquidation→ market_trades       → Large Trade Detection
# - Chesed:     Nessie-Whale      → market_trades       → Whale Watch (>$100k)
# - Geburah:    Nessie-Funding    → N/A (Coinbase no funding) → Futures Basis
# - Tiferet:    Nessie-Kline      → candles_1m          → OHLCV Charts
# - Netzach:    Nessie-Sentiment  → user_orders         → Order Flow Sentiment
#
# New (3):
# - Hod:        Nessie-Technical  → candles + level2    → Technical Analysis (RSI, MACD, BB)
# - Yesod:      Nessie-Infrastructure → ticker + level2 → Order Book Health/Latency
# - Malkuth:    Nessie-Reality    → user_trades         → Player Behavior/PnL

import asyncio
import json
import os
import time
import hmac
import hashlib
import base64
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import websockets
import httpx
import numpy as np
import statistics

# ============================================================================
# COINBASE ADVANCED TRADE CONFIGURATION
# ============================================================================

COINBASE_WS_URL = "wss://advanced-trade-ws.coinbase.com"
COINBASE_REST_URL = "https://api.coinbase.com/api/v3/brokerage"

# Product ID format: "BTC-USD", "ETH-USD", etc.
DEFAULT_PRODUCT = "BTC-USD"

# Coinbase channels:
# - "level2" - Order book (top 50 bids/asks)
# - "ticker" - Best bid/ask, 24h stats
# - "market_trades" - Trade executions
# - "candles_1m" - 1-minute candles
# - "user" - Authenticated user events (orders, fills)
# - "heartbeats" - Connection health


@dataclass
class BotConfig:
    """Configuration for a Lochness bot"""
    name: str
    sephira: str
    channels: List[str]
    product_id: str = DEFAULT_PRODUCT
    reconnect_delay: float = 5.0
    max_reconnect_attempts: int = 10
    heartbeat_interval: float = 30.0


@dataclass
class MarketData:
    """Normalized market data point"""
    timestamp: float
    product_id: str
    data: Dict[str, Any]
    source_bot: str


class CoinbaseAuth:
    """Coinbase Advanced Trade authentication"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
    
    def get_auth_headers(self, timestamp: str, method: str, request_path: str, body: str = "") -> Dict[str, str]:
        """Generate authentication headers for REST API"""
        if not self.api_key or not self.api_secret:
            return {}
        
        message = timestamp + method + request_path + body
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(signature).decode()
        
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature_b64,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }
    
    def get_ws_auth(self) -> Dict[str, Any]:
        """Generate WebSocket authentication payload"""
        if not self.api_key or not self.api_secret:
            return {}
        
        timestamp = str(int(time.time()))
        message = timestamp + "GET" + "/users/self/verify"
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(signature).decode()
        
        return {
            "type": "subscribe",
            "channel": "user",
            "api_key": self.api_key,
            "timestamp": timestamp,
            "signature": signature_b64
        }


# ============================================================================
# BASE BOT FRAMEWORK
# ============================================================================

class LochnessBot(ABC):
    """Base class for all Lochness Coinbase monitoring bots"""
    
    def __init__(self, config: BotConfig, data_callback: Optional[Callable] = None, auth: Optional[CoinbaseAuth] = None):
        self.config = config
        self.data_callback = data_callback
        self.auth = auth or CoinbaseAuth()
        self.running = False
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.reconnect_attempts = 0
        self.last_heartbeat = 0
        self.message_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
        # Data buffers
        self.price_buffer = deque(maxlen=1000)
        self.volume_buffer = deque(maxlen=1000)
        self.trade_buffer = deque(maxlen=5000)
        self.order_book = {"bids": {}, "asks": {}}
        
    async def start(self):
        """Start the bot"""
        self.running = True
        self.reconnect_attempts = 0
        await self._connect_and_run()
    
    async def stop(self):
        """Stop the bot"""
        self.running = False
        if self.ws:
            await self.ws.close()
    
    async def _connect_and_run(self):
        """Main connection loop with reconnection logic"""
        while self.running and self.reconnect_attempts < self.config.max_reconnect_attempts:
            try:
                await self._connect()
                await self._run()
            except websockets.exceptions.ConnectionClosed as e:
                self.error_count += 1
                print(f"[{self.config.name}] Connection closed: {e}, reconnecting...")
            except Exception as e:
                self.error_count += 1
                print(f"[{self.config.name}] Error: {e}, reconnecting...")
            
            if self.running:
                self.reconnect_attempts += 1
                await asyncio.sleep(self.config.reconnect_delay * min(self.reconnect_attempts, 5))
        
        if self.reconnect_attempts >= self.config.max_reconnect_attempts:
            print(f"[{self.config.name}] Max reconnection attempts reached, stopping")
    
    async def _connect(self):
        """Establish WebSocket connection"""
        print(f"[{self.config.name}] Connecting to {COINBASE_WS_URL}")
        
        self.ws = await websockets.connect(
            COINBASE_WS_URL,
            ping_interval=20,
            ping_timeout=10,
            max_size=2**24  # 16MB to handle large level2 snapshots
        )
        
        # Subscribe to channels - try different formats for channels that fail
        # level2, heartbeats, and candles_1m might need special handling
        
        # Build subscribe message - try with singular "channel" first for compatibility
        subscribe_msg = {
            "type": "subscribe",
            "product_ids": [self.config.product_id],
        }
        
        # Try different formats based on channel
        # For channels that work with array, use "channels"
        # For single channel, use "channel"
        if len(self.config.channels) == 1:
            subscribe_msg["channel"] = self.config.channels[0]
        else:
            # For multiple channels, try array format
            subscribe_msg["channels"] = self.config.channels

        # Add authentication for user channel
        if "user" in self.config.channels and self.auth.api_key:
            ws_auth = self.auth.get_ws_auth()
            subscribe_msg.update(ws_auth)
        
        await self.ws.send(json.dumps(subscribe_msg))
        self.reconnect_attempts = 0
        print(f"[{self.config.name}] Connected and subscribed to {self.config.channels}")
    
    async def _run(self):
        """Main message processing loop"""
        async for message in self.ws:
            if not self.running:
                break

            self.message_count += 1
            self.last_heartbeat = time.time()

            try:
                data = json.loads(message)
                await self._process_message(data)
            except json.JSONDecodeError:
                pass
            except Exception as e:
                self.error_count += 1
                print(f"[{self.config.name}] Message processing error: {e}")

            # Handle heartbeats
            if time.time() - self.last_heartbeat > self.config.heartbeat_interval:
                await self._send_heartbeat()
    
    @abstractmethod
    async def _process_message(self, data: Dict[str, Any]):
        """Process incoming WebSocket message - implemented by subclasses"""
        pass
    
    async def _send_heartbeat(self):
        """Send ping to keep connection alive"""
        if self.ws:
            try:
                await self.ws.ping()
            except Exception:
                pass
    
    def _emit_data(self, data: MarketData):
        """Emit normalized data to callback"""
        if self.data_callback:
            try:
                if asyncio.iscoroutinefunction(self.data_callback):
                    asyncio.create_task(self.data_callback(data))
                else:
                    self.data_callback(data)
            except Exception as e:
                print(f"[{self.config.name}] Callback error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        return {
            "name": self.config.name,
            "sephira": self.config.sephira,
            "product_id": self.config.product_id,
            "channels": self.config.channels,
            "running": self.running,
            "uptime_seconds": time.time() - self.start_time,
            "messages_processed": self.message_count,
            "errors": self.error_count,
            "reconnect_attempts": self.reconnect_attempts,
        }


# ============================================================================
# EXISTING 7 BOTS
# ============================================================================

class NessiePrime(LochnessBot):
    """Keter - Market Depth Monitor (level2)"""

    def __init__(self, data_callback=None, auth=None):
        config = BotConfig(
            name="Nessie-Prime",
            sephira="Keter",
            channels=["level2"],  # Try "level2" alone
        )
        super().__init__(config, data_callback, auth)
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process level2 order book updates"""
        if data.get("channel") != "level2":
            return
        
        events = data.get("events", [])
        for event in events:
            if event.get("type") == "snapshot":
                # Initialize order book
                self.order_book = {"bids": {}, "asks": {}}
                for update in event.get("updates", []):
                    side = update.get("side")
                    price = float(update.get("price_level", 0))
                    size = float(update.get("new_quantity", 0))
                    if side == "bid":
                        if size > 0:
                            self.order_book["bids"][price] = size
                        elif price in self.order_book["bids"]:
                            del self.order_book["bids"][price]
                    elif side == "ask":
                        if size > 0:
                            self.order_book["asks"][price] = size
                        elif price in self.order_book["asks"]:
                            del self.order_book["asks"][price]
            
            elif event.get("type") == "update":
                # Apply incremental updates
                for update in event.get("updates", []):
                    side = update.get("side")
                    price = float(update.get("price_level", 0))
                    size = float(update.get("new_quantity", 0))
                    if side == "bid":
                        if size > 0:
                            self.order_book["bids"][price] = size
                        elif price in self.order_book["bids"]:
                            del self.order_book["bids"][price]
                    elif side == "ask":
                        if size > 0:
                            self.order_book["asks"][price] = size
                        elif price in self.order_book["asks"]:
                            del self.order_book["asks"][price]
            
            # Emit depth data periodically
            await self._emit_depth()
    
    async def _emit_depth(self):
        """Emit current order book depth"""
        if not self.order_book["bids"] or not self.order_book["asks"]:
            return
        
        # Sort and take top 20
        bids = sorted(self.order_book["bids"].items(), key=lambda x: x[0], reverse=True)[:20]
        asks = sorted(self.order_book["asks"].items(), key=lambda x: x[0])[:20]
        
        best_bid = bids[0][0] if bids else 0
        best_ask = asks[0][0] if asks else 0
        spread = best_ask - best_bid if best_bid and best_ask else 0
        spread_pct = (spread / best_bid * 100) if best_bid else 0
        
        bid_depth = sum(q for _, q in bids)
        ask_depth = sum(q for _, q in asks)
        
        market_data = MarketData(
            timestamp=time.time(),
            product_id=self.config.product_id,
            data={
                "type": "market_depth",
                "best_bid": best_bid,
                "best_ask": best_ask,
                "spread": spread,
                "spread_pct": spread_pct,
                "bid_depth": bid_depth,
                "ask_depth": ask_depth,
                "imbalance": (bid_depth - ask_depth) / (bid_depth + ask_depth) if (bid_depth + ask_depth) > 0 else 0,
                "bids": [[p, q] for p, q in bids],
                "asks": [[p, q] for p, q in asks],
            },
            source_bot=self.config.name
        )
        self._emit_data(market_data)


class NessieArbitrage(LochnessBot):
    """Chokmah - Best Bid/Ask Ticker (ticker channel)"""
    
    def __init__(self, data_callback=None, auth=None):
        config = BotConfig(
            name="Nessie-Arbitrage",
            sephira="Chokmah",
            channels=["ticker"],
        )
        super().__init__(config, data_callback, auth)
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process ticker updates"""
        if data.get("channel") != "ticker":
            return
        
        events = data.get("events", [])
        for event in events:
            tickers = event.get("tickers", [])
            for ticker in tickers:
                bid = float(ticker.get("best_bid", 0))
                ask = float(ticker.get("best_ask", 0))
                bid_size = float(ticker.get("best_bid_size", 0))
                ask_size = float(ticker.get("best_ask_size", 0))
                price_24h = float(ticker.get("price_24h", 0))
                volume_24h = float(ticker.get("volume_24h", 0))
                low_24h = float(ticker.get("low_24h", 0))
                high_24h = float(ticker.get("high_24h", 0))
                
                spread = ask - bid
                mid = (bid + ask) / 2
                spread_bps = (spread / mid * 10000) if mid > 0 else 0
                change_24h = ((mid - price_24h) / price_24h * 100) if price_24h > 0 else 0
                
                market_data = MarketData(
                    timestamp=time.time(),
                    product_id=self.config.product_id,
                    data={
                        "type": "book_ticker",
                        "bid": bid,
                        "ask": ask,
                        "bid_size": bid_size,
                        "ask_size": ask_size,
                        "spread": spread,
                        "spread_bps": spread_bps,
                        "mid_price": mid,
                        "price_24h": price_24h,
                        "volume_24h": volume_24h,
                        "change_24h_pct": change_24h,
                        "low_24h": low_24h,
                        "high_24h": high_24h,
                    },
                    source_bot=self.config.name
                )
                self._emit_data(market_data)


class NessieLiquidation(LochnessBot):
    """Binah - Large Trade Detection (market_trades channel)
    
    Note: Coinbase doesn't have explicit liquidation events like Binance.
    We detect large trades that could be liquidations.
    """
    
    def __init__(self, data_callback=None, auth=None, large_trade_threshold: float = 50000):
        config = BotConfig(
            name="Nessie-Liquidation",
            sephira="Binah",
            channels=["market_trades"],
        )
        super().__init__(config, data_callback, auth)
        self.large_trade_threshold = large_trade_threshold
        self.large_trades = deque(maxlen=1000)
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process market trades for large trade detection"""
        if data.get("channel") != "market_trades":
            return
        
        events = data.get("events", [])
        for event in events:
            trades = event.get("trades", [])
            for trade in trades:
                price = float(trade.get("price", 0))
                size = float(trade.get("size", 0))
                side = trade.get("side", "").upper()
                trade_id = trade.get("trade_id", "")
                timestamp = trade.get("time", "")
                
                notional = price * size
                
                if notional >= self.large_trade_threshold:
                    large_trade = {
                        "product_id": trade.get("product_id", self.config.product_id),
                        "price": price,
                        "size": size,
                        "notional": notional,
                        "side": side,
                        "trade_id": trade_id,
                        "time": timestamp,
                    }
                    
                    self.large_trades.append(large_trade)
                    
                    market_data = MarketData(
                        timestamp=time.time(),
                        product_id=trade.get("product_id", self.config.product_id),
                        data={
                            "type": "large_trade",
                            **large_trade,
                        },
                        source_bot=self.config.name
                    )
                    self._emit_data(market_data)


class NessieWhale(LochnessBot):
    """Chesed - Whale Watcher (market_trades with higher threshold)"""
    
    def __init__(self, data_callback=None, auth=None, whale_threshold_usd: float = 100000):
        config = BotConfig(
            name="Nessie-Whale",
            sephira="Chesed",
            channels=["market_trades"],
        )
        super().__init__(config, data_callback, auth)
        self.whale_threshold = whale_threshold_usd
        self.whale_trades = deque(maxlen=500)
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process trades for whale detection"""
        if data.get("channel") != "market_trades":
            return
        
        events = data.get("events", [])
        for event in events:
            trades = event.get("trades", [])
            for trade in trades:
                price = float(trade.get("price", 0))
                size = float(trade.get("size", 0))
                side = trade.get("side", "").upper()
                trade_id = trade.get("trade_id", "")
                timestamp = trade.get("time", "")
                
                notional = price * size
                
                if notional >= self.whale_threshold:
                    whale_trade = {
                        "product_id": trade.get("product_id", self.config.product_id),
                        "price": price,
                        "size": size,
                        "notional": notional,
                        "side": side,
                        "trade_id": trade_id,
                        "time": timestamp,
                    }
                    
                    self.whale_trades.append(whale_trade)
                    
                    market_data = MarketData(
                        timestamp=time.time(),
                        product_id=trade.get("product_id", self.config.product_id),
                        data={
                            "type": "whale_trade",
                            **whale_trade,
                        },
                        source_bot=self.config.name
                    )
                    self._emit_data(market_data)


class NessieFunding(LochnessBot):
    """Geburah - Futures Basis Monitor
    
    Coinbase doesn't have funding rates like Binance perpetuals.
    Instead, monitor futures basis (futures price - spot price).
    """
    
    def __init__(self, data_callback=None, auth=None):
        config = BotConfig(
            name="Nessie-Funding",
            sephira="Geburah",
            channels=["ticker"],
        )
        super().__init__(config, data_callback, auth)
        
        # Track spot and futures for basis calculation
        self.spot_product = "BTC-USD"
        self.futures_products = ["BTC-USD-PERP", "BTC-USD-2025Q1"]  # Example futures
        
        self.basis_history = deque(maxlen=1000)
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process ticker for basis monitoring"""
        if data.get("channel") != "ticker":
            return
        
        events = data.get("events", [])
        for event in events:
            tickers = event.get("tickers", [])
            for ticker in tickers:
                product = ticker.get("product_id", "")
                mid = (float(ticker.get("best_bid", 0)) + float(ticker.get("best_ask", 0))) / 2
                
                if product == self.spot_product:
                    self.spot_price = mid
                elif product in self.futures_products:
                    futures_price = mid
                    if hasattr(self, 'spot_price') and self.spot_price > 0:
                        basis = futures_price - self.spot_price
                        basis_pct = (basis / self.spot_price * 100) if self.spot_price > 0 else 0
                        annualized = basis_pct * (365 / 30)  # Rough monthly to annual
                        
                        self.basis_history.append({
                            "spot": self.spot_price,
                            "futures": futures_price,
                            "basis": basis,
                            "basis_pct": basis_pct,
                            "annualized_pct": annualized,
                            "product": product,
                            "time": time.time(),
                        })
                        
                        market_data = MarketData(
                            timestamp=time.time(),
                            product_id=product,
                            data={
                                "type": "futures_basis",
                                "spot_price": self.spot_price,
                                "futures_price": futures_price,
                                "basis": basis,
                                "basis_pct": basis_pct,
                                "annualized_pct": annualized,
                                "product": product,
                            },
                            source_bot=self.config.name
                        )
                        self._emit_data(market_data)


class NessieKline(LochnessBot):
    """Tiferet - Candlestick Aggregator (candles_1m)"""

    def __init__(self, data_callback=None, auth=None):
        config = BotConfig(
            name="Nessie-Kline",
            sephira="Tiferet",
            channels=["candles"],  # Try "candles" instead of "candles_1m"
        )
        super().__init__(config, data_callback, auth)
        self.klines = deque(maxlen=1440)
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process candle updates"""
        if data.get("channel") != "candles_1m":
            return
        
        events = data.get("events", [])
        for event in events:
            candles = event.get("candles", [])
            for candle in candles:
                # Coinbase candle format
                kline = {
                    "product_id": candle.get("product_id", self.config.product_id),
                    "start": candle.get("start"),
                    "end": candle.get("end"),
                    "open": float(candle.get("open", 0)),
                    "high": float(candle.get("high", 0)),
                    "low": float(candle.get("low", 0)),
                    "close": float(candle.get("close", 0)),
                    "volume": float(candle.get("volume", 0)),
                }
                
                self.klines.append(kline)
                self.price_buffer.append(kline["close"])
                self.volume_buffer.append(kline["volume"])
                
                market_data = MarketData(
                    timestamp=time.time(),
                    product_id=kline["product_id"],
                    data={
                        "type": "kline",
                        **kline,
                    },
                    source_bot=self.config.name
                )
                self._emit_data(market_data)


class NessieSentiment(LochnessBot):
    """Netzach - Order Flow Sentiment (user channel for authenticated orders)"""
    
    def __init__(self, data_callback=None, auth=None):
        config = BotConfig(
            name="Nessie-Sentiment",
            sephira="Netzach",
            channels=["user"],  # Requires auth
        )
        super().__init__(config, data_callback, auth)
        
        self.order_flow = deque(maxlen=1000)
        self.buy_volume = 0
        self.sell_volume = 0
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process user order events"""
        if data.get("channel") != "user":
            return
        
        events = data.get("events", [])
        for event in events:
            if event.get("type") == "fill":
                fills = event.get("fills", [])
                for fill in fills:
                    price = float(fill.get("price", 0))
                    size = float(fill.get("size", 0))
                    side = fill.get("side", "").upper()
                    product_id = fill.get("product_id", self.config.product_id)
                    order_id = fill.get("order_id", "")
                    trade_id = fill.get("trade_id", "")
                    timestamp = fill.get("time", "")
                    
                    notional = price * size
                    
                    if side == "BUY":
                        self.buy_volume += notional
                    else:
                        self.sell_volume += notional
                    
                    total = self.buy_volume + self.sell_volume
                    ratio = self.buy_volume / self.sell_volume if self.sell_volume > 0 else float('inf')
                    sentiment = "bullish" if ratio > 1.2 else "bearish" if ratio < 0.8 else "neutral"
                    
                    self.order_flow.append({
                        "price": price,
                        "size": size,
                        "notional": notional,
                        "side": side,
                        "product_id": product_id,
                        "timestamp": timestamp,
                    })
                    
                    market_data = MarketData(
                        timestamp=time.time(),
                        product_id=product_id,
                        data={
                            "type": "order_flow",
                            "price": price,
                            "size": size,
                            "notional": notional,
                            "side": side,
                            "buy_volume": self.buy_volume,
                            "sell_volume": self.sell_volume,
                            "buy_sell_ratio": ratio,
                            "sentiment": sentiment,
                        },
                        source_bot=self.config.name
                    )
                    self._emit_data(market_data)


# ============================================================================
# NEW 3 BOTS - MISSING SEPHIROTH
# ============================================================================

class NessieTechnical(LochnessBot):
    """Hod - Technical Analysis (candles_1m + level2)"""
    
    def __init__(self, data_callback=None, auth=None):
        config = BotConfig(
            name="Nessie-Technical",
            sephira="Hod",
            channels=["candles_1m", "level2"],
        )
        super().__init__(config, data_callback, auth)
        
        self.closes = deque(maxlen=200)
        self.highs = deque(maxlen=200)
        self.lows = deque(maxlen=200)
        self.volumes = deque(maxlen=200)
        
        self.rsi = 50.0
        self.macd = {"macd": 0, "signal": 0, "histogram": 0}
        self.bollinger = {"upper": 0, "middle": 0, "lower": 0}
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process candles and level2 for technical analysis"""
        channel = data.get("channel")
        
        if channel == "candles_1m":
            await self._process_candle(data)
    
    async def _process_candle(self, data: Dict[str, Any]):
        """Process completed candlestick"""
        events = data.get("events", [])
        for event in events:
            candles = event.get("candles", [])
            for candle in candles:
                close = float(candle.get("close", 0))
                high = float(candle.get("high", 0))
                low = float(candle.get("low", 0))
                volume = float(candle.get("volume", 0))
                
                self.closes.append(close)
                self.highs.append(high)
                self.lows.append(low)
                self.volumes.append(volume)
                
                if len(self.closes) < 26:
                    return
                
                self._update_rsi()
                self._update_macd()
                self._update_bollinger()
                
                signals = self._generate_signals(close)
                
                market_data = MarketData(
                    timestamp=time.time(),
                    product_id=self.config.product_id,
                    data={
                        "type": "technical_analysis",
                        "price": close,
                        "rsi": self.rsi,
                        "macd": self.macd,
                        "bollinger": self.bollinger,
                        "signals": signals,
                        "volume_24h": sum(self.volumes),
                    },
                    source_bot=self.config.name
                )
                self._emit_data(market_data)
    
    def _update_rsi(self, period: int = 14):
        if len(self.closes) < period + 1:
            return
        
        deltas = np.diff(list(self.closes)[-(period+1):])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            self.rsi = 100
        else:
            rs = avg_gain / avg_loss
            self.rsi = 100 - (100 / (1 + rs))
    
    def _update_macd(self, fast: int = 12, slow: int = 26, signal: int = 9):
        closes = list(self.closes)
        if len(closes) < slow:
            return
        
        ema_fast = self._ema(closes, fast)
        ema_slow = self._ema(closes, slow)
        
        macd_line = ema_fast - ema_slow
        self.macd["macd"] = macd_line
        self.macd["signal"] = self.macd["signal"] * 0.8 + macd_line * 0.2
        self.macd["histogram"] = self.macd["macd"] - self.macd["signal"]
    
    def _update_bollinger(self, period: int = 20, std_dev: float = 2.0):
        if len(self.closes) < period:
            return
        
        recent = list(self.closes)[-period:]
        middle = np.mean(recent)
        std = np.std(recent)
        
        self.bollinger["middle"] = middle
        self.bollinger["upper"] = middle + std_dev * std
        self.bollinger["lower"] = middle - std_dev * std
    
    def _ema(self, data: List[float], period: int) -> float:
        if len(data) < period:
            return data[-1]
        
        k = 2 / (period + 1)
        ema = data[0]
        for price in data[1:]:
            ema = price * k + ema * (1 - k)
        return ema
    
    def _generate_signals(self, price: float) -> Dict[str, Any]:
        signals = {}
        
        if self.rsi > 70:
            signals["rsi"] = "overbought"
        elif self.rsi < 30:
            signals["rsi"] = "oversold"
        else:
            signals["rsi"] = "neutral"
        
        if self.macd["histogram"] > 0 and self.macd["macd"] > self.macd["signal"]:
            signals["macd"] = "bullish"
        elif self.macd["histogram"] < 0 and self.macd["macd"] < self.macd["signal"]:
            signals["macd"] = "bearish"
        else:
            signals["macd"] = "neutral"
        
        if price > self.bollinger["upper"]:
            signals["bollinger"] = "breakout_up"
        elif price < self.bollinger["lower"]:
            signals["bollinger"] = "breakout_down"
        else:
            width = self.bollinger["upper"] - self.bollinger["lower"]
            if width > 0:
                pos = (price - self.bollinger["lower"]) / width
                signals["bollinger"] = "upper" if pos > 0.8 else "lower" if pos < 0.2 else "middle"
            else:
                signals["bollinger"] = "neutral"
        
        return signals


class NessieInfrastructure(LochnessBot):
    """Yesod - Order Book Infrastructure Monitor (ticker + level2)"""
    
    def __init__(self, data_callback=None, auth=None):
        config = BotConfig(
            name="Nessie-Infrastructure",
            sephira="Yesod",
            channels=["ticker", "level2"],
        )
        super().__init__(config, data_callback, auth)
        
        self.spread_samples = deque(maxlen=1000)
        self.depth_samples = deque(maxlen=1000)
        self.update_intervals = deque(maxlen=1000)
        self.last_update = 0
        self.health_score = 100.0
        self.staleness_threshold = 5.0
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process ticker and level2 for infrastructure health"""
        now = time.time()
        
        if self.last_update > 0:
            interval = now - self.last_update
            self.update_intervals.append(interval)
        self.last_update = now
        
        channel = data.get("channel")
        
        if channel == "ticker":
            await self._process_ticker(data, now)
        elif channel == "level2":
            await self._process_level2(data, now)
    
    async def _process_ticker(self, data: Dict[str, Any], now: float):
        events = data.get("events", [])
        for event in events:
            tickers = event.get("tickers", [])
            for ticker in tickers:
                bid = float(ticker.get("best_bid", 0))
                ask = float(ticker.get("best_ask", 0))
                bid_qty = float(ticker.get("best_bid_size", 0))
                ask_qty = float(ticker.get("best_ask_size", 0))
                
                if bid > 0 and ask > 0:
                    spread = ask - bid
                    mid = (bid + ask) / 2
                    spread_bps = (spread / mid * 10000) if mid > 0 else 0
                    
                    self.spread_samples.append(spread_bps)
                    self.depth_samples.append(bid_qty + ask_qty)
        
        await self._assess_health(now)
    
    async def _process_level2(self, data: Dict[str, Any], now: float):
        if not self.order_book["bids"] or not self.order_book["asks"]:
            return
        
        # Calculate depth metrics
        mid = (max(self.order_book["bids"].keys()) + min(self.order_book["asks"].keys())) / 2 if self.order_book["bids"] and self.order_book["asks"] else 0
        
        if mid > 0:
            depth_1pct = self._depth_within_pct(0.01)
            depth_5pct = self._depth_within_pct(0.05)
            
            best_bid = max(self.order_book["bids"].keys()) if self.order_book["bids"] else 0
            best_ask = min(self.order_book["asks"].keys()) if self.order_book["asks"] else 0
            spread = best_ask - best_bid
            spread_bps = (spread / mid * 10000) if mid > 0 else 0
            
            bid_vol = sum(self.order_book["bids"].values())
            ask_vol = sum(self.order_book["asks"].values())
            imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol) if (bid_vol + ask_vol) > 0 else 0
            
            market_data = MarketData(
                timestamp=now,
                product_id=self.config.product_id,
                data={
                    "type": "infrastructure",
                    "spread_bps": spread_bps,
                    "depth_1pct": depth_1pct,
                    "depth_5pct": depth_5pct,
                    "imbalance": imbalance,
                    "health_score": self.health_score,
                    "update_latency_ms": statistics.mean(self.update_intervals) * 1000 if self.update_intervals else 0,
                },
                source_bot=self.config.name
            )
            self._emit_data(market_data)
    
    def _depth_within_pct(self, pct: float) -> float:
        if not self.order_book["bids"] or not self.order_book["asks"]:
            return 0
        
        mid = (max(self.order_book["bids"].keys()) + min(self.order_book["asks"].keys())) / 2
        lower = mid * (1 - pct)
        upper = mid * (1 + pct)
        
        total = 0
        for price, qty in self.order_book["bids"].items():
            if lower <= price <= mid:
                total += qty
        for price, qty in self.order_book["asks"].items():
            if mid <= price <= upper:
                total += qty
        return total
    
    async def _assess_health(self, now: float):
        if not self.spread_samples or not self.update_intervals:
            return
        
        avg_spread = statistics.mean(self.spread_samples)
        spread_score = max(0, 100 - avg_spread * 10)
        
        avg_interval = statistics.mean(self.update_intervals)
        latency_score = max(0, 100 - avg_interval * 1000)
        
        stale = now - self.last_update > self.staleness_threshold
        stale_penalty = 50 if stale else 0
        
        if self.depth_samples:
            avg_depth = statistics.mean(self.depth_samples)
            depth_score = min(100, avg_depth / 10)
        else:
            depth_score = 0
        
        self.health_score = (spread_score + latency_score + depth_score) / 3 - stale_penalty
        self.health_score = max(0, min(100, self.health_score))


class NessieReality(LochnessBot):
    """Malkuth - Player Behavior & PnL Tracker (user channel)"""
    
    def __init__(self, data_callback=None, auth=None):
        config = BotConfig(
            name="Nessie-Reality",
            sephira="Malkuth",
            channels=["user"],  # Requires auth for user trades
        )
        super().__init__(config, data_callback, auth)
        
        self.user_fills = deque(maxlen=1000)
        self.pnl = 0.0
        self.position = 0.0
        self.avg_entry = 0.0
        self.realized_pnl = 0.0
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process user fills for PnL tracking"""
        if data.get("channel") != "user":
            return
        
        events = data.get("events", [])
        for event in events:
            if event.get("type") == "fill":
                fills = event.get("fills", [])
                for fill in fills:
                    price = float(fill.get("price", 0))
                    size = float(fill.get("size", 0))
                    side = fill.get("side", "").upper()
                    product_id = fill.get("product_id", self.config.product_id)
                    order_id = fill.get("order_id", "")
                    trade_id = fill.get("trade_id", "")
                    timestamp = fill.get("time", "")
                    
                    notional = price * size
                    
                    # Track position
                    if side == "BUY":
                        if self.position >= 0:
                            # Adding to long or reducing short
                            total_cost = self.avg_entry * self.position + price * size
                            self.position += size
                            self.avg_entry = total_cost / self.position if self.position > 0 else 0
                        else:
                            # Reducing short position
                            realized = (self.avg_entry - price) * min(size, abs(self.position))
                            self.realized_pnl += realized
                            self.position += size
                            if self.position > 0:
                                self.avg_entry = price
                    else:  # SELL
                        if self.position <= 0:
                            # Adding to short or reducing long
                            total_cost = self.avg_entry * abs(self.position) + price * size
                            self.position -= size
                            self.avg_entry = total_cost / abs(self.position) if self.position < 0 else 0
                        else:
                            # Reducing long position
                            realized = (price - self.avg_entry) * min(size, self.position)
                            self.realized_pnl += realized
                            self.position -= size
                            if self.position < 0:
                                self.avg_entry = price
                    
                    # Unrealized PnL
                    unrealized = 0
                    if self.position > 0:
                        unrealized = (price - self.avg_entry) * self.position
                    elif self.position < 0:
                        unrealized = (self.avg_entry - price) * abs(self.position)
                    
                    total_pnl = self.realized_pnl + unrealized
                    
                    fill_data = {
                        "price": price,
                        "size": size,
                        "notional": notional,
                        "side": side,
                        "product_id": product_id,
                        "timestamp": timestamp,
                    }
                    
                    self.user_fills.append(fill_data)
                    
                    market_data = MarketData(
                        timestamp=time.time(),
                        product_id=product_id,
                        data={
                            "type": "user_fill",
                            "fill": fill_data,
                            "position": self.position,
                            "avg_entry": self.avg_entry,
                            "unrealized_pnl": unrealized,
                            "realized_pnl": self.realized_pnl,
                            "total_pnl": total_pnl,
                        },
                        source_bot=self.config.name
                    )
                    self._emit_data(market_data)


# ============================================================================
# BOT ORCHESTRATOR
# ============================================================================

class LochnessOrchestrator:
    """Manages all 10 Lochness bots"""
    
    def __init__(self, data_callback=None, api_key: str = "", api_secret: str = ""):
        self.data_callback = data_callback
        self.auth = CoinbaseAuth(api_key, api_secret)
        self.bots: List[LochnessBot] = []
        self.running = False
        
        self._init_bots()
    
    def _init_bots(self):
        """Initialize all 10 Lochness bots"""
        # Existing 7
        self.bots.append(NessiePrime(self.data_callback, self.auth))           # Keter
        self.bots.append(NessieArbitrage(self.data_callback, self.auth))       # Chokmah
        self.bots.append(NessieLiquidation(self.data_callback, self.auth))     # Binah
        self.bots.append(NessieWhale(self.data_callback, self.auth))           # Chesed
        self.bots.append(NessieFunding(self.data_callback, self.auth))         # Geburah
        self.bots.append(NessieKline(self.data_callback, self.auth))           # Tiferet
        self.bots.append(NessieSentiment(self.data_callback, self.auth))       # Netzach
        
        # NEW: Missing 3
        self.bots.append(NessieTechnical(self.data_callback, self.auth))       # Hod
        self.bots.append(NessieInfrastructure(self.data_callback, self.auth))  # Yesod
        self.bots.append(NessieReality(self.data_callback, self.auth))         # Malkuth
    
    async def start_all(self):
        """Start all bots"""
        self.running = True
        tasks = [bot.start() for bot in self.bots]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_all(self):
        """Stop all bots"""
        self.running = False
        tasks = [bot.stop() for bot in self.bots]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_all_stats(self) -> List[Dict[str, Any]]:
        """Get stats for all bots"""
        return [bot.get_stats() for bot in self.bots]
    
    def get_sephirah_coverage(self) -> Dict[str, str]:
        """Get Sephirah → Bot mapping"""
        return {bot.config.sephira: bot.config.name for bot in self.bots}


# ============================================================================
# ABYSSAL EXCHANGE BRIDGE
# ============================================================================

class AbyssalExchangeBridge:
    """Bridge Lochness market data to Abyssal Assets Exchange"""
    
    def __init__(self, abyssal_api_url: str = None):
        self.api_url = abyssal_api_url or os.getenv("ABYSSAL_API_URL", "http://localhost:8000")
        self.latest_data = {}
        self.order_book = {"bids": [], "asks": []}
    
    async def on_market_data(self, data: MarketData):
        """Receive market data from Lochness bots"""
        key = f"{data.source_bot}:{data.product_id}"
        self.latest_data[key] = data
        
        # Update order book from depth data
        if data.data.get("type") == "market_depth":
            self.order_book["bids"] = data.data.get("bids", [])
            self.order_book["asks"] = data.data.get("asks", [])
        
        # Forward to Abyssal Exchange
        await self._forward_to_abyssal(data)
    
    async def _forward_to_abyssal(self, data: MarketData):
        """Send relevant data to Abyssal Exchange API"""
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                if data.data.get("type") == "market_depth":
                    await client.post(
                        f"{self.api_url}/api/market/depth",
                        json={
                            "product_id": data.product_id,
                            "bids": data.data.get("bids", []),
                            "asks": data.data.get("asks", []),
                            "timestamp": data.timestamp,
                        }
                    )
                elif data.data.get("type") == "book_ticker":
                    await client.post(
                        f"{self.api_url}/api/market/ticker",
                        json={
                            "product_id": data.product_id,
                            "bid": data.data.get("bid"),
                            "ask": data.data.get("ask"),
                            "spread_bps": data.data.get("spread_bps"),
                            "timestamp": data.timestamp,
                        }
                    )
                elif data.data.get("type") == "whale_trade":
                    await client.post(
                        f"{self.api_url}/api/market/whale-alert",
                        json={
                            "product_id": data.product_id,
                            "notional": data.data.get("notional"),
                            "side": data.data.get("side"),
                            "timestamp": data.timestamp,
                        }
                    )
                elif data.data.get("type") == "futures_basis":
                    await client.post(
                        f"{self.api_url}/api/market/basis",
                        json={
                            "product_id": data.product_id,
                            "basis": data.data.get("basis"),
                            "basis_pct": data.data.get("basis_pct"),
                            "annualized": data.data.get("annualized_pct"),
                            "timestamp": data.timestamp,
                        }
                    )
                elif data.data.get("type") == "technical_analysis":
                    await client.post(
                        f"{self.api_url}/api/market/technical",
                        json={
                            "product_id": data.product_id,
                            "rsi": data.data.get("rsi"),
                            "macd": data.data.get("macd"),
                            "bollinger": data.data.get("bollinger"),
                            "signals": data.data.get("signals"),
                            "timestamp": data.timestamp,
                        }
                    )
                elif data.data.get("type") in ("sentiment", "sentiment_public"):
                    await client.post(
                        f"{self.api_url}/api/market/sentiment",
                        json={
                            "product_id": data.product_id,
                            "sentiment": data.data.get("sentiment", "neutral"),
                            "sentiment_score": data.data.get("sentiment_score", 0),
                            "momentum_24h_pct": data.data.get("momentum_24h_pct", 0),
                            "timestamp": data.timestamp,
                            "source_bot": data.source_bot,
                        }
                    )
                # Periodic NSSP token sync on whale/depth events
                if data.data.get("type") in ("market_depth", "whale_trade", "book_ticker"):
                    try:
                        await client.post("http://localhost:8010/api/tokens/sync", timeout=2)
                    except Exception:
                        pass
        except Exception as e:
            print(f"[AbyssalBridge] Forward error: {e}")
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get aggregated market summary for Abyssal UI"""
        summary = {}
        for key, data in self.latest_data.items():
            bot_name, product = key.split(":", 1)
            if product not in summary:
                summary[product] = {}
            summary[product][bot_name] = {
                "type": data.data.get("type"),
                "data": {k: v for k, v in data.data.items() if k not in ["bids", "asks"]},
                "timestamp": data.timestamp,
            }
        return summary


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Run all 10 Lochness bots with Abyssal bridge"""
    print("=" * 60)
    print("LOCHNESS MONSTERS - COINBASE ADVANCED TRADE")
    print("10 SEPHIROT BOTS")
    print("=" * 60)
    
    # Initialize bridge
    bridge = AbyssalExchangeBridge()
    
    # Initialize orchestrator (add API keys for authenticated channels)
    api_key = os.getenv("COINBASE_API_KEY", "")
    api_secret = os.getenv("COINBASE_API_SECRET", "")
    
    orchestrator = LochnessOrchestrator(
        data_callback=bridge.on_market_data,
        api_key=api_key,
        api_secret=api_secret
    )
    
    # Print Sephirah coverage
    print("\nSephirah Coverage (Coinbase):")
    for sephira, bot_name in orchestrator.get_sephirah_coverage().items():
        print(f"  {sephira:>8} → {bot_name}")
    
    # Show channel mapping
    print("\nChannel Mapping:")
    for bot in orchestrator.bots:
        print(f"  {bot.config.sephira:>8} ({bot.config.name:>20}) → {bot.config.channels}")
    
    if not api_key or not api_secret:
        print("\n⚠️  No Coinbase API credentials found.")
        print("   Set COINBASE_API_KEY and COINBASE_API_SECRET for:")
        print("   - Nessie-Sentiment (user channel)")
        print("   - Nessie-Reality (user channel)")
        print("   Running with public channels only.")
    
    # Start all bots
    print("\nStarting all bots...")
    await orchestrator.start_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")