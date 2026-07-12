import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, Moon, Sun } from 'lucide-react';
import { useThemeContext } from '../../context/ThemeContext';
import { useStockContext } from '../../context/StockContext';
import { searchStocks } from '../../lib/api';
import type { SearchResult } from '../../types';

const Header: React.FC = () => {
  const { theme, toggleTheme } = useThemeContext();
  const { setSelectedTicker, recentSearches } = useStockContext();
  const navigate = useNavigate();

  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [, setSearching] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.trim().length < 1) {
        setResults([]);
        return;
      }
      setSearching(true);
      try {
        const res = await searchStocks(query);
        setResults(res);
        setShowDropdown(true);
      } catch {
        setResults([]);
      } finally {
        setSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (ticker: string) => {
    setSelectedTicker(ticker);
    setQuery('');
    setShowDropdown(false);
    navigate(`/dashboard?ticker=${ticker}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && query.trim()) {
      handleSelect(query.trim().toUpperCase());
    }
    if (e.key === 'Escape') {
      setShowDropdown(false);
      inputRef.current?.blur();
    }
  };

  return (
    <header className="sticky top-0 z-30 h-16 flex items-center justify-between px-6 bg-background/80 backdrop-blur-xl border-b border-border">
      {/* Search Bar */}
      <div className="relative w-full max-w-md" ref={dropdownRef}>
        <div className="relative flex items-center">
          <Search className="absolute left-3 w-4 h-4 text-muted-foreground" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => query.trim() && setShowDropdown(true)}
            onKeyDown={handleKeyDown}
            placeholder="Search stocks... (e.g. AAPL, RELIANCE.NS)"
            className="w-full h-10 pl-10 pr-10 rounded-lg bg-secondary/50 border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all"
          />
          {query && (
            <button
              onClick={() => { setQuery(''); setResults([]); setShowDropdown(false); }}
              className="absolute right-3 text-muted-foreground hover:text-foreground"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Dropdown */}
        <AnimatePresence>
          {showDropdown && (results.length > 0 || recentSearches.length > 0) && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="absolute top-12 left-0 right-0 bg-card border border-border rounded-xl shadow-2xl overflow-hidden max-h-80 overflow-y-auto"
            >
              {results.length > 0 ? (
                <div className="py-1">
                  {results.map((r) => (
                    <button
                      key={r.ticker}
                      onClick={() => handleSelect(r.ticker)}
                      className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-accent/50 transition-colors text-left"
                    >
                      <div>
                        <span className="font-semibold text-sm text-foreground">{r.ticker}</span>
                        <span className="text-xs text-muted-foreground ml-2">{r.name}</span>
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="p-3">
                  <p className="text-xs text-muted-foreground mb-2 px-1">Recent Searches</p>
                  <div className="flex flex-wrap gap-1.5">
                    {recentSearches.map((t) => (
                      <button
                        key={t}
                        onClick={() => handleSelect(t)}
                        className="px-3 py-1 text-xs rounded-full bg-secondary text-foreground hover:bg-primary/20 transition-colors"
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 ml-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={toggleTheme}
          className="p-2.5 rounded-lg hover:bg-accent transition-colors"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4 text-amber-400" />
          ) : (
            <Moon className="w-4 h-4 text-slate-600" />
          )}
        </motion.button>
      </div>
    </header>
  );
};

export default Header;
