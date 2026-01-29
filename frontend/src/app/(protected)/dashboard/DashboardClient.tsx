/**
 * Dashboard Client Component
 *
 * Client-side component for the dashboard with real portfolio data.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { PortfolioSummary, PortfolioAllocationChart, PieList } from '@/components/dashboard';
import { PortfolioSelector } from '@/components/portfolios/PortfolioSelector';
import { RebalanceModal } from '@/components/rebalance';
import type { Portfolio } from '@/types';
import type { IBKRStatus } from '@/types';
import type { Pie } from '@/types/pie';
import * as portfolioApi from '@/services/portfolioApi';
import * as pieApi from '@/services/pieApi';
import * as ibkrApi from '@/services/ibkrApi';

interface DashboardClientProps {
  userEmail: string;
}

export function DashboardClient({ userEmail }: DashboardClientProps) {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string | null>(null);
  const [pies, setPies] = useState<Pie[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRebalanceModalOpen, setIsRebalanceModalOpen] = useState(false);
  const [ibkrStatus, setIbkrStatus] = useState<IBKRStatus | null>(null);
  const [isCheckingIBKR, setIsCheckingIBKR] = useState(false);

  // Load portfolios on mount
  const loadPortfolios = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await portfolioApi.getPortfolios();
      setPortfolios(data);
      // Select first portfolio by default if none selected
      if (data.length > 0 && !selectedPortfolioId) {
        setSelectedPortfolioId(data[0].id);
      } else if (data.length === 0) {
        // No portfolios, stop loading
        setIsLoading(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load portfolios');
      setIsLoading(false);
    }
  }, [selectedPortfolioId]);

  // Load pies when portfolio changes
  const loadPies = useCallback(async () => {
    if (!selectedPortfolioId) return;
    
    try {
      setIsLoading(true);
      setError(null);
      const response = await pieApi.getPies(false, selectedPortfolioId);
      setPies(response.pies);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load pies');
    } finally {
      setIsLoading(false);
    }
  }, [selectedPortfolioId]);

  useEffect(() => {
    loadPortfolios();
  }, [loadPortfolios]);

  useEffect(() => {
    loadPies();
  }, [loadPies]);

  // Check IBKR connection status (non-blocking)
  const checkIBKRStatus = useCallback(async () => {
    try {
      setIsCheckingIBKR(true);
      // Don't set error state for IBKR failures - it's optional
      const status = await ibkrApi.getIBKRStatus();
      setIbkrStatus(status);
    } catch (err) {
      // Silently fail - IBKR connection is optional
      setIbkrStatus({
        authenticated: false,
        connected: false,
        message: err instanceof Error ? err.message : 'IBKR Gateway not available',
      });
    } finally {
      setIsCheckingIBKR(false);
    }
  }, []);

  // Load IBKR status on mount (non-blocking, don't wait for it)
  useEffect(() => {
    // Run async but don't block dashboard loading
    checkIBKRStatus().catch(() => {
      // Ignore errors - IBKR is optional
    });
  }, [checkIBKRStatus]);

  const selectedPortfolio = portfolios.find((p) => p.id === selectedPortfolioId) || null;

  if (isLoading && portfolios.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Welcome back
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {userEmail}
            </p>
          </div>
          <PortfolioSelector
            value={selectedPortfolioId}
            onChange={setSelectedPortfolioId}
          />
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">
            {error}
          </div>
        )}

        {ibkrStatus && !ibkrStatus.authenticated && (
          <div className="mb-6 rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-yellow-800 dark:border-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400">
            <div className="flex items-start">
              <svg
                className="mr-2 h-5 w-5 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <div>
                <p className="font-medium">{ibkrStatus.message}</p>
                {!ibkrStatus.connected && (
                  <p className="mt-1 text-sm">
                    Make sure the IBKR Client Portal Gateway is running on localhost:5000
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Portfolio Summary */}
        <div className="mb-8">
          <PortfolioSummary portfolio={selectedPortfolio} pies={pies} />
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Portfolio Allocation Chart */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Portfolio Allocation
              </h2>
              <Link
                href="/portfolios"
                className="text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
              >
                Manage Pies →
              </Link>
            </div>
            <PortfolioAllocationChart pies={pies} />
          </div>

          {/* Pie List */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Your Pies
              </h2>
              <Link
                href="/portfolios"
                className="text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
              >
                View All →
              </Link>
            </div>
            <PieList pies={pies} />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Quick Actions
          </h2>
          <div className="mt-4 flex flex-wrap gap-4">
            <Link
              href="/portfolios"
              className="inline-flex items-center rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
            >
              Manage Portfolios
            </Link>
            <button
              onClick={checkIBKRStatus}
              disabled={isCheckingIBKR}
              className={`inline-flex items-center rounded-lg border px-4 py-2 text-sm font-medium ${
                ibkrStatus?.authenticated
                  ? 'border-green-300 bg-green-50 text-green-700 dark:border-green-700 dark:bg-green-900/20 dark:text-green-400'
                  : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isCheckingIBKR ? (
                <>
                  <svg
                    className="mr-2 h-4 w-4 animate-spin"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Checking...
                </>
              ) : ibkrStatus?.authenticated ? (
                <>
                  <svg
                    className="mr-2 h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  IBKR Connected
                </>
              ) : (
                <>
                  Connect IBKR Account
                  {ibkrStatus && !ibkrStatus.connected && (
                    <span className="ml-2 rounded bg-yellow-100 px-2 py-0.5 text-xs text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400">
                      Gateway Offline
                    </span>
                  )}
                </>
              )}
            </button>
            <button
              onClick={() => setIsRebalanceModalOpen(true)}
              disabled={!selectedPortfolioId}
              className="inline-flex items-center rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
            >
              Rebalance Portfolio
            </button>
          </div>
        </div>
      </main>

      {/* Rebalance Modal */}
      {selectedPortfolioId && (
        <RebalanceModal
          portfolioId={selectedPortfolioId}
          isOpen={isRebalanceModalOpen}
          onClose={() => setIsRebalanceModalOpen(false)}
          onRebalanced={loadPies}
        />
      )}
    </div>
  );
}
