"""
Market Service Layer
====================
Shared business logic for market data queries.
Extracted from server/main.py for clean architecture and testability.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, asc
from collections import defaultdict
import json

from .models import (
    Hat, Volume24h, PriceHistory, MarketListing, Order, OrderSide, OrderStatus,
    OrderBookSnapshot, CircuitBreaker, Hat, User
)


# ============================================================
# CONSTANTS
# ============================================================

ORDER_BOOK_DEPTH = 20
ORDER_BOOK_REFRESH_INTERVAL = 2  # seconds
CIRCUIT_BREAKER_THRESHOLD = 0.15  # 15%
CIRCUIT_BREAKER_COOLDOWN = 300  # 5 minutes


# ============================================================
# BASE QUERIES
# ============================================================

def get_market_base_query(db: Session):
    """
    Shared base query for market data - single query with all joins.
    Eliminates N+1 queries by joining all required tables in one query.
    """
    day_ago = datetime.utcnow() - timedelta(hours=24)
    price_24h_ago = db.query(
        PriceHistory.hat_id,
        PriceHistory.price.label("price_24h_ago")
    ).filter(
        PriceHistory.timestamp <= day_ago
    ).distinct(PriceHistory.hat_id).subquery()
    
    return db.query(
        Hat.id,
        Hat.name,
        Hat.rarity,
        Hat.base_buy_price,
        Hat.base_sell_price,
        Hat.zone,
        func.coalesce(Volume24h.volume, 0).label("volume"),
        func.coalesce(Volume24h.last_trade_price, Hat.base_sell_price).label("last_price"),
        price_24h_ago.c.price_24h_ago,
        func.count(MarketListing.id).label("listings_count"),
    ).outerjoin(
        Volume24h, Volume24h.hat_id == Hat.id
    ).outerjoin(
        price_24h_ago, price_24h_ago.c.hat_id == Hat.id
    ).outerjoin(
        MarketListing,
        and_(
            MarketListing.hat_id == Hat.id,
            MarketListing.is_active == True,
            MarketListing.expires_at > datetime.utcnow()
        )
    ).group_by(
        Hat.id, Hat.name, Hat.rarity, Hat.base_buy_price, Hat.base_sell_price, Hat.zone,
        Volume24h.volume, Volume24h.last_trade_price,
        price_24h_ago.c.price_24h_ago
    )


def get_market_summary_base_query(db: Session):
    """
    Extended base query for market summary with bid/ask.
    Includes best bid/ask via subqueries.
    """
    from server.models import Order, OrderSide, OrderStatus  # Avoid circular import
    
    day_ago = datetime.utcnow() - timedelta(hours=24)
    price_24h_ago = db.query(
        PriceHistory.hat_id,
        PriceHistory.price.label("price_24h_ago")
    ).filter(
        PriceHistory.timestamp <= day_ago
    ).distinct(PriceHistory.hat_id).subquery()
    
    # Subqueries for best bid/ask per hat
    best_bid_subq = db.query(
        Order.hat_id,
        func.max(Order.price).label("best_bid")
    ).filter(
        Order.side == OrderSide.BUY,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).group_by(Order.hat_id).subquery()
    
    best_ask_subq = db.query(
        Order.hat_id,
        func.min(Order.price).label("best_ask")
    ).filter(
        Order.side == OrderSide.SELL,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).group_by(Order.hat_id).subquery()
    
    base = db.query(
        Hat.id,
        Hat.name,
        Hat.rarity,
        Hat.zone,
        Hat.base_buy_price,
        Hat.base_sell_price,
        func.coalesce(Volume24h.volume, 0).label("volume"),
        func.coalesce(Volume24h.last_trade_price, Hat.base_sell_price).label("last_price"),
        func.coalesce(price_24h_ago.c.price_24h_ago, None).label("price_24h_ago"),
        func.count(MarketListing.id).label("listings_count"),
        best_bid_subq.c.best_bid,
        best_ask_subq.c.best_ask,
    ).outerjoin(
        Volume24h, Volume24h.hat_id == Hat.id
    ).outerjoin(
        price_24h_ago, price_24h_ago.c.hat_id == Hat.id
    ).outerjoin(
        MarketListing,
        and_(
            MarketListing.hat_id == Hat.id,
            MarketListing.is_active == True,
            MarketListing.expires_at > datetime.utcnow()
        )
    ).outerjoin(
        db.query(
            PriceHistory.hat_id,
            PriceHistory.price.label("price_24h_ago")
        ).filter(
            PriceHistory.timestamp <= datetime.utcnow() - timedelta(hours=24)
        ).distinct(PriceHistory.hat_id).subquery(),
        PriceHistory.hat_id == Hat.id
    ).outerjoin(
        best_bid_subq, best_bid_subq.c.hat_id == Hat.id
    ).outerjoin(
        best_ask_subq, best_ask_subq.c.hat_id == Hat.id
    ).group_by(
        Hat.id, Hat.name, Hat.rarity, Hat.zone, Hat.base_buy_price, Hat.base_sell_price,
        Volume24h.volume, Volume24h.last_trade_price,
        best_bid_subq.c.best_bid, best_ask_subq.c.best_ask
    )
    
    return base


# ============================================================
# PUBLIC API FUNCTIONS
# ============================================================

def get_market_data(db: Session) -> List[dict]:
    """
    Get market summary with all data in a single query.
    Returns list of MarketItemSummary dicts.
    """
    results = get_market_base_query(db).all()
    
    result = []
    for row in results:
        last_price = row.last_price
        change = 0.0
        if row.price_24h_ago and row.price_24h_ago > 0:
            change = ((last_price - row.price_24h_ago) / row.price_24h_ago) * 100
        
        result.append({
            "id": row.id,
            "name": row.name,
            "rarity": row.rarity,
            "buy_price": row.base_buy_price,
            "sell_price": row.base_sell_price,
            "volume_24h": row.volume,
            "price_change_24h": round(change, 2),
            "listings_count": row.listings_count,
        })
    return result


def get_market_summary_data(db: Session) -> List[dict]:
    """
    Get full market summary with order book data, 24h volume, price changes.
    Single query with bid/ask subqueries - no N+1.
    """
    from server.models import Order, OrderSide, OrderStatus, PriceHistory
    
    day_ago = datetime.utcnow() - timedelta(hours=24)
    price_24h_ago = db.query(
        PriceHistory.hat_id,
        PriceHistory.price.label("price_24h_ago")
    ).filter(
        PriceHistory.timestamp <= day_ago
    ).distinct(PriceHistory.hat_id).subquery()
    
    # Subqueries for best bid/ask per hat
    best_bid_subq = db.query(
        Order.hat_id,
        func.max(Order.price).label("best_bid")
    ).filter(
        Order.side == OrderSide.BUY,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).group_by(Order.hat_id).subquery()
    
    best_ask_subq = db.query(
        Order.hat_id,
        func.min(Order.price).label("best_ask")
    ).filter(
        Order.side == OrderSide.SELL,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).group_by(Order.hat_id).subquery()
    
    # Single query with all joins including bid/ask
    results = db.query(
        Hat.id,
        Hat.name,
        Hat.rarity,
        Hat.zone,
        Hat.base_buy_price,
        Hat.base_sell_price,
        func.coalesce(Volume24h.volume, 0).label("volume"),
        func.coalesce(Volume24h.last_trade_price, Hat.base_sell_price).label("last_price"),
        func.coalesce(price_24h_ago.c.price_24h_ago, None).label("price_24h_ago"),
        func.count(MarketListing.id).label("listings_count"),
        best_bid_subq.c.best_bid,
        best_ask_subq.c.best_ask,
    ).outerjoin(
        Volume24h, Volume24h.hat_id == Hat.id
    ).outerjoin(
        price_24h_ago, price_24h_ago.c.hat_id == Hat.id
    ).outerjoin(
        MarketListing,
        and_(
            MarketListing.hat_id == Hat.id,
            MarketListing.is_active == True,
            MarketListing.expires_at > datetime.utcnow()
        )
    ).outerjoin(
        db.query(
            PriceHistory.hat_id,
            PriceHistory.price.label("price_24h_ago")
        ).filter(
            PriceHistory.timestamp <= datetime.utcnow() - timedelta(hours=24)
        ).distinct(PriceHistory.hat_id).subquery(),
        PriceHistory.hat_id == Hat.id
    ).outerjoin(
        best_bid_subq, best_bid_subq.c.hat_id == Hat.id
    ).outerjoin(
        best_ask_subq, best_ask_subq.c.hat_id == Hat.id
    ).group_by(
        Hat.id, Hat.name, Hat.rarity, Hat.zone, Hat.base_buy_price, Hat.base_sell_price,
        Volume24h.volume, Volume24h.last_trade_price,
        best_bid_subq.c.best_bid, best_ask_subq.c.best_ask
    ).all()
    
    result = []
    for row in results:
        last_price = row.last_price
        change = 0.0
        if row.price_24h_ago and row.price_24h_ago > 0:
            change = ((last_price - row.price_24h_ago) / row.price_24h_ago) * 100
        
        bid_price = row.best_bid
        ask_price = row.best_ask
        spread_pct = 0.0
        if bid_price and ask_price and bid_price > 0:
            spread_pct = ((ask_price - bid_price) / bid_price) * 100
        
        result.append({
            "id": row.id,
            "name": row.name,
            "rarity": row.rarity,
            "zone": row.zone,
            "current_price": last_price,
            "volume_24h": row.volume,
            "price_change_24h": round(change, 2),
            "best_bid": bid_price,
            "best_ask": ask_price,
            "spread_pct": round(spread_pct, 2),
        })
    return result


# ============================================================
# ORDER BOOK SNAPSHOT (Materialized View)
# ============================================================

ORDER_BOOK_DEPTH = 20
ORDER_BOOK_REFRESH_INTERVAL = 2  # seconds

def get_order_book_snapshot(db: Session, hat_id: str, depth: int = 20) -> dict:
    """
    Get order book snapshot - uses materialized view if available,
    falls back to live query.
    """
    from server.models import OrderBookSnapshot, Order, OrderSide, OrderStatus, Volume24h
    
    snapshot = db.query(OrderBookSnapshot).filter(OrderBookSnapshot.hat_id == hat_id).first()
    
    if snapshot and snapshot.bids and snapshot.asks:
        bids = json.loads(snapshot.bids)
        asks = json.loads(snapshot.asks)
        
        bids = bids[:depth]
        asks = asks[:depth]
        
        return {
            "hat_id": hat_id,
            "bids": bids,
            "asks": asks,
            "spread": snapshot.spread,
            "spread_pct": snapshot.spread_pct,
            "timestamp": snapshot.updated_at.isoformat() if snapshot.updated_at else datetime.utcnow().isoformat(),
            "source": "materialized_view",
        }
    
    # Fallback: live query
    from server.models import Order, OrderSide, OrderStatus
    from sqlalchemy import desc, asc
    
    buy_orders = db.query(Order).filter(
        Order.hat_id == hat_id,
        Order.side == OrderSide.BUY,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).order_by(Order.price.desc(), Order.created_at.asc()).limit(20).all()
    
    sell_orders = db.query(Order).filter(
        Order.hat_id == hat_id,
        Order.side == OrderSide.SELL,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).order_by(Order.price.asc(), Order.created_at.asc()).limit(20).all()
    
    bid_levels = defaultdict(lambda: {'quantity': 0, 'orders': 0})
    for o in buy_orders:
        remaining = o.quantity - o.filled_quantity
        bid_levels[o.price]['quantity'] += remaining
        bid_levels[o.price]['orders'] += 1
    
    ask_levels = defaultdict(lambda: {'quantity': 0, 'orders': 0})
    for o in sell_orders:
        remaining = o.quantity - o.filled_quantity
        ask_levels[o.price]['quantity'] += remaining
        ask_levels[o.price]['orders'] += 1
    
    bids = [{"price": p, "quantity": v['quantity'], "orders": v['orders']} for p, v in sorted(bid_levels.items(), key=lambda x: -x[0])]
    asks = [{"price": p, "quantity": v['quantity'], "orders": v['orders']} for p, v in sorted(ask_levels.items(), key=lambda x: x[0])]
    
    spread = 0
    spread_pct = 0.0
    if bids and asks:
        spread = asks[0]['price'] - bids[0]['price']
        spread_pct = (spread / bids[0]['price']) * 100 if bids[0]['price'] > 0 else 0
    
    return {
        "hat_id": hat_id,
        "bids": bids,
        "asks": asks,
        "spread": spread,
        "spread_pct": round(spread_pct, 2),
        "timestamp": datetime.utcnow().isoformat(),
        "source": "live_query",
    }


# ============================================================
# BACKGROUND JOBS
# ============================================================

def refresh_order_book_snapshots(db: Session) -> int:
    """
    Background job to refresh all order book snapshots.
    Returns number of snapshots updated.
    """
    from server.models import OrderBookSnapshot, Order, OrderSide, OrderStatus, Volume24h
    from sqlalchemy import desc, asc
    
    hats = db.query(Hat.id).all()
    if not hats:
        return 0
    
    now = datetime.utcnow()
    updated = 0
    
    for (hat_id,) in hats:
        # Get top bids
        buy_orders = db.query(Order).filter(
            Order.hat_id == hat_id,
            Order.side == OrderSide.BUY,
            Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
        ).order_by(Order.price.desc(), Order.created_at.asc()).limit(20).all()
        
        # Get top asks
        sell_orders = db.query(Order).filter(
            Order.hat_id == hat_id,
            Order.side == OrderSide.SELL,
            Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
        ).order_by(Order.price.asc(), Order.created_at.asc()).limit(20).all()
        
        # Aggregate by price level
        bid_levels = defaultdict(lambda: {'quantity': 0, 'orders': 0})
        for o in buy_orders:
            remaining = o.quantity - o.filled_quantity
            if remaining > 0:
                bid_levels[o.price]['quantity'] += remaining
                bid_levels[o.price]['orders'] += 1
        
        ask_levels = defaultdict(lambda: {'quantity': 0, 'orders': 0})
        for o in sell_orders:
            remaining = o.quantity - o.filled_quantity
            if remaining > 0:
                ask_levels[o.price]['quantity'] += remaining
                ask_levels[o.price]['orders'] += 1
        
        bids = [{"price": p, "quantity": v['quantity'], "orders": v['orders']} 
                for p, v in sorted(bid_levels.items(), key=lambda x: -x[0])]
        asks = [{"price": p, "quantity": v['quantity'], "orders": v['orders']} 
                for p, v in sorted(ask_levels.items(), key=lambda x: x[0])]
        
        spread = 0
        spread_pct = 0.0
        best_bid = bids[0]['price'] if bids else None
        best_ask = asks[0]['price'] if asks else None
        if best_bid and best_ask:
            spread = best_ask - best_bid
            spread_pct = (spread / best_bid) * 100 if best_bid > 0 else 0
        
        total_bid_volume = sum(b['quantity'] for b in bids)
        total_ask_volume = sum(a['quantity'] for a in asks)
        
        # Get last trade price
        vol = db.query(Volume24h).filter(Volume24h.hat_id == hat_id).first()
        last_trade_price = vol.last_trade_price if vol else None
        
        # Upsert snapshot
        snapshot = db.query(OrderBookSnapshot).filter(OrderBookSnapshot.hat_id == hat_id).first()
        if not snapshot:
            snapshot = OrderBookSnapshot(hat_id=hat_id)
            db.add(snapshot)
        
        snapshot.bids = json.dumps(bids)
        snapshot.asks = json.dumps(asks)
        snapshot.best_bid = best_bid
        snapshot.best_ask = best_ask
        snapshot.spread = spread
        snapshot.spread_pct = round(spread_pct, 2)
        snapshot.total_bid_volume = total_bid_volume
        snapshot.total_ask_volume = total_ask_volume
        snapshot.bid_levels = len(bids)
        snapshot.ask_levels = len(asks)
        snapshot.order_count = len(bids) + len(asks)
        snapshot.last_trade_price = last_trade_price
        snapshot.updated_at = datetime.utcnow()
        updated += 1
    
    db.commit()
    return updated


async def order_book_refresh_loop():
    """Continuous background loop for order book snapshot refresh."""
    import asyncio
    from server.database import SessionLocal
    
    while True:
        try:
            db = SessionLocal()
            try:
                await refresh_order_book_snapshots(db)
            finally:
                db.close()
        except Exception as e:
            print(f"[OrderBookSnapshot] Refresh error: {e}")
        
        await asyncio.sleep(2)  # ORDER_BOOK_REFRESH_INTERVAL


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_price_change_24h(db: Session, hat_id: str) -> float:
    """Calculate 24h price change for a specific hat."""
    from server.models import Volume24h, PriceHistory
    
    day_ago = datetime.utcnow() - timedelta(hours=24)
    vol = db.query(Volume24h).filter(Volume24h.hat_id == hat_id).first()
    last_price = vol.last_trade_price if vol and vol.last_trade_price else None
    
    if not last_price:
        return 0.0
    
    old_record = db.query(PriceHistory).filter(
        PriceHistory.hat_id == hat_id,
        PriceHistory.timestamp <= datetime.utcnow() - timedelta(hours=24)
    ).order_by(PriceHistory.timestamp.desc()).first()
    
    if old_record and old_record.price > 0:
        return ((last_price - old_record.price) / old_record.price) * 100
    return 0.0


def get_market_stats(db: Session) -> dict:
    """Get aggregate market statistics."""
    from sqlalchemy import func
    from server.models import Volume24h, MarketListing
    
    total_volume = db.query(func.coalesce(func.sum(Volume24h.volume), 0)).scalar() or 0
    total_listings = db.query(MarketListing).filter(MarketListing.is_active == True).count()
    
    return {
        "total_volume_24h": total_volume,
        "total_listings": total_listings,
        "top_gainers": [],
        "top_losers": [],
    }


def calculate_price_change(current: float, previous: float) -> float:
    """Calculate percentage price change."""
    if previous and previous > 0:
        return round(((current - previous) / previous) * 100, 2)
    return 0.0


def get_spread_pct(bid: Optional[int], ask: Optional[int]) -> float:
    """Calculate spread percentage from bid/ask."""
    if bid and ask and bid > 0:
        return round(((ask - bid) / bid) * 100, 2)
    return 0.0