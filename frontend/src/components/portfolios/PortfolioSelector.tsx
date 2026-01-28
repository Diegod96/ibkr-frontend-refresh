'use client';

import { useEffect, useState } from 'react';
import type { Portfolio } from '@/types';
import * as portfolioApi from '@/services/portfolioApi';

export function PortfolioSelector({
  value,
  onChange,
}: {
  value?: string | null;
  onChange: (id: string) => void;
}) {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const data = await portfolioApi.getPortfolios();
        if (mounted) setPortfolios(data);
      } catch (e) {
        // ignore for now
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, []);

  if (loading) return <div>Loading portfolios...</div>;

  return (
    <select
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      className="rounded border px-2 py-1"
    >
      <option value="">Select portfolio</option>
      {portfolios.map((p) => (
        <option key={p.id} value={p.id}>
          {p.name}
        </option>
      ))}
    </select>
  );
}
