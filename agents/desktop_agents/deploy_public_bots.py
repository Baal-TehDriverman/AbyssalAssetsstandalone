#!/usr/bin/env python3
"""
Deploy Lochness Coinbase bots - Public channels only (7 bots)
Keter, Chokmah, Binah, Chesed, Geburah, Tiferet, Netzach-public
"""

import asyncio
import os
import sys
import time
import httpx
sys.path.insert(0, '/home/tehlappy/Desktop/Lilith/Core_Systems/AI/abyssal-agents')

from lochness_bots_coinbase import (
    LochnessBot, BotConfig, MarketData, CoinbaseAuth,
    NessiePrime, NessieArbitrage, NessieLiquidation, NessieWhale,
    NessieFunding, NessieKline,
    AbyssalExchangeBridge,
    COINBASE_WS_URL, DEFAULT_PRODUCT
)


class NessieSentimentPublic(LochnessBot):
    """Netzach-public - Sentiment from public ticker (no auth required)"""

    def __init__(self, data_callback=None, auth=None):
        config = BotConfig(
            name="Nessie-Sentiment-Public",
            sephira="Netzach-public",
            channels=["ticker"],
        )
        super().__init__(config, data_callback, auth)
        self.trade_count = 0

    async def _process_message(self, data: dict):
        """Process ticker for sentiment proxy (bid/ask pressure)"""
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

                total_size = bid_size + ask_size
                if total_size > 0:
                    bid_dominance = bid_size / total_size
                    mid = (bid + ask) / 2
                    momentum = ((mid - price_24h) / price_24h * 100) if price_24h > 0 else 0

                    sentiment_score = (bid_dominance - 0.5) * 2 + (momentum / 10)

                    if sentiment_score > 0.3:
                        sentiment = "bullish"
                    elif sentiment_score < -0.3:
                        sentiment = "bearish"
                    else:
                        sentiment = "neutral"

                    self.trade_count += 1

                    market_data = MarketData(
                        timestamp=time.time(),
                        product_id=self.config.product_id,
                        data={
                            "type": "sentiment_public",
                            "bid": bid,
                            "ask": ask,
                            "bid_size": bid_size,
                            "ask_size": ask_size,
                            "bid_dominance": bid_dominance,
                            "momentum_24h_pct": momentum,
                            "sentiment_score": sentiment_score,
                            "sentiment": sentiment,
                        },
                        source_bot=self.config.name
                    )
                    self._emit_data(market_data)


class PublicLochnessOrchestrator:
    """Manages only the 7 public Lochness bots"""

    def __init__(self, data_callback=None):
        self.data_callback = data_callback
        self.auth = CoinbaseAuth()
        self.bots = []
        self.running = False
        self._init_public_bots()

    def _init_public_bots(self):
        """Initialize the 7 public bots"""
        self.bots.append(NessiePrime(self.data_callback, self.auth))
        self.bots.append(NessieArbitrage(self.data_callback, self.auth))
        self.bots.append(NessieLiquidation(self.data_callback, self.auth, large_trade_threshold=50000))
        self.bots.append(NessieWhale(self.data_callback, self.auth, whale_threshold_usd=100000))
        self.bots.append(NessieFunding(self.data_callback, self.auth))
        self.bots.append(NessieKline(self.data_callback, self.auth))
        self.bots.append(NessieSentimentPublic(self.data_callback, self.auth))

    async def start_all(self):
        """Start all public bots"""
        self.running = True
        print(f"Starting {len(self.bots)} public Lochness bots...")
        tasks = [bot.start() for bot in self.bots]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_all(self):
        """Stop all bots"""
        self.running = False
        tasks = [bot.stop() for bot in self.bots]
        await asyncio.gather(*tasks, return_exceptions=True)

    def get_all_stats(self):
        """Get stats for all bots"""
        return [bot.get_stats() for bot in self.bots]

    def get_sephirah_coverage(self):
        """Get Sephirah -> Bot mapping"""
        return {bot.config.sephira: bot.config.name for bot in self.bots}


async def verify_bridge(bridge: AbyssalExchangeBridge, duration: int = 10):
    """Verify Abyssal Exchange bridge forwarding"""
    print(f"\n{'='*60}")
    print(f"VERIFYING ABYSSAL EXCHANGE BRIDGE FOR {duration}s")
    print(f"{'='*60}")

    async with httpx.AsyncClient() as client:
        try:
            api_url = os.getenv("ABYSSAL_API_URL", "http://localhost:8000")
            resp = await client.get(f"{api_url}/health", timeout=5)
            print(f"✓ Abyssal Exchange health: {resp.json()}")
        except Exception as e:
            print(f"✗ Abyssal Exchange health check failed: {e}")
            return

    print("\nWaiting for data to flow through bridge...")
    await asyncio.sleep(duration)

    summary = bridge.get_market_summary()

    expected_types = {
        "market_depth": "Depth (Keter/Nessie-Prime)",
        "book_ticker": "Ticker (Chokmah/Nessie-Arbitrage, Geburah/Nessie-Funding)",
        "large_trade": "Large Trades (Binah/Nessie-Liquidation)",
        "whale_trade": "Whale Alerts (Chesed/Nessie-Whale)",
        "futures_basis": "Basis (Geburah/Nessie-Funding)",
        "kline": "Technical/Candles (Tiferet/Nessie-Kline)",
        "sentiment_public": "Sentiment (Netzach-public/Nessie-Sentiment-Public)",
    }

    print("\n--- Bridge Data Summary ---")
    if not summary:
        print("  No data received yet (may need more time for market activity)")
    else:
        for product, bots_data in summary.items():
            print(f"\nProduct: {product}")
            for bot_name, data in bots_data.items():
                data_type = data.get("type", "unknown")
                desc = expected_types.get(data_type, data_type)
                ts = data.get("timestamp", 0)
                age = time.time() - ts
                status = "✓ FRESH" if age < 5 else f"⚠ STALE ({age:.1f}s)"
                filtered_data = {k: v for k, v in data.get("data", {}).items() if k not in ["bids", "asks"]}
                print(f"  {bot_name}: {desc} - {status}")
                print(f"    Data: {filtered_data}")

    print("\n--- Testing Abyssal Exchange API (Hat Market) ---")
    endpoints = [
        ("/api/market/summary", "Market Summary"),
        ("/api/market/stats", "Market Stats"),
        ("/api/hats", "Hats List"),
    ]

    async with httpx.AsyncClient() as client:
        for endpoint, name in endpoints:
            try:
                resp = await client.get(f"{api_url}{endpoint}", timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"  ✓ {name} ({endpoint}): OK - {len(data) if isinstance(data, list) else 'dict'} items")
                else:
                    print(f"  ⚠ {name} ({endpoint}): HTTP {resp.status_code}")
            except Exception as e:
                print(f"  ✗ {name} ({endpoint}): {e}")


async def run_daemon(orchestrator: PublicLochnessOrchestrator, bridge: AbyssalExchangeBridge):
    """Run Lochness bots persistently, printing stats every 60s."""
    bot_task = asyncio.create_task(orchestrator.start_all())
    await asyncio.sleep(5)

    print("\n--- Bot Connection Status ---")
    for stat in orchestrator.get_all_stats():
        status = "✓ RUNNING" if stat["running"] else "✗ STOPPED"
        print(f"  {stat['sephira']:>12} ({stat['name']}): {status} | Msgs: {stat['messages_processed']} | Errors: {stat['errors']}")

    print("\nLochness daemon active — forwarding to Abyssal Exchange. Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(60)
            summary = bridge.get_market_summary()
            btc = summary.get("BTC-USD", {})
            arb = btc.get("Nessie-Arbitrage", {}).get("data", {})
            mid = arb.get("mid_price", 0)
            print(f"[Lochness] BTC=${mid:,.2f} | bots={len(orchestrator.bots)} | forwarding→{bridge.api_url}")
    except asyncio.CancelledError:
        pass
    finally:
        await orchestrator.stop_all()
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass


async def main():
    daemon = "--daemon" in sys.argv or os.getenv("LOCHNESS_DAEMON", "").lower() in ("1", "true", "yes")
    verify_only = "--verify" in sys.argv

    print("=" * 60)
    print("LOCHNESS MONSTERS - COINBASE PUBLIC CHANNELS ONLY")
    print("7 SEPHIROTH BOTS (no auth required)")
    print("=" * 60)

    bridge = AbyssalExchangeBridge(os.getenv("ABYSSAL_API_URL", "http://localhost:8000"))
    orchestrator = PublicLochnessOrchestrator(data_callback=bridge.on_market_data)

    print("\nSephirah Coverage (Public Channels Only):")
    for sephira, bot_name in orchestrator.get_sephirah_coverage().items():
        bot = next(b for b in orchestrator.bots if b.config.sephira == sephira)
        print(f"  {sephira:>12} -> {bot_name:>25} -> {bot.config.channels}")

    print("\n" + "=" * 60)
    print("Starting all public bots...")
    print("=" * 60 + "\n")

    if daemon:
        await run_daemon(orchestrator, bridge)
        return

    bot_task = asyncio.create_task(orchestrator.start_all())
    await asyncio.sleep(5)

    print("\n--- Bot Connection Status ---")
    for stat in orchestrator.get_all_stats():
        status = "✓ RUNNING" if stat["running"] else "✗ STOPPED"
        print(f"  {stat['sephira']:>12} ({stat['name']}): {status} | Msgs: {stat['messages_processed']} | Errors: {stat['errors']}")

    if verify_only or not daemon:
        await verify_bridge(bridge, duration=15)

    print("\n--- Final Bot Stats ---")
    for stat in orchestrator.get_all_stats():
        uptime = stat['uptime_seconds']
        print(f"  {stat['sephira']:>12}: {stat['messages_processed']} msgs, {stat['errors']} errors, {uptime:.1f}s uptime")

    if not verify_only:
        print("\nTip: use --daemon or LOCHNESS_DAEMON=1 for persistent forwarding.")
    print("\nShutting down...")
    await orchestrator.stop_all()
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass
    print("Done.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted, shutting down...")