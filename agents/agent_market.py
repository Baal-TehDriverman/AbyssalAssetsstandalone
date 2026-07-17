# Wave 2 — Netzach: Market / CLOB

from agents import SubAgent, AgentManifest, register_agent

manifest = AgentManifest(
    id="market",
    name="Abyssal Exchange",
    version="1.0.1",
    sephira="NETZACH",
    description="Market system — CLOB, order book, hat trading, market maker config, fee structure",
    wave=2,
)


class MarketAgent(SubAgent):
    def _register_routes(self):
        super()._register_routes()

        @self.router.get("/fees")
        async def fee_structure():
            return {
                "buy_fee_pct": 3.0,
                "sell_fee_pct": 3.0,
                "burn_split": 1.0,
                "treasury_split": 2.0,
                "market_maker_spread": 0.02,
            }

        @self.router.get("/order-types")
        async def order_types():
            return {
                "order_types": ["LIMIT", "MARKET"],
                "sides": ["BUY", "SELL"],
                "statuses": ["OPEN", "PARTIAL", "FILLED", "CANCELLED"],
            }


agent = MarketAgent(manifest)
register_agent(agent)
