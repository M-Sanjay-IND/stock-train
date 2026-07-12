import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  DollarSign, TrendingUp, TrendingDown, BarChart3, Activity, Clock,
  ArrowUpRight, ArrowDownRight,
} from 'lucide-react';
import { useStock } from '../hooks/useStock';
import { useStockContext } from '../context/StockContext';
import MetricCard from '../components/ui/MetricCard';
import PriceChart from '../components/charts/PriceChart';
import CandlestickChart from '../components/charts/CandlestickChart';
import VolumeChart from '../components/charts/VolumeChart';
import TechnicalChart from '../components/charts/TechnicalChart';
import ExportButtons from '../components/ui/ExportButtons';
import { CardSkeleton, ChartSkeleton } from '../components/ui/Skeleton';
import {
  formatCurrency, formatLargeNumber, formatPercentRaw, formatVolume, cn, getPriceColor
} from '../lib/utils';

const Dashboard: React.FC = () => {
  const [searchParams] = useSearchParams();
  const tickerParam = searchParams.get('ticker');
  const { selectedTicker, setSelectedTicker } = useStockContext();

  const ticker = tickerParam || selectedTicker || 'AAPL';

  useEffect(() => {
    if (tickerParam) setSelectedTicker(tickerParam);
  }, [tickerParam, setSelectedTicker]);

  const { info, history, technical, analytics, loading, error } = useStock(ticker);

  const priceChange = analytics?.price_change ?? 0;
  const priceChangePct = analytics?.price_change_pct ?? 0;
  const isPositive = priceChange >= 0;

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => <CardSkeleton key={i} />)}
        </div>
        <ChartSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <Activity className="w-12 h-12 text-muted-foreground" />
        <h2 className="text-xl font-semibold">Error Loading Data</h2>
        <p className="text-muted-foreground">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stock Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between flex-wrap gap-4"
      >
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-foreground">{ticker}</h1>
            <span className={cn(
              'px-2.5 py-1 rounded-full text-xs font-semibold',
              isPositive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
            )}>
              {isPositive ? <ArrowUpRight className="inline w-3 h-3 mr-0.5" /> : <ArrowDownRight className="inline w-3 h-3 mr-0.5" />}
              {formatPercentRaw(priceChangePct)}
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1">{info?.name || ticker}</p>
        </div>

        <div className="text-right">
          <p className="text-3xl font-bold text-foreground">{formatCurrency(info?.current_price)}</p>
          <p className={cn('text-sm font-medium', getPriceColor(priceChange))}>
            {priceChange >= 0 ? '+' : ''}{priceChange?.toFixed(2)} ({formatPercentRaw(priceChangePct)})
          </p>
        </div>
      </motion.div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Market Cap" value={formatLargeNumber(info?.market_cap ?? null)} icon={DollarSign} delay={0} />
        <MetricCard label="Volume" value={formatVolume(analytics?.avg_daily_volume ?? null)} icon={BarChart3} delay={1} />
        <MetricCard label="52W High" value={formatCurrency(analytics?.fifty_two_week_high ?? null)} icon={TrendingUp} delay={2} />
        <MetricCard label="52W Low" value={formatCurrency(analytics?.fifty_two_week_low ?? null)} icon={TrendingDown} delay={3} />
        <MetricCard label="Volatility" value={analytics?.volatility ? `${(analytics.volatility * 100).toFixed(1)}%` : '—'} icon={Activity} delay={4} />
        <MetricCard label="Sharpe Ratio" value={analytics?.sharpe_ratio?.toFixed(2) ?? '—'} icon={Activity} delay={5} />
        <MetricCard label="Max Drawdown" value={analytics?.max_drawdown ? `${(analytics.max_drawdown * 100).toFixed(1)}%` : '—'} icon={TrendingDown} delay={6} />
        <MetricCard label="CAGR" value={analytics?.cagr ? `${(analytics.cagr * 100).toFixed(1)}%` : '—'} icon={TrendingUp} delay={7} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Price Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-foreground">Price History</h3>
            <ExportButtons data={history} filename={`${ticker}_history`} />
          </div>
          <PriceChart data={history} />
        </motion.div>

        {/* Candlestick */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-foreground mb-4">Candlestick Chart</h3>
          <CandlestickChart data={history} />
        </motion.div>
      </div>

      {/* Volume */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-card p-6"
      >
        <h3 className="text-lg font-semibold text-foreground mb-4">Volume</h3>
        <VolumeChart data={history} />
      </motion.div>

      {/* Technical Indicators */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="glass-card p-6"
      >
        <h3 className="text-lg font-semibold text-foreground mb-4">Technical Indicators</h3>
        <TechnicalChart data={technical.series} />
      </motion.div>

      {/* Technical Snapshot */}
      {technical.latest && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-foreground mb-4">Indicator Snapshot</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {[
              { label: 'RSI', value: technical.latest.rsi?.toFixed(1) },
              { label: 'MACD', value: technical.latest.macd?.toFixed(4) },
              { label: 'SMA 20', value: technical.latest.sma_20?.toFixed(2) },
              { label: 'SMA 50', value: technical.latest.sma_50?.toFixed(2) },
              { label: 'EMA 20', value: technical.latest.ema_20?.toFixed(2) },
              { label: 'ATR', value: technical.latest.atr?.toFixed(2) },
              { label: 'BB Upper', value: technical.latest.bb_upper?.toFixed(2) },
              { label: 'BB Lower', value: technical.latest.bb_lower?.toFixed(2) },
              { label: 'Momentum', value: technical.latest.momentum?.toFixed(2) },
              { label: 'Volatility', value: technical.latest.volatility ? (technical.latest.volatility * 100).toFixed(2) + '%' : '—' },
            ].map(({ label, value }) => (
              <div key={label} className="p-3 rounded-lg bg-secondary/30">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{label}</p>
                <p className="text-sm font-semibold text-foreground mt-0.5">{value ?? '—'}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Dashboard;
