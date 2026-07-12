import axios from 'axios';
import type {
  StockInfo,
  StockHistory,
  SearchResult,
  TechnicalLatest,
  TechnicalSeries,
  Analytics,
  ForecastResponse,
  TrainingResult,
  TrainedModelInfo,
  WatchlistEntry,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 min for training
  headers: { 'Content-Type': 'application/json' },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.error || error.message || 'An error occurred';
    console.error('[API Error]', message);
    return Promise.reject(new Error(message));
  }
);

// --- Health ---
export const checkHealth = () => api.get('/health');

// --- Stock Search & Info ---
export const searchStocks = async (query: string): Promise<SearchResult[]> => {
  const { data } = await api.get(`/stocks/search?q=${encodeURIComponent(query)}`);
  return data.results;
};

export const getStockInfo = async (ticker: string): Promise<StockInfo> => {
  const { data } = await api.get(`/stocks/info/${ticker}`);
  return data.data;
};

// --- History ---
export const getHistory = async (ticker: string, period = '2y'): Promise<StockHistory[]> => {
  const { data } = await api.get(`/history/${ticker}?period=${period}`);
  return data.data;
};

// --- Technical ---
export const getTechnical = async (
  ticker: string,
  limit = 200
): Promise<{ latest: TechnicalLatest; series: TechnicalSeries[] }> => {
  const { data } = await api.get(`/technical/${ticker}?limit=${limit}`);
  return { latest: data.latest, series: data.series };
};

// --- Analytics ---
export const getAnalytics = async (
  ticker: string
): Promise<{ analytics: Analytics; info: StockInfo }> => {
  const { data } = await api.get(`/analytics/${ticker}`);
  return { analytics: data.analytics, info: data.info };
};

// --- Forecast ---
export const getForecast = async (ticker: string): Promise<ForecastResponse> => {
  const { data } = await api.get(`/forecast/${ticker}`);
  return data;
};

export const trainModels = async (ticker: string): Promise<TrainingResult> => {
  const { data } = await api.post(`/train/${ticker}`);
  return data;
};

export const getMetrics = async (
  ticker: string
): Promise<{ best_model: string | null; models: TrainedModelInfo[] }> => {
  const { data } = await api.get(`/metrics/${ticker}`);
  return { best_model: data.best_model, models: data.models };
};

// --- Watchlist ---
export const getWatchlist = async (): Promise<WatchlistEntry[]> => {
  const { data } = await api.get('/watchlist');
  return data.watchlist;
};

export const addToWatchlist = async (ticker: string, notes = ''): Promise<WatchlistEntry> => {
  const { data } = await api.post('/watchlist', { ticker, notes });
  return data.entry;
};

export const removeFromWatchlist = async (ticker: string): Promise<void> => {
  await api.delete(`/watchlist/${ticker}`);
};

export default api;
