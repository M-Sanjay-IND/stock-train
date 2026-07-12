// TypeScript interfaces for all API responses and data structures

// --- Stock Data ---
export interface StockInfo {
  ticker: string;
  name: string;
  exchange: string;
  sector: string;
  industry: string;
  market_cap: number | null;
  current_price: number | null;
  currency: string;
  previous_close: number | null;
  day_high: number | null;
  day_low: number | null;
  fifty_two_week_high: number | null;
  fifty_two_week_low: number | null;
  average_volume: number | null;
  pe_ratio: number | null;
  dividend_yield: number | null;
  beta: number | null;
  last_updated: string;
}

export interface StockHistory {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface SearchResult {
  ticker: string;
  name: string;
}

// --- Technical Indicators ---
export interface TechnicalLatest {
  date: string;
  close: number;
  sma_20: number | null;
  sma_50: number | null;
  ema_20: number | null;
  ema_50: number | null;
  rsi: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  bb_upper: number | null;
  bb_middle: number | null;
  bb_lower: number | null;
  bb_width: number | null;
  atr: number | null;
  momentum: number | null;
  daily_return: number | null;
  volatility: number | null;
}

export interface TechnicalSeries {
  date: string;
  close: number;
  open: number;
  high: number;
  low: number;
  volume: number;
  sma_20: number | null;
  sma_50: number | null;
  ema_20: number | null;
  ema_50: number | null;
  rsi: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  bb_upper: number | null;
  bb_middle: number | null;
  bb_lower: number | null;
  atr: number | null;
  [key: string]: number | string | null;
}

// --- Analytics ---
export interface Analytics {
  current_price: number;
  previous_close: number;
  price_change: number;
  price_change_pct: number;
  daily_return: number | null;
  monthly_return: number | null;
  annual_return: number | null;
  cagr: number | null;
  volatility: number | null;
  sharpe_ratio: number | null;
  sortino_ratio: number | null;
  max_drawdown: number | null;
  avg_daily_volume: number | null;
  avg_volume_10d: number | null;
  fifty_two_week_high: number;
  fifty_two_week_low: number;
  total_trading_days: number;
  crossovers: Crossover[];
}

export interface Crossover {
  type: string;
  description: string;
  date?: string;
}

// --- Forecast ---
export interface ForecastDay {
  days: number;
  predicted_price: number;
  current_price: number;
  change_pct: number;
  trend: 'bullish' | 'bearish';
  confidence_upper: number;
  confidence_lower: number;
  daily_predictions?: number[];
}

export interface ActualVsPredicted {
  date: string;
  actual: number;
  predicted: number;
}

export interface ModelMetrics {
  rmse: number | null;
  mae: number | null;
  mape: number | null;
  r2_score: number | null;
}

export interface TrainedModelInfo {
  id: number;
  ticker: string;
  model_type: string;
  rmse: number | null;
  mae: number | null;
  mape: number | null;
  r2_score: number | null;
  trained_at: string | null;
  training_loss: number[] | null;
  validation_loss: number[] | null;
}

export interface ForecastResponse {
  ticker: string;
  model_type: string;
  current_price: number;
  forecasts: Record<string, ForecastDay>;
  actual_vs_predicted: ActualVsPredicted[];
  metrics: ModelMetrics;
  all_models: TrainedModelInfo[];
  training_loss?: number[];
  validation_loss?: number[];
  trained_at: string | null;
  error?: string;
}

export interface TrainingResult {
  ticker: string;
  data_points: number;
  train_size: number;
  test_size: number;
  features_count: number;
  models: Record<string, any>;
  comparison: ModelMetrics[];
  best_model: string | null;
  error?: string;
}

// --- Watchlist ---
export interface WatchlistEntry {
  id: number;
  ticker: string;
  added_at: string;
  notes: string;
  stock?: StockInfo;
}

// --- UI State ---
export type ThemeMode = 'dark' | 'light';

export interface AppState {
  selectedTicker: string | null;
  recentSearches: string[];
  theme: ThemeMode;
}
