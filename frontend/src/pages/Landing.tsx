import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { TrendingUp, BarChart3, Brain, Shield, ArrowRight, Activity, Zap, Globe } from 'lucide-react';

const features = [
  { icon: TrendingUp, title: 'Price Forecasting', description: 'LSTM, Random Forest, XGBoost & Linear Regression models predict future stock prices with confidence intervals.' },
  { icon: BarChart3, title: 'Technical Analysis', description: 'SMA, EMA, RSI, MACD, Bollinger Bands, ATR and 15+ indicators computed in real-time.' },
  { icon: Brain, title: 'Smart ML Pipeline', description: 'Models train once and cache intelligently. Retrained only when market data changes significantly.' },
  { icon: Shield, title: 'Risk Analytics', description: 'Sharpe Ratio, Sortino Ratio, Max Drawdown, Volatility and CAGR analysis for every stock.' },
  { icon: Zap, title: 'Real-time Data', description: 'Live market data from Yahoo Finance for US, Indian, and international stock exchanges.' },
  { icon: Globe, title: 'Global Coverage', description: 'Support for NASDAQ, NYSE, NSE, BSE and every Yahoo Finance supported ticker worldwide.' },
];

const popularStocks = [
  { ticker: 'AAPL', name: 'Apple' },
  { ticker: 'NVDA', name: 'NVIDIA' },
  { ticker: 'TSLA', name: 'Tesla' },
  { ticker: 'MSFT', name: 'Microsoft' },
  { ticker: 'GOOGL', name: 'Alphabet' },
  { ticker: 'RELIANCE.NS', name: 'Reliance' },
];

const Landing: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[calc(100vh-8rem)] flex flex-col">
      {/* Hero */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-16 relative"
      >
        {/* Background glow */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-primary/10 rounded-full blur-[120px]" />
        </div>

        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.6 }}
          className="relative z-10"
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-medium mb-6">
            <Activity className="w-3.5 h-3.5" />
            AI-Powered Stock Analytics
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-foreground mb-6">
            Intelligent <br className="hidden md:block" />
            <span className="gradient-text">Stock Forecast</span>{' '}
            <span className="text-muted-foreground/50">Platform</span>
          </h1>

          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-8 leading-relaxed">
            Intelligent Stock Forecasting & Financial Analytics Platform.
            Predict market movements with machine learning.
          </p>

          <div className="flex items-center justify-center gap-4">
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => navigate('/dashboard?ticker=AAPL')}
              className="px-6 py-3 rounded-xl gradient-primary text-white font-semibold shadow-lg shadow-primary/25 flex items-center gap-2"
            >
              Get Started
              <ArrowRight className="w-4 h-4" />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => navigate('/forecast')}
              className="px-8 py-4 rounded-xl border border-border bg-background hover:bg-accent hover:border-accent text-foreground font-medium transition-all"
            >
              Start Forecasting
            </motion.button>
          </div>
        </motion.div>
      </motion.section>

      {/* Quick Access */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="py-8"
      >
        <p className="text-center text-sm text-muted-foreground mb-4">Popular Stocks</p>
        <div className="flex flex-wrap justify-center gap-2">
          {popularStocks.map(({ ticker, name }) => (
            <motion.button
              key={ticker}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate(`/dashboard?ticker=${ticker}`)}
              className="px-4 py-2 rounded-lg glass-card-hover text-sm font-medium"
            >
              <span className="text-foreground">{ticker}</span>
              <span className="text-muted-foreground ml-1.5 text-xs">{name}</span>
            </motion.button>
          ))}
        </div>
      </motion.section>

      {/* Features */}
      <section className="py-12">
        <h2 className="text-2xl font-bold text-center mb-8 text-foreground">Platform Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map(({ icon: Icon, title, description }, i) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * i + 0.4 }}
              className="glass-card-hover p-6 group"
            >
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                <Icon className="w-5 h-5 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Landing;
