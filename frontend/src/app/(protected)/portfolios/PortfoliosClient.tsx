/**
 * Portfolios Client Component
 *
 * Client-side component for managing pies and slices.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/Button';
import { PieCard, PieFormModal, SliceFormModal } from '@/components/pies';
import { PortfolioSelector } from '@/components/portfolios/PortfolioSelector';
import type { Pie, Slice, CreatePieData, UpdatePieData, CreateSliceData, UpdateSliceData } from '@/types/pie';
import * as pieApi from '@/services/pieApi';

export function PortfoliosClient() {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string | null>(null);
  const [pies, setPies] = useState<Pie[]>([]);
  const [totalAllocation, setTotalAllocation] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal states
  const [isPieModalOpen, setIsPieModalOpen] = useState(false);
  const [isSliceModalOpen, setIsSliceModalOpen] = useState(false);
  const [editingPie, setEditingPie] = useState<Pie | null>(null);
  const [editingSlice, setEditingSlice] = useState<Slice | null>(null);
  const [activePieId, setActivePieId] = useState<string | null>(null);

  // Load pies on mount
  const loadPies = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await pieApi.getPies(false, selectedPortfolioId ?? undefined);
      setPies(response.pies);
      setTotalAllocation(response.total_allocation);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load pies');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPies();
  }, [loadPies, selectedPortfolioId]);

  // Pie handlers
  const handleCreatePie = () => {
    setEditingPie(null);
    setIsPieModalOpen(true);
  };

  const handleEditPie = (pie: Pie) => {
    setEditingPie(pie);
    setIsPieModalOpen(true);
  };

  const handlePieSubmit = async (data: CreatePieData | UpdatePieData) => {
    if (editingPie) {
      await pieApi.updatePie(editingPie.id, data as UpdatePieData);
    } else {
      await pieApi.createPie(data as CreatePieData);
    }
    await loadPies();
  };

  const handleDeletePie = async (pieId: string) => {
    try {
      await pieApi.deletePie(pieId);
      await loadPies();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete pie');
    }
  };

  // Slice handlers
  const handleAddSlice = (pieId: string) => {
    setActivePieId(pieId);
    setEditingSlice(null);
    setIsSliceModalOpen(true);
  };

  const handleEditSlice = (pieId: string, sliceId: string) => {
    const pie = pies.find((p) => p.id === pieId);
    const slice = pie?.slices.find((s) => s.id === sliceId);
    if (slice) {
      setActivePieId(pieId);
      setEditingSlice(slice);
      setIsSliceModalOpen(true);
    }
  };

  const handleSliceSubmit = async (data: CreateSliceData | UpdateSliceData) => {
    if (!activePieId) return;

    if (editingSlice) {
      await pieApi.updateSlice(activePieId, editingSlice.id, data as UpdateSliceData);
    } else {
      await pieApi.createSlice(activePieId, data as CreateSliceData);
    }
    await loadPies();
  };

  const handleDeleteSlice = async (pieId: string, sliceId: string) => {
    try {
      await pieApi.deleteSlice(pieId, sliceId);
      await loadPies();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete slice');
    }
  };

  // Get current total weight for the active pie
  const getActivePieTotalWeight = () => {
    if (!activePieId) return 0;
    const pie = pies.find((p) => p.id === activePieId);
    return pie?.total_slice_weight || 0;
  };

  if (isLoading) {
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
        {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Portfolios
              </h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                Manage your portfolio pies and slices
              </p>
            </div>
           <div className="flex items-center space-x-4">
             <PortfolioSelector
               value={selectedPortfolioId}
               onChange={(id) => setSelectedPortfolioId(id)}
             />
             <Button onClick={handleCreatePie}>
              <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Pie
            </Button>
          </div>
          </div>

        {/* Allocation summary */}
        <div className="mb-6 rounded-lg border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Allocation
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {totalAllocation}%
              </p>
            </div>
            <div className="w-48">
              <div className="h-3 bg-gray-200 rounded-full dark:bg-gray-700">
                <div
                  className={`h-3 rounded-full transition-all ${
                    totalAllocation > 100
                      ? 'bg-red-500'
                      : totalAllocation === 100
                      ? 'bg-green-500'
                      : 'bg-primary-500'
                  }`}
                  style={{ width: `${Math.min(totalAllocation, 100)}%` }}
                />
              </div>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 text-right">
                {100 - totalAllocation}% remaining
              </p>
            </div>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400">
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-2 text-red-500 hover:text-red-700"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Pies list */}
        {pies.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"
              />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900 dark:text-white">
              No pies yet
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Create your first pie to start organizing your portfolio.
            </p>
            <div className="mt-6">
              <Button onClick={handleCreatePie}>
                <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create Your First Pie
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {pies.map((pie) => (
              <PieCard
                key={pie.id}
                pie={pie}
                onEdit={handleEditPie}
                onDelete={handleDeletePie}
                onAddSlice={handleAddSlice}
                onEditSlice={handleEditSlice}
                onDeleteSlice={handleDeleteSlice}
              />
            ))}
          </div>
        )}

        {/* Modals */}
        <PieFormModal
          isOpen={isPieModalOpen}
          onClose={() => setIsPieModalOpen(false)}
          onSubmit={handlePieSubmit}
          pie={editingPie}
          currentTotalAllocation={totalAllocation}
        />

        <SliceFormModal
          isOpen={isSliceModalOpen}
          onClose={() => {
            setIsSliceModalOpen(false);
            setActivePieId(null);
          }}
          onSubmit={handleSliceSubmit}
          slice={editingSlice}
          currentTotalWeight={getActivePieTotalWeight()}
        />
      </main>
    </div>
  );
}
