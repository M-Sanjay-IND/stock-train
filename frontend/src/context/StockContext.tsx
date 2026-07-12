import React, { createContext, useContext, useState, useCallback } from 'react';

interface StockContextType {
  selectedTicker: string | null;
  setSelectedTicker: (ticker: string | null) => void;
  recentSearches: string[];
  addRecentSearch: (ticker: string) => void;
  clearRecentSearches: () => void;
}

const StockContext = createContext<StockContextType>({
  selectedTicker: null,
  setSelectedTicker: () => {},
  recentSearches: [],
  addRecentSearch: () => {},
  clearRecentSearches: () => {},
});

export const useStockContext = () => useContext(StockContext);

export const StockProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [recentSearches, setRecentSearches] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('stockvision-recent');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const addRecentSearch = useCallback((ticker: string) => {
    setRecentSearches((prev) => {
      const updated = [ticker, ...prev.filter((t) => t !== ticker)].slice(0, 10);
      localStorage.setItem('stockvision-recent', JSON.stringify(updated));
      return updated;
    });
  }, []);

  const clearRecentSearches = useCallback(() => {
    setRecentSearches([]);
    localStorage.removeItem('stockvision-recent');
  }, []);

  return (
    <StockContext.Provider
      value={{
        selectedTicker,
        setSelectedTicker,
        recentSearches,
        addRecentSearch,
        clearRecentSearches,
      }}
    >
      {children}
    </StockContext.Provider>
  );
};
