-- Abyssal Assets — PostgreSQL Initialization
-- Runs on first container startup

-- ===========================
-- EXTENSIONS
-- ===========================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ===========================
-- TIMEZONE
-- ===========================
SET timezone = 'UTC';

-- ===========================
-- CUSTOM TYPES
-- ===========================
DO $$ BEGIN
    CREATE TYPE rarity_enum AS ENUM (
        'noob', 'common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE zone_enum AS ENUM (
        'shallows', 'standard', 'deep', 'abyssal', 'trench'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE order_side_enum AS ENUM ('buy', 'sell');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE order_status_enum AS ENUM ('open', 'filled', 'cancelled', 'partial');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ===========================
-- PERFORMANCE SETTINGS
-- ===========================
-- Enable parallel query
SET max_parallel_workers_per_gather = 4;

-- Enable JIT for complex queries
SET jit = on;
SET jit_above_cost = 100000;

-- ===========================
-- INDEX RECOMMENDATIONS (for reference)
-- These will be created by SQLAlchemy but good to know:
-- 
-- CREATE INDEX CONCURRENTLY idx_orders_user_status ON orders(user_id, status);
-- CREATE INDEX CONCURRENTLY idx_orders_hat_side ON orders(hat_id, side);
-- CREATE INDEX CONCURRENTLY idx_market_listings_active ON market_listings(is_active, expires_at);
-- CREATE INDEX CONCURRENTLY idx_trades_hat_created ON trades(hat_id, created_at DESC);
-- CREATE INDEX CONCURRENTLY idx_inventory_user ON inventory_items(user_id);
-- CREATE INDEX CONCURRENTLY idx_dredge_logs_user_created ON dredge_logs(user_id, created_at DESC);

-- ===========================
-- GRANTS
-- ===========================
GRANT ALL PRIVILEGES ON DATABASE abyssal_assets TO abyssal;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO abyssal;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO abyssal;

-- Default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO abyssal;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO abyssal;

-- ===========================
-- VERIFICATION
-- ===========================
SELECT 'Abyssal Assets DB initialized successfully' as status;