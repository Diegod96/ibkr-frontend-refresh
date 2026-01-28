-- Migration: Create portfolios table
-- Phase 3.1: Portfolio Layer Implementation

-- ============================================================================
-- PORTFOLIOS TABLE
-- ============================================================================
-- A user can have multiple portfolios (e.g., Roth IRA, Brokerage, 401k)

CREATE TABLE IF NOT EXISTS public.portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    account_type VARCHAR(50), -- 'roth_ira', 'traditional_ira', 'brokerage', '401k', etc.
    ibkr_account_id VARCHAR(50), -- IBKR account identifier
    auto_invest_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_portfolio_name_per_user UNIQUE (user_id, name)
);

-- Index for faster user queries
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON public.portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolios_user_active ON public.portfolios(user_id, auto_invest_enabled);

-- ============================================================================
-- UPDATE PIES TABLE TO REFERENCE PORTFOLIOS
-- ============================================================================
-- Add portfolio_id column to pies (allows NULL initially for migration)
ALTER TABLE public.pies ADD COLUMN IF NOT EXISTS portfolio_id UUID REFERENCES public.portfolios(id) ON DELETE CASCADE;

-- Create index for the new foreign key
CREATE INDEX IF NOT EXISTS idx_pies_portfolio_id ON public.pies(portfolio_id);

-- ============================================================================
-- UPDATED_AT TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp (if not exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for portfolios
DROP TRIGGER IF EXISTS update_portfolios_updated_at ON public.portfolios;
CREATE TRIGGER update_portfolios_updated_at
    BEFORE UPDATE ON public.portfolios
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on portfolios
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;

-- Users can only see their own portfolios
CREATE POLICY "Users can view own portfolios"
    ON public.portfolios FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own portfolios
CREATE POLICY "Users can insert own portfolios"
    ON public.portfolios FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own portfolios
CREATE POLICY "Users can update own portfolios"
    ON public.portfolios FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own portfolios
CREATE POLICY "Users can delete own portfolios"
    ON public.portfolios FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- DATA MIGRATION: CREATE DEFAULT PORTFOLIOS FOR EXISTING USERS
-- ============================================================================
-- Create a "Default Portfolio" for each user who has pies but no portfolios

INSERT INTO public.portfolios (user_id, name, description, account_type, auto_invest_enabled)
SELECT DISTINCT
    u.id as user_id,
    'Default Portfolio' as name,
    'Migrated from existing pies' as description,
    'brokerage' as account_type,
    false as auto_invest_enabled
FROM public.users u
WHERE u.id NOT IN (
    SELECT DISTINCT user_id FROM public.portfolios
)
AND EXISTS (
    SELECT 1 FROM public.pies p WHERE p.user_id = u.id
);

-- Update existing pies to reference the default portfolios
UPDATE public.pies
SET portfolio_id = (
    SELECT p.id
    FROM public.portfolios p
    WHERE p.user_id = public.pies.user_id
    AND p.name = 'Default Portfolio'
    LIMIT 1
)
WHERE portfolio_id IS NULL;

-- ============================================================================
-- UPDATE RLS POLICIES TO USE PORTFOLIO RELATIONSHIP
-- ============================================================================
-- Drop old policies that depend on user_id
DROP POLICY IF EXISTS "Users can view own pies" ON public.pies;
DROP POLICY IF EXISTS "Users can insert own pies" ON public.pies;
DROP POLICY IF EXISTS "Users can update own pies" ON public.pies;
DROP POLICY IF EXISTS "Users can delete own pies" ON public.pies;

-- Drop slice policies that depend on pie user_id
DROP POLICY IF EXISTS "Users can view own slices" ON public.slices;
DROP POLICY IF EXISTS "Users can insert own slices" ON public.slices;
DROP POLICY IF EXISTS "Users can update own slices" ON public.slices;
DROP POLICY IF EXISTS "Users can delete own slices" ON public.slices;

-- Create new pies policies based on portfolio ownership
CREATE POLICY "Users can view own pies"
    ON public.pies FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.portfolios
            WHERE portfolios.id = pies.portfolio_id
            AND portfolios.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own pies"
    ON public.pies FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.portfolios
            WHERE portfolios.id = pies.portfolio_id
            AND portfolios.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own pies"
    ON public.pies FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.portfolios
            WHERE portfolios.id = pies.portfolio_id
            AND portfolios.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.portfolios
            WHERE portfolios.id = pies.portfolio_id
            AND portfolios.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own pies"
    ON public.pies FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.portfolios
            WHERE portfolios.id = pies.portfolio_id
            AND portfolios.user_id = auth.uid()
        )
    );

-- Create new slices policies based on portfolio ownership
CREATE POLICY "Users can view own slices"
    ON public.slices FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.pies
            JOIN public.portfolios ON portfolios.id = pies.portfolio_id
            WHERE pies.id = slices.pie_id
            AND portfolios.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own slices"
    ON public.slices FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.pies
            JOIN public.portfolios ON portfolios.id = pies.portfolio_id
            WHERE pies.id = slices.pie_id
            AND portfolios.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own slices"
    ON public.slices FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.pies
            JOIN public.portfolios ON portfolios.id = pies.portfolio_id
            WHERE pies.id = slices.pie_id
            AND portfolios.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.pies
            JOIN public.portfolios ON portfolios.id = pies.portfolio_id
            WHERE pies.id = slices.pie_id
            AND portfolios.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own slices"
    ON public.slices FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.pies
            JOIN public.portfolios ON portfolios.id = pies.portfolio_id
            WHERE pies.id = slices.pie_id
            AND portfolios.user_id = auth.uid()
        )
    );

-- ============================================================================
-- MAKE PORTFOLIO_ID NON-NULLABLE AFTER MIGRATION
-- ============================================================================
-- This will fail if any pies still don't have portfolio_id assigned
ALTER TABLE public.pies ALTER COLUMN portfolio_id SET NOT NULL;

-- ============================================================================
-- REMOVE OLD USER_ID COLUMN FROM PIES
-- ============================================================================
-- Drop the old user_id foreign key and column
ALTER TABLE public.pies DROP CONSTRAINT IF EXISTS pies_user_id_fkey;
ALTER TABLE public.pies DROP COLUMN IF EXISTS user_id;

-- Drop old index
DROP INDEX IF EXISTS idx_pies_user_id;