import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Star, Trash2, Plus, Loader2, TrendingUp, TrendingDown } from 'lucide-react';
import { getWatchlist, addToWatchlist, removeFromWatchlist } from '../lib/api';
import type { WatchlistEntry } from '../types';
import { formatCurrency, cn, getPriceColor } from '../lib/utils';

const Watchlist: React.FC = () => {
  const navigate = useNavigate();
  const [entries, setEntries] = useState<WatchlistEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [newTicker, setNewTicker] = useState('');

  const fetchWatchlist = async () => {
    try {
      const data = await getWatchlist();
      setEntries(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const handleAdd = async () => {
    if (!newTicker.trim()) return;
    setAdding(true);
    try {
      await addToWatchlist(newTicker.trim());
      setNewTicker('');
      await fetchWatchlist();
    } catch (err) {
      console.error(err);
    } finally {
      setAdding(false);
    }
  };

  const handleRemove = async (ticker: string) => {
    try {
      await removeFromWatchlist(ticker);
      setEntries((prev) => prev.filter((e) => e.ticker !== ticker));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <Star className="w-6 h-6 text-amber-400" /> Watchlist
        </h1>
        <p className="text-sm text-muted-foreground mt-1">Track your favorite stocks</p>
      </motion.div>

      {/* Add to watchlist */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-4 flex items-center gap-3"
      >
        <input
          type="text"
          value={newTicker}
          onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
          onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
          placeholder="Add ticker (e.g. AAPL)"
          className="flex-1 h-10 px-4 rounded-lg bg-secondary border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
        <button
          onClick={handleAdd}
          disabled={adding || !newTicker.trim()}
          className="h-10 px-4 rounded-lg gradient-primary text-white text-sm font-medium flex items-center gap-2 disabled:opacity-50"
        >
          {adding ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
          Add
        </button>
      </motion.div>

      {/* Watchlist Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="glass-card p-6 space-y-3">
              <div className="skeleton h-5 w-20" />
              <div className="skeleton h-8 w-32" />
              <div className="skeleton h-4 w-24" />
            </div>
          ))}
        </div>
      ) : entries.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <Star className="w-12 h-12 text-muted-foreground" />
          <p className="text-muted-foreground">Your watchlist is empty. Add stocks above.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {entries.map((entry, i) => {
              const stock = entry.stock;
              return (
                <motion.div
                  key={entry.ticker}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ delay: i * 0.05 }}
                  className="glass-card-hover p-6 cursor-pointer group"
                  onClick={() => navigate(`/dashboard?ticker=${entry.ticker}`)}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-foreground">{entry.ticker}</h3>
                      <p className="text-xs text-muted-foreground">{stock?.name || entry.ticker}</p>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleRemove(entry.ticker); }}
                      className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg hover:bg-red-500/10 text-red-400 transition-all"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  {stock?.current_price && (
                    <p className="text-2xl font-bold text-foreground mt-3">
                      {formatCurrency(stock.current_price)}
                    </p>
                  )}
                  {stock?.sector && (
                    <p className="text-xs text-muted-foreground mt-2">{stock.sector}</p>
                  )}
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
};

export default Watchlist;
