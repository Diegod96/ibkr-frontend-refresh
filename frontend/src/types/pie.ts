/**
 * Pie and Slice Types
 *
 * TypeScript interfaces for pie and slice data structures.
 */

export interface Slice {
  id: string;
  pie_id: string;
  symbol: string;
  name: string | null;
  target_weight: number;
  display_order: number;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Pie {
  id: string;
  user_id: string;
  portfolio_id?: string | null;
  name: string;
  description: string | null;
  color: string;
  icon: string | null;
  target_allocation: number;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  slices: Slice[];
  total_slice_weight: number;
  slice_count: number;
}

export interface PieListResponse {
  pies: Pie[];
  total_allocation: number;
}

// Create/Update DTOs
export interface CreatePieData {
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  target_allocation?: number;
  portfolio_id?: string | null;
}

export interface UpdatePieData {
  name?: string;
  description?: string;
  color?: string;
  icon?: string;
  target_allocation?: number;
  is_active?: boolean;
  portfolio_id?: string | null;
}

export interface CreateSliceData {
  symbol: string;
  name?: string;
  target_weight: number;
  notes?: string;
}

export interface UpdateSliceData {
  symbol?: string;
  name?: string;
  target_weight?: number;
  notes?: string;
  is_active?: boolean;
}

// Predefined colors for pies
export const PIE_COLORS = [
  '#3B82F6', // Blue
  '#10B981', // Green
  '#F59E0B', // Amber
  '#EF4444', // Red
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#06B6D4', // Cyan
  '#F97316', // Orange
  '#6366F1', // Indigo
  '#84CC16', // Lime
] as const;
