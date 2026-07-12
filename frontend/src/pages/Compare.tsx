import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { GitCompare, Loader2, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';
import { getStockInfo, getAnalytics } from '../lib/api';
import type { StockInfo, Analytics } from '../types';
import { formatCurrency, formatPercent, formatLargeNumber, cn, getPriceColor } from '../lib/utils';

const Compare: React.FC = () => {
  const [tickers, setTickers] = useState<string[]>(['', '', '']);
  const [stocks, setStocks] = useState<(StockInfo | null)[]>([null, null, null]);
  const [analytics, setAnalytics] = useState<(Analytics | null)[]>([null, null, null]);
  const [loading, setLoading] = useState(false);

  const updateTicker = (i: number, val: string) => {
    const updated = [...tickers];
    updated[i] = val.toUpperCase();
    setTickers(updated);
  };

  const handleCompare = async () => {
    const validTickers = tickers.filter(t => t.trim());
    if (validTickers.length < 2) return;

    setLoading(true);
    try {
      const results = await Promise.allSettled(
        tickers.map(async (t, i) => {
          if (!t.trim()) return { info: null, analytics: null };
          const [info, analyticsData] = await Promise.all([
            getStockInfo(t),
            getAnalytics(t),
          ]);
          return { info, analytics: analyticsData.analytics };
        })
      );

      setStocks(results.map(r => r.status === 'fulfilled' ? r.value.info : null));
      setAnalytics(results.map(r => r.status === 'fulfilled' ? r.value.analytics : null));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const metrics = [
    { label: 'Current Price', key: 'current_price', format: formatCurrency },
    { label: 'Daily Return', key: 'daily_return', format: (v: any) => formatPercent(v) },
    { label: 'Monthly Return', key: 'monthly_return', format: (v: any) => formatPercent(v) },
    { label: 'Annual Return', key: 'annual_return', format: (v: any) => formatPercent(v) },
    { label: 'CAGR', key: 'cagr', format: (v: any) => formatPercent(v) },
    { label: 'Volatility', key: 'volatility', format: (v: any) => v !== null ? `${(v * 100).toFixed(2)}%` : '—' },
    { label: 'Sharpe Ratio', key: 'sharpe_ratio', format: (v: any) => v?.toFixed(3) ?? '—' },
    { label: 'Sortino Ratio', key: 'sortino_ratio', format: (v: any) => v?.toFixed(3) ?? '—' },
    { label: 'Max Drawdown', key: 'max_drawdown', format: (v: any) => v !== null ? `${(v * 100).toFixed(2)}%` : '—' },
    { label: '52W High', key: 'fifty_two_week_high', format: formatCurrency },
    { label: '52W Low', key: 'fifty_two_week_low', format: formatCurrency },
  ];

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <GitCompare className="w-6 h-6 text-primary" /> Stock Comparison
        </h1>
        <p className="text-sm text-muted-foreground mt-1">Compare up to 3 stocks side by side</p>
      </motion.div>

      {/* Input */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6"
      >
        <div className="flex flex-wrap items-end gap-4">
          {tickers.map((t, i) => (
            <div key={i}>
              <label className="text-xs text-muted-foreground mb-1 block">Stock {i + 1}</label>
              <input
                type="text"
                value={t}
                onChange={(e) => updateTicker(i, e.target.value)}
                placeholder={['AAPL', 'MSFT', 'GOOGL'][i]}
                className="w-32 h-10 px-3 rounded-lg bg-secondary border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
          ))}
          <button
            onClick={handleCompare}
            disabled={loading || tickers.filter(t => t.trim()).length < 2}
            className="h-10 px-5 rounded-lg gradient-primary text-white text-sm font-medium flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
            Compare
          </button>
        </div>
      </motion.div>

      {/* Comparison Table */}
      {stocks.some(s => s !== null) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 overflow-x-auto"
        >
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 text-muted-foreground font-medium">Metric</th>
                {stocks.map((s, i) => s && (
                  <th key={i} className="text-right py-3 px-4 text-foreground font-semibold">
                    {tickers[i]}
                    <span className="block text-xs text-muted-foreground font-normal">{s.name}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {metrics.map(({ label, key, format }) => (
                <tr key={key} className="border-b border-border/50 hover:bg-accent/30 transition-colors">
                  <td className="py-3 px-4 text-muted-foreground">{label}</td>
                  {analytics.map((a, i) => stocks[i] && (
                    <td key={i} className="text-right py-3 px-4 font-mono text-foreground">
                      {a ? format((a as any)[key]) : '—'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </motion.div>
      )}
    </div>
  );
};

export default Compare;
