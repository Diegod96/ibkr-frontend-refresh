/**
 * IBKR API Service
 */

import { fetchAPI, supabase } from '@/lib/supabase';
import { API_URL } from '@/lib/supabase';
import type { IBKRStatus, IBKRAccount } from '@/types';

/**
 * Check IBKR Gateway connection and authentication status
 * Includes timeout to prevent hanging
 */
export async function getIBKRStatus(): Promise<IBKRStatus> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

  try {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (session?.access_token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${session.access_token}`;
    }

    const response = await fetch(`${API_URL}/ibkr/status`, {
      signal: controller.signal,
      headers,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'An error occurred' }));
      throw new Error(error.message || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timed out - IBKR Gateway may not be running');
    }
    throw error;
  }
}

/**
 * Get list of available IBKR accounts
 */
export async function getIBKRAccounts(): Promise<IBKRAccount[]> {
  return fetchAPI<IBKRAccount[]>('/ibkr/accounts');
}
