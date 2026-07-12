import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { StockProvider } from './context/StockContext';
import ErrorBoundary from './components/ui/ErrorBoundary';
import Layout from './components/layout/Layout';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Forecast from './pages/Forecast';
import Compare from './pages/Compare';
import Watchlist from './pages/Watchlist';
import About from './pages/About';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <StockProvider>
        <ErrorBoundary>
          <BrowserRouter>
            <Routes>
              {/* Layout routes */}
              <Route element={<Layout />}>
                <Route path="/" element={<Landing />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/forecast" element={<Forecast />} />
                <Route path="/compare" element={<Compare />} />
                <Route path="/watchlist" element={<Watchlist />} />
                <Route path="/about" element={<About />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<NotFound />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </ErrorBoundary>
      </StockProvider>
    </ThemeProvider>
  );
};

export default App;
