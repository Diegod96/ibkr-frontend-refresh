# Database Schema Documentation

This document describes the database schema for the IBKR Frontend Refresh application.

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   users     │───────│  portfolios  │───────│    pies     │
└─────────────┘  1:N  └──────────────┘  1:N  └─────────────┘
                            │                      │
                            │                      │ 1:N
                            │                      ▼
                            │               ┌─────────────┐
                            │               │   slices    │
                            │               └─────────────┘
                            │                      │
                            │                      │ 1:N
                            │                      ▼
                            │               ┌─────────────┐
                            │               │ build_rules │
                            │               └─────────────┘
                            │
                            │ 1:N
                            ▼
                     ┌──────────────┐
                     │   deposits   │
                     └──────────────┘
                            │
                            │ 1:N
                            ▼
                     ┌──────────────┐
                     │ transactions │◄─── slices, build_rules
                     └──────────────┘
```

## Tables

### users

Stores user account information linked to Supabase Auth.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, FK → auth.users | Supabase Auth user ID |
| email | VARCHAR(255) | NOT NULL, UNIQUE | User email address |
| display_name | VARCHAR(100) | | Optional display name |
| ibkr_connected | BOOLEAN | DEFAULT FALSE | IBKR account connection status |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

### portfolios

Represents user portfolios (e.g., Roth IRA, Brokerage, 401k).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Auto-generated UUID |
| user_id | UUID | FK → users, NOT NULL | Owner user ID |
| name | VARCHAR(100) | NOT NULL | Portfolio name |
| description | TEXT | | Optional description |
| account_type | VARCHAR(50) | | Account type (roth_ira, brokerage, etc.) |
| ibkr_account_id | VARCHAR(50) | | IBKR account identifier |
| auto_invest_enabled | BOOLEAN | DEFAULT FALSE | Auto-invest toggle |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

**Constraints:**
- UNIQUE (user_id, name) - Portfolio names must be unique per user

### pies

Themed groupings of assets within a portfolio.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Auto-generated UUID |
| portfolio_id | UUID | FK → portfolios, NOT NULL | Parent portfolio ID |
| name | VARCHAR(100) | NOT NULL | Pie name (e.g., "Semiconductors") |
| description | TEXT | | Optional description |
| target_weight | DECIMAL(5,2) | NOT NULL, 0-100 | Target allocation percentage |
| color | VARCHAR(7) | | Hex color for UI (e.g., '#FF5733') |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

**Constraints:**
- UNIQUE (portfolio_id, name) - Pie names must be unique per portfolio
- CHECK (target_weight >= 0 AND target_weight <= 100)
- **Trigger validation:** Sum of pie weights in a portfolio must not exceed 100%

### slices

Individual holdings within a pie.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Auto-generated UUID |
| pie_id | UUID | FK → pies, NOT NULL | Parent pie ID |
| ticker | VARCHAR(10) | NOT NULL | Stock/ETF ticker symbol |
| name | VARCHAR(100) | | Company/ETF name |
| target_weight | DECIMAL(5,2) | NOT NULL, 0-100 | Target allocation within pie |
| position_type | VARCHAR(20) | DEFAULT 'full' | 'full' or 'build' |
| current_shares | DECIMAL(12,4) | DEFAULT 0 | Current shares held |
| average_cost | DECIMAL(12,4) | | Average cost basis |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

**Constraints:**
- UNIQUE (pie_id, ticker) - Tickers must be unique per pie
- CHECK (target_weight >= 0 AND target_weight <= 100)
- CHECK (position_type IN ('full', 'build'))
- **Trigger validation:** Sum of slice weights in a pie must not exceed 100%

### build_rules

Configuration for position building triggers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Auto-generated UUID |
| slice_id | UUID | FK → slices, NOT NULL | Parent slice ID |
| trigger_type | VARCHAR(30) | NOT NULL, CHECK | Type of trigger |
| parameters | JSONB | DEFAULT '{}' | Trigger-specific parameters |
| is_active | BOOLEAN | DEFAULT TRUE | Trigger active status |
| last_triggered_at | TIMESTAMPTZ | | Last trigger execution time |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

**Trigger Types:**
- `time_interval` - Buy at regular intervals
- `price_pullback` - Buy on price dips
- `price_breakout` - Buy on price breakouts
- `ma_crossover` - Moving average signals
- `rsi_oversold` - RSI below threshold
- `volume_spike` - Volume-based triggers
- `bollinger_lower` - Price touches lower Bollinger Band
- `earnings_pre` - Before earnings announcement
- `earnings_post` - After earnings announcement

**Example Parameters:**
```json
// time_interval
{"interval_days": 7, "amount_per_interval": 100}

// price_pullback
{"pullback_percent": 5, "from_high_days": 30}

// ma_crossover
{"fast_period": 10, "slow_period": 50}

// rsi_oversold
{"threshold": 30, "period": 14}
```

### deposits

Tracks cash deposits into portfolios.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Auto-generated UUID |
| portfolio_id | UUID | FK → portfolios, NOT NULL | Target portfolio ID |
| amount | DECIMAL(12,2) | NOT NULL, > 0 | Deposit amount |
| source | VARCHAR(50) | | Deposit source |
| status | VARCHAR(20) | DEFAULT 'pending' | Allocation status |
| allocated_amount | DECIMAL(12,2) | DEFAULT 0 | Amount allocated to trades |
| deposited_at | TIMESTAMPTZ | DEFAULT NOW() | Deposit timestamp |
| allocated_at | TIMESTAMPTZ | | Full allocation timestamp |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

**Status Values:**
- `pending` - Awaiting allocation
- `allocated` - Fully allocated
- `partial` - Partially allocated
- `cancelled` - Deposit cancelled

### transactions

Records all trade executions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Auto-generated UUID |
| slice_id | UUID | FK → slices, NOT NULL | Associated slice |
| deposit_id | UUID | FK → deposits | Source deposit (if auto-invest) |
| build_rule_id | UUID | FK → build_rules | Triggering rule (if position building) |
| transaction_type | VARCHAR(10) | NOT NULL, CHECK | 'buy' or 'sell' |
| ticker | VARCHAR(10) | NOT NULL | Stock/ETF ticker |
| shares | DECIMAL(12,4) | NOT NULL, > 0 | Number of shares |
| price | DECIMAL(12,4) | NOT NULL, > 0 | Execution price |
| total_amount | DECIMAL(12,2) | NOT NULL | Total transaction value |
| commission | DECIMAL(8,2) | DEFAULT 0 | Commission/fees |
| ibkr_order_id | VARCHAR(50) | | IBKR order reference |
| status | VARCHAR(20) | DEFAULT 'pending' | Order status |
| executed_at | TIMESTAMPTZ | | Execution timestamp |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Record update timestamp |

**Status Values:**
- `pending` - Order created
- `submitted` - Submitted to IBKR
- `filled` - Fully executed
- `partial` - Partially filled
- `cancelled` - Order cancelled
- `failed` - Order failed

## Row Level Security (RLS)

All tables have RLS enabled with policies ensuring users can only access their own data:

- **users**: `auth.uid() = id`
- **portfolios**: `user_id = auth.uid()`
- **pies**: Portfolio belongs to user
- **slices**: Pie's portfolio belongs to user
- **build_rules**: Slice's pie's portfolio belongs to user
- **deposits**: Portfolio belongs to user
- **transactions**: Slice's pie's portfolio belongs to user

## Indexes

Performance indexes are created on:
- Foreign key columns (user_id, portfolio_id, pie_id, slice_id)
- Frequently queried columns (ticker, status, trigger_type)
- Date columns (executed_at)
