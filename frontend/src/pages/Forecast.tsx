import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Brain, TrendingUp, TrendingDown, RefreshCw, Loader2, Zap } from 'lucide-react';
import { useStockContext } from '../context/StockContext';
import { getForecast, trainModels } from '../lib/api';
import type { ForecastResponse } from '../types';
import ForecastChart from '../components/charts/ForecastChart';
import TrainingChart from '../components/charts/TrainingChart';
import MetricCard from '../components/ui/MetricCard';
import { ChartSkeleton, CardSkeleton } from '../components/ui/Skeleton';
import { formatCurrency, formatPercentRaw, cn, timeAgo } from '../lib/utils';

const Forecast: React.FC = () => {
  const [searchParams] = useSearchParams();
  const tickerParam = searchParams.get('ticker');
  const { selectedTicker, setSelectedTicker } = useStockContext();
  const ticker = tickerParam || selectedTicker || 'AAPL';

  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset selected model when ticker changes
  useEffect(() => {
    setSelectedModel(undefined);
  }, [ticker]);

  useEffect(() => {
    if (tickerParam) setSelectedTicker(tickerParam);
  }, [tickerParam, setSelectedTicker]);

  useEffect(() => {
    const fetchForecast = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getForecast(ticker, selectedModel);
        if (data.error) {
          setError(data.error);
        } else {
          setForecast(data);
        }
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchForecast();
  }, [ticker, selectedModel]);

  const handleRetrain = async () => {
    setTraining(true);
    try {
      await trainModels(ticker);
      const data = await getForecast(ticker, selectedModel);
      setForecast(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setTraining(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <CardSkeleton key={i} />)}
        </div>
        <ChartSkeleton />
      </div>
    );
  }

  if (error && !forecast) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <Brain className="w-12 h-12 text-muted-foreground" />
        <h2 className="text-xl font-semibold">Forecast Unavailable</h2>
        <p className="text-muted-foreground text-center max-w-md">{error}</p>
        <button
          onClick={handleRetrain}
          disabled={training}
          className="flex items-center gap-2 px-4 py-2 rounded-lg gradient-primary text-white text-sm font-medium"
        >
          {training ? <Loader2 className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
          {training ? 'Training Models...' : 'Train Models'}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">ML Forecast</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {ticker} · Model: <span className="text-primary font-medium">{forecast?.model_type || '—'}</span>
            {forecast?.trained_at && <span className="ml-2">· Trained {timeAgo(forecast.trained_at)}</span>}
          </p>
        </div>
        <button
          onClick={handleRetrain}
          disabled={training}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-secondary hover:bg-accent text-sm font-medium transition-colors disabled:opacity-50"
        >
          {training ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          {training ? 'Retraining...' : 'Retrain Models'}
        </button>
      </motion.div>

      {/* Forecast Cards */}
      {forecast?.forecasts && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(['1_day', '7_day', '30_day'] as const).map((key, i) => {
            const f = forecast.forecasts[key];
            if (!f) return null;
            const isUp = f.trend === 'bullish';
            return (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className={cn('glass-card p-6 border-l-4', isUp ? 'border-l-emerald-500' : 'border-l-red-500')}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="stat-label">{f.days}-Day Forecast</span>
                  {isUp ? (
                    <TrendingUp className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <TrendingDown className="w-5 h-5 text-red-400" />
                  )}
                </div>
                <p className="stat-value">{formatCurrency(f.predicted_price)}</p>
                <p className={cn('text-sm font-medium mt-1', isUp ? 'text-emerald-400' : 'text-red-400')}>
                  {formatPercentRaw(f.change_pct)} · {f.trend.toUpperCase()}
                </p>
                <div className="mt-3 pt-3 border-t border-border/50 text-xs text-muted-foreground space-y-1">
                  <p>Range: {formatCurrency(f.confidence_lower)} – {formatCurrency(f.confidence_upper)}</p>
                  <p>Current: {formatCurrency(f.current_price)}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Actual vs Predicted Chart */}
      {forecast?.actual_vs_predicted && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-foreground mb-4">Actual vs Predicted</h3>
          <ForecastChart
            actualVsPredicted={forecast.actual_vs_predicted}
            forecasts={forecast.forecasts}
          />
        </motion.div>
      )}

      {/* Model Comparison */}
      {forecast?.all_models && forecast.all_models.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-foreground mb-4">Model Comparison</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-muted-foreground font-medium">Model</th>
                  <th className="text-right py-3 px-4 text-muted-foreground font-medium">RMSE</th>
                  <th className="text-right py-3 px-4 text-muted-foreground font-medium">MAE</th>
                  <th className="text-right py-3 px-4 text-muted-foreground font-medium">MAPE (%)</th>
                  <th className="text-right py-3 px-4 text-muted-foreground font-medium">R² Score</th>
                  <th className="text-right py-3 px-4 text-muted-foreground font-medium">Trained</th>
                </tr>
              </thead>
              <tbody>
                {forecast.all_models.map((m) => (
                  <tr
                    key={m.model_type}
                    onClick={() => {
                      if (m.model_type !== forecast.model_type) {
                        setSelectedModel(m.model_type);
                      }
                    }}
                    className={cn(
                      'border-b border-border/50 hover:bg-accent/30 transition-colors cursor-pointer',
                      m.model_type === forecast.model_type && 'bg-primary/5'
                    )}
                  >
                    <td className="py-3 px-4 font-medium text-foreground flex items-center gap-2">
                      {m.model_type === forecast.model_type && (
                        <Zap className="w-3.5 h-3.5 text-primary" />
                      )}
                      {m.model_type.replace('_', ' ').toUpperCase()}
                    </td>
                    <td className="text-right py-3 px-4 font-mono text-foreground">{m.rmse?.toFixed(4) ?? '—'}</td>
                    <td className="text-right py-3 px-4 font-mono text-foreground">{m.mae?.toFixed(4) ?? '—'}</td>
                    <td className="text-right py-3 px-4 font-mono text-foreground">{m.mape?.toFixed(2) ?? '—'}</td>
                    <td className="text-right py-3 px-4 font-mono text-foreground">{m.r2_score?.toFixed(4) ?? '—'}</td>
                    <td className="text-right py-3 px-4 text-muted-foreground text-xs">{m.trained_at ? timeAgo(m.trained_at) : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* Training Loss */}
      {(forecast?.training_loss || forecast?.all_models?.find(m => m.model_type === 'lstm')?.training_loss) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-foreground mb-4">LSTM Training Progress</h3>
          <TrainingChart
            trainingLoss={forecast?.training_loss || forecast?.all_models?.find(m => m.model_type === 'lstm')?.training_loss || null}
            validationLoss={forecast?.validation_loss || forecast?.all_models?.find(m => m.model_type === 'lstm')?.validation_loss || null}
          />
        </motion.div>
      )}

      {/* Metrics Summary */}
      {forecast?.metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard label="RMSE" value={forecast.metrics.rmse?.toFixed(4) ?? '—'} delay={0} />
          <MetricCard label="MAE" value={forecast.metrics.mae?.toFixed(4) ?? '—'} delay={1} />
          <MetricCard label="MAPE" value={forecast.metrics.mape ? `${forecast.metrics.mape.toFixed(2)}%` : '—'} delay={2} />
          <MetricCard label="R² Score" value={forecast.metrics.r2_score?.toFixed(4) ?? '—'} delay={3} />
        </div>
      )}
    </div>
  );
};

export default Forecast;
