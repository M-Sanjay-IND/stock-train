import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, TrendingDown, Percent, Activity, ShieldCheck } from 'lucide-react';
import { useStock } from '../hooks/useStock';
import { useStockContext } from '../context/StockContext';
import MetricCard from '../components/ui/MetricCard';
import { CardSkeleton } from '../components/ui/Skeleton';
import { formatCurrency, formatPercent, cn } from '../lib/utils';

const Analytics: React.FC = () => {
  const [searchParams] = useSearchParams();
  const tickerParam = searchParams.get('ticker');
  const { selectedTicker, setSelectedTicker } = useStockContext();
  const ticker = tickerParam || selectedTicker || 'AAPL';

  useEffect(() => {
    if (tickerParam) setSelectedTicker(tickerParam);
  }, [tickerParam, setSelectedTicker]);

  const { info, analytics, loading, error } = useStock(ticker);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {[...Array(12)].map((_, i) => <CardSkeleton key={i} />)}
        </div>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <BarChart3 className="w-12 h-12 text-muted-foreground" />
        <h2 className="text-xl font-semibold">No analytics data</h2>
        <p className="text-muted-foreground">Search for a stock to view analytics.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-2xl font-bold text-foreground">Financial Analytics</h1>
        <p className="text-sm text-muted-foreground mt-1">{info?.name || ticker} ({ticker})</p>
      </motion.div>

      {/* Returns */}
      <div>
        <h2 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
          <Percent className="w-5 h-5 text-primary" /> Returns
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            label="Daily Return"
            value={analytics.daily_return !== null ? formatPercent(analytics.daily_return) : '—'}
            change={analytics.daily_return ? analytics.daily_return * 100 : null}
            delay={0}
          />
          <MetricCard
            label="Monthly Return"
            value={analytics.monthly_return !== null ? formatPercent(analytics.monthly_return) : '—'}
            change={analytics.monthly_return ? analytics.monthly_return * 100 : null}
            delay={1}
          />
          <MetricCard
            label="Annual Return"
            value={analytics.annual_return !== null ? formatPercent(analytics.annual_return) : '—'}
            change={analytics.annual_return ? analytics.annual_return * 100 : null}
            delay={2}
          />
          <MetricCard
            label="CAGR"
            value={analytics.cagr !== null ? formatPercent(analytics.cagr) : '—'}
            icon={TrendingUp}
            delay={3}
          />
        </div>
      </div>

      {/* Risk Metrics */}
      <div>
        <h2 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-primary" /> Risk Metrics
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard label="Volatility" value={analytics.volatility !== null ? `${(analytics.volatility * 100).toFixed(2)}%` : '—'} icon={Activity} delay={4} />
          <MetricCard label="Sharpe Ratio" value={analytics.sharpe_ratio?.toFixed(3) ?? '—'} delay={5} />
          <MetricCard label="Sortino Ratio" value={analytics.sortino_ratio?.toFixed(3) ?? '—'} delay={6} />
          <MetricCard label="Max Drawdown" value={analytics.max_drawdown !== null ? `${(analytics.max_drawdown * 100).toFixed(2)}%` : '—'} icon={TrendingDown} delay={7} />
        </div>
      </div>

      {/* Price Info */}
      <div>
        <h2 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-primary" /> Price Overview
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard label="Current Price" value={formatCurrency(analytics.current_price)} delay={8} />
          <MetricCard label="Previous Close" value={formatCurrency(analytics.previous_close)} delay={9} />
          <MetricCard label="52W High" value={formatCurrency(analytics.fifty_two_week_high)} icon={TrendingUp} delay={10} />
          <MetricCard label="52W Low" value={formatCurrency(analytics.fifty_two_week_low)} icon={TrendingDown} delay={11} />
        </div>
      </div>

      {/* Crossovers */}
      {analytics.crossovers.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6"
        >
          <h2 className="text-lg font-semibold text-foreground mb-4">Moving Average Signals</h2>
          <div className="space-y-3">
            {analytics.crossovers.map((c, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-secondary/30">
                <div className={cn(
                  'w-2 h-2 rounded-full',
                  c.type.includes('bullish') || c.type === 'golden_cross' ? 'bg-emerald-400' : 'bg-red-400'
                )} />
                <p className="text-sm text-foreground">{c.description}</p>
                {c.date && <span className="text-xs text-muted-foreground ml-auto">{c.date}</span>}
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Analytics;
