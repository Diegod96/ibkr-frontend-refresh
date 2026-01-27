-- IBKR Frontend Refresh - Initial Database Schema
-- Phase 1: Foundation
-- 
-- This migration creates the core tables for the portfolio management system:
-- - users: User accounts (linked to Supabase Auth)
-- - portfolios: User portfolios (e.g., Roth IRA, Brokerage)
-- - pies: Themed groupings of assets within a portfolio
-- - slices: Individual holdings within a pie
-- - build_rules: Rules for position building triggers
-- - deposits: Cash deposits into portfolios
-- - transactions: Trade execution history

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- ============================================================================
-- Links to Supabase Auth users via auth.users(id)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(100),
    ibkr_connected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- PORTFOLIOS TABLE
-- ============================================================================
-- A user can have multiple portfolios (e.g., Roth IRA, Brokerage, 401k)
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    account_type VARCHAR(50), -- 'roth_ira', 'traditional_ira', 'brokerage', '401k', etc.
    ibkr_account_id VARCHAR(50), -- IBKR account identifier
    auto_invest_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_portfolio_name_per_user UNIQUE (user_id, name)
);

-- ============================================================================
-- PIES TABLE
-- ============================================================================
-- A pie is a themed grouping of assets within a portfolio
-- Pie weights within a portfolio must sum to 100%
CREATE TABLE pies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    target_weight DECIMAL(5,2) NOT NULL CHECK (target_weight >= 0 AND target_weight <= 100),
    color VARCHAR(7), -- Hex color for UI display (e.g., '#FF5733')
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_pie_name_per_portfolio UNIQUE (portfolio_id, name)
);

-- ============================================================================
-- SLICES TABLE
-- ============================================================================
-- A slice is an individual holding within a pie
-- Slice weights within a pie must sum to 100%
CREATE TABLE slices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pie_id UUID NOT NULL REFERENCES pies(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    name VARCHAR(100), -- Company/ETF name
    target_weight DECIMAL(5,2) NOT NULL CHECK (target_weight >= 0 AND target_weight <= 100),
    position_type VARCHAR(20) DEFAULT 'full' CHECK (position_type IN ('full', 'build')),
    current_shares DECIMAL(12,4) DEFAULT 0,
    average_cost DECIMAL(12,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_ticker_per_pie UNIQUE (pie_id, ticker)
);

-- ============================================================================
-- BUILD_RULES TABLE
-- ============================================================================
-- Rules for position building (when position_type = 'build')
CREATE TABLE build_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slice_id UUID NOT NULL REFERENCES slices(id) ON DELETE CASCADE,
    trigger_type VARCHAR(30) NOT NULL CHECK (trigger_type IN (
        'time_interval',      -- Buy at regular intervals
        'price_pullback',     -- Buy on price dips
        'price_breakout',     -- Buy on price breakouts
        'ma_crossover',       -- Moving average signals
        'rsi_oversold',       -- RSI below threshold
        'volume_spike',       -- Volume-based triggers
        'bollinger_lower',    -- Price touches lower Bollinger Band
        'earnings_pre',       -- Before earnings announcement
        'earnings_post'       -- After earnings announcement
    )),
    parameters JSONB NOT NULL DEFAULT '{}', -- Trigger-specific parameters
    -- Example parameters:
    -- time_interval: {"interval_days": 7, "amount_per_interval": 100}
    -- price_pullback: {"pullback_percent": 5, "from_high_days": 30}
    -- ma_crossover: {"fast_period": 10, "slow_period": 50}
    -- rsi_oversold: {"threshold": 30, "period": 14}
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- DEPOSITS TABLE
-- ============================================================================
-- Track cash deposits into portfolios
CREATE TABLE deposits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    source VARCHAR(50), -- 'bank_transfer', 'dividend', 'manual', etc.
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'allocated', 'partial', 'cancelled')),
    allocated_amount DECIMAL(12,2) DEFAULT 0,
    deposited_at TIMESTAMPTZ DEFAULT NOW(),
    allocated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- TRANSACTIONS TABLE
-- ============================================================================
-- Record all trade executions
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slice_id UUID NOT NULL REFERENCES slices(id) ON DELETE SET NULL,
    deposit_id UUID REFERENCES deposits(id) ON DELETE SET NULL,
    build_rule_id UUID REFERENCES build_rules(id) ON DELETE SET NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('buy', 'sell')),
    ticker VARCHAR(10) NOT NULL,
    shares DECIMAL(12,4) NOT NULL CHECK (shares > 0),
    price DECIMAL(12,4) NOT NULL CHECK (price > 0),
    total_amount DECIMAL(12,2) NOT NULL,
    commission DECIMAL(8,2) DEFAULT 0,
    ibkr_order_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'submitted', 'filled', 'partial', 'cancelled', 'failed')),
    executed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX idx_pies_portfolio_id ON pies(portfolio_id);
CREATE INDEX idx_slices_pie_id ON slices(pie_id);
CREATE INDEX idx_slices_ticker ON slices(ticker);
CREATE INDEX idx_build_rules_slice_id ON build_rules(slice_id);
CREATE INDEX idx_build_rules_trigger_type ON build_rules(trigger_type);
CREATE INDEX idx_deposits_portfolio_id ON deposits(portfolio_id);
CREATE INDEX idx_deposits_status ON deposits(status);
CREATE INDEX idx_transactions_slice_id ON transactions(slice_id);
CREATE INDEX idx_transactions_ticker ON transactions(ticker);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_executed_at ON transactions(executed_at);

-- ============================================================================
-- FUNCTIONS FOR WEIGHT VALIDATION
-- ============================================================================

-- Function to validate pie weights sum to 100% within a portfolio
CREATE OR REPLACE FUNCTION validate_pie_weights()
RETURNS TRIGGER AS $$
DECLARE
    total_weight DECIMAL(5,2);
BEGIN
    SELECT COALESCE(SUM(target_weight), 0) INTO total_weight
    FROM pies
    WHERE portfolio_id = COALESCE(NEW.portfolio_id, OLD.portfolio_id);
    
    -- Allow weights that sum to <= 100 (in progress) or exactly 100 (complete)
    IF total_weight > 100 THEN
        RAISE EXCEPTION 'Pie weights in portfolio cannot exceed 100%%. Current total: %%', total_weight;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to validate slice weights sum to 100% within a pie
CREATE OR REPLACE FUNCTION validate_slice_weights()
RETURNS TRIGGER AS $$
DECLARE
    total_weight DECIMAL(5,2);
BEGIN
    SELECT COALESCE(SUM(target_weight), 0) INTO total_weight
    FROM slices
    WHERE pie_id = COALESCE(NEW.pie_id, OLD.pie_id);
    
    -- Allow weights that sum to <= 100 (in progress) or exactly 100 (complete)
    IF total_weight > 100 THEN
        RAISE EXCEPTION 'Slice weights in pie cannot exceed 100%%. Current total: %%', total_weight;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS FOR WEIGHT VALIDATION
-- ============================================================================
CREATE TRIGGER trigger_validate_pie_weights
    AFTER INSERT OR UPDATE ON pies
    FOR EACH ROW
    EXECUTE FUNCTION validate_pie_weights();

CREATE TRIGGER trigger_validate_slice_weights
    AFTER INSERT OR UPDATE ON slices
    FOR EACH ROW
    EXECUTE FUNCTION validate_slice_weights();

-- ============================================================================
-- FUNCTION FOR UPDATED_AT TIMESTAMPS
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers to all tables
CREATE TRIGGER trigger_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_portfolios_updated_at BEFORE UPDATE ON portfolios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_pies_updated_at BEFORE UPDATE ON pies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_slices_updated_at BEFORE UPDATE ON slices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_build_rules_updated_at BEFORE UPDATE ON build_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_deposits_updated_at BEFORE UPDATE ON deposits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trigger_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE pies ENABLE ROW LEVEL SECURITY;
ALTER TABLE slices ENABLE ROW LEVEL SECURITY;
ALTER TABLE build_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE deposits ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Users can only access their own data
CREATE POLICY users_policy ON users FOR ALL USING (auth.uid() = id);

CREATE POLICY portfolios_policy ON portfolios FOR ALL USING (
    user_id = auth.uid()
);

CREATE POLICY pies_policy ON pies FOR ALL USING (
    portfolio_id IN (SELECT id FROM portfolios WHERE user_id = auth.uid())
);

CREATE POLICY slices_policy ON slices FOR ALL USING (
    pie_id IN (SELECT id FROM pies WHERE portfolio_id IN (SELECT id FROM portfolios WHERE user_id = auth.uid()))
);

CREATE POLICY build_rules_policy ON build_rules FOR ALL USING (
    slice_id IN (SELECT id FROM slices WHERE pie_id IN (SELECT id FROM pies WHERE portfolio_id IN (SELECT id FROM portfolios WHERE user_id = auth.uid())))
);

CREATE POLICY deposits_policy ON deposits FOR ALL USING (
    portfolio_id IN (SELECT id FROM portfolios WHERE user_id = auth.uid())
);

CREATE POLICY transactions_policy ON transactions FOR ALL USING (
    slice_id IN (SELECT id FROM slices WHERE pie_id IN (SELECT id FROM pies WHERE portfolio_id IN (SELECT id FROM portfolios WHERE user_id = auth.uid())))
);
