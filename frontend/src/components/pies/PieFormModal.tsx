/**
 * Pie Form Modal Component
 *
 * Modal dialog for creating and editing pies.
 */

'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import type { Pie, CreatePieData, UpdatePieData } from '@/types/pie';
import { PIE_COLORS } from '@/types/pie';

interface PieFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreatePieData | UpdatePieData) => Promise<void>;
  pie?: Pie | null;
  currentTotalAllocation: number;
}

export function PieFormModal({
  isOpen,
  onClose,
  onSubmit,
  pie,
  currentTotalAllocation,
}: PieFormModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [color, setColor] = useState(PIE_COLORS[0]);
  const [targetAllocation, setTargetAllocation] = useState('0');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditing = !!pie;

  // Calculate max allocation allowed
  const existingAllocation = pie?.target_allocation || 0;
  const maxAllocation = 100 - currentTotalAllocation + existingAllocation;

  useEffect(() => {
    if (pie) {
      setName(pie.name);
      setDescription(pie.description || '');
      setColor(pie.color);
      setTargetAllocation(pie.target_allocation.toString());
    } else {
      setName('');
      setDescription('');
      setColor(PIE_COLORS[Math.floor(Math.random() * PIE_COLORS.length)]);
      setTargetAllocation('0');
    }
    setError(null);
  }, [pie, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const allocation = parseFloat(targetAllocation) || 0;

    if (allocation > maxAllocation) {
      setError(`Allocation cannot exceed ${maxAllocation}%`);
      setIsLoading(false);
      return;
    }

    try {
      await onSubmit({
        name,
        description: description || undefined,
        color,
        target_allocation: allocation,
        // parent component (PortfoliosClient) will inject selected portfolio id if needed
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md mx-4 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          {isEditing ? 'Edit Pie' : 'Create New Pie'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          <Input
            label="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Tech Growth"
            required
            maxLength={100}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description (optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the theme or strategy of this pie..."
              rows={3}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Color
            </label>
            <div className="flex flex-wrap gap-2">
              {PIE_COLORS.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => setColor(c)}
                  className={`h-8 w-8 rounded-full transition-all ${
                    color === c
                      ? 'ring-2 ring-offset-2 ring-primary-500'
                      : 'hover:scale-110'
                  }`}
                  style={{ backgroundColor: c }}
                />
              ))}
            </div>
          </div>

          <Input
            label={`Target Allocation (max ${maxAllocation.toFixed(0)}%)`}
            type="number"
            value={targetAllocation}
            onChange={(e) => setTargetAllocation(e.target.value)}
            min={0}
            max={maxAllocation}
            step={0.01}
            helperText={`${currentTotalAllocation}% currently allocated across all pies`}
          />

          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" isLoading={isLoading}>
              {isEditing ? 'Save Changes' : 'Create Pie'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
