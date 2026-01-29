/**
 * Type definitions for the IBKR Frontend Refresh application
 */

// ============================================================================
// User Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  display_name: string | null;
  ibkr_connected: boolean;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Portfolio Types
// ============================================================================

export interface Portfolio {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  account_type: string | null;
  ibkr_account_id: string | null;
  auto_invest_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface PortfolioCreate {
  name: string;
  description?: string;
  account_type?: string;
  ibkr_account_id?: string;
  auto_invest_enabled?: boolean;
}

export interface PortfolioUpdate {
  name?: string;
  description?: string;
  account_type?: string;
  ibkr_account_id?: string;
  auto_invest_enabled?: boolean;
}

// ============================================================================
// Pie Types
// ============================================================================

export interface Pie {
  id: string;
  portfolio_id: string;
  name: string;
  description: string | null;
  target_weight: number;
  color: string | null;
  created_at: string;
  updated_at: string;
}

export interface PieCreate {
  portfolio_id: string;
  name: string;
  description?: string;
  target_weight: number;
  color?: string;
}

export interface PieUpdate {
  name?: string;
  description?: string;
  target_weight?: number;
  color?: string;
}

// ============================================================================
// Slice Types
// ============================================================================

export type PositionType = 'full' | 'build';

export interface Slice {
  id: string;
  pie_id: string;
  ticker: string;
  name: string | null;
  target_weight: number;
  position_type: PositionType;
  current_shares: number;
  average_cost: number | null;
  created_at: string;
  updated_at: string;
}

export interface SliceCreate {
  pie_id: string;
  ticker: string;
  name?: string;
  target_weight: number;
  position_type?: PositionType;
}

export interface SliceUpdate {
  name?: string;
  target_weight?: number;
  position_type?: PositionType;
}

// ============================================================================
// Build Rule Types
// ============================================================================

export type TriggerType =
  | 'time_interval'
  | 'price_pullback'
  | 'price_breakout'
  | 'ma_crossover'
  | 'rsi_oversold'
  | 'volume_spike'
  | 'bollinger_lower'
  | 'earnings_pre'
  | 'earnings_post';

export interface BuildRule {
  id: string;
  slice_id: string;
  trigger_type: TriggerType;
  parameters: Record<string, unknown>;
  is_active: boolean;
  last_triggered_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface BuildRuleCreate {
  slice_id: string;
  trigger_type: TriggerType;
  parameters?: Record<string, unknown>;
  is_active?: boolean;
}

export interface BuildRuleUpdate {
  parameters?: Record<string, unknown>;
  is_active?: boolean;
}

// ============================================================================
// Deposit Types
// ============================================================================

export type DepositStatus = 'pending' | 'allocated' | 'partial' | 'cancelled';
export type DepositSource = 'bank_transfer' | 'dividend' | 'manual';

export interface Deposit {
  id: string;
  portfolio_id: string;
  amount: number;
  source: DepositSource | null;
  status: DepositStatus;
  allocated_amount: number;
  deposited_at: string;
  allocated_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DepositCreate {
  portfolio_id: string;
  amount: number;
  source?: DepositSource;
}

// ============================================================================
// Transaction Types
// ============================================================================

export type TransactionType = 'buy' | 'sell';
export type TransactionStatus = 'pending' | 'submitted' | 'filled' | 'partial' | 'cancelled' | 'failed';

export interface Transaction {
  id: string;
  slice_id: string;
  deposit_id: string | null;
  build_rule_id: string | null;
  transaction_type: TransactionType;
  ticker: string;
  shares: number;
  price: number;
  total_amount: number;
  commission: number;
  ibkr_order_id: string | null;
  status: TransactionStatus;
  executed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  slice_id: string;
  deposit_id?: string;
  build_rule_id?: string;
  transaction_type: TransactionType;
  ticker: string;
  shares: number;
  price: number;
  total_amount: number;
  commission?: number;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiError {
  message: string;
  detail?: string;
}

export interface HealthCheck {
  status: 'healthy' | 'unhealthy';
  version: string;
  environment: string;
  timestamp: string;
}

// ============================================================================
// IBKR Types
// ============================================================================

export interface IBKRStatus {
  authenticated: boolean;
  connected: boolean;
  message: string;
  details?: Record<string, unknown> | null;
}

export interface IBKRAccount {
  account_id: string;
  account_title: string | null;
  account_type: string | null;
}
