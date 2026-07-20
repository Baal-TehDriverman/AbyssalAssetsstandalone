import sys

with open('/home/tehlappy/Desktop/Lilith/Core_Systems/AI/abyssal-assets/server/main.py', 'r') as f:
    content = f.read()

# Fix 2: Add Index to MarketListing
import_str = "from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum as SQLEnum, func, and_"
import_repl = "from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum as SQLEnum, func, and_, Index"
content = content.replace(import_str, import_repl)

ml_str = """class MarketListing(Base):
    __tablename__ = "market_listings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))"""
ml_repl = """class MarketListing(Base):
    __tablename__ = "market_listings"
    __table_args__ = (
        Index('ix_market_listings_hat_active_expires', 'hat_id', 'is_active', 'expires_at'),
    )
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))"""
content = content.replace(ml_str, ml_repl)

# Fix 3 & 8: Connection Pooling and WAL
db_str = """if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)"""
db_repl = """from sqlalchemy.pool import QueuePool
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
    engine = create_engine(DATABASE_URL)"""
content = content.replace(db_str, db_repl)

# Fix 1, 4, 5, 6: Delete redundant get_market
start_idx = content.find('# Market Data - OPTIMIZED: Single query with joins instead of N+1\n@app.get("/api/market", response_model=List[MarketItemSummary])')
if start_idx != -1:
    end_idx = content.find('# Market Data - OPTIMIZED: Single query with joins instead of N+1\ndef _get_market_base_query(db: Session):', start_idx)
    if end_idx != -1:
        content = content[:start_idx] + content[end_idx:]
        print("Removed redundant get_market endpoint!")

with open('/home/tehlappy/Desktop/Lilith/Core_Systems/AI/abyssal-assets/server/main.py', 'w') as f:
    f.write(content)
print("Applied fixes 1-6!")
