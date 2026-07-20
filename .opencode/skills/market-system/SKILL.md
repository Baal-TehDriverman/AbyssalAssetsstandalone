---
name: market-system
description: Use when working on the Abyssal Exchange CLOB, orders, market listings, trading mechanics, fees (3%), vault system, or market maker bots. Server models in server/main.py, client CLOB UI at client/src/ (1539 lines).
---

# Market System — The Abyssal Exchange

## Order Types
- **Buy orders** — 3% fee (1% burn, 2% to Nessie's Treasury)
- **Sell orders** — Items held in escrow until filled
- **Market listings** — Fixed-price listings with duration (1-168 hours)

## Database Models
- `Order` — id, user_id, hat_id, side (buy/sell), price, quantity, filled_quantity, status, expires_at
- `MarketListing` — id, seller_id, hat_id, price, quantity, duration, is_active, sold_quantity
- `Trade` — id, buy_order_id, sell_order_id, hat_id, price, quantity, buyer_id, seller_id, fee_paid

## CLOB (Client, 1539 lines)
- Buy/sell order walls visualization
- Depth chart with cumulative volume
- Spread display
- Order entry form
- Trade history feed
- Real-time updates via WebSocket

## Known Issues
- Market matching engine is NOT implemented on server — orders sit OPEN forever
- Price history and 24h volume are placeholder (return 0)
- WebSocket market feed does not push trade events
- No circuit breakers or price limits implemented yet
- No market maker bot running
- Vault/discontinued system not wired

## Market Rules (from GDD)
- 3% fee on all buys: 1% burned, 2% to Nessie's Treasury
- Discontinued hats: can only be traded, not dredged
- Limited edition hats: serial numbered, max supply tracked
- World first kill: guaranteed Mythic if undiscovered
