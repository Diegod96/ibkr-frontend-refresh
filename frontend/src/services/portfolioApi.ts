/**
 * Portfolio API Service
 */

import { fetchAPI } from '@/lib/supabase';
import type { Portfolio, PortfolioCreate, PortfolioUpdate } from '@/types';

export async function getPortfolios(): Promise<Portfolio[]> {
  return fetchAPI<Portfolio[]>('/portfolios');
}

export async function createPortfolio(data: PortfolioCreate): Promise<Portfolio> {
  return fetchAPI<Portfolio>('/portfolios', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updatePortfolio(id: string, data: PortfolioUpdate): Promise<Portfolio> {
  return fetchAPI<Portfolio>(`/portfolios/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deletePortfolio(id: string): Promise<void> {
  await fetchAPI(`/portfolios/${id}`, { method: 'DELETE' });
}
