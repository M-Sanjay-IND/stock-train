import { useState, useEffect, useCallback } from 'react';
import { getStockInfo, getHistory, getTechnical, getAnalytics } from '../lib/api';
import type { StockInfo, StockHistory, TechnicalLatest, TechnicalSeries, Analytics } from '../types';
import { useStockContext } from '../context/StockContext';

interface UseStockReturn {
  info: StockInfo | null;
  history: StockHistory[];
  technical: { latest: TechnicalLatest | null; series: TechnicalSeries[] };
  analytics: Analytics | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useStock(ticker: string | null): UseStockReturn {
  const [info, setInfo] = useState<StockInfo | null>(null);
  const [history, setHistory] = useState<StockHistory[]>([]);
  const [technical, setTechnical] = useState<{ latest: TechnicalLatest | null; series: TechnicalSeries[] }>({ latest: null, series: [] });
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { addRecentSearch } = useStockContext();

  const fetchData = useCallback(async () => {
    if (!ticker) return;

    setLoading(true);
    setError(null);

    try {
      const [infoRes, historyRes, techRes, analyticsRes] = await Promise.allSettled([
        getStockInfo(ticker),
        getHistory(ticker),
        getTechnical(ticker),
        getAnalytics(ticker),
      ]);

      if (infoRes.status === 'fulfilled') setInfo(infoRes.value);
      if (historyRes.status === 'fulfilled') setHistory(historyRes.value);
      if (techRes.status === 'fulfilled') setTechnical(techRes.value);
      if (analyticsRes.status === 'fulfilled') setAnalytics(analyticsRes.value.analytics);

      addRecentSearch(ticker.toUpperCase());
    } catch (err: any) {
      setError(err.message || 'Failed to fetch stock data');
    } finally {
      setLoading(false);
    }
  }, [ticker, addRecentSearch]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { info, history, technical, analytics, loading, error, refetch: fetchData };
}
