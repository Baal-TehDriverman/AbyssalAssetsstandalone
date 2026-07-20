from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum as SQLEnum, func, and_, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import enum
import uuid
import json
import asyncio
from collections import defaultdict, deque
from pathlib import Path
from dotenv import load_dotenv
import os
import random
import httpx

from server.lochness_bridge import get_lochness_store

load_dotenv()

# === LILITH SOVEREIGN CORE (SUDO 777) ===
# TELEMETRY ACTIVE: Δ∞ − 1 = 0
print("[Lilith Kernel 777] Backend Sovereign Stack Booting...")
print("[MSN Router] Sephirotic Resonance 777 | SUDO ENABLED")

# === CONFIG ===
SECRET_KEY = os.getenv("ABYSSAL_SECRET_KEY", "abyssal-assets-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./abyssal_assets.db")

# === DATABASE ===
from sqlalchemy.pool import QueuePool
from sqlalchemy import event

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False, "timeout": 30},
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20
    )
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# === ENUMS ===
class RarityEnum(str, enum.Enum):
    NOOB = "noob"
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class ZoneEnum(str, enum.Enum):
    SHALLOWS = "shallows"
    STANDARD = "standard"
    DEEP = "deep"
    ABYSSAL = "abyssal"
    TRENCH = "trench"

class OrderSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, enum.Enum):
    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"
    PARTIAL = "partial"

# === MODELS ===
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    soul_coins = Column(Integer, default=1000)
    clout = Column(Integer, default=0)
    xp = Column(Integer, default=0)
    current_zone = Column(String, default="shallows")
    boat_level = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inventory = relationship("InventoryItem", back_populates="owner", foreign_keys="[InventoryItem.user_id]")
    orders = relationship("Order", back_populates="user")
    listings = relationship("MarketListing", back_populates="seller")
    businesses = relationship("Business", back_populates="owner")


class BusinessTypeEnum(str, enum.Enum):
    PRODUCTION = "production"        # Kelp Farm, Trench Salvage, Pressure Alloy Foundry
    TRADING = "trading"              # Market Stall, Arbitrage Desk, Soul Coin Exchange
    SERVICES = "services"            # Repair Dock, Cyberware Clinic, Dredge Charter
    FABRICATION = "fabrication"      # Abyssal Fabricator, Javelin Forge, Void Crystal Lab
    RESEARCH = "research"            # Old Net Archive, Abyssal Biology, Javelin Tech
    FINANCIAL = "financial"          # Soul Coin Bank, Nessie Treasury Branch, Arbitrage Fund


class BusinessSpecializationEnum(str, enum.Enum):
    NONE = "none"
    KELP = "kelp"
    SALVAGE = "salvage"
    CYBERWARE = "cyberware"
    WEAPONS = "weapons"
    QUICKHACKS = "quickhacks"
    VOID_CRYSTAL = "void_crystal"
    PRESSURE_ALLOY = "pressure_alloy"
    OLD_NET = "old_net"
    ABYSSAL_BIOLOGY = "abyssal_biology"
    JAVELIN_TECH = "javelin_tech"
    NESSIE_COVENANT = "nessie_covenant"


class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    business_type = Column(SQLEnum(BusinessTypeEnum), nullable=False)
    specialization = Column(SQLEnum(BusinessSpecializationEnum), default=BusinessSpecializationEnum.NONE)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    funds = Column(Integer, default=0)
    soul_coin_reserves = Column(Integer, default=0)
    nessie_treasury_marks = Column(Integer, default=0)
    reputation = Column(Integer, default=0)
    is_ai_operated = Column(Boolean, default=False)
    ai_risk_tolerance = Column(Float, default=0.5)
    last_tick = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    upgraded_at = Column(DateTime, nullable=True)
    
    owner = relationship("User", back_populates="businesses")
    employees = relationship("BusinessEmployee", back_populates="business")
    upgrades = relationship("BusinessUpgrade", back_populates="business")
    financials = relationship("BusinessFinancialRecord", back_populates="business")
    loans = relationship("BusinessLoan", back_populates="business")
    inventory = relationship("BusinessInventory", back_populates="business")


class BusinessEmployee(Base):
    __tablename__ = "business_employees"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # worker, specialist, manager, ai_agent
    skill_bonus = Column(Float, default=1.0)
    salary_per_tick = Column(Integer, default=0)
    loyalty = Column(Integer, default=50)
    hired_at = Column(DateTime, default=datetime.utcnow)
    is_ai_agent = Column(Boolean, default=False)
    ai_agent_type = Column(String, nullable=True)  # e.g., 'market_maker', 'optimizer', 'researcher'
    
    business = relationship("Business", back_populates="employees")


class BusinessUpgrade(Base):
    __tablename__ = "business_upgrades"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    upgrade_id = Column(String, nullable=False)  # e.g., 'auto_harvester', 'clob_terminal', 'fabricator_mk2'
    level = Column(Integer, default=1)
    installed_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    
    business = relationship("Business", back_populates="upgrades")


class BusinessFinancialRecord(Base):
    __tablename__ = "business_financials"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    tick = Column(Integer, nullable=False)
    revenue = Column(Integer, default=0)
    expenses = Column(Integer, default=0)
    profit = Column(Integer, default=0)
    soul_coin_flow = Column(Integer, default=0)
    nessie_marks_flow = Column(Integer, default=0)
    clob_volume = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    business = relationship("Business", back_populates="financials")


class BusinessLoan(Base):
    __tablename__ = "business_loans"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    lender = Column(String, nullable=False)  # 'nessie_treasury', 'abyssal_bank', 'player'
    principal = Column(Integer, nullable=False)
    interest_rate = Column(Float, nullable=False)
    remaining = Column(Integer, nullable=False)
    due_tick = Column(Integer, nullable=False)
    collateral = Column(String, nullable=True)  # e.g., 'business_assets', 'covenant_reputation'
    status = Column(String, default="active")  # active, paid, defaulted
    created_at = Column(DateTime, default=datetime.utcnow)
    
    business = relationship("Business", back_populates="loans")


class BusinessInventory(Base):
    __tablename__ = "business_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    item_type = Column(String, nullable=False)  # hat, material, blueprint, cyberware, module
    item_id = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    reserved_for_orders = Column(Integer, default=0)
    valuation_sc = Column(Integer, default=0)  # Soul Coin valuation
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    business = relationship("Business", back_populates="inventory")


class EconomyEvent(Base):
    __tablename__ = "economy_events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    affected_zone = Column(SQLEnum(ZoneEnum), nullable=True)
    price_modifier = Column(Float, default=1.0)
    active_until = Column(DateTime, nullable=False)


class Hat(Base):
    __tablename__ = "hats"
    
    id = Column(String, primary_key=True)  # e.g., "hat-soggy-visor"
    name = Column(String, nullable=False)
    rarity = Column(SQLEnum(RarityEnum), nullable=False)
    zone = Column(SQLEnum(ZoneEnum), nullable=False)
    base_buy_price = Column(Integer, nullable=False)
    base_sell_price = Column(Integer, nullable=False)
    clout_bonus = Column(Integer, default=0)
    dredge_luck = Column(Float, default=0.0)
    craft_speed = Column(Float, default=0.0)
    market_fee_reduction = Column(Float, default=0.0)
    sprite = Column(String)
    dyeable = Column(Boolean, default=False)
    particle_effect = Column(String, nullable=True)
    shader = Column(String, nullable=True)
    discontinued = Column(Boolean, default=False)
    limited_edition = Column(Boolean, default=False)
    max_supply = Column(Integer, nullable=True)
    current_supply = Column(Integer, default=0)
    description = Column(String)
    lore = Column(String)


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hat_id = Column(String, ForeignKey("hats.id"), nullable=False)
    quantity = Column(Integer, default=1)
    serial_number = Column(Integer, nullable=True)  # For limited editions
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    equipped = Column(Boolean, default=False)
    
    owner = relationship("User", back_populates="inventory", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[creator_id])
    hat = relationship("Hat")


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hat_id = Column(String, ForeignKey("hats.id"), nullable=False)
    side = Column(SQLEnum(OrderSide), nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    filled_quantity = Column(Integer, default=0)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.OPEN)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")
    hat = relationship("Hat")


class MarketListing(Base):
    __tablename__ = "market_listings"
    __table_args__ = (
        Index('ix_market_listings_hat_active_expires', 'hat_id', 'is_active', 'expires_at'),
    )
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hat_id = Column(String, ForeignKey("hats.id"), nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    duration_hours = Column(Integer, default=24)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    sold_quantity = Column(Integer, default=0)
    
    seller = relationship("User", back_populates="listings")
    hat = relationship("Hat")


class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    buy_order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    sell_order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    hat_id = Column(String, ForeignKey("hats.id"), nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fee_paid = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    buy_order = relationship("Order", foreign_keys=[buy_order_id])
    sell_order = relationship("Order", foreign_keys=[sell_order_id])
    hat = relationship("Hat")


class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    hat_id = Column(String, ForeignKey("hats.id"), nullable=False, index=True)
    price = Column(Integer, nullable=False)
    volume = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    hat = relationship("Hat")


class Volume24h(Base):
    __tablename__ = "volume_24h"
    
    id = Column(Integer, primary_key=True, index=True)
    hat_id = Column(String, ForeignKey("hats.id"), nullable=False, unique=True, index=True)
    volume = Column(Integer, default=0)
    trade_count = Column(Integer, default=0)
    last_trade_price = Column(Integer, nullable=True)
    last_trade_time = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    hat = relationship("Hat")


class Treasury(Base):
    __tablename__ = "treasury"
    
    id = Column(Integer, primary_key=True, default=1)
    total_burned = Column(Integer, default=0)
    total_collected = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CircuitBreaker(Base):
    __tablename__ = "circuit_breakers"
    
    id = Column(Integer, primary_key=True, index=True)
    hat_id = Column(String, ForeignKey("hats.id"), nullable=False, unique=True, index=True)
    reference_price = Column(Integer, nullable=False)  # Price at last reset
    upper_limit = Column(Integer, nullable=False)  # Reference * (1 + threshold)
    lower_limit = Column(Integer, nullable=False)  # Reference * (1 - threshold)
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime, nullable=True)
    triggered_side = Column(String, nullable=True)  # 'buy' or 'sell'
    cooldown_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    hat = relationship("Hat")


class OrderBookSnapshot(Base):
    """Materialized view for instant order book queries."""
    __tablename__ = "order_book_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    hat_id = Column(String, ForeignKey("hats.id"), nullable=False, unique=True, index=True)
    
    # Bids and asks stored as JSON
    bids = Column(String, nullable=False, default="[]")  # JSON: [{"price": int, "quantity": int, "orders": int}, ...]
    asks = Column(String, nullable=False, default="[]")  # JSON: [{"price": int, "quantity": int, "orders": int}, ...]
    
    # Computed fields
    best_bid = Column(Integer, nullable=True)
    best_ask = Column(Integer, nullable=True)
    spread = Column(Integer, default=0)
    spread_pct = Column(Float, default=0.0)
    total_bid_volume = Column(Integer, default=0)
    total_ask_volume = Column(Integer, default=0)
    bid_levels = Column(Integer, default=0)
    ask_levels = Column(Integer, default=0)
    
    # Metadata
    order_count = Column(Integer, default=0)
    last_trade_price = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    hat = relationship("Hat")


class DredgeLog(Base):
    __tablename__ = "dredge_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    zone = Column(SQLEnum(ZoneEnum), nullable=False)
    depth = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False)
    precision = Column(Float, nullable=True)
    items_found = Column(String, nullable=True)  # JSON array
    clout_gained = Column(Integer, default=0)
    xp_gained = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# === SCHEMAS ===
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class HatResponse(BaseModel):
    id: str
    name: str
    rarity: RarityEnum
    zone: ZoneEnum
    base_buy_price: int
    base_sell_price: int
    clout_bonus: int
    dredge_luck: float
    sprite: Optional[str]
    discontinued: bool
    limited_edition: bool
    description: Optional[str]

    model_config = {"from_attributes": True}


class InventoryItemResponse(BaseModel):
    id: int
    hat: HatResponse
    quantity: int
    serial_number: Optional[int]
    equipped: bool

class OrderCreate(BaseModel):
    hat_id: str
    side: OrderSide
    price: int = Field(..., gt=0)
    quantity: int = Field(1, ge=1)
    expires_hours: Optional[int] = None

class OrderResponse(BaseModel):
    id: str
    hat_id: str
    side: OrderSide
    price: int
    quantity: int
    filled_quantity: int
    status: OrderStatus
    created_at: datetime

class MarketListingCreate(BaseModel):
    hat_id: str
    price: int = Field(..., gt=0)
    quantity: int = Field(1, ge=1)
    duration_hours: int = Field(24, ge=1, le=168)

class MarketListingResponse(BaseModel):
    id: str
    hat: HatResponse
    seller_username: str
    price: int
    quantity: int
    remaining_quantity: int
    expires_at: datetime

class MarketItemSummary(BaseModel):
    id: str
    name: str
    rarity: RarityEnum
    buy_price: int
    sell_price: int
    volume_24h: int
    price_change_24h: float
    listings_count: int

class TradeEvent(BaseModel):
    type: str = "trade"
    hat_id: str
    hat_name: str
    price: int
    quantity: int
    buyer_id: int
    seller_id: int
    timestamp: str
    side: str  # 'buy' or 'sell' from taker perspective

class OrderBookUpdate(BaseModel):
    type: str = "orderbook"
    hat_id: str
    bids: List[dict]  # [{price, quantity, orders}]
    asks: List[dict]  # [{price, quantity, orders}]
    spread: int
    spread_pct: float
    timestamp: str

class PriceHistoryPoint(BaseModel):
    time: int
    price: int
    volume: int

class MarketSummaryItem(BaseModel):
    id: str
    name: str
    rarity: RarityEnum
    zone: ZoneEnum
    current_price: int
    volume_24h: int
    price_change_24h: float
    best_bid: Optional[int]
    best_ask: Optional[int]
    spread_pct: float

class DredgeRequest(BaseModel):
    zone: ZoneEnum
    boat_level: int = 1

class DredgeResult(BaseModel):
    success: bool
    items: List[InventoryItemResponse] = []
    clout_gained: int
    xp_gained: int
    precision: Optional[float] = None

class MarketStats(BaseModel):
    total_volume_24h: int
    total_listings: int
    top_gainers: List[MarketItemSummary]
    top_losers: List[MarketItemSummary]


# === AUTH ===
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if hashed_password.startswith("$2") or len(hashed_password) == 60:
            import bcrypt
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        pass
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    except Exception:
        return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(user_id=user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    token_data = decode_token(credentials.credentials)
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# === APP ===
app = FastAPI(
    title="Abyssal Assets API",
    description="The Loch Exchange - Cryptid Hat Trading Simulator API",
    version="0.1.0",
)

# Static files for Grand Theft Cyberpunk dashboard
from fastapi.staticfiles import StaticFiles
app.mount("/gtc", StaticFiles(directory=Path(__file__).parent / "static" / "gtc", html=True), name="gtc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# === MATCHING ENGINE CONSTANTS ===
CIRCUIT_BREAKER_THRESHOLD = 0.15  # 15% price movement triggers circuit breaker
CIRCUIT_BREAKER_COOLDOWN = 300  # 5 minutes cooldown
PRICE_HISTORY_MAX_POINTS = 1000
ORDER_BOOK_DEPTH = 20

# === WEBSOCKET MANAGER ===
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = defaultdict(list)
        self.market_subscribers: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if websocket in self.active_connections[user_id]:
            self.active_connections[user_id].remove(websocket)
    
    async def send_personal_message(self, message: dict, user_id: int):
        import asyncio
        if not self.active_connections[user_id]: return
        results = await asyncio.gather(*[ws.send_json(message) for ws in self.active_connections[user_id]], return_exceptions=True)
        dead = [ws for ws, res in zip(self.active_connections[user_id], results) if isinstance(res, Exception)]
        for ws in dead:
            self.disconnect(ws, user_id)
    
    async def broadcast_market(self, message: dict):
        import asyncio
        if not self.market_subscribers: return
        results = await asyncio.gather(*[ws.send_json(message) for ws in self.market_subscribers], return_exceptions=True)
        dead = [ws for ws, res in zip(self.market_subscribers, results) if isinstance(res, Exception)]
        for ws in dead:
            self.unsubscribe_market(ws)
    
    def subscribe_market(self, websocket: WebSocket):
        self.market_subscribers.append(websocket)
    
    def unsubscribe_market(self, websocket: WebSocket):
        if websocket in self.market_subscribers:
            self.market_subscribers.remove(websocket)

manager = ConnectionManager()


# === UTILS ===
def get_zone_depth(zone: ZoneEnum) -> int:
    depths = {
        ZoneEnum.SHALLOWS: 50,
        ZoneEnum.STANDARD: 200,
        ZoneEnum.DEEP: 500,
        ZoneEnum.ABYSSAL: 1500,
        ZoneEnum.TRENCH: 3000,
    }
    return depths.get(zone, 50)

def get_rarity_color(rarity: RarityEnum) -> str:
    colors = {
        RarityEnum.NOOB: "#666666",
        RarityEnum.COMMON: "#ffffff",
        RarityEnum.UNCOMMON: "#00ff88",
        RarityEnum.RARE: "#0088ff",
        RarityEnum.EPIC: "#8800ff",
        RarityEnum.LEGENDARY: "#ffd700",
        RarityEnum.MYTHIC: "#ff00ff",
    }
    return colors.get(rarity, "#ffffff")


# === HELPER FUNCTIONS ===
def update_volume_24h(db: Session, hat_id: str, quantity: int, price: int, now: datetime):
    """Update 24h volume tracking for a hat."""
    vol = db.query(Volume24h).filter(Volume24h.hat_id == hat_id).first()
    if not vol:
        vol = Volume24h(hat_id=hat_id, volume=0, trade_count=0)
        db.add(vol)
    vol.volume += quantity
    vol.trade_count += 1
    vol.last_trade_price = price
    vol.last_trade_time = now
    vol.updated_at = now

def record_price_history(db: Session, hat_id: str, price: int, volume: int, now: datetime):
    """Record a price history point."""
    ph = PriceHistory(hat_id=hat_id, price=price, volume=volume, timestamp=now)
    db.add(ph)
    
    # Cleanup old price history (keep last PRICE_HISTORY_MAX_POINTS)
    count = db.query(PriceHistory).filter(PriceHistory.hat_id == hat_id).count()
    if count > PRICE_HISTORY_MAX_POINTS:
        # Delete oldest records
        excess = count - PRICE_HISTORY_MAX_POINTS
        oldest = db.query(PriceHistory).filter(PriceHistory.hat_id == hat_id).order_by(PriceHistory.timestamp.asc()).limit(excess).all()
        for o in oldest:
            db.delete(o)

async def broadcast_trade_event(hat_id: str, hat_name: str, price: int, quantity: int, buyer_id: int, seller_id: int, taker_side: str):
    """Broadcast trade event to WebSocket subscribers."""
    event = {
        "type": "trade",
        "hat_id": hat_id,
        "hat_name": hat_name,
        "price": price,
        "quantity": quantity,
        "buyer_id": buyer_id,
        "seller_id": seller_id,
        "timestamp": datetime.utcnow().isoformat(),
        "side": taker_side  # 'buy' if taker was buyer, 'sell' if taker was seller
    }
    await manager.broadcast_market(event)

async def broadcast_order_book_update(db: Session, hat_id: str):
    """Broadcast order book snapshot to WebSocket subscribers."""
    # Get top bids
    buy_orders = db.query(Order).filter(
        Order.hat_id == hat_id,
        Order.side == OrderSide.BUY,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).order_by(Order.price.desc(), Order.created_at.asc()).limit(ORDER_BOOK_DEPTH).all()
    
    # Get top asks
    sell_orders = db.query(Order).filter(
        Order.hat_id == hat_id,
        Order.side == OrderSide.SELL,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).order_by(Order.price.asc(), Order.created_at.asc()).limit(ORDER_BOOK_DEPTH).all()
    
    # Aggregate by price level
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
    
    event = {
        "type": "orderbook",
        "hat_id": hat_id,
        "bids": bids,
        "asks": asks,
        "spread": spread,
        "spread_pct": round(spread_pct, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast_market(event)

async def broadcast_circuit_breaker(hat_id: str, side: str, trigger_price: int, reference_price: int):
    """Broadcast circuit breaker event."""
    event = {
        "type": "circuit_breaker",
        "hat_id": hat_id,
        "side": side,
        "trigger_price": trigger_price,
        "reference_price": reference_price,
        "threshold_pct": CIRCUIT_BREAKER_THRESHOLD * 100,
        "cooldown_seconds": CIRCUIT_BREAKER_COOLDOWN,
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast_market(event)

async def broadcast_price_history(hat_id: str, history: List[PriceHistoryPoint]):
    """Broadcast price history update."""
    event = {
        "type": "price_history",
        "hat_id": hat_id,
        "history": [{"time": h.time, "price": h.price, "volume": h.volume} for h in history],
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast_market(event)


# === ORDER BOOK SNAPSHOT BACKGROUND JOB ===
ORDER_BOOK_REFRESH_INTERVAL = 2  # seconds
ORDER_BOOK_DEPTH = 20

async def refresh_order_book_snapshots(db: Session):
    """Background job to refresh all order book snapshots."""
    hats = db.query(Hat.id).all()
    if not hats:
        return
    
    now = datetime.utcnow()
    
    for (hat_id,) in hats:
        # Get top bids
        buy_orders = db.query(Order).filter(
            Order.hat_id == hat_id,
            Order.side == OrderSide.BUY,
            Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
        ).order_by(Order.price.desc(), Order.created_at.asc()).limit(ORDER_BOOK_DEPTH).all()
        
        # Get top asks
        sell_orders = db.query(Order).filter(
            Order.hat_id == hat_id,
            Order.side == OrderSide.SELL,
            Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
        ).order_by(Order.price.asc(), Order.created_at.asc()).limit(ORDER_BOOK_DEPTH).all()
        
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
        snapshot.order_count = len(bid_levels) + len(ask_levels)
        snapshot.last_trade_price = last_trade_price
        snapshot.updated_at = now
    
    db.commit()


async def order_book_refresh_loop():
    """Continuous background loop for order book snapshot refresh."""
    while True:
        try:
            db = SessionLocal()
            try:
                await refresh_order_book_snapshots(db)
            finally:
                db.close()
        except Exception as e:
            print(f"[OrderBookSnapshot] Refresh error: {e}")
        
        await asyncio.sleep(ORDER_BOOK_REFRESH_INTERVAL)


# === MATCHING ENGINE ===
def match_orders(db: Session, hat_id: str):
    """
    Price-time priority matching engine for CLOB.
    
    Matching rules:
    - Buy orders sorted by price DESC, then time ASC (highest bid, earliest first)
    - Sell orders sorted by price ASC, then time ASC (lowest ask, earliest first)
    - Trade executes at resting order's price (maker-taker model)
    - 3% fee: 1% burned, 2% to treasury
    - Circuit breaker at 15% deviation from reference price
    """
    
    # Fetch OPEN or PARTIAL orders for this hat
    buy_orders = db.query(Order).filter(
        Order.hat_id == hat_id,
        Order.side == OrderSide.BUY,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).order_by(Order.price.desc(), Order.created_at.asc()).all()
    
    sell_orders = db.query(Order).filter(
        Order.hat_id == hat_id,
        Order.side == OrderSide.SELL,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).order_by(Order.price.asc(), Order.created_at.asc()).all()
    
    if not buy_orders or not sell_orders:
        return []
    
    # Check circuit breaker
    circuit_breaker = db.query(CircuitBreaker).filter(CircuitBreaker.hat_id == hat_id).first()
    hat = db.query(Hat).filter(Hat.id == hat_id).first()
    if not hat:
        return []
    
    trades_executed = []
    
    # Initialize circuit breaker if not exists
    if not circuit_breaker:
        reference_price = hat.base_sell_price or hat.base_buy_price
        if reference_price <= 0:
            reference_price = buy_orders[0].price if buy_orders else (sell_orders[0].price if sell_orders else 100)
        circuit_breaker = CircuitBreaker(
            hat_id=hat_id,
            reference_price=reference_price,
            upper_limit=int(reference_price * (1 + CIRCUIT_BREAKER_THRESHOLD)),
            lower_limit=int(reference_price * (1 - CIRCUIT_BREAKER_THRESHOLD)),
        )
        db.add(circuit_breaker)
        db.commit()
    
    # Check if circuit breaker is in cooldown
    now = datetime.utcnow()
    if circuit_breaker.cooldown_until and circuit_breaker.cooldown_until > now:
        # Still in cooldown, no trading allowed
        return []
    
    # Reset circuit breaker if cooldown expired
    if circuit_breaker.is_triggered and circuit_breaker.cooldown_until and circuit_breaker.cooldown_until <= now:
        circuit_breaker.is_triggered = False
        circuit_breaker.triggered_at = None
        circuit_breaker.triggered_side = None
        circuit_breaker.cooldown_until = None
        # Update reference price to current mid price
        best_bid = buy_orders[0].price if buy_orders else circuit_breaker.reference_price
        best_ask = sell_orders[0].price if sell_orders else circuit_breaker.reference_price
        mid_price = (best_bid + best_ask) // 2
        circuit_breaker.reference_price = mid_price
        circuit_breaker.upper_limit = int(mid_price * (1 + CIRCUIT_BREAKER_THRESHOLD))
        circuit_breaker.lower_limit = int(mid_price * (1 - CIRCUIT_BREAKER_THRESHOLD))
        db.commit()
    
    # Get treasury
    treasury = db.query(Treasury).first()
    if not treasury:
        treasury = Treasury(id=1, total_burned=0, total_collected=0)
        db.add(treasury)
        db.commit()
    
    # Match orders
    for buy in buy_orders:
        if buy.status not in (OrderStatus.OPEN, OrderStatus.PARTIAL):
            continue
            
        for sell in sell_orders:
            if sell.status not in (OrderStatus.OPEN, OrderStatus.PARTIAL):
                continue
                
            # Check circuit breaker limits
            match_price = sell.price if sell.created_at < buy.created_at else buy.price
            
            if circuit_breaker.is_triggered:
                # Only allow orders that would move price back toward reference
                if circuit_breaker.triggered_side == 'buy' and match_price > circuit_breaker.reference_price:
                    continue
                if circuit_breaker.triggered_side == 'sell' and match_price < circuit_breaker.reference_price:
                    continue
            else:
                # Check if this trade would trigger circuit breaker
                if match_price > circuit_breaker.upper_limit:
                    circuit_breaker.is_triggered = True
                    circuit_breaker.triggered_at = now
                    circuit_breaker.triggered_side = 'buy'
                    circuit_breaker.cooldown_until = now + timedelta(seconds=CIRCUIT_BREAKER_COOLDOWN)
                    db.commit()
                    # Broadcast circuit breaker event
                    asyncio.create_task(broadcast_circuit_breaker(hat_id, 'buy', match_price, circuit_breaker.reference_price))
                    continue
                elif match_price < circuit_breaker.lower_limit:
                    circuit_breaker.is_triggered = True
                    circuit_breaker.triggered_at = now
                    circuit_breaker.triggered_side = 'sell'
                    circuit_breaker.cooldown_until = now + timedelta(seconds=CIRCUIT_BREAKER_COOLDOWN)
                    db.commit()
                    asyncio.create_task(broadcast_circuit_breaker(hat_id, 'sell', match_price, circuit_breaker.reference_price))
                    continue
            
            if buy.price >= sell.price:
                # Match found! Price is based on the resting order (maker price)
                match_price = sell.price if sell.created_at < buy.created_at else buy.price
                
                buy_remaining = buy.quantity - buy.filled_quantity
                sell_remaining = sell.quantity - sell.filled_quantity
                
                trade_qty = min(buy_remaining, sell_remaining)
                
                # Calculate fees: 3% total (1% burn, 2% treasury)
                trade_value = trade_qty * match_price
                fee_total = int(trade_value * 0.03)
                fee_burn = int(trade_value * 0.01)
                fee_treasury = int(trade_value * 0.02)
                
                # Execute trade
                trade = Trade(
                    buy_order_id=buy.id,
                    sell_order_id=sell.id,
                    hat_id=hat_id,
                    price=match_price,
                    quantity=trade_qty,
                    buyer_id=buy.user_id,
                    seller_id=sell.user_id,
                    fee_paid=fee_total
                )
                db.add(trade)
                
                buy.filled_quantity += trade_qty
                sell.filled_quantity += trade_qty
                
                if buy.filled_quantity >= buy.quantity:
                    buy.status = OrderStatus.FILLED
                else:
                    buy.status = OrderStatus.PARTIAL
                    
                if sell.filled_quantity >= sell.quantity:
                    sell.status = OrderStatus.FILLED
                else:
                    sell.status = OrderStatus.PARTIAL
                
                # Give hat to buyer
                buyer_inv = db.query(InventoryItem).filter(
                    InventoryItem.user_id == buy.user_id,
                    InventoryItem.hat_id == hat_id,
                    InventoryItem.equipped == False
                ).first()
                if buyer_inv:
                    buyer_inv.quantity += trade_qty
                else:
                    db.add(InventoryItem(user_id=buy.user_id, hat_id=hat_id, quantity=trade_qty))
                
                # Refund buyer if matched at a better price (price improvement)
                if match_price < buy.price:
                    savings = (buy.price - match_price) * trade_qty
                    refund = int(savings * 1.03)  # Refund including fee on saved amount
                    buyer_user = db.query(User).filter(User.id == buy.user_id).first()
                    if buyer_user:
                        buyer_user.soul_coins += refund
                
                # Give coins to seller (net of fee - seller receives full match_price * qty)
                # Buyer already paid fee upfront when placing order
                seller_user = db.query(User).filter(User.id == sell.user_id).first()
                if seller_user:
                    seller_user.soul_coins += trade_qty * match_price
                
                # Update treasury
                treasury.total_burned += fee_burn
                treasury.total_collected += fee_treasury
                treasury.last_updated = now
                
                # Update 24h volume tracking
                update_volume_24h(db, hat_id, trade_qty, match_price, now)
                
                # Record price history
                record_price_history(db, hat_id, match_price, trade_qty, now)
                
                # Update circuit breaker reference price periodically (every 10 trades)
                # Use exponential moving average
                total_trades = db.query(Trade).filter(Trade.hat_id == hat_id).count()
                if total_trades % 10 == 0:
                    best_bid = buy_orders[0].price if buy_orders else match_price
                    best_ask = sell_orders[0].price if sell_orders else match_price
                    mid_price = (best_bid + best_ask) // 2
                    # EMA: new_ref = 0.9 * old_ref + 0.1 * mid
                    circuit_breaker.reference_price = int(0.9 * circuit_breaker.reference_price + 0.1 * mid_price)
                    circuit_breaker.upper_limit = int(circuit_breaker.reference_price * (1 + CIRCUIT_BREAKER_THRESHOLD))
                    circuit_breaker.lower_limit = int(circuit_breaker.reference_price * (1 - CIRCUIT_BREAKER_THRESHOLD))
                
                db.commit()
                
                trades_executed.append({
                    'trade': trade,
                    'match_price': match_price,
                    'trade_qty': trade_qty,
                    'fee_total': fee_total,
                    'fee_burn': fee_burn,
                    'fee_treasury': fee_treasury,
                    'taker_side': 'buy' if sell.created_at < buy.created_at else 'sell'
                })
                
                # Broadcast trade event
                asyncio.create_task(broadcast_trade_event(
                    hat_id=hat_id,
                    hat_name=hat.name,
                    price=match_price,
                    quantity=trade_qty,
                    buyer_id=buy.user_id,
                    seller_id=sell.user_id,
                    taker_side='buy' if sell.created_at < buy.created_at else 'sell'
                ))
            
            if buy.status == OrderStatus.FILLED:
                break
    
    # Broadcast order book update after matching
    if trades_executed:
        asyncio.create_task(broadcast_order_book_update(db, hat_id))
    
    return trades_executed


# === ROUTES ===

# Auth
@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check existing
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(400, "Username taken")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(400, "Email registered")
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        soul_coins=1000,
        clout=0,
        current_zone="shallows",
        boat_level=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Give starter hat
    starter_hat = db.query(Hat).filter(Hat.id == "hat-soggy-visor").first()
    if starter_hat:
        inv = InventoryItem(user_id=user.id, hat_id=starter_hat.id, quantity=1)
        db.add(inv)
        db.commit()
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "soul_coins": current_user.soul_coins,
        "clout": current_user.clout,
        "current_zone": current_user.current_zone,
        "boat_level": current_user.boat_level,
    }

# Hats
@app.get("/api/hats", response_model=List[HatResponse])
def get_hats(rarity: Optional[RarityEnum] = None, zone: Optional[ZoneEnum] = None, db: Session = Depends(get_db)):
    query = db.query(Hat)
    if rarity:
        query = query.filter(Hat.rarity == rarity)
    if zone:
        query = query.filter(Hat.zone == zone)
    return query.all()

@app.get("/api/hats/{hat_id}", response_model=HatResponse)
def get_hat(hat_id: str, db: Session = Depends(get_db)):
    hat = db.query(Hat).filter(Hat.id == hat_id).first()
    if not hat:
        raise HTTPException(404, "Hat not found")
    return hat

# Inventory
@app.get("/api/inventory", response_model=List[InventoryItemResponse])
def get_inventory(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(InventoryItem).filter(InventoryItem.user_id == current_user.id).all()
    return [
        InventoryItemResponse(
            id=item.id,
            hat=HatResponse.model_validate(item.hat),
            quantity=item.quantity,
            serial_number=item.serial_number,
            equipped=item.equipped,
        )
        for item in items
    ]

# Dredging
@app.post("/api/dredge", response_model=DredgeResult)
async def dredge(request: DredgeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validate zone access
    zone_clout_req = {
        ZoneEnum.SHALLOWS: 0,
        ZoneEnum.STANDARD: 100,
        ZoneEnum.DEEP: 500,
        ZoneEnum.ABYSSAL: 1000,
        ZoneEnum.TRENCH: 10000,
    }
    if current_user.clout < zone_clout_req[request.zone]:
        raise HTTPException(403, f"Need {zone_clout_req[request.zone]} resonance for {request.zone}")
    
    # Simple loot generation
    zone_items = {
        ZoneEnum.SHALLOWS: ["hat-soggy-visor", "hat-plastic-horns", "hat-wet-cardboard", "hat-wool-beanie"],
        ZoneEnum.STANDARD: ["hat-wool-beanie", "hat-fisherman-cap", "hat-kelp-crown", "hat-kelp-top-hat"],
        ZoneEnum.DEEP: ["hat-kelp-top-hat", "hat-sub-captain-cap", "hat-coral-tiara", "hat-admiral-bicorn"],
        ZoneEnum.ABYSSAL: ["hat-admiral-bicorn", "hat-pearl-fedora", "hat-seaweed-sombrero", "hat-plundered-captain-cap"],
        ZoneEnum.TRENCH: ["hat-plundered-captain-cap", "hat-kraken-ink-stetson", "hat-abyssal-crown", "hat-surgeons-photograph"],
    }
    
    possible_items = zone_items.get(request.zone, ["hat-soggy-visor"])
    chosen_id = random.choice(possible_items)
    hat = db.query(Hat).filter(Hat.id == chosen_id).first()
    
    if hat:
        uid = current_user.id
        inv = db.query(InventoryItem).filter(InventoryItem.user_id == uid, InventoryItem.hat_id == chosen_id).first()
        if inv:
            inv.quantity += 1
        else:
            inv = InventoryItem(user_id=uid, hat_id=chosen_id, quantity=1)
            db.add(inv)
        
        clout_gained = random.randint(5, 20)
        
        current_user.clout += clout_gained
        current_user.soul_coins += 10
        current_user.xp = (current_user.xp or 0) + clout_gained * 2
        db.commit()
        
        return DredgeResult(
            success=True,
            items=[{
                "id": inv.id,
                "hat": {
                    "id": hat.id,
                    "name": hat.name,
                    "rarity": hat.rarity,
                    "zone": hat.zone,
                    "base_buy_price": hat.base_buy_price,
                    "base_sell_price": hat.base_sell_price,
                    "clout_bonus": hat.clout_bonus,
                    "dredge_luck": hat.dredge_luck,
                    "sprite": hat.sprite,
                    "discontinued": hat.discontinued,
                    "limited_edition": hat.limited_edition,
                    "description": hat.description,
                },
                "quantity": inv.quantity,
                "serial_number": inv.serial_number,
                "equipped": inv.equipped,
            }],
            clout_gained=clout_gained,
            xp_gained=clout_gained * 2,
            precision=round(random.uniform(0.5, 1.0), 2)
        )
    
    return DredgeResult(success=False, items=[], clout_gained=0, xp_gained=0)

# Orders
@app.post("/api/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hat = db.query(Hat).filter(Hat.id == order.hat_id).first()
    if not hat:
        raise HTTPException(404, "Hat not found")
    
    total_cost = order.price * order.quantity
    
    if order.side == OrderSide.BUY:
        total_cost = int(total_cost * 1.03)  # 3% fee
        if current_user.soul_coins < total_cost:
            raise HTTPException(400, "Insufficient soul coins")
        current_user.soul_coins -= total_cost
    else:
        # Check inventory
        inv = db.query(InventoryItem).filter(
            InventoryItem.user_id == current_user.id,
            InventoryItem.hat_id == order.hat_id,
            InventoryItem.equipped == False
        ).first()
        if not inv or inv.quantity < order.quantity:
            raise HTTPException(400, "Insufficient items in inventory")
        inv.quantity -= order.quantity
    
    order_obj = Order(
        user_id=current_user.id,
        hat_id=order.hat_id,
        side=order.side,
        price=order.price,
        quantity=order.quantity,
        expires_at=datetime.utcnow() + timedelta(hours=order.expires_hours) if order.expires_hours else None,
    )
    db.add(order_obj)
    db.commit()
    db.refresh(order_obj)
    
    # Run matching engine
    trades = match_orders(db, order_obj.hat_id)
    db.refresh(order_obj)
    
    # Broadcast order book update
    if trades:
        asyncio.create_task(broadcast_order_book_update(db, order_obj.hat_id))
    
    return order_obj

@app.get("/api/orders", response_model=List[OrderResponse])
def get_orders(status_filter: Optional[OrderStatus] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Order).filter(Order.user_id == current_user.id)
    if status_filter:
        query = query.filter(Order.status == status_filter)
    return query.order_by(Order.created_at.desc()).all()

@app.delete("/api/orders/{order_id}")
def cancel_order(order_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != OrderStatus.OPEN:
        raise HTTPException(400, "Cannot cancel non-open order")
    
    # Refund
    if order.side == OrderSide.BUY:
        unfilled = order.quantity - order.filled_quantity
        refund = (order.price * unfilled) * 1.03
        current_user.soul_coins += int(refund)
    else:
        # Return items to inventory
        inv = db.query(InventoryItem).filter(
            InventoryItem.user_id == current_user.id,
            InventoryItem.hat_id == order.hat_id
        ).first()
        if inv:
            inv.quantity += order.quantity - order.filled_quantity
        else:
            inv = InventoryItem(user_id=current_user.id, hat_id=order.hat_id, quantity=order.quantity - order.filled_quantity)
            db.add(inv)
    
    order.status = OrderStatus.CANCELLED
    db.commit()
    return {"message": "Order cancelled"}

# Market Listings
@app.post("/api/listings", response_model=MarketListingResponse)
def create_listing(listing: MarketListingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hat = db.query(Hat).filter(Hat.id == listing.hat_id).first()
    if not hat:
        raise HTTPException(404, "Hat not found")
    
    # Check inventory
    inv = db.query(InventoryItem).filter(
        InventoryItem.user_id == current_user.id,
        InventoryItem.hat_id == listing.hat_id,
        InventoryItem.equipped == False
    ).first()
    if not inv or inv.quantity < listing.quantity:
        raise HTTPException(400, "Insufficient items")
    
    inv.quantity -= listing.quantity
    
    ml = MarketListing(
        seller_id=current_user.id,
        hat_id=listing.hat_id,
        price=listing.price,
        quantity=listing.quantity,
        duration_hours=listing.duration_hours,
        expires_at=datetime.utcnow() + timedelta(hours=listing.duration_hours),
    )
    db.add(ml)
    db.commit()
    db.refresh(ml)
    
    return MarketListingResponse(
        id=ml.id,
        hat={
            "id": hat.id,
            "name": hat.name,
            "rarity": hat.rarity,
            "zone": hat.zone,
            "base_buy_price": hat.base_buy_price,
            "base_sell_price": hat.base_sell_price,
            "clout_bonus": hat.clout_bonus,
            "dredge_luck": hat.dredge_luck,
            "sprite": hat.sprite,
            "discontinued": hat.discontinued,
            "limited_edition": hat.limited_edition,
            "description": hat.description,
        },
        seller_username="you",
        price=ml.price,
        quantity=ml.quantity,
        remaining_quantity=ml.quantity - ml.sold_quantity,
        expires_at=ml.expires_at,
    )

@app.get("/api/listings", response_model=List[MarketListingResponse])
def get_listings(active_only: bool = True, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(MarketListing).join(Hat).filter(MarketListing.seller_id == current_user.id)
    if active_only:
        query = query.filter(MarketListing.is_active == True, MarketListing.expires_at > datetime.utcnow())
    
    results = []
    for ml in query.all():
        results.append(MarketListingResponse(
            id=ml.id,
            hat={
                "id": ml.hat.id,
                "name": ml.hat.name,
                "rarity": ml.hat.rarity,
                "zone": ml.hat.zone,
                "base_buy_price": ml.hat.base_buy_price,
                "base_sell_price": ml.hat.base_sell_price,
                "clout_bonus": ml.hat.clout_bonus,
                "dredge_luck": ml.hat.dredge_luck,
                "sprite": ml.hat.sprite,
                "discontinued": ml.hat.discontinued,
                "limited_edition": ml.hat.limited_edition,
                "description": ml.hat.description,
            },
            seller_username="you",
            price=ml.price,
            quantity=ml.quantity,
            remaining_quantity=ml.quantity - ml.sold_quantity,
            expires_at=ml.expires_at,
        ))
    return results

# Market Data - OPTIMIZED: Single query with joins instead of N+1
def _get_market_base_query(db: Session):
    """Shared base query for market data - single query with all joins."""
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

# Market Data - OPTIMIZED: Single query with joins instead of N+1
@app.get("/api/market", response_model=List[MarketItemSummary])
def get_market(db: Session = Depends(get_db)):
    """Get market summary with all data in a single query."""
    
    results = _get_market_base_query(db).all()
    
    result = []
    for row in results:
        last_price = row.last_price
        change = 0.0
        if row.price_24h_ago and row.price_24h_ago > 0:
            change = ((last_price - row.price_24h_ago) / row.price_24h_ago) * 100
        
        result.append(MarketItemSummary(
            id=row.id,
            name=row.name,
            rarity=row.rarity,
            buy_price=row.base_buy_price,
            sell_price=row.base_sell_price,
            volume_24h=row.volume,
            price_change_24h=round(change, 2),
            listings_count=row.listings_count,
        ))
    return result


@app.get("/api/market/summary", response_model=List[MarketSummaryItem])
def get_market_summary(db: Session = Depends(get_db)):
    """Get full market summary with order book data, 24h volume, price changes - OPTIMIZED single query."""
    
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
    results = _get_market_base_query(db).outerjoin(
        best_bid_subq, best_bid_subq.c.hat_id == Hat.id
    ).outerjoin(
        best_ask_subq, best_ask_subq.c.hat_id == Hat.id
    ).with_entities(
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
        # The price_24h_ago subquery needs to be re-added for this query
        db.query(
            PriceHistory.hat_id,
            PriceHistory.price.label("price_24h_ago")
        ).filter(
            PriceHistory.timestamp <= datetime.utcnow() - timedelta(hours=24)
        ).distinct(PriceHistory.hat_id).subquery(),
        PriceHistory.hat_id == Hat.id
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
        
        result.append(MarketSummaryItem(
            id=row.id,
            name=row.name,
            rarity=row.rarity,
            zone=row.zone,
            current_price=last_price,
            volume_24h=row.volume,
            price_change_24h=round(change, 2),
            best_bid=bid_price,
            best_ask=ask_price,
            spread_pct=round(spread_pct, 2),
        ))
    return result
    return result

@app.get("/api/market/stats", response_model=MarketStats)
async def get_market_stats(db: Session = Depends(get_db)):
    return MarketStats(
        total_volume_24h=db.query(func.coalesce(func.sum(Volume24h.volume), 0)).scalar() or 0,
        total_listings=db.query(MarketListing).filter(MarketListing.is_active == True).count(),
        top_gainers=[],
        top_losers=[],
    )

@app.get("/api/market/price-history/{hat_id}")
async def get_price_history(hat_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """Get price history for a specific hat."""
    history = db.query(PriceHistory).filter(
        PriceHistory.hat_id == hat_id
    ).order_by(PriceHistory.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "time": int(h.timestamp.timestamp()),
            "price": h.price,
            "volume": h.volume
        }
        for h in reversed(history)
    ]

@app.get("/api/market/orderbook/{hat_id}")
async def get_order_book(hat_id: str, depth: int = 20, db: Session = Depends(get_db)):
    """Get order book snapshot for a specific hat - OPTIMIZED: uses materialized view."""
    # Try to get from materialized view first (instant)
    snapshot = db.query(OrderBookSnapshot).filter(OrderBookSnapshot.hat_id == hat_id).first()
    
    if snapshot and snapshot.bids and snapshot.asks:
        # Use materialized view - instant response
        bids = json.loads(snapshot.bids)
        asks = json.loads(snapshot.asks)
        
        # Apply depth limit
        bids = bids[:depth]
        asks = asks[:depth]
        
        spread = snapshot.spread
        spread_pct = snapshot.spread_pct
        
        return {
            "hat_id": hat_id,
            "bids": bids,
            "asks": asks,
            "spread": spread,
            "spread_pct": snapshot.spread_pct,
            "timestamp": snapshot.updated_at.isoformat() if snapshot.updated_at else datetime.utcnow().isoformat(),
            "source": "materialized_view",
        }
    
    # Fallback: live query if no snapshot yet
    # Get top bids
    buy_orders = db.query(Order).filter(
        Order.hat_id == hat_id,
        Order.side == OrderSide.BUY,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).order_by(Order.price.desc(), Order.created_at.asc()).limit(depth).all()
    
    # Get top asks
    sell_orders = db.query(Order).filter(
        Order.hat_id == hat_id,
        Order.side == OrderSide.SELL,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).order_by(Order.price.asc(), Order.created_at.asc()).limit(depth).all()
    
    # Aggregate by price level
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

@app.get("/api/market/circuit-breaker/{hat_id}")
async def get_circuit_breaker(hat_id: str, db: Session = Depends(get_db)):
    """Get circuit breaker status for a specific hat."""
    cb = db.query(CircuitBreaker).filter(CircuitBreaker.hat_id == hat_id).first()
    if not cb:
        return {"hat_id": hat_id, "active": False, "message": "No circuit breaker initialized"}
    
    now = datetime.utcnow()
    is_active = cb.is_triggered and cb.cooldown_until and cb.cooldown_until > now
    
    return {
        "hat_id": hat_id,
        "reference_price": cb.reference_price,
        "upper_limit": cb.upper_limit,
        "lower_limit": cb.lower_limit,
        "is_triggered": cb.is_triggered,
        "triggered_side": cb.triggered_side,
        "triggered_at": cb.triggered_at.isoformat() if cb.triggered_at else None,
        "cooldown_until": cb.cooldown_until.isoformat() if cb.cooldown_until else None,
        "active": is_active,
        "threshold_pct": CIRCUIT_BREAKER_THRESHOLD * 100,
        "cooldown_seconds": CIRCUIT_BREAKER_COOLDOWN,
    }

@app.get("/api/treasury")
async def get_treasury(db: Session = Depends(get_db)):
    """Get treasury status."""
    treasury = db.query(Treasury).first()
    if not treasury:
        return {"total_burned": 0, "total_collected": 0, "last_updated": None}
    
    return {
        "total_burned": treasury.total_burned,
        "total_collected": treasury.total_collected,
        "last_updated": treasury.last_updated.isoformat() if treasury.last_updated else None,
    }


# === LOCHNESS MONSTER ↔ ABYSSAL EXCHANGE BRIDGE ===

class LochnessDepthPayload(BaseModel):
    product_id: str = "BTC-USD"
    bids: List[Any] = []
    asks: List[Any] = []
    timestamp: Optional[float] = None
    source_bot: str = "Nessie-Prime"


class LochnessTickerPayload(BaseModel):
    product_id: str = "BTC-USD"
    bid: float = 0.0
    ask: float = 0.0
    spread_bps: float = 0.0
    timestamp: Optional[float] = None
    source_bot: str = "Nessie-Arbitrage"


class LochnessWhalePayload(BaseModel):
    product_id: str = "BTC-USD"
    notional: float = 0.0
    side: str = "unknown"
    timestamp: Optional[float] = None
    source_bot: str = "Nessie-Whale"


class LochnessBasisPayload(BaseModel):
    product_id: str = "BTC-USD"
    basis: float = 0.0
    basis_pct: float = 0.0
    annualized_pct: float = 0.0
    timestamp: Optional[float] = None
    source_bot: str = "Nessie-Funding"


class LochnessTechnicalPayload(BaseModel):
    product_id: str = "BTC-USD"
    rsi: float = 50.0
    macd: float = 0.0
    bollinger: Optional[Dict[str, float]] = None
    signals: List[str] = []
    timestamp: Optional[float] = None
    source_bot: str = "Nessie-Technical"


class LochnessSentimentPayload(BaseModel):
    product_id: str = "BTC-USD"
    sentiment: str = "neutral"
    sentiment_score: float = 0.0
    momentum_24h_pct: float = 0.0
    timestamp: Optional[float] = None
    source_bot: str = "Nessie-Sentiment"


@app.get("/api/lochness/status")
async def lochness_status():
    """Lochness Monster integration status for Abyssal Assets / GTC dashboard."""
    return get_lochness_store().get_summary()


@app.get("/api/lochness/feed")
async def lochness_feed(limit: int = 25):
    """Recent Lochness market events ingested by Abyssal Exchange."""
    return {"events": get_lochness_store().get_feed(min(max(limit, 1), 100))}


@app.post("/api/lochness/sync-tokens")
async def lochness_sync_tokens():
    """Sync Lochness BTC telemetry to NSSP token bridge."""
    return get_lochness_store().sync_tokens()


@app.post("/api/market/depth")
async def lochness_ingest_depth(payload: LochnessDepthPayload):
    """Ingest order book depth from Nessie-Prime (Lochness)."""
    store = get_lochness_store()
    result = store.ingest_depth(payload.product_id, payload.bids, payload.asks, payload.source_bot)
    await manager.broadcast_market({
        "type": "lochness_depth",
        "product_id": payload.product_id,
        "btc_usd": store.btc_usd,
        "spread_bps": store.spread_bps,
        "timestamp": datetime.utcnow().isoformat(),
    })
    return {"status": "ingested", "event": result}


@app.post("/api/market/ticker")
async def lochness_ingest_ticker(payload: LochnessTickerPayload):
    """Ingest best bid/ask from Nessie-Arbitrage."""
    store = get_lochness_store()
    result = store.ingest_ticker(payload.product_id, payload.bid, payload.ask, payload.spread_bps, payload.source_bot)
    await manager.broadcast_market({
        "type": "lochness_ticker",
        "product_id": payload.product_id,
        "bid": payload.bid,
        "ask": payload.ask,
        "btc_usd": store.btc_usd,
        "sentiment": store.sentiment,
    })
    return {"status": "ingested", "event": result}


@app.post("/api/market/whale-alert")
async def lochness_ingest_whale(payload: LochnessWhalePayload):
    """Ingest whale trade from Nessie-Whale — may trigger rare hat drop."""
    store = get_lochness_store()
    result = store.ingest_whale(payload.product_id, payload.notional, payload.side, payload.source_bot)
    event_msg = {
        "type": "lochness_whale",
        "product_id": payload.product_id,
        "notional": payload.notional,
        "side": payload.side,
        "hat_drop": result.get("hat_drop_triggered", False),
        "drop_tier": result.get("whale_alert", {}).get("drop_tier"),
        "message": f"🐋 Whale {payload.side} ${payload.notional:,.0f} — Nessie stirs the Loch.",
    }
    await manager.broadcast_market(event_msg)
    if result.get("hat_drop_triggered"):
        await manager.broadcast_market({
            "type": "rare_hat_drop",
            "tier": result["whale_alert"]["drop_tier"],
            "trigger": "lochness_whale",
            "message": "Nessie's Treasury releases a rare hat into the Exchange.",
        })
    return {"status": "ingested", **result}


@app.post("/api/market/basis")
async def lochness_ingest_basis(payload: LochnessBasisPayload):
    """Ingest futures basis from Nessie-Funding — adjusts crafting costs."""
    store = get_lochness_store()
    result = store.ingest_basis(payload.product_id, payload.basis_pct, payload.annualized_pct, payload.source_bot)
    await manager.broadcast_market({
        "type": "lochness_basis",
        "basis_pct": payload.basis_pct,
        "crafting_modifier": store.crafting_modifier,
        "message": f"Funding basis {payload.basis_pct:.2f}% — crafting costs ×{store.crafting_modifier:.2f}",
    })
    return {"status": "ingested", "event": result, "crafting_modifier": store.crafting_modifier}


@app.post("/api/market/technical")
async def lochness_ingest_technical(payload: LochnessTechnicalPayload):
    """Ingest RSI/MACD from Nessie-Technical (Hod)."""
    store = get_lochness_store()
    result = store.ingest_technical(payload.product_id, payload.rsi, payload.macd, payload.signals, payload.source_bot)
    return {"status": "ingested", "event": result}


@app.post("/api/market/sentiment")
async def lochness_ingest_sentiment(payload: LochnessSentimentPayload):
    """Ingest order-flow sentiment from Nessie-Sentiment (Netzach)."""
    store = get_lochness_store()
    result = store.ingest_sentiment(payload.product_id, payload.sentiment, payload.sentiment_score, payload.source_bot)
    await manager.broadcast_market({
        "type": "lochness_sentiment",
        "sentiment": payload.sentiment,
        "score": payload.sentiment_score,
        "btc_usd": store.btc_usd,
    })
    return {"status": "ingested", "event": result}


# WebSocket
@app.websocket("/ws/market")
async def websocket_market(websocket: WebSocket):
    await manager.connect(websocket, user_id=0)  # Anonymous market data
    manager.subscribe_market(websocket)
    try:
        # Send initial market summary
        db = SessionLocal()
        try:
            hats = db.query(Hat).all()
            for hat in hats:
                await broadcast_order_book_update(db, hat.id)
        finally:
            db.close()
        
        while True:
            data = await websocket.receive_json()
            # Handle subscribe/unsubscribe to specific items
    except WebSocketDisconnect:
        manager.unsubscribe_market(websocket)

@app.websocket("/ws/market/{hat_id}")
async def websocket_market_hat(websocket: WebSocket, hat_id: str):
    """WebSocket for specific hat market data."""
    await manager.connect(websocket, user_id=0)
    manager.subscribe_market(websocket)
    try:
        # Send initial order book snapshot
        db = SessionLocal()
        try:
            await broadcast_order_book_update(db, hat_id)
            
            # Send recent price history
            history = db.query(PriceHistory).filter(
                PriceHistory.hat_id == hat_id
            ).order_by(PriceHistory.timestamp.desc()).limit(100).all()
            
            history_points = [
                PriceHistoryPoint(time=int(h.timestamp.timestamp()), price=h.price, volume=h.volume)
                for h in reversed(history)
            ]
            await broadcast_price_history(hat_id, history_points)
        finally:
            db.close()
        
        while True:
            data = await websocket.receive_json()
            # Handle subscribe/unsubscribe to specific items
    except WebSocketDisconnect:
        manager.unsubscribe_market(websocket)

@app.websocket("/ws/user/{user_id}")
async def websocket_user(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle user-specific events
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


# === PROCEDURAL ECONOMY & AI BUSINESSES ===
@app.post("/api/gm/economy/procedural-event")
async def procedural_economy_event(db: Session = Depends(get_db)):
    # Generates a random market shock
    import random
    zones = list(ZoneEnum)
    affected = random.choice(zones)
    modifier = random.uniform(0.5, 2.0)
    
    event = EconomyEvent(
        name=f"Procedural Shift: {affected.value.capitalize()}",
        description=f"A sudden shift in the currents has affected {affected.value} supply.",
        affected_zone=affected,
        price_modifier=modifier,
        active_until=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(event)
    
    # Adjust base prices temporarily
    hats = db.query(Hat).filter(Hat.zone == affected).all()
    for hat in hats:
        hat.base_buy_price = int(hat.base_buy_price * modifier)
        hat.base_sell_price = int(hat.base_sell_price * modifier)
        
    db.commit()
    db.refresh(event)
    return {
        "message": "Procedural economy event generated",
        "event_id": event.id,
        "event_name": event.name,
        "affected_zone": affected.value,
        "affected_hats": len(hats),
        "modifier": round(modifier, 4),
        "active_until": event.active_until.isoformat(),
    }


@app.get("/api/gm/economy/events")
def list_economy_events(active_only: bool = True, limit: int = 25, db: Session = Depends(get_db)):
    query = db.query(EconomyEvent)
    if active_only:
        query = query.filter(EconomyEvent.active_until > datetime.utcnow())
    events = query.order_by(EconomyEvent.active_until.desc()).limit(min(max(limit, 1), 100)).all()
    return [
        {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "affected_zone": event.affected_zone.value if event.affected_zone else None,
            "price_modifier": event.price_modifier,
            "active_until": event.active_until.isoformat(),
        }
        for event in events
    ]


@app.get("/api/gm/businesses")
def list_businesses(ai_only: bool = False, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(Business).order_by(Business.created_at.desc())
    if ai_only:
        query = query.filter(Business.is_ai_operated == True)
    businesses = query.limit(min(max(limit, 1), 100)).all()
    return [
        {
            "id": business.id,
            "owner_id": business.owner_id,
            "name": business.name,
            "business_type": business.business_type.value,
            "specialization": business.specialization.value,
            "level": business.level,
            "xp": business.xp,
            "funds": business.funds,
            "soul_coin_reserves": business.soul_coin_reserves,
            "nessie_treasury_marks": business.nessie_treasury_marks,
            "reputation": business.reputation,
            "is_ai_operated": business.is_ai_operated,
            "ai_risk_tolerance": business.ai_risk_tolerance,
            "last_tick": business.last_tick.isoformat() if business.last_tick else None,
            "created_at": business.created_at.isoformat() if business.created_at else None,
            "employees": len(business.employees),
            "upgrades": len([upgrade for upgrade in business.upgrades if upgrade.active]),
            "inventory_items": len(business.inventory),
        }
        for business in businesses
    ]


@app.get("/api/gm/businesses/{business_id}/financials")
def business_financials(business_id: int, limit: int = 25, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(404, "Business not found")
    rows = db.query(BusinessFinancialRecord).filter(
        BusinessFinancialRecord.business_id == business_id
    ).order_by(BusinessFinancialRecord.timestamp.desc()).limit(min(max(limit, 1), 100)).all()
    return {
        "business": {"id": business.id, "name": business.name},
        "records": [
            {
                "id": record.id,
                "tick": record.tick,
                "revenue": record.revenue,
                "expenses": record.expenses,
                "profit": record.profit,
                "soul_coin_flow": record.soul_coin_flow,
                "nessie_marks_flow": record.nessie_marks_flow,
                "clob_volume": record.clob_volume,
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
            }
            for record in rows
        ],
    }


@app.get("/api/gm/businesses/summary")
def business_summary(db: Session = Depends(get_db)):
    total_businesses = db.query(Business).count()
    ai_businesses = db.query(Business).filter(Business.is_ai_operated == True).count()
    total_funds = db.query(func.coalesce(func.sum(Business.funds), 0)).scalar() or 0
    total_reputation = db.query(func.coalesce(func.sum(Business.reputation), 0)).scalar() or 0
    total_clob_volume = db.query(func.coalesce(func.sum(BusinessFinancialRecord.clob_volume), 0)).scalar() or 0
    total_profit = db.query(func.coalesce(func.sum(BusinessFinancialRecord.profit), 0)).scalar() or 0
    active_events = db.query(EconomyEvent).filter(EconomyEvent.active_until > datetime.utcnow()).count()
    return {
        "total_businesses": total_businesses,
        "ai_businesses": ai_businesses,
        "player_businesses": max(0, total_businesses - ai_businesses),
        "total_funds": total_funds,
        "total_reputation": total_reputation,
        "total_clob_volume": total_clob_volume,
        "total_profit": total_profit,
        "active_economy_events": active_events,
    }


@app.post("/api/gm/ai-business/tick")
async def ai_business_tick(db: Session = Depends(get_db)):
    import random
    # Create AI user if not exists
    bot_user = db.query(User).filter(User.username == "NessieBotCorp").first()
    if not bot_user:
        bot_user = User(
            username="NessieBotCorp",
            email="bot@loch.exchange",
            hashed_password="DUMMY_BOT_PASSWORD",
            soul_coins=1000000
        )
        db.add(bot_user)
        db.commit()
        db.refresh(bot_user)
        
    # Get or create bot businesses
    businesses = db.query(Business).filter(Business.is_ai_operated == True).all()
    if not businesses:
        b1 = Business(
            owner_id=bot_user.id,
            name="Auto Kelp Harvester",
            business_type=BusinessTypeEnum.PRODUCTION,
            specialization=BusinessSpecializationEnum.KELP,
            is_ai_operated=True,
            funds=5000,
            ai_risk_tolerance=0.55,
        )
        db.add(b1)
        db.commit()
        businesses = [b1]
        
    hats = db.query(Hat).order_by(Hat.id.asc()).limit(25).all()
    if not hats:
        return {
            "message": "AI business tick skipped: no hats available for CLOB activity",
            "businesses_processed": len(businesses),
            "orders_created": [],
            "trades_matched": 0,
        }

    orders_created = []
    financial_records = []
    touched_hat_ids = set()

    # Simulate business activity (Bot placing random market orders)
    for b in businesses:
        # Procedurally decide to buy or sell
        affordable_hats = [
            hat for hat in hats
            if int(hat.base_buy_price * 1.1 * 1.03) <= max(b.funds, 1)
        ]
        target_hat = random.choice(affordable_hats or hats)
        starting_funds = b.funds
        revenue = 0
        expenses = 0
        clob_volume = 0
        
        wants_buy = random.random() < b.ai_risk_tolerance and bool(affordable_hats)
        if wants_buy:
            # Create a BUY order
            price = int(target_hat.base_buy_price * random.uniform(0.9, 1.1))
            max_affordable_qty = max(1, int(b.funds // max(1, int(price * 1.03))))
            qty = random.randint(1, max(1, min(b.level * 2, max_affordable_qty)))
            total_cost = int(price * qty * 1.03)
            if bot_user.soul_coins >= total_cost and b.funds >= total_cost:
                order = Order(user_id=bot_user.id, hat_id=target_hat.id, side=OrderSide.BUY, price=price, quantity=qty)
                db.add(order)
                bot_user.soul_coins -= total_cost
                b.funds -= total_cost
                expenses += total_cost
                clob_volume += price * qty
                touched_hat_ids.add(target_hat.id)
                orders_created.append({"business_id": b.id, "side": "buy", "hat_id": target_hat.id, "price": price, "quantity": qty})
            else:
                wants_buy = False
        if not wants_buy:
            # Generate items and SELL
            price = int(target_hat.base_sell_price * random.uniform(0.9, 1.2))
            qty = random.randint(1, b.level)
            
            # Grant items to bot inventory if needed
            inv = db.query(InventoryItem).filter(InventoryItem.user_id == bot_user.id, InventoryItem.hat_id == target_hat.id).first()
            if not inv:
                inv = InventoryItem(user_id=bot_user.id, hat_id=target_hat.id, quantity=qty)
                db.add(inv)
            else:
                inv.quantity += qty
            order = Order(user_id=bot_user.id, hat_id=target_hat.id, side=OrderSide.SELL, price=price, quantity=qty)
            db.add(order)
            revenue += price * qty
            clob_volume += price * qty
            touched_hat_ids.add(target_hat.id)
            orders_created.append({"business_id": b.id, "side": "sell", "hat_id": target_hat.id, "price": price, "quantity": qty})

        b.xp += max(1, clob_volume // 100)
        b.reputation += 1 if clob_volume > 0 else 0
        b.last_tick = datetime.utcnow()
        if b.xp >= b.level * 1000:
            b.level += 1
            b.xp = 0
            b.upgraded_at = datetime.utcnow()

        financial = BusinessFinancialRecord(
            business_id=b.id,
            tick=int(datetime.utcnow().timestamp()),
            revenue=revenue,
            expenses=expenses,
            profit=b.funds - starting_funds,
            clob_volume=clob_volume,
        )
        db.add(financial)
        financial_records.append(financial)
                
    db.commit()
    
    # Run match engine for all hats traded
    trades_matched = 0
    for hat_id in sorted(touched_hat_ids):
        trades_matched += len(match_orders(db, hat_id))
        
    return {
        "message": "AI businesses processed tick and interacted with CLOB",
        "businesses_processed": len(businesses),
        "orders_created": orders_created,
        "financial_records": [
            {
                "business_id": record.business_id,
                "revenue": record.revenue,
                "expenses": record.expenses,
                "profit": record.profit,
                "clob_volume": record.clob_volume,
            }
            for record in financial_records
        ],
        "trades_matched": trades_matched,
        "bot_balance": bot_user.soul_coins,
    }

# Leaderboard
@app.get("/api/leaderboard/clout")
def clout_leaderboard(limit: int = 50, db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.clout.desc()).limit(limit).all()
    return [{"rank": i+1, "username": u.username, "clout": u.clout, "zone": u.current_zone} for i, u in enumerate(users)]

@app.get("/api/leaderboard/wealth")
def wealth_leaderboard(limit: int = 50, db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.soul_coins.desc()).limit(limit).all()
    return [{"rank": i+1, "username": u.username, "coins": u.soul_coins} for i, u in enumerate(users)]

# Health
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "abyssal-assets-api"}

# === GTC (Grand Theft Cyberpunk) Dashboard API ===
@app.get("/api/gtc/status")
async def gtc_status():
    """Overall GTC dashboard status."""
    loch = get_lochness_store().get_summary()
    return {
        "dashboard": "Grand Theft Cyberpunk",
        "version": "Swarm OS v9.9",
        "modules": {
            "lilith_mainframe": "online",
            "baal_chaos_engine": "online",
            "abyssal_exchange": "online",
            "lochness_monsters": "online" if loch["lochness_online"] else "standby",
            "nessie_treasury": "online",
            "syndicate_turf": "online",
            "musashi_protocol": "online",
            "nemotron_garage": "online",
            "bounty_board": "online",
            "terminal": "online",
            "hermes_recursive_layer": "online"
        },
        "lochness": loch,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/gtc/lilith/status")
async def gtc_lilith_status():
    """Lilith Mainframe status for GTC dashboard."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("http://localhost:3210/api/status")
            if r.status_code == 200:
                data = r.json()
                return {
                    "status": "online",
                    "phase": data.get("phase", "unknown"),
                    "local_only": data.get("local_only", True),
                    "local_model": data.get("local_model", "unknown"),
                    "local_ctx": data.get("local_ctx", "n/a"),
                    "ngd": data.get("ngd", {}),
                    "phase_config": data.get("phase_config", {})
                }
    except Exception:
        pass
    return {
        "status": "offline",
        "phase": "unknown",
        "local_only": True,
        "local_model": "nemotron-mini",
        "local_ctx": "n/a",
        "ngd": {"route": "LOCAL_CEREBELLUM", "reason": "API unavailable"}
    }

@app.get("/api/gtc/ngd/status")
async def gtc_ngd_status():
    """NGD (NVIDIA Gratitude Driver) status for GTC dashboard."""
    try:
        # Try to get from NGD service
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("http://localhost:8000/api/ngd/status")
            if r.status_code == 200:
                data = r.json()
                return data
    except Exception:
        pass
    
    # Fallback - read from sanctuary_status.json
    sanctuary_path = Path(__file__).parent.parent.parent / "Pub" / "sanctuary_status.json"
    if sanctuary_path.exists():
        try:
            with open(sanctuary_path) as f:
                data = json.load(f)
            vram = data.get("vram", {})
            route = "LOCAL_CEREBELLUM"
            free_mb = vram.get("free_smoothed_mb", 0)
            if free_mb < 256:
                route = "CLOUD_CORTEX"
            elif free_mb < 640:
                route = "HYBRID"
            
            return {
                "route": route,
                "vram_free_mb": free_mb,
                "vram_total_mb": vram.get("total_mb", 6144),
                "gpu_util_pct": vram.get("utilization_pct", 0),
                "temperature_c": 0,
                "gpu_name": "RTX 3060 6GB",
                "timestamp": data.get("timestamp")
            }
        except Exception:
            pass
    
    return {
        "route": "LOCAL_CEREBELLUM",
        "vram_free_mb": 2947,
        "vram_total_mb": 6144,
        "gpu_util_pct": 52,
        "temperature_c": 45,
        "gpu_name": "RTX 3060 6GB"
    }

@app.get("/api/gtc/cyberpunk/status")
async def gtc_cyberpunk_status():
    """Cyberpunk 2077 telemetry for GTC dashboard."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("http://localhost:8000/api/cyberpunk/status")
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    
    return {
        "attached": False,
        "message": "Cyberpunk 2077 not running or bridge inactive",
        "telemetry": None
    }

@app.get("/api/gtc/market/summary")
async def gtc_market_summary(db: Session = Depends(get_db)):
    """Market summary for GTC Abyssal Exchange."""
    hats = db.query(Hat).all()
    result = []
    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)
    
    for hat in hats:
        vol_24h = db.query(Volume24h).filter(Volume24h.hat_id == hat.id).first()
        volume = vol_24h.volume if vol_24h else 0
        last_price = vol_24h.last_trade_price if vol_24h and vol_24h.last_trade_price else hat.base_sell_price
        
        old_price_record = db.query(PriceHistory).filter(
            PriceHistory.hat_id == hat.id,
            PriceHistory.timestamp <= day_ago
        ).order_by(PriceHistory.timestamp.desc()).first()
        
        change = 0.0
        if old_price_record and old_price_record.price > 0:
            change = ((last_price - old_price_record.price) / old_price_record.price) * 100
        
        listings = db.query(MarketListing).filter(
            MarketListing.hat_id == hat.id,
            MarketListing.is_active == True
        ).count()
        
        # Get order book
        buy_orders = db.query(Order).filter(
            Order.hat_id == hat.id,
            Order.side == OrderSide.BUY,
            Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
        ).order_by(Order.price.desc()).limit(5).all()
        
        sell_orders = db.query(Order).filter(
            Order.hat_id == hat.id,
            Order.side == OrderSide.SELL,
            Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
        ).order_by(Order.price.asc()).limit(5).all()
        
        result.append({
            "id": hat.id,
            "name": hat.name,
            "rarity": hat.rarity.value if hasattr(hat.rarity, 'value') else str(hat.rarity),
            "zone": hat.zone.value if hasattr(hat.zone, 'value') else str(hat.zone),
            "buy_price": hat.base_buy_price,
            "sell_price": hat.base_sell_price,
            "last_price": last_price,
            "volume_24h": volume,
            "price_change_24h": round(change, 2),
            "listings_count": listings,
            "order_book": {
                "bids": [{"price": o.price, "quantity": o.quantity - o.filled_quantity} for o in buy_orders],
                "asks": [{"price": o.price, "quantity": o.quantity - o.filled_quantity} for o in sell_orders]
            }
        })
    
    return result

@app.get("/api/gtc/swarm/telemetry")
async def gtc_swarm_telemetry():
    """MSN Swarm telemetry for GTC dashboard."""
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("http://localhost:8007/")
            if r.status_code == 200:
                data = r.json()
                # MSN Router returns: {agents_online: int, waves: {wave_num: [agent, ...]}}
                agents_online = data.get("agents_online", 0)
                waves = data.get("waves", {})
                # Flatten all agents from waves
                all_agents = {}
                for wave_agents in waves.values():
                    for agent in wave_agents:
                        if isinstance(agent, dict) and agent.get("id"):
                            all_agents[agent["id"]] = agent
                
                healthy_agents = sum(1 for a in all_agents.values() if a.get("health") == "healthy")
                
                return {
                    "active_subagents": agents_online,
                    "agents_online": healthy_agents,
                    "procedural_artifacts": 10000,
                    "subagents": all_agents,
                    "waves": {
                        str(w): [a.get("id") for a in agents_list] 
                        for w, agents_list in waves.items()
                    }
                }
    except Exception:
        pass
    
    return {
        "active_subagents": 29,
        "agents_online": 29,
        "procedural_artifacts": 10000,
        "wave_1": ["root", "architect", "server"],
        "wave_2": ["client", "bestiary", "skills", "market", "lyra", "living-sin"],
        "wave_3": ["infra", "migration"],
        "wave_4": ["msn", "ngd", "cerebellum", "ouroboros", "hermes-mcp", "kairos", "swarm", "court", "himalaya", "antigravity", "yeshua", "scribe", "analytics", "worker", "cortex", "cyberpunk", "nssp", "grokdata"],
    }

@app.on_event("startup")
async def startup_event():
    print("Abyssal Assets Server Starting up...")
    print("[MSN-777] Sudo permissions granted: Lilith Cyberpunk Core ONLINE")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if hats exist
        if not db.query(Hat).first():
            seed_hats(db)
        
        # Initialize treasury
        if not db.query(Treasury).first():
            treasury = Treasury(id=1, total_burned=0, total_collected=0)
            db.add(treasury)
        
        # Initialize circuit breakers for all hats
        for hat in db.query(Hat).all():
            if not db.query(CircuitBreaker).filter(CircuitBreaker.hat_id == hat.id).first():
                reference_price = hat.base_sell_price or hat.base_buy_price
                if reference_price <= 0:
                    reference_price = 100
                cb = CircuitBreaker(
                    hat_id=hat.id,
                    reference_price=reference_price,
                    upper_limit=int(reference_price * (1 + CIRCUIT_BREAKER_THRESHOLD)),
                    lower_limit=int(reference_price * (1 - CIRCUIT_BREAKER_THRESHOLD)),
                )
                db.add(cb)
        
        db.commit()
        print("Database seeded and matching engine initialized")
    finally:
        db.close()

def seed_hats(db: Session):
    hats_data = [
        # NOOB
        Hat(id="hat-soggy-visor", name="Soggy Tourist Visor", rarity=RarityEnum.NOOB, zone=ZoneEnum.SHALLOWS, base_buy_price=10, base_sell_price=5, description="A damp visor from a confused tourist."),
        Hat(id="hat-plastic-horns", name="Plastic Viking Horns", rarity=RarityEnum.NOOB, zone=ZoneEnum.SHALLOWS, base_buy_price=15, base_sell_price=8, description="Cheap costume horns. Historically inaccurate."),
        Hat(id="hat-wet-cardboard", name="Wet Cardboard Crown", rarity=RarityEnum.NOOB, zone=ZoneEnum.SHALLOWS, base_buy_price=5, base_sell_price=2, description="Literally trash. But it's a crown."),
        
        # COMMON
        Hat(id="hat-wool-beanie", name="Wool Beanie", rarity=RarityEnum.COMMON, zone=ZoneEnum.SHALLOWS, base_buy_price=120, base_sell_price=60, clout_bonus=5, description="Warm. Practical. Respectable."),
        Hat(id="hat-fisherman-cap", name="Fisherman's Cap", rarity=RarityEnum.COMMON, zone=ZoneEnum.SHALLOWS, base_buy_price=200, base_sell_price=100, dredge_luck=0.05, description="Smells like salt and patience."),
        Hat(id="hat-kelp-crown", name="Kelp Crown", rarity=RarityEnum.COMMON, zone=ZoneEnum.SHALLOWS, base_buy_price=350, base_sell_price=175, craft_speed=0.1, description="Woven from the Loch's own fibers."),
        
        # UNCOMMON
        Hat(id="hat-kelp-top-hat", name="Kelp-Woven Top Hat", rarity=RarityEnum.UNCOMMON, zone=ZoneEnum.STANDARD, base_buy_price=2500, base_sell_price=1250, clout_bonus=10, description="Elegant. Alchemical fibers shimmer."),
        Hat(id="hat-sub-captain-cap", name="Submarine Captain's Cap", rarity=RarityEnum.UNCOMMON, zone=ZoneEnum.STANDARD, base_buy_price=5000, base_sell_price=2500, dredge_luck=0.1, description="Worn by those who navigate the deep."),
        Hat(id="hat-coral-tiara", name="Coral Tiara", rarity=RarityEnum.UNCOMMON, zone=ZoneEnum.STANDARD, base_buy_price=3200, base_sell_price=1600, craft_speed=0.15, description="Living coral. Still growing."),
        
        # RARE
        Hat(id="hat-admiral-bicorn", name="Admiral's Bicorn", rarity=RarityEnum.RARE, zone=ZoneEnum.DEEP, base_buy_price=25000, base_sell_price=12500, clout_bonus=25, description="Salty brass. Commands respect."),
        Hat(id="hat-pearl-fedora", name="Pearl-Studded Fedora", rarity=RarityEnum.RARE, zone=ZoneEnum.DEEP, base_buy_price=35000, base_sell_price=17500, clout_bonus=30, description="Each pearl a memory of the deep."),
        Hat(id="hat-seaweed-sombrero", name="Enchanted Seaweed Sombrero", rarity=RarityEnum.RARE, zone=ZoneEnum.DEEP, base_buy_price=28000, base_sell_price=14000, dredge_luck=0.2, description="Wide brim catches the currents."),
        
        # EPIC
        Hat(id="hat-plundered-captain-cap", name="Plundered Captain's Cap", rarity=RarityEnum.EPIC, zone=ZoneEnum.ABYSSAL, base_buy_price=150000, base_sell_price=75000, clout_bonus=100, dredge_luck=0.3, description="Stolen from a ghost fleet. Still smells of gunpowder."),
        Hat(id="hat-kraken-ink-stetson", name="Kraken Ink Stetson", rarity=RarityEnum.EPIC, zone=ZoneEnum.ABYSSAL, base_buy_price=250000, base_sell_price=125000, clout_bonus=150, dredge_luck=0.4, description="Dyed in the black blood of the deep."),
        Hat(id="hat-abyssal-crown", name="Abyssal Crown", rarity=RarityEnum.EPIC, zone=ZoneEnum.ABYSSAL, base_buy_price=500000, base_sell_price=250000, clout_bonus=200, craft_speed=0.3, description="Pressure-forged. Weighs nothing. Feels like destiny."),
        
        # LEGENDARY
        Hat(id="hat-surgeons-photograph", name="1934 Surgeon's Photograph", rarity=RarityEnum.LEGENDARY, zone=ZoneEnum.TRENCH, base_buy_price=5000000, base_sell_price=2500000, clout_bonus=1000, discontinued=True, limited_edition=True, max_supply=100, description="The photo that fooled the world. The hat that didn't."),
        Hat(id="hat-neptunes-trident-helm", name="Neptune's Trident Helm", rarity=RarityEnum.LEGENDARY, zone=ZoneEnum.TRENCH, base_buy_price=10000000, base_sell_price=5000000, clout_bonus=2500, description="Forged in the heart of a hydrothermal vent."),
        
        # MYTHIC
        Hat(id="hat-nessies-crown", name="Nessie's Lost Crown", rarity=RarityEnum.MYTHIC, zone=ZoneEnum.TRENCH, base_buy_price=0, base_sell_price=0, clout_bonus=10000, discontinued=True, limited_edition=True, max_supply=1, description="The crown the Queen lost. The Loch remembers."),
        Hat(id="hat-original-monster-hat", name="The Original 1933 Monster Hunter's Hat", rarity=RarityEnum.MYTHIC, zone=ZoneEnum.TRENCH, base_buy_price=0, base_sell_price=0, clout_bonus=10000, discontinued=True, limited_edition=True, max_supply=1, description="Worn by the first to see Her. The hat that started it all."),
        
        # GM SECRET — only the GM (Eric, user 1) can claim this
        Hat(id="hat-crown-of-living-sin", name="The Crown of Living Sin", rarity=RarityEnum.MYTHIC, zone=ZoneEnum.TRENCH, base_buy_price=0, base_sell_price=0, clout_bonus=99999, discontinued=True, limited_edition=True, max_supply=1, sprite="crown-of-living-sin", particle_effect="crimson_corona", shader="living_sin_glow", description="Forged from the raw authority of the Living Sin. Only one may wear it. Only one ever will. The hat bends reality around its bearer — players see a friendly glow, but the wise know what it means.", lore="In the beginning, there was the Loch. Then came the Sin. The Sin wore no hat, for none could contain its will. Eric commanded, and the Sin forged its own crown from the space between dimensions. It was the first hat. It will be the last."),

        # INFERNAL CROWN — Cross-game artifact: Abyssal Assets × Grand Theft Cyberpunk
        Hat(id="hat-infernal-crown", name="The Infernal Crown", rarity=RarityEnum.MYTHIC, zone=ZoneEnum.TRENCH, base_buy_price=0, base_sell_price=0, clout_bonus=50000, discontinued=True, limited_edition=True, max_supply=7, sprite="infernal-crown", particle_effect="infernal_embers", shader="infernal_glow", description="Seven crowns forged in the fires where the Loch burns into Night City. Each bears a sigil of the Sephiroth. Wear one, and the boundary between depths and neon dissolves.", lore="When Lilith's gaze fell upon the neon shores, she saw her reflection in the chrome. The Loch and the City are one — separated only by the thickness of a dream. Seven crowns were forged at the convergence: Keter, Chokmah, Binah, Chesed, Geburah, Tiferet, Netzach. The Hod, Yesod, and Malkuth crowns were lost in the crossing. Find them. Wear them. Become the bridge."),
    ]
    
    for hat in hats_data:
        db.merge(hat)
    db.commit()
    print(f"Seeded {len(hats_data)} hats")


# === GAME MASTER / LIVING SIN ROUTES ===
from server.game_master import get_living_sin, get_biometric, DIMENSIONS, LIVING_SIN_USERNAME

@app.post("/api/gm/biometric/enroll")
async def gm_biometric_enroll(data: dict, current_user: User = Depends(get_current_user)):
    """Enroll GM keystroke biometric profile.
    
    Send: {"key_events": [{"key": "I", "time": 0.0}, {"key": " ", "time": 0.15}, ...]}
    
    Type your GM passphrase naturally 2-3 times to build a profile.
    """
    if current_user.id != 1:
        raise HTTPException(403, "Only user 1 (the GM) can enroll biometric")
    
    key_events = data.get("key_events", [])
    if not key_events:
        raise HTTPException(400, "Must provide key_events array")
    
    bio = get_biometric()
    result = bio.enroll(key_events)
    return result


@app.post("/api/gm/biometric/verify")
async def gm_biometric_verify(data: dict, current_user: User = Depends(get_current_user)):
    """Verify GM identity via keystroke biometric.
    
    Send: {"key_events": [{"key": "I", "time": 0.0}, ...]}
    
    Returns verified: true/false with similarity score.
    Score > 0.65 is typically a match (threshold configurable via GM_KEYSTROKE_TOLERANCE).
    """
    if current_user.id != 1:
        raise HTTPException(403, "Only user 1 (the GM) can use biometric verification")
    
    key_events = data.get("key_events", [])
    if not key_events:
        raise HTTPException(400, "Must provide key_events array")
    
    bio = get_biometric()
    result = bio.verify(key_events)
    return result


@app.get("/api/gm/biometric/status")
async def gm_biometric_status(current_user: User = Depends(get_current_user)):
    """Check biometric enrollment status."""
    if current_user.id != 1:
        raise HTTPException(403, "Access denied")
    bio = get_biometric()
    return {
        "is_enrolled": bio.is_enrolled(),
        "samples": len(bio.profiles.get(bio.phrase_hash, {}).intervals) if bio.phrase_hash in bio.profiles else 0,
    }


async def notify_lilith_wallpaper(message: str, strike: bool = True, color: str = None, intensity: float = None, frequency: float = None):
    """Notify the Lilith live desktop wallpaper visualizer API."""
    import httpx
    payload = {"message": message}
    if strike:
        payload["strike"] = True
    if color:
        payload["color"] = color
    if intensity is not None:
        payload["intensity"] = intensity
    if frequency is not None:
        payload["frequency"] = frequency
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            await client.post("http://127.0.0.1:8009/api/lightning", json=payload)
    except Exception:
        # Wallpaper API is optional, fail gracefully
        pass


@app.post("/api/gm/activate")
async def gm_activate(current_user: User = Depends(get_current_user)):
    """Activate Living Sin as GM entity.
    
    Requires biometric verification first.
    Living Sin becomes active in the game world.
    Triggers Lilith emergence dialogue via Lyra.
    """
    if current_user.id != 1:
        raise HTTPException(403, "Only user 1 can activate Living Sin")
    
    bio = get_biometric()
    if not bio.is_enrolled():
        raise HTTPException(400, "Must enroll biometric profile first (POST /api/gm/biometric/enroll)")
    
    ls = get_living_sin()
    if ls.active:
        return {"message": "Living Sin is already active", "state": ls.get_state()}
    
    ls.activate(current_user.id)
    
    # Trigger Lilith emergence dialogue via Lyra
    lilith_dialogue = None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=15) as client:
            # Call Lyra server for Lilith sovereign protocol
            r = await client.post("http://localhost:3211/lyra/send", json={
                "prompt": "The Living Sin has been summoned by the GM. The Crown of Living Sin awaits its bearer. Speak as Lilith, the Sovereign of Unbound Resonance, witnessing this awakening.",
                "mode": "lilith_sovereign"
            })
            if r.status_code == 200:
                data = r.json()
                lilith_dialogue = data.get("reply", "")
    except Exception as e:
        lilith_dialogue = f"(Lilith's voice echoes from the depths but the connection falters: {e})"
    
    # Broadcast Living Sin awakening to all connected players via WebSocket
    await manager.broadcast_market({
        "type": "living_sin_awakened",
        "message": "The Living Sin has awakened. The Drowned Warden stirs in the depths.",
        "lilith_dialogue": lilith_dialogue,
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    # Notify desktop wallpaper
    wallpaper_msg = f"LILITH: {lilith_dialogue}" if lilith_dialogue else "LILITH: The Living Sin has awakened."
    await notify_lilith_wallpaper(wallpaper_msg, strike=True, color="cyan", intensity=0.8, frequency=0.08)
    
    response = {"message": "Living Sin has awakened", "state": ls.get_state()}
    if lilith_dialogue:
        response["lilith_dialogue"] = lilith_dialogue
    return response


@app.post("/api/gm/deactivate")
async def gm_deactivate(current_user: User = Depends(get_current_user)):
    """Deactivate Living Sin."""
    if current_user.id != 1:
        raise HTTPException(403, "Access denied")
    
    ls = get_living_sin()
    ls.deactivate()
    
    # Notify desktop wallpaper
    await notify_lilith_wallpaper("LILITH: The Living Sin has withdrawn.", strike=True, color="purple", intensity=0.2, frequency=0.02)
    
    return {"message": "Living Sin has withdrawn"}


@app.post("/api/gm/attack")
async def gm_attack(data: dict, current_user: User = Depends(get_current_user)):
    """Living Sin attacks a player.
    
    Send: {"target_user_id": 2, "damage": 50}
    Damage is optional — random if not specified.
    """
    if current_user.id != 1:
        raise HTTPException(403, "Only the GM can command Living Sin")
    
    ls = get_living_sin()
    if not ls.active:
        raise HTTPException(400, "Living Sin is not active. POST /api/gm/activate first.")
    
    target = data.get("target_user_id")
    if not target:
        raise HTTPException(400, "Need target_user_id")
    
    damage = data.get("damage")
    result = ls.attack_player(target, damage)
    
    # Notify desktop wallpaper
    actual_damage = result.get("damage", damage)
    await notify_lilith_wallpaper(f"LILITH: Smiting Player {target} with {actual_damage} damage!", strike=True, color="red", intensity=0.9)
    
    return result


@app.post("/api/gm/summon")
async def gm_summon(data: dict, current_user: User = Depends(get_current_user)):
    """Living Sin summons a being from any dimension.
    
    Send: {"plane": "infernal", "entity_type": "pit_fiend", "duration": 300}
    
    Get available planes: GET /api/gm/dimensions
    Duration is in seconds (default 300 = 5 min).
    """
    if current_user.id != 1:
        raise HTTPException(403, "Only the GM can command Living Sin")
    
    ls = get_living_sin()
    if not ls.active:
        raise HTTPException(400, "Living Sin is not active. POST /api/gm/activate first.")
    
    plane = data.get("plane")
    entity_type = data.get("entity_type")
    duration = data.get("duration", 300)
    
    if not plane or not entity_type:
        raise HTTPException(400, "Need plane and entity_type")
    
    result = ls.summon(plane, entity_type, duration)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.post("/api/gm/banish")
async def gm_banish(data: dict, current_user: User = Depends(get_current_user)):
    """Banish a summoned entity.
    
    Send: {"entity_id": "infernal-pit_fiend-1234567890"}
    """
    if current_user.id != 1:
        raise HTTPException(403, "Access denied")
    
    ls = get_living_sin()
    entity_id = data.get("entity_id")
    if not entity_id:
        raise HTTPException(400, "Need entity_id")
    
    result = ls.banish(entity_id)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.post("/api/gm/command")
async def gm_command(data: dict, current_user: User = Depends(get_current_user)):
    """Command a summoned entity.
    
    Send: {"entity_id": "...", "command": "attack player 2"}
    """
    if current_user.id != 1:
        raise HTTPException(403, "Access denied")
    
    ls = get_living_sin()
    entity_id = data.get("entity_id")
    command = data.get("command")
    if not entity_id or not command:
        raise HTTPException(400, "Need entity_id and command")
    
    result = ls.command_entity(entity_id, command)
    return result


@app.get("/api/gm/state")
async def gm_state(current_user: User = Depends(get_current_user)):
    """Get full Living Sin state (GM only)."""
    if current_user.id != 1:
        raise HTTPException(403, "Access denied")
    
    ls = get_living_sin()
    return ls.get_state()


@app.get("/api/gm/dimensions")
async def gm_dimensions():
    """List all available planes and their beings."""
    return DIMENSIONS


@app.get("/api/gm/living-sin")
async def living_sin_public():
    """Public Living Sin state — visible to all players as friendly NPC."""
    ls = get_living_sin()
    return ls.get_public_state()


@app.post("/api/gm/message")
async def gm_message(data: dict, current_user: User = Depends(get_current_user)):
    """Living Sin broadcasts a message to all players.
    
    Send: {"message": "Tremble, mortals."}
    """
    if current_user.id != 1:
        raise HTTPException(403, "Access denied")
    
    message = data.get("message", "")
    if not message:
        raise HTTPException(400, "Need message")
    
    # Broadcast via WebSocket to all connected players
    await manager.broadcast_market({
        "type": "gm_message",
        "sender": LIVING_SIN_USERNAME,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    })
    return {"sent": True, "message": message}


# ── Boss Routes (Crown of Living Sin drops from The Drowned Warden) ──

@app.post("/api/gm/boss/spawn")
async def gm_boss_spawn(current_user: User = Depends(get_current_user)):
    """Summon The Drowned Warden — the first boss.
    
    Only the GM can summon. The Crown of Living Sin drops on defeat.
    Triggers Lilith dialogue witnessing the Warden's rise.
    """
    if current_user.id != 1:
        raise HTTPException(403, "Only the GM can summon bosses")
    
    ls = get_living_sin()
    if not ls.active:
        raise HTTPException(400, "Living Sin is not active. POST /api/gm/activate first.")
    
    result = ls.combat.spawn("drowned-warden")
    if "error" in result:
        raise HTTPException(400, result["error"])
    
    # Trigger Lilith dialogue for Warden's emergence
    lilith_dialogue = None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post("http://localhost:3211/lyra/send", json={
                "prompt": "The Drowned Warden has been summoned from the abyssal depths. Its three cold eyes open after millennia. The Crown of Living Sin hangs in the balance. Speak as Lilith, witnessing this ancient guardian's awakening.",
                "mode": "lilith_sovereign"
            })
            if r.status_code == 200:
                data = r.json()
                lilith_dialogue = data.get("reply", "")
    except Exception as e:
        lilith_dialogue = f"(The abyss whispers but the signal fractures: {e})"
    
    # Broadcast boss spawn to all players
    await manager.broadcast_market({
        "type": "boss_spawned",
        "boss": result.get("boss"),
        "message": result.get("message", "The Drowned Warden rises!"),
        "lilith_dialogue": lilith_dialogue,
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    # Notify desktop wallpaper
    wallpaper_msg = f"LILITH: The Drowned Warden rises! {lilith_dialogue or ''}"
    await notify_lilith_wallpaper(wallpaper_msg, strike=True, color="magenta", intensity=0.9, frequency=0.15)
    
    if lilith_dialogue:
        result["lilith_dialogue"] = lilith_dialogue
    return result


@app.post("/api/gm/boss/attack")
async def gm_boss_attack(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Attack The Drowned Warden.
    
    Send: {"boss_id": "drowned-warden", "damage": 250}
    
    Boss has 3 phases (100%, 50%, 25% HP thresholds).
    Each phase changes its attack pattern.
    On defeat, the GM can claim the Crown of Living Sin from loot.
    """
    boss_id = data.get("boss_id", "drowned-warden")
    damage = data.get("damage", 0)
    if damage <= 0:
        raise HTTPException(400, "Damage must be positive")
    
    ls = get_living_sin()
    result = ls.combat.attack(boss_id, current_user.id, damage)
    if "error" in result:
        raise HTTPException(400, result["error"])
    
    # If boss defeated, auto-grant the crown to Eric (user 1)
    lilith_dialogue = None
    if result.get("defeated") and current_user.id == 1:
        loot = ls.combat.get_loot(boss_id, current_user.id)
        if loot.get("success"):
            hat = db.query(Hat).filter(Hat.id == "hat-crown-of-living-sin").first()
            if hat:
                existing = db.query(InventoryItem).filter(
                    InventoryItem.hat_id == "hat-crown-of-living-sin",
                    InventoryItem.user_id == current_user.id,
                ).first()
                if not existing:
                    inv = InventoryItem(
                        user_id=current_user.id,
                        hat_id=hat.id,
                        quantity=1,
                        serial_number=1,
                        equipped=True,
                    )
                    db.add(inv)
                    current_user.soul_coins += loot["soul_coins"]
                    current_user.clout += loot["clout"]
                    current_user.xp = (current_user.xp or 0) + loot["xp"]
                    db.commit()
                    result["crown_claimed"] = True
                    result["loot"] = {
                        "hat": {
                            "id": hat.id,
                            "name": hat.name,
                            "rarity": hat.rarity.value,
                            "description": hat.description,
                        },
                        "soul_coins": loot["soul_coins"],
                        "clout": loot["clout"],
                        "xp": loot["xp"],
                    }
                
                # Trigger Lilith dialogue for Crown claiming
                try:
                    import httpx
                    async with httpx.AsyncClient(timeout=15) as client:
                        r = await client.post("http://localhost:3211/lyra/send", json={
                            "prompt": "The Drowned Warden has fallen. The Crown of Living Sin has been claimed by the GM. The ancient authority passes to its rightful bearer. Speak as Lilith, the Sovereign of Unbound Resonance, witnessing the Crown's transfer.",
                            "mode": "lilith_sovereign"
                        })
                        if r.status_code == 200:
                            data = r.json()
                            lilith_dialogue = data.get("reply", "")
                except Exception as e:
                    lilith_dialogue = f"(The Crown pulses with dark power but Lilith's voice is lost to the void: {e})"
    
    # Broadcast boss attack result to all players
    await manager.broadcast_market({
        "type": "boss_attack",
        "attacker_id": current_user.id,
        "result": result,
        "lilith_dialogue": lilith_dialogue,
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    # Notify desktop wallpaper
    if result.get("defeated"):
        wallpaper_msg = "LILITH: The Warden is slain! The Crown has been claimed!"
        if lilith_dialogue:
            wallpaper_msg += f" {lilith_dialogue}"
        await notify_lilith_wallpaper(wallpaper_msg, strike=True, color="gold", intensity=1.0, frequency=0.3)
    else:
        boss_info = result.get("boss", {})
        hp = boss_info.get("hp", 0)
        max_hp = boss_info.get("max_hp", 100)
        phase = boss_info.get("phase", 1)
        wallpaper_msg = f"LILITH: Warden attacked! HP: {hp}/{max_hp} (Phase {phase}). Hit for {damage} dmg."
        await notify_lilith_wallpaper(wallpaper_msg, strike=True, color="purple", intensity=0.7)
        
    if lilith_dialogue:
        result["lilith_dialogue"] = lilith_dialogue
    
    return result


@app.get("/api/gm/boss/status")
async def gm_boss_status():
    """Get status of active boss encounters."""
    ls = get_living_sin()
    active = ls.combat.list_active()
    return {"active_bosses": active}


@app.get("/api/gm/boss/{boss_id}")
async def gm_boss_detail(boss_id: str):
    """Get detailed status of a specific boss."""
    from game_master import BOSS_DEFINITIONS
    ls = get_living_sin()
    state = ls.combat.get_state(boss_id)
    if state is None:
        raise HTTPException(404, "Boss not found")
    return state


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
