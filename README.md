# Stock Forecast

**Intelligent Stock Forecasting & Financial Analytics Platform**

A full-stack web application for stock price forecasting, financial analytics, and interactive charting — powered by Machine Learning.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![React](https://img.shields.io/badge/React-18-61dafb)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178c6)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-ff6f00)
![Flask](https://img.shields.io/badge/Flask-3.0-000000)

---

## Features

- **Real-time Stock Data** — Fetch live market data from Yahoo Finance for any supported ticker
- **Technical Indicators** — SMA, EMA, RSI, MACD, Bollinger Bands, ATR, and more
- **Financial Analytics** — CAGR, Sharpe Ratio, Sortino Ratio, Max Drawdown, Volatility
- **ML Forecasting** — LSTM, Random Forest, XGBoost, Linear Regression with automatic model selection
- **Interactive Charts** — Candlestick, price, volume, technical overlays, forecast visualization
- **Smart Model Caching** — Models are trained once and reused; retrained only when data changes
- **Watchlist** — Save and track your favorite stocks
- **Stock Comparison** — Compare up to 3 stocks side-by-side
- **Export** — Download CSV data and PDF reports
- **Dark/Light Theme** — Professional fintech UI with glassmorphism design

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React, TypeScript, Vite, Tailwind CSS, shadcn/ui, Recharts, Plotly.js, Framer Motion |
| Backend | Flask, Python 3.12, SQLAlchemy, yfinance, ta (Technical Analysis) |
| ML | TensorFlow/Keras (LSTM), Scikit-learn, XGBoost |
| Database | SQLite (dev), PostgreSQL-ready |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm 9+

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python run.py
```

Backend runs at `http://localhost:5000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## Project Structure

```
stock-forecast/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── config.py            # Configuration
│   │   ├── models/              # SQLAlchemy models
│   │   ├── repositories/        # Data access layer
│   │   ├── services/            # Business logic
│   │   ├── routes/              # REST API endpoints
│   │   └── ml/                  # ML pipeline
│   ├── saved_models/            # Trained model files
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom hooks
│   │   ├── context/             # React context
│   │   ├── lib/                 # Utilities & API client
│   │   └── types/               # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── docs/                        # Documentation
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/stocks/search?q=` | Search stocks |
| GET | `/history/<ticker>` | Historical data |
| GET | `/technical/<ticker>` | Technical indicators |
| GET | `/analytics/<ticker>` | Financial analytics |
| GET | `/forecast/<ticker>` | Price forecast |
| GET | `/metrics/<ticker>` | Model metrics |
| POST | `/train/<ticker>` | Train models |
| GET | `/watchlist` | Get watchlist |
| POST | `/watchlist` | Add to watchlist |
| DELETE | `/watchlist/<ticker>` | Remove from watchlist |

---

## License

MIT
