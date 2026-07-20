# Lochness Monsters - Binance WebSocket Monitoring Bots
# =======================================================
# 7 Sephiroth-aligned bots monitoring Binance streams
# Missing: Hod (Technical), Yesod (Infrastructure), Malkuth (Reality)
#
# Existing (7):
# - Keter:      Nessie-Prime      → depth20@100ms      → Market Depth
# - Chokmah:    Nessie-Arbitrage  → bookTicker         → Arbitrage
# - Binah:      Nessie-Liquidation→ forceOrder         → Liquidations
# - Chesed:     Nessie-Whale      → aggTrade>100k      → Whale Watch
# - Geburah:    Nessie-Funding    → premiumIndex       → Funding Rates
# - Tiferet:    Nessie-Kline      → kline_1m           → OHLCV Charts
# - Netzach:    Nessie-Sentiment  → longShortRatio     → Sentiment
#
# Missing (3):
# - Hod:        Nessie-Technical  → kline + depth      → Technical Analysis (RSI, MACD, BB)
# - Yesod:      Nessie-Infrastructure → bookTicker + depth → Order Book Health
# - Malkuth:    Nessie-Reality    → userDataStream     → Player Behavior/PnL

import asyncio
import json
import os
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import websockets
import httpx
import numpy as np

# ============================================================================
# BASE BOT FRAMEWORK
# ============================================================================

@dataclass
class BotConfig:
    """Configuration for a Lochness bot"""
    name: str
    sephira: str
    stream: str
    symbol: str = "BTCUSDT"
    interval: str = "1m"
    reconnect_delay: float = 5.0
    max_reconnect_attempts: int = 10
    heartbeat_interval: float = 30.0


@dataclass
class MarketData:
    """Normalized market data point"""
    timestamp: float
    symbol: str
    data: Dict[str, Any]
    source_bot: str


class LochnessBot(ABC):
    """Base class for all Lochness Binance monitoring bots"""
    
    def __init__(self, config: BotConfig, data_callback: Optional[Callable] = None):
        self.config = config
        self.data_callback = data_callback
        self.running = False
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.reconnect_attempts = 0
        self.last_heartbeat = 0
        self.message_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
        # Data buffers for analysis
        self.price_buffer = deque(maxlen=1000)
        self.volume_buffer = deque(maxlen=1000)
        self.trade_buffer = deque(maxlen=5000)
        
    @property
    def binance_ws_url(self) -> str:
        """Base Binance WebSocket URL"""
        return f"wss://stream.binance.com:9443/ws/{self.config.symbol.lower()}@{self.config.stream}"
    
    @property
    def binance_combined_url(self) -> str:
        """Combined stream URL for multiple streams"""
        return "wss://stream.binance.com:9443/stream"
    
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
                await asyncio.sleep(self.config.reconnect_delay * self.reconnect_attempts)
        
        if self.reconnect_attempts >= self.config.max_reconnect_attempts:
            print(f"[{self.config.name}] Max reconnection attempts reached, stopping")
    
    async def _connect(self):
        """Establish WebSocket connection"""
        url = self.binance_ws_url
        print(f"[{self.config.name}] Connecting to {url}")
        self.ws = await websockets.connect(url, ping_interval=20, ping_timeout=10)
        self.reconnect_attempts = 0
        print(f"[{self.config.name}] Connected")
    
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
            
            # Periodic heartbeat
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
    
    async def _emit_data(self, data: MarketData):
        """Emit normalized data to callback"""
        if self.data_callback:
            try:
                await self.data_callback(data)
            except Exception as e:
                print(f"[{self.config.name}] Callback error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        return {
            "name": self.config.name,
            "sephira": self.config.sephira,
            "running": self.running,
            "uptime_seconds": time.time() - self.start_time,
            "messages_processed": self.message_count,
            "errors": self.error_count,
            "reconnect_attempts": self.reconnect_attempts,
        }


# ============================================================================
# EXISTING BOTS (Reference implementations)
# ============================================================================

class NessiePrime(LochnessBot):
    """Keter - Market Depth Monitor (depth20@100ms)"""
    
    def __init__(self, data_callback=None):
        config = BotConfig(
            name="Nessie-Prime",
            sephira="Keter",
            stream="depth20@100ms",
        )
        super().__init__(config, data_callback)
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process order book depth update"""
        if "bids" not in data or "asks" not in data:
            return
        
        bids = [[float(p), float(q)] for p, q in data["bids"][:20]]
        asks = [[float(p), float(q)] for p, q in data["asks"][:20]]
        
        # Calculate spread and depth metrics
        best_bid = bids[0][0] if bids else 0
        best_ask = asks[0][0] if asks else 0
        spread = best_ask - best_bid if best_bid and best_ask else 0
        spread_pct = (spread / best_bid * 100) if best_bid else 0
        
        bid_depth = sum(q for _, q in bids)
        ask_depth = sum(q for _, q in asks)
        
        market_data = MarketData(
            timestamp=time.time(),
            symbol=self.config.symbol,
            data={
                "type": "market_depth",
                "best_bid": best_bid,
                "best_ask": best_ask,
                "spread": spread,
                "spread_pct": spread_pct,
                "bid_depth": bid_depth,
                "ask_depth": ask_depth,
                "imbalance": (bid_depth - ask_depth) / (bid_depth + ask_depth) if (bid_depth + ask_depth) > 0 else 0,
                "bids": bids,
                "asks": asks,
            },
            source_bot=self.config.name
        )
        self._emit_data(market_data)


class NessieArbitrage(LochnessBot):
    """Chokmah - Arbitrage Scanner (bookTicker)"""
    
    def __init__(self, data_callback=None):
        config = BotConfig(
            name="Nessie-Arbitrage",
            sephira="Chokmah",
            stream="bookTicker",
        )
        super().__init__(config, data_callback)
        self.last_prices = {}
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process best bid/ask ticker"""
        if "b" not in data or "a" not in data:
            return
        
        bid = float(data["b"])
        ask = float(data["a"])
        bid_qty = float(data["B"])
        ask_qty = float(data["A"])
        
        # Cross-exchange arbitrage would go here
        # For now, track spread
        spread = ask - bid
        mid = (bid + ask) / 2
        spread_bps = (spread / mid * 10000) if mid > 0 else 0
        
        market_data = MarketData(
            timestamp=time.time(),
            symbol=self.config.symbol,
            data={
                "type": "book_ticker",
                "bid": bid,
                "ask": ask,
                "bid_qty": bid_qty,
                "ask_qty": ask_qty,
                "spread": spread,
                "spread_bps": spread_bps,
                "mid_price": mid,
            },
            source_bot=self.config.name
        )
        self._emit_data(market_data)


class NessieLiquidation(LochnessBot):
    """Binah - Liquidation Tracker (forceOrder)"""
    
    def __init__(self, data_callback=None):
        config = BotConfig(
            name="Nessie-Liquidation",
            sephira="Binah",
            stream="forceOrder",
        )
        super().__init__(config, data_callback)
        self.liquidations = deque(maxlen=1000)
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process liquidation event"""
        if "o" not in data:
            return
        
        order = data["o"]
        liquidation = {
            "symbol": order.get("s"),
            "side": order.get("S"),
            "price": float(order.get("p", 0)),
            "quantity": float(order.get("q", 0)),
            "status": order.get("X"),
            "time": data.get("E", time.time() * 1000),
        }
        
        self.liquidations.append(liquidation)
        
        market_data = MarketData(
            timestamp=time.time(),
            symbol=liquidation["symbol"],
            data={
                "type": "liquidation",
                **liquidation,
                "notional": liquidation["price"] * liquidation["quantity"],
            },
            source_bot=self.config.name
        )
        self._emit_data(market_data)


class NessieWhale(LochnessBot):
    """Chesed - Whale Watcher (aggTrade)"""
    
    def __init__(self, data_callback=None, whale_threshold_usd: float = 100000):
        config = BotConfig(
            name="Nessie-Whale",
            sephira="Chesed",
            stream="aggTrade",
        )
        super().__init__(config, data_callback)
        self.whale_threshold = whale_threshold_usd
        self.whale_trades = deque(maxlen=500)
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process aggregated trade"""
        if "p" not in data or "q" not in data:
            return
        
        price = float(data["p"])
        qty = float(data["q"])
        notional = price * qty
        
        is_whale = notional >= self.whale_threshold
        
        if is_whale:
            whale_trade = {
                "symbol": data.get("s"),
                "price": price,
                "quantity": qty,
                "notional": notional,
                "side": "BUY" if data.get("m", False) else "SELL",  # m = isBuyerMaker
                "trade_id": data.get("a"),
                "time": data.get("T", time.time() * 1000),
            }
            self.whale_trades.append(whale_trade)
            
            market_data = MarketData(
                timestamp=time.time(),
                symbol=whale_trade["symbol"],
                data={
                    "type": "whale_trade",
                    **whale_trade,
                },
                source_bot=self.config.name
            )
            self._emit_data(market_data)


class NessieFunding(LochnessBot):
    """Geburah - Funding Rate Monitor (premiumIndex)"""
    
    def __init__(self, data_callback=None):
        config = BotConfig(
            name="Nessie-Funding",
            sephira="Geburah",
            stream="premiumIndex",
        )
        super().__init__(config, data_callback)
        self.funding_history = deque(maxlen=1000)
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process premium index / funding rate update"""
        if "p" not in data or "r" not in data:
            return
        
        mark_price = float(data["p"])
        index_price = float(data["i"]) if "i" in data else mark_price
        funding_rate = float(data["r"])
        next_funding_time = data.get("T", 0)
        
        # Calculate annualized funding rate
        annualized_rate = funding_rate * 3 * 365 * 100  # 3x daily, percentage
        
        self.funding_history.append({
            "mark_price": mark_price,
            "index_price": index_price,
            "funding_rate": funding_rate,
            "annualized_rate_pct": annualized_rate,
            "next_funding_time": next_funding_time,
            "time": time.time(),
        })
        
        market_data = MarketData(
            timestamp=time.time(),
            symbol=self.config.symbol,
            data={
                "type": "funding_rate",
                "mark_price": mark_price,
                "index_price": index_price,
                "funding_rate": funding_rate,
                "annualized_rate_pct": annualized_rate,
                "next_funding_time": next_funding_time,
            },
            source_bot=self.config.name
        )
        self._emit_data(market_data)


class NessieKline(LochnessBot):
    """Tiferet - Candlestick Aggregator (kline_1m)"""
    
    def __init__(self, data_callback=None):
        config = BotConfig(
            name="Nessie-Kline",
            sephira="Tiferet",
            stream="kline_1m",
        )
        super().__init__(config, data_callback)
        self.klines = deque(maxlen=1440)  # 24 hours of 1m candles
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process kline/candlestick data"""
        if "k" not in data:
            return
        
        k = data["k"]
        if not k.get("x", False):  # x = is_final (closed candle)
            return
        
        kline = {
            "symbol": k.get("s"),
            "open_time": k.get("t"),
            "close_time": k.get("T"),
            "open": float(k.get("o", 0)),
            "high": float(k.get("h", 0)),
            "low": float(k.get("l", 0)),
            "close": float(k.get("c", 0)),
            "volume": float(k.get("v", 0)),
            "trades": k.get("n", 0),
            "is_final": True,
        }
        
        self.klines.append(kline)
        
        # Update price buffers for technical analysis
        self.price_buffer.append(kline["close"])
        self.volume_buffer.append(kline["volume"])
        
        market_data = MarketData(
            timestamp=time.time(),
            symbol=kline["symbol"],
            data={
                "type": "kline",
                **kline,
            },
            source_bot=self.config.name
        )
        self._emit_data(market_data)


class NessieSentiment(LochnessBot):
    """Netzach - Sentiment Tracker (longShortRatio)"""
    
    def __init__(self, data_callback=None):
        config = BotConfig(
            name="Nessie-Sentiment",
            sephira="Netzach",
            stream="longShortRatio",
        )
        super().__init__(config, data_callback)
        self.ratio_history = deque(maxlen=1000)
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process long/short ratio"""
        if "longShortRatio" not in data:
            return
        
        ratio = float(data["longShortRatio"])
        long_account = float(data.get("longAccount", 0))
        short_account = float(data.get("shortAccount", 0))
        
        # Interpret ratio: >1 = more longs (bullish), <1 = more shorts (bearish)
        sentiment = "bullish" if ratio > 1.2 else "bearish" if ratio < 0.8 else "neutral"
        
        self.ratio_history.append({
            "ratio": ratio,
            "long_account": long_account,
            "short_account": short_account,
            "sentiment": sentiment,
            "time": time.time(),
        })
        
        market_data = MarketData(
            timestamp=time.time(),
            symbol=self.config.symbol,
            data={
                "type": "sentiment",
                "long_short_ratio": ratio,
                "long_account_pct": long_account * 100,
                "short_account_pct": short_account * 100,
                "sentiment": sentiment,
            },
            source_bot=self.config.name
        )
        self._emit_data(market_data)


# ============================================================================
# NEW BOTS - MISSING 3 SEPHIROTH
# ============================================================================

class NessieTechnical(LochnessBot):
    """Hod - Technical Analysis (RSI, MACD, Bollinger Bands, Volume Profile)
    
    Streams: kline_1m + depth20@100ms
    Outputs: Technical signals → Abyssal crafting bonuses
    """
    
    def __init__(self, data_callback=None):
        config = BotConfig(
            name="Nessie-Technical",
            sephira="Hod",
            stream="kline_1m",  # Primary, will also subscribe to depth
        )
        super().__init__(config, data_callback)
        
        # Technical indicator buffers
        self.closes = deque(maxlen=200)
        self.highs = deque(maxlen=200)
        self.lows = deque(maxlen=200)
        self.volumes = deque(maxlen=200)
        
        # Indicator states
        self.rsi = 50.0
        self.macd = {"macd": 0, "signal": 0, "histogram": 0}
        self.bollinger = {"upper": 0, "middle": 0, "lower": 0}
        self.volume_profile = {}
        
    async def _process_message(self, data: Dict[str, Any]):
        """Process kline for technical analysis"""
        # Handle both kline and depth stream messages
        if "k" in data:  # Kline stream
            await self._process_kline(data)
        elif "bids" in data:  # Depth stream
            await self._process_depth(data)
    
    async def _process_kline(self, data: Dict[str, Any]):
        """Process completed candlestick"""
        k = data["k"]
        if not k.get("x", False):
            return
        
        close = float(k["c"])
        high = float(k["h"])
        low = float(k["l"])
        volume = float(k["v"])
        
        self.closes.append(close)
        self.highs.append(high)
        self.lows.append(low)
        self.volumes.append(volume)
        
        # Need minimum data for indicators
        if len(self.closes) < 26:
            return
        
        # Calculate indicators
        self._update_rsi()
        self._update_macd()
        self._update_bollinger()
        
        # Generate signals
        signals = self._generate_signals(close)
        
        market_data = MarketData(
            timestamp=time.time(),
            symbol=self.config.symbol,
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
    
    async def _process_depth(self, data: Dict[str, Any]):
        """Process order book for volume profile"""
        bids = [[float(p), float(q)] for p, q in data.get("bids", [])]
        asks = [[float(p), float(q)] for p, q in data.get("asks", [])]
        
        # Build volume profile at price levels
        for price, qty in bids + asks:
            price_level = round(price, -1)  # Round to nearest 10
            self.volume_profile[price_level] = self.volume_profile.get(price_level, 0) + qty
        
        # Keep top 50 price levels
        sorted_levels = sorted(self.volume_profile.items(), key=lambda x: x[1], reverse=True)[:50]
        self.volume_profile = dict(sorted_levels)
    
    def _update_rsi(self, period: int = 14):
        """Calculate RSI"""
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
        """Calculate MACD"""
        closes = list(self.closes)
        if len(closes) < slow:
            return
        
        ema_fast = self._ema(closes, fast)
        ema_slow = self._ema(closes, slow)
        
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        # Simplified: use previous MACD values
        self.macd["macd"] = macd_line
        self.macd["signal"] = self.macd["signal"] * 0.8 + macd_line * 0.2
        self.macd["histogram"] = self.macd["macd"] - self.macd["signal"]
    
    def _update_bollinger(self, period: int = 20, std_dev: float = 2.0):
        """Calculate Bollinger Bands"""
        if len(self.closes) < period:
            return
        
        recent = list(self.closes)[-period:]
        middle = np.mean(recent)
        std = np.std(recent)
        
        self.bollinger["middle"] = middle
        self.bollinger["upper"] = middle + std_dev * std
        self.bollinger["lower"] = middle - std_dev * std
    
    def _ema(self, data: List[float], period: int) -> float:
        """Exponential Moving Average"""
        if len(data) < period:
            return data[-1]
        
        k = 2 / (period + 1)
        ema = data[0]
        for price in data[1:]:
            ema = price * k + ema * (1 - k)
        return ema
    
    def _generate_signals(self, price: float) -> Dict[str, Any]:
        """Generate trading signals from indicators"""
        signals = {}
        
        # RSI signals
        if self.rsi > 70:
            signals["rsi"] = "overbought"
        elif self.rsi < 30:
            signals["rsi"] = "oversold"
        else:
            signals["rsi"] = "neutral"
        
        # MACD signals
        if self.macd["histogram"] > 0 and self.macd["macd"] > self.macd["signal"]:
            signals["macd"] = "bullish"
        elif self.macd["histogram"] < 0 and self.macd["macd"] < self.macd["signal"]:
            signals["macd"] = "bearish"
        else:
            signals["macd"] = "neutral"
        
        # Bollinger signals
        if price > self.bollinger["upper"]:
            signals["bollinger"] = "breakout_up"
        elif price < self.bollinger["lower"]:
            signals["bollinger"] = "breakout_down"
        else:
            # Position within bands
            width = self.bollinger["upper"] - self.bollinger["lower"]
            if width > 0:
                pos = (price - self.bollinger["lower"]) / width
                signals["bollinger"] = "upper" if pos > 0.8 else "lower" if pos < 0.2 else "middle"
            else:
                signals["bollinger"] = "neutral"
        
        return signals


class NessieInfrastructure(LochnessBot):
    """Yesod - Order Book Infrastructure Monitor
    
    Streams: bookTicker + depth20@100ms
    Outputs: Exchange health, latency, order book quality → NGD route selection
    """
    
    def __init__(self, data_callback=None):
        config = BotConfig(
            name="Nessie-Infrastructure",
            sephira="Yesod",
            stream="bookTicker",  # Primary
        )
        super().__init__(config, data_callback)
        
        # Infrastructure metrics
        self.latency_samples = deque(maxlen=1000)
        self.spread_samples = deque(maxlen=1000)
        self.depth_samples = deque(maxlen=1000)
        self.update_intervals = deque(maxlen=1000)
        self.last_update = 0
        
        # Health scores
        self.health_score = 100.0
        self.staleness_threshold = 5.0  # seconds
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process book ticker or depth update"""
        now = time.time()
        
        # Track update frequency
        if self.last_update > 0:
            interval = now - self.last_update
            self.update_intervals.append(interval)
        self.last_update = now
        
        if "b" in data and "a" in data:  # bookTicker
            await self._process_book_ticker(data, now)
        elif "bids" in data:  # depth
            await self._process_depth(data, now)
    
    async def _process_book_ticker(self, data: Dict[str, Any], now: float):
        """Process best bid/ask"""
        bid = float(data.get("b", 0))
        ask = float(data.get("a", 0))
        bid_qty = float(data.get("B", 0))
        ask_qty = float(data.get("A", 0))
        
        if bid > 0 and ask > 0:
            spread = ask - bid
            mid = (bid + ask) / 2
            spread_bps = (spread / mid * 10000) if mid > 0 else 0
            
            self.spread_samples.append(spread_bps)
            self.depth_samples.append(bid_qty + ask_qty)
        
        await self._assess_health()
    
    async def _process_depth(self, data: Dict[str, Any], now: float):
        """Process order book depth for quality metrics"""
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        
        if not bids or not asks:
            return
        
        # Calculate depth at various levels
        depth_1pct = self._calculate_depth_within_pct(bids, asks, 0.01)
        depth_5pct = self._calculate_depth_within_pct(bids, asks, 0.05)
        
        # Top of book quality
        best_bid = float(bids[0][0])
        best_ask = float(asks[0][0])
        spread = best_ask - best_bid
        mid = (best_bid + best_ask) / 2
        spread_bps = (spread / mid * 10000) if mid > 0 else 0
        
        # Order book imbalance
        bid_vol = sum(float(q) for _, q in bids[:10])
        ask_vol = sum(float(q) for _, q in asks[:10])
        imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol) if (bid_vol + ask_vol) > 0 else 0
        
        market_data = MarketData(
            timestamp=now,
            symbol=self.config.symbol,
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
    
    def _calculate_depth_within_pct(self, bids, asks, pct: float) -> float:
        """Calculate total volume within X% of mid price"""
        if not bids or not asks:
            return 0
        
        mid = (float(bids[0][0]) + float(asks[0][0])) / 2
        lower = mid * (1 - pct)
        upper = mid * (1 + pct)
        
        total = 0
        for price, qty in bids:
            p = float(price)
            if lower <= p <= mid:
                total += float(qty)
        for price, qty in asks:
            p = float(price)
            if mid <= p <= upper:
                total += float(qty)
        return total
    
    async def _assess_health(self):
        """Assess exchange infrastructure health"""
        if not self.spread_samples or not self.update_intervals:
            return
        
        # Spread health (tighter = better)
        avg_spread = statistics.mean(self.spread_samples)
        spread_score = max(0, 100 - avg_spread * 10)  # Penalize wide spreads
        
        # Latency health (consistent = better)
        avg_interval = statistics.mean(self.update_intervals)
        latency_score = max(0, 100 - avg_interval * 1000)  # Penalize slow updates
        
        # Staleness check
        stale = time.time() - self.last_update > self.staleness_threshold
        stale_penalty = 50 if stale else 0
        
        # Depth health
        if self.depth_samples:
            avg_depth = statistics.mean(self.depth_samples)
            depth_score = min(100, avg_depth / 10)  # Normalize
        else:
            depth_score = 0
        
        # Combined health score
        self.health_score = (spread_score + latency_score + depth_score) / 3 - stale_penalty
        self.health_score = max(0, min(100, self.health_score))


class NessieReality(LochnessBot):
    """Malkuth - Player Behavior & PnL Tracker
    
    Streams: userDataStream (requires API key) + aggTrade
    Outputs: Player analytics, PnL, positioning → Business dashboard
    
    Note: userDataStream requires authenticated API connection.
    This bot provides the framework; actual implementation needs API credentials.
    """
    
    def __init__(self, data_callback=None, api_key: str = "", api_secret: str = ""):
        config = BotConfig(
            name="Nessie-Reality",
            sephira="Malkuth",
            stream="aggTrade",  # Fallback to public trades
        )
        super().__init__(config, data_callback)
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.listen_key = None
        
        # Player tracking (aggregated from public data)
        self.large_traders = {}  # Track by trade patterns
        self.pnl_estimates = {}
        self.position_estimates = {}
        
    async def _process_message(self, data: Dict[str, Any]):
        """Process aggregate trades for player behavior inference"""
        if "p" not in data or "q" not in data:
            return
        
        await self._analyze_public_trade(data)
    
    async def _analyze_public_trade(self, data: Dict[str, Any]):
        """Analyze public trade for whale/player behavior"""
        price = float(data["p"])
        qty = float(data["q"])
        notional = price * qty
        side = "SELL" if data.get("m", False) else "BUY"  # m = isBuyerMaker
        trade_id = data.get("a")
        timestamp = data.get("T", time.time() * 1000)
        
        # Track large trades as potential whale/player activity
        if notional > 50000:  # $50k+ trades
            trader_id = f"trader_{trade_id % 10000}"  # Simplified
            
            if trader_id not in self.large_traders:
                self.large_traders[trader_id] = {
                    "trades": [],
                    "total_volume": 0,
                    "total_notional": 0,
                    "buy_volume": 0,
                    "sell_volume": 0,
                    "first_seen": timestamp,
                    "last_seen": timestamp,
                }
            
            trader = self.large_traders[trader_id]
            trader["trades"].append({
                "price": price,
                "qty": qty,
                "notional": notional,
                "side": side,
                "time": timestamp,
            })
            trader["total_volume"] += qty
            trader["total_notional"] += notional
            trader["last_seen"] = timestamp
            
            if side == "BUY":
                trader["buy_volume"] += qty
            else:
                trader["sell_volume"] += qty
            
            # Estimate PnL (simplified)
            if len(trader["trades"]) > 1:
                await self._estimate_pnl(trader_id, trader)
            
            # Emit player behavior data
            market_data = MarketData(
                timestamp=time.time(),
                symbol=self.config.symbol,
                data={
                    "type": "player_behavior",
                    "trader_id": trader_id,
                    "trade_notional": notional,
                    "side": side,
                    "trader_stats": {
                        "trade_count": len(trader["trades"]),
                        "total_notional": trader["total_notional"],
                        "buy_ratio": trader["buy_volume"] / trader["total_volume"] if trader["total_volume"] > 0 else 0,
                        "estimated_pnl": self.pnl_estimates.get(trader_id, 0),
                    },
                },
                source_bot=self.config.name
            )
            self._emit_data(market_data)
    
    async def _estimate_pnl(self, trader_id: str, trader: Dict[str, Any]):
        """Simple PnL estimation from trade history"""
        # This is a very simplified model
        # Real implementation would need position tracking
        trades = trader["trades"]
        if len(trades) < 2:
            return
        
        # Average entry price vs current price
        buy_trades = [t for t in trades if t["side"] == "BUY"]
        sell_trades = [t for t in trades if t["side"] == "SELL"]
        
        if buy_trades and sell_trades:
            avg_buy = sum(t["price"] * t["qty"] for t in buy_trades) / sum(t["qty"] for t in buy_trades)
            avg_sell = sum(t["price"] * t["qty"] for t in sell_trades) / sum(t["qty"] for t in sell_trades)
            current_price = trades[-1]["price"]
            
            # Unrealized PnL on remaining position
            buy_vol = sum(t["qty"] for t in buy_trades)
            sell_vol = sum(t["qty"] for t in sell_trades)
            position = buy_vol - sell_vol
            
            if position > 0:
                unrealized = (current_price - avg_buy) * position
            else:
                unrealized = (avg_sell - current_price) * abs(position)
            
            # Realized PnL
            matched_vol = min(buy_vol, sell_vol)
            realized = (avg_sell - avg_buy) * matched_vol
            
            self.pnl_estimates[trader_id] = realized + unrealized


# ============================================================================
# BOT ORCHESTRATOR
# ============================================================================

class LochnessOrchestrator:
    """Manages all 10 Lochness bots (7 existing + 3 new)"""
    
    def __init__(self, data_callback=None):
        self.data_callback = data_callback
        self.bots: List[LochnessBot] = []
        self.running = False
        
        # Initialize all 10 bots
        self._init_bots()
    
    def _init_bots(self):
        """Initialize all 10 Lochness bots"""
        # Existing 7
        self.bots.append(NessiePrime(self.data_callback))
        self.bots.append(NessieArbitrage(self.data_callback))
        self.bots.append(NessieLiquidation(self.data_callback))
        self.bots.append(NessieWhale(self.data_callback))
        self.bots.append(NessieFunding(self.data_callback))
        self.bots.append(NessieKline(self.data_callback))
        self.bots.append(NessieSentiment(self.data_callback))
        
        # NEW: Missing 3
        self.bots.append(NessieTechnical(self.data_callback))      # Hod
        self.bots.append(NessieInfrastructure(self.data_callback)) # Yesod
        self.bots.append(NessieReality(self.data_callback))        # Malkuth
    
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
# DATA INTEGRATION - ABYSSAL EXCHANGE CLOB
# ============================================================================

class AbyssalExchangeBridge:
    """Bridge Lochness market data to Abyssal Assets Exchange"""
    
    def __init__(self, abyssal_api_url: str = "http://localhost:8000"):
        self.api_url = abyssal_api_url
        self.latest_data = {}
        self.order_book = {"bids": [], "asks": []}
    
    async def on_market_data(self, data: MarketData):
        """Receive market data from Lochness bots"""
        key = f"{data.source_bot}:{data.symbol}"
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
                # Map bot data to Abyssal endpoints
                if data.data.get("type") == "market_depth":
                    await client.post(
                        f"{self.api_url}/api/market/depth",
                        json={
                            "symbol": data.symbol,
                            "bids": data.data.get("bids", []),
                            "asks": data.data.get("asks", []),
                            "timestamp": data.timestamp,
                        }
                    )
                elif data.data.get("type") == "book_ticker":
                    await client.post(
                        f"{self.api_url}/api/market/ticker",
                        json={
                            "symbol": data.symbol,
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
                            "symbol": data.symbol,
                            "notional": data.data.get("notional"),
                            "side": data.data.get("side"),
                            "timestamp": data.timestamp,
                        }
                    )
                elif data.data.get("type") == "funding_rate":
                    await client.post(
                        f"{self.api_url}/api/market/funding",
                        json={
                            "symbol": data.symbol,
                            "rate": data.data.get("funding_rate"),
                            "annualized": data.data.get("annualized_rate_pct"),
                            "timestamp": data.timestamp,
                        }
                    )
        except Exception as e:
            print(f"[AbyssalBridge] Forward error: {e}")
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get aggregated market summary for Abyssal UI"""
        summary = {}
        for key, data in self.latest_data.items():
            bot_name, symbol = key.split(":", 1)
            if symbol not in summary:
                summary[symbol] = {}
            summary[symbol][bot_name] = {
                "type": data.data.get("type"),
                "data": {k: v for k, v in data.data.items() if k not in ["bids", "asks"]},  # Skip large arrays
                "timestamp": data.timestamp,
            }
        return summary


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Run all 10 Lochness bots with Abyssal bridge"""
    print("=" * 60)
    print("LOCHNESS MONSTERS - 10 SEPHIROT BOTS")
    print("=" * 60)
    
    # Initialize bridge
    bridge = AbyssalExchangeBridge()
    
    # Initialize orchestrator
    orchestrator = LochnessOrchestrator(data_callback=bridge.on_market_data)
    
    # Print Sephirah coverage
    print("\nSephirah Coverage:")
    for sephira, bot_name in orchestrator.get_sephirah_coverage().items():
        print(f"  {sephira:>8} → {bot_name}")
    
    # Start all bots
    print("\nStarting all bots...")
    await orchestrator.start_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")