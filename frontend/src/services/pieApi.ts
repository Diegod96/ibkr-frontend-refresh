/**
 * Pie API Service
 *
 * Client-side API functions for pie and slice management.
 */

import { fetchAPI } from '@/lib/supabase';
import type {
  Pie,
  PieListResponse,
  Slice,
  CreatePieData,
  UpdatePieData,
  CreateSliceData,
  UpdateSliceData,
} from '@/types/pie';

// ============================================================================
// Pie API
// ============================================================================

export async function getPies(includeInactive = false, portfolioId?: string): Promise<PieListResponse> {
  const params = new URLSearchParams();
  if (includeInactive) params.set('include_inactive', 'true');
  if (portfolioId) params.set('portfolio_id', portfolioId);
  const qs = params.toString() ? `?${params.toString()}` : '';
  return fetchAPI<PieListResponse>(`/pies${qs}`);
}

export async function getPie(pieId: string): Promise<Pie> {
  return fetchAPI<Pie>(`/pies/${pieId}`);
}

export async function createPie(data: CreatePieData): Promise<Pie> {
  return fetchAPI<Pie>('/pies', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updatePie(pieId: string, data: UpdatePieData): Promise<Pie> {
  return fetchAPI<Pie>(`/pies/${pieId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deletePie(pieId: string): Promise<void> {
  await fetchAPI(`/pies/${pieId}`, { method: 'DELETE' });
}

export async function reorderPies(pieIds: string[]): Promise<void> {
  await fetchAPI('/pies/reorder', {
    method: 'POST',
    body: JSON.stringify({ ids: pieIds }),
  });
}

// ============================================================================
// Slice API
// ============================================================================

export async function getSlices(pieId: string, includeInactive = false): Promise<Slice[]> {
  const params = includeInactive ? '?include_inactive=true' : '';
  return fetchAPI<Slice[]>(`/pies/${pieId}/slices${params}`);
}

export async function getSlice(pieId: string, sliceId: string): Promise<Slice> {
  return fetchAPI<Slice>(`/pies/${pieId}/slices/${sliceId}`);
}

export async function createSlice(pieId: string, data: CreateSliceData): Promise<Slice> {
  return fetchAPI<Slice>(`/pies/${pieId}/slices`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateSlice(
  pieId: string,
  sliceId: string,
  data: UpdateSliceData
): Promise<Slice> {
  return fetchAPI<Slice>(`/pies/${pieId}/slices/${sliceId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteSlice(pieId: string, sliceId: string): Promise<void> {
  await fetchAPI(`/pies/${pieId}/slices/${sliceId}`, { method: 'DELETE' });
}

export async function reorderSlices(pieId: string, sliceIds: string[]): Promise<void> {
  await fetchAPI(`/pies/${pieId}/slices/reorder`, {
    method: 'POST',
    body: JSON.stringify({ ids: sliceIds }),
  });
}
