import React from 'react';
import { motion } from 'framer-motion';
import { Settings as SettingsIcon, Moon, Sun, Palette } from 'lucide-react';
import { useThemeContext } from '../context/ThemeContext';
import { useStockContext } from '../context/StockContext';

const Settings: React.FC = () => {
  const { theme, setTheme } = useThemeContext();
  const { recentSearches, clearRecentSearches } = useStockContext();

  return (
    <div className="space-y-6 max-w-2xl">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-primary" /> Settings
        </h1>
      </motion.div>

      {/* Theme */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
          <Palette className="w-5 h-5 text-primary" /> Appearance
        </h2>
        <div className="flex gap-3">
          <button
            onClick={() => setTheme('dark')}
            className={`flex items-center gap-2 px-4 py-3 rounded-xl border-2 transition-all ${
              theme === 'dark' ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/30'
            }`}
          >
            <Moon className="w-5 h-5" />
            <div className="text-left">
              <p className="text-sm font-medium text-foreground">Dark</p>
              <p className="text-xs text-muted-foreground">Dark background</p>
            </div>
          </button>
          <button
            onClick={() => setTheme('light')}
            className={`flex items-center gap-2 px-4 py-3 rounded-xl border-2 transition-all ${
              theme === 'light' ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/30'
            }`}
          >
            <Sun className="w-5 h-5" />
            <div className="text-left">
              <p className="text-sm font-medium text-foreground">Light</p>
              <p className="text-xs text-muted-foreground">Light background</p>
            </div>
          </button>
        </div>
      </motion.div>

      {/* Recent Searches */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-foreground">Recent Searches</h2>
          <button
            onClick={clearRecentSearches}
            className="text-xs text-red-400 hover:text-red-300 transition-colors"
          >
            Clear All
          </button>
        </div>
        {recentSearches.length === 0 ? (
          <p className="text-sm text-muted-foreground">No recent searches</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {recentSearches.map(t => (
              <span key={t} className="px-3 py-1.5 text-xs rounded-full bg-secondary text-foreground">
                {t}
              </span>
            ))}
          </div>
        )}
      </motion.div>

      {/* Info */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-6">
        <h2 className="text-lg font-semibold text-foreground mb-2">About</h2>
        <div className="text-sm text-muted-foreground space-y-1">
          <p>StockVision AI v1.0.0</p>
          <p>Intelligent Stock Forecasting & Financial Analytics Platform</p>
        </div>
      </motion.div>
    </div>
  );
};

export default Settings;
