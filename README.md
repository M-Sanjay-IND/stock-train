<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/TypeScript-6-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/XGBoost-2.0-FF6600?style=for-the-badge&logo=xgboost&logoColor=white" />
  <img src="https://img.shields.io/badge/CUDA-RTX_5070_Ti-76B900?style=for-the-badge&logo=nvidia&logoColor=white" />
</p>

# 📈 Stock Train — ML-Powered Stock Forecasting & Financial Analytics Platform

A full-stack, production-grade web application for **real-time stock price forecasting**, **financial analytics**, and **interactive charting** — powered by an ensemble of Machine Learning models running on local GPU hardware via a secure ngrok tunnel.

> **Live Frontend:** [stock-train-a3enk0tql-sanjay-ms-projects-bedd0557.vercel.app](https://stock-train-a3enk0tql-sanjay-ms-projects-bedd0557.vercel.app)
>
> **Backend:** Exposed locally via [ngrok](https://ngrok.com) tunnel (see [Architecture](#-architecture--how-it-works) below)

---

## 📸 Screenshots

### Dashboard — Stock Overview
> Real-time stock data with price history, candlestick charts, volume analysis, key metrics (market cap, 52W high/low, volatility, Sharpe ratio, max drawdown, CAGR), and technical indicators (SMA/EMA, Bollinger Bands, RSI, MACD).

![Dashboard Overview](docs/project/dashboard-overview.png)

![Dashboard — Volume & Technical Indicators](docs/project/dashboard-indicators.png)

---

### ML Forecast — Price Predictions
> 1-day, 7-day, and 30-day price forecasts with confidence intervals, actual vs predicted charts, and model comparison table showing RMSE, MAE, MAPE, and R² scores. One-click model retraining.

![Forecast Page](docs/project/forecast-page.png)

---

### Financial Analytics
> Comprehensive financial metrics: daily/monthly/annual returns, CAGR, risk metrics (volatility, Sharpe ratio, Sortino ratio, max drawdown), price overview, and moving average crossover signals.

![Analytics Page](docs/project/analytics-page.png)

---

### Stock Comparison
> Side-by-side comparison of up to 3 stocks across all key metrics — returns, risk, valuation, and price levels.

![Compare Page](docs/project/compare-page.png)

---

### Watchlist
> Save and track your favorite stocks with real-time price updates and sector information.

![Watchlist Page](docs/project/watchlist-page.png)

---

### Model Comparison Table
> Detailed performance metrics for all trained ML models — Linear Regression, Random Forest, and XGBoost — with RMSE, MAE, MAPE (%), R² Score, and time since last training.

![Model Comparison](docs/project/model-comparison.png)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Real-Time Stock Data** | Fetch live market data from Yahoo Finance for any supported ticker worldwide (US, Indian NSE/BSE, etc.) |
| **Technical Indicators** | SMA 20/50, EMA 20/50, RSI, MACD (signal + histogram), Bollinger Bands (upper/lower), ATR, Momentum, Daily Return, Volatility, Lag features |
| **Financial Analytics** | CAGR, Sharpe Ratio, Sortino Ratio, Max Drawdown, Volatility, Moving Average crossover signals |
| **ML Forecasting** | Ensemble of 4 models — Linear Regression, Random Forest, XGBoost, LSTM — with automatic best-model selection based on RMSE |
| **Interactive Charts** | Candlestick charts (Plotly.js), area price charts (Recharts), volume bars, technical overlays, actual vs predicted visualization |
| **Confidence Intervals** | Every forecast includes upper/lower confidence bounds scaled by model RMSE and forecast horizon |
| **Model Comparison** | Side-by-side metrics table (RMSE, MAE, MAPE, R²) for all trained models with training timestamps |
| **One-Click Retraining** | Retrain all models for any ticker with a single button — training runs on local GPU hardware |
| **Smart Model Caching** | Models are persisted to disk and reused; only retrained when data changes (hash-based invalidation) |
| **Watchlist** | Save and track favorite stocks with real-time price and sector info |
| **Stock Comparison** | Compare up to 3 stocks side-by-side across all analytics metrics |
| **CSV Export** | Download historical price data as CSV |
| **Dark Theme** | Premium fintech-grade dark UI with glassmorphism design and smooth animations |

---

## 🧠 Machine Learning Models — Deep Dive

The forecasting engine uses an **ensemble of 4 ML models**, each selected for a specific strength. After training, the system automatically selects the **best-performing model** (lowest RMSE on test data) for predictions.

### 1. Linear Regression (Baseline)

| | |
|---|---|
| **Library** | `scikit-learn` — `LinearRegression` |
| **Role** | Baseline model for benchmarking |
| **Why chosen** | Provides a fast, interpretable lower bound. If a complex model can't beat linear regression, it's overfitting. Also acts as a sanity check — stock prices have strong linear autocorrelation over short horizons, making this a surprisingly competitive baseline. |
| **Strengths** | Near-instant training, fully interpretable coefficients, zero hyperparameters, extremely low computational cost |
| **Weaknesses** | Cannot capture non-linear patterns, market regime changes, or interaction effects between features |

### 2. Random Forest Regressor

| | |
|---|---|
| **Library** | `scikit-learn` — `RandomForestRegressor` |
| **Config** | 100 estimators, max depth 15, parallel jobs (`n_jobs=-1`) |
| **Role** | Non-linear model with built-in feature importance |
| **Why chosen** | Random Forests handle non-linear relationships between technical indicators and price movement without requiring feature scaling. The ensemble of 100 decision trees reduces variance and provides robust predictions. Built-in feature importance ranking reveals which indicators (RSI, MACD, moving averages) drive predictions most. |
| **Strengths** | Handles non-linearity, resistant to overfitting (bagging), provides feature importance, no scaling required, parallel training |
| **Weaknesses** | Cannot extrapolate beyond training data range, higher memory usage, slower inference than linear |

### 3. XGBoost (Extreme Gradient Boosting)

| | |
|---|---|
| **Library** | `xgboost` — `XGBRegressor` (with `GradientBoostingRegressor` fallback) |
| **Config** | 200 estimators, max depth 6, learning rate 0.1 |
| **Role** | State-of-the-art gradient boosting for tabular data |
| **Why chosen** | XGBoost is the go-to algorithm for structured/tabular prediction tasks. It sequentially builds trees that correct the errors of previous trees, capturing complex non-linear patterns and feature interactions that Random Forest misses. L1/L2 regularization prevents overfitting. It consistently wins Kaggle competitions on tabular financial data. The sklearn `GradientBoostingRegressor` fallback ensures the system works even without the XGBoost library installed. |
| **Strengths** | Highest accuracy on tabular data, built-in regularization, handles missing values, fast via histogram-based splits, GPU-accelerable |
| **Weaknesses** | Sensitive to hyperparameters, sequential training (harder to parallelize than RF), can overfit with too many boosting rounds |

### 4. LSTM (Long Short-Term Memory Neural Network)

| | |
|---|---|
| **Framework** | `PyTorch` — custom 3-layer stacked LSTM |
| **Architecture** | LSTM(256) → Dropout(0.2) → LSTM(128) → Dropout(0.2) → LSTM(64) → Dropout(0.2) → Dense(16) → ReLU → Dense(1) |
| **Config** | Lookback window: 100 steps, 150 epochs, batch size 128, Adam optimizer (lr=0.001), early stopping (patience=10) |
| **Role** | Time-series deep learning model for sequential pattern recognition |
| **Why chosen** | Stock prices are time-series data with temporal dependencies — today's price depends on patterns from the past days/weeks. LSTM networks are specifically designed for this: their gating mechanism (forget gate, input gate, output gate) learns which past information to retain and which to discard. The 3-layer stacked architecture captures patterns at multiple time scales — short-term momentum, medium-term trends, and longer-term cycles. Running on an **NVIDIA RTX 5070 Ti** GPU with CUDA acceleration makes training feasible in seconds rather than minutes. |
| **Strengths** | Captures temporal dependencies, handles variable-length sequences, learns complex non-linear time patterns, GPU-accelerated training |
| **Weaknesses** | Requires feature scaling (MinMax), longer training time, needs more data, harder to interpret, sensitive to hyperparameters |

### Feature Engineering Pipeline

All models consume a rich feature matrix built from raw OHLCV (Open, High, Low, Close, Volume) data:

```
Raw OHLCV Data → Technical Indicators → Engineered Features → ML-Ready Matrix
```

**Computed Features (30+):**
- **Moving Averages:** SMA 20, SMA 50, EMA 20, EMA 50
- **Momentum:** RSI (14), MACD (12/26/9), Signal Line, Histogram, Momentum
- **Volatility:** Bollinger Bands (upper/lower), ATR (14), Daily Return, Rolling Volatility
- **Lag Features:** Close price lagged by 1, 5, 10, and 20 days
- **Engineered Ratios:** Close/SMA20, Close/SMA50, Volume/SMA20, Price Range, Price Range %

### Model Selection & Training Flow

```
User Requests Forecast
        │
        ▼
   Has cached model with matching data hash?
        │
    ┌───┴───┐
    Yes     No
    │       │
    │       ▼
    │   Train ALL 4 models
    │       │
    │       ▼
    │   Evaluate on test set (RMSE, MAE, MAPE, R²)
    │       │
    │       ▼
    │   Select best model (lowest RMSE)
    │       │
    │       ▼
    │   Save models + scalers to disk
    │       │
    └───┬───┘
        │
        ▼
   Load best model → Generate forecasts
        │
        ▼
   Return predictions with confidence intervals
```

---

## 🏗️ Architecture — How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                          │
│                                                                 │
│   Vercel (CDN) ──serves──▶ React Frontend (SPA)                │
│   stock-train-a3enk0tql-sanjay-ms-projects-bedd0557             │
│   .vercel.app                                                   │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS API Calls
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     NGROK SECURE TUNNEL                         │
│                                                                 │
│   https://<random-id>.ngrok-free.app ◀──encrypted──▶ :5000     │
│                                                                 │
│   • TLS termination at ngrok edge                               │
│   • DDoS protection                                             │
│   • Request inspection dashboard                                │
│   • No port forwarding / firewall changes needed                │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ localhost:5000
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│            LOCAL MACHINE — ROG Zephyrus G16 (2025)             │
│                                                                 │
│   ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│   │ Flask API   │  │ ML Pipeline  │  │ NVIDIA RTX 5070 Ti │   │
│   │ Server      │──│ Training &   │──│ CUDA GPU Accel.    │   │
│   │ (Port 5000) │  │ Inference    │  │ 12GB GDDR7 VRAM   │   │
│   └─────────────┘  └──────────────┘  └────────────────────┘   │
│         │                                                       │
│   ┌─────────────┐  ┌──────────────┐                            │
│   │ SQLite DB   │  │ Saved Models │                            │
│   │ (Cache +    │  │ (.joblib,    │                            │
│   │  Watchlist) │  │  .pt files)  │                            │
│   └─────────────┘  └──────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Why ngrok? — Benefits of the Local GPU Backend Architecture

This project uses a **split architecture** where the frontend is deployed to Vercel's global CDN, while the backend runs **locally on a high-performance GPU machine** and is exposed to the internet via an ngrok secure tunnel. Here's why:

| Benefit | Details |
|---------|---------|
| **GPU Acceleration** | The LSTM model and training pipeline leverage the **NVIDIA RTX 5070 Ti** (12GB GDDR7, CUDA cores) via PyTorch CUDA. Training that would take minutes on a cloud CPU completes in **seconds** on local GPU hardware. The RTX 5070 Ti's Blackwell architecture and tensor cores provide massive throughput for neural network operations. |
| **Zero Cloud GPU Costs** | Cloud GPU instances (AWS p3, GCP A100) cost $3–30+/hour. Running locally on existing hardware eliminates these costs entirely while providing comparable or superior performance for single-user workloads. |
| **Security** | ngrok provides **TLS encryption** end-to-end. Traffic is encrypted from the browser to the ngrok edge, then tunneled securely to your local machine. No ports need to be opened on your router/firewall. The tunnel URL is randomized and can be protected with ngrok's built-in authentication. |
| **Full Control** | Your data, models, and code never leave your machine. No cloud vendor has access to your trading strategies, watchlists, or model weights. All computation stays on your hardware. |
| **Instant Iteration** | Edit code → restart Flask → changes are live through the same tunnel. No CI/CD pipeline, no Docker build, no cloud deployment wait. Development velocity is maximized. |
| **Inspection & Debugging** | ngrok's local dashboard (`http://localhost:4040`) provides real-time request/response inspection, replay, and latency metrics — invaluable for API debugging. |
| **ROG Zephyrus G16 (2025)** | The ASUS ROG Zephyrus G16 (2025) with RTX 5070 Ti provides a powerful mobile workstation: up to 120W GPU TGP, PCIe 5.0, DDR5 RAM, and whisper-quiet cooling — making it ideal for running ML inference and training workloads while maintaining portability. |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 19, TypeScript 6, Vite 8, Tailwind CSS 3, Radix UI primitives, Recharts, Plotly.js, Framer Motion, Axios, React Router 7 |
| **Backend** | Flask 3, Python 3.12, Flask-SQLAlchemy, Flask-CORS, yfinance, ta (Technical Analysis library) |
| **ML / AI** | PyTorch (LSTM with CUDA), Scikit-learn (Linear Regression, Random Forest), XGBoost, joblib (model serialization) |
| **Database** | SQLite (development — stores cached data, trained model metadata, watchlist) |
| **Deployment** | Vercel (frontend CDN), ngrok (backend tunnel), local GPU compute |
| **GPU** | NVIDIA RTX 5070 Ti — CUDA-accelerated PyTorch training & inference |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** and **npm 9+**
- **NVIDIA GPU with CUDA** (optional but recommended — falls back to CPU)
- **ngrok** account (free tier works) — [sign up here](https://ngrok.com)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/stock-train.git
cd stock-train
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Install PyTorch with CUDA (for GPU acceleration)
# Visit https://pytorch.org/get-started/locally/ for your specific CUDA version
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

# Start the Flask server
python run.py
```

The backend runs at `http://localhost:5000`.

### 3. Expose Backend via ngrok

In a **separate terminal**:

```bash
ngrok http 5000
```

ngrok will display a public URL like `https://xxxx-xx-xx-xx-xx.ngrok-free.app`. Copy this URL — you'll need it for the frontend.

> **Tip:** Visit `http://localhost:4040` to access ngrok's request inspection dashboard.

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set the API URL to your ngrok tunnel
# Create a .env file or set the environment variable:
echo "VITE_API_URL=https://your-ngrok-url.ngrok-free.app" > .env

# Start the development server
npm run dev
```

The frontend runs at `http://localhost:5173`.

### 5. Deploy Frontend to Vercel (Production)

1. Push your code to GitHub
2. Connect the repository to [Vercel](https://vercel.com)
3. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Set environment variable:
   - `VITE_API_URL` = your ngrok HTTPS URL
5. Deploy

---

## 📡 API Reference

**Base URL:** `http://localhost:5000` (or your ngrok tunnel URL)

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check — returns service status, version, and timestamp |
| `GET` | `/stocks/search?q={query}` | Search stocks by ticker or company name |
| `GET` | `/stocks/info/{ticker}` | Get stock info (name, sector, exchange, market cap, 52W range) |

### Market Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/history/{ticker}?period={period}&force={bool}` | Historical OHLCV data. Periods: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `max` |
| `GET` | `/technical/{ticker}?limit={n}&series={bool}` | Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Momentum, Volatility) |
| `GET` | `/analytics/{ticker}?returns={bool}` | Financial analytics (returns, CAGR, Sharpe, Sortino, drawdown, MA signals) |

### ML Forecasting

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/forecast/{ticker}` | Get price predictions (1-day, 7-day, 30-day) with confidence intervals. Auto-trains if no model exists. |
| `POST` | `/train/{ticker}` | Force retrain all ML models (Linear Regression, Random Forest, XGBoost, LSTM) |
| `GET` | `/metrics/{ticker}` | Get evaluation metrics (RMSE, MAE, MAPE, R²) for all trained models |

### Watchlist

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/watchlist` | Get all watchlist entries |
| `POST` | `/watchlist` | Add to watchlist — Body: `{"ticker": "AAPL"}` |
| `DELETE` | `/watchlist/{ticker}` | Remove from watchlist |

### Error Format

All errors return a consistent JSON structure:
```json
{
  "error": "Description of what went wrong",
  "status": 400
}
```

---

## 📂 Project Structure

```
stock-train/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory with CORS
│   │   ├── config.py                # Configuration (DB, ML params, caching)
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   ├── repositories/           # Data access layer (DB queries)
│   │   ├── services/               # Business logic (data, technical analysis)
│   │   ├── routes/                  # REST API endpoint handlers
│   │   │   ├── health.py           # Health check endpoint
│   │   │   ├── stocks.py           # Stock search & info
│   │   │   ├── analytics.py        # Financial analytics
│   │   │   ├── technical.py        # Technical indicators
│   │   │   ├── forecast.py         # ML predictions & training
│   │   │   └── watchlist.py        # Watchlist CRUD
│   │   └── ml/                      # Machine Learning pipeline
│   │       ├── feature_engineering.py   # 30+ feature computation
│   │       ├── preprocessing.py         # Scaling, splitting, sequences
│   │       ├── trainer.py               # Multi-model training orchestrator
│   │       ├── predictor.py             # Inference & forecast generation
│   │       ├── model_manager.py         # Model caching & loading
│   │       └── models/
│   │           ├── linear_model.py      # Linear Regression wrapper
│   │           ├── random_forest_model.py   # Random Forest wrapper
│   │           ├── xgboost_model.py     # XGBoost wrapper (with sklearn fallback)
│   │           └── lstm_model.py        # PyTorch LSTM (3-layer, CUDA-enabled)
│   ├── saved_models/                # Persisted trained model files
│   ├── requirements.txt
│   ├── run.py                       # Entry point
│   └── Dockerfile                   # Container config (optional)
├── frontend/
│   ├── src/
│   │   ├── App.tsx                  # Router & layout
│   │   ├── main.tsx                 # React entry point
│   │   ├── index.css                # Global styles & Tailwind
│   │   ├── pages/
│   │   │   ├── Landing.tsx          # Landing / hero page
│   │   │   ├── Dashboard.tsx        # Stock overview dashboard
│   │   │   ├── Analytics.tsx        # Financial analytics page
│   │   │   ├── Forecast.tsx         # ML forecast & model comparison
│   │   │   ├── Compare.tsx          # Multi-stock comparison
│   │   │   ├── Watchlist.tsx        # Watchlist management
│   │   │   └── NotFound.tsx         # 404 page
│   │   ├── components/
│   │   │   ├── charts/              # Recharts & Plotly chart components
│   │   │   ├── layout/              # Sidebar, header, layout shell
│   │   │   └── ui/                  # Radix UI primitives (Button, Card, etc.)
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── context/                 # React Context (theme, stock state)
│   │   ├── lib/                     # API client, utilities
│   │   └── types/                   # TypeScript type definitions
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── vercel.json                  # Vercel deployment config
├── docs/
│   └── project/                     # Project screenshots
├── .env.example                     # Environment variable template
├── .gitignore
└── README.md                        # ← You are here
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Frontend
VITE_API_URL=https://your-ngrok-url.ngrok-free.app   # or http://localhost:5000

# Backend
FLASK_ENV=development
FLASK_DEBUG=1
# SECURITY: In production, the app will refuse to start unless this is set to a secure string!
SECRET_KEY=your-secure-random-key-here
DATABASE_URL=sqlite:///stockvision.db

# ML Configuration
MODEL_CACHE_HOURS=24       # Hours before models are considered stale
LSTM_EPOCHS=50             # LSTM training epochs (increase for better accuracy)
LSTM_LOOKBACK=60           # Number of past days LSTM considers
```

---

## 🧪 How to Use

1. **Search for a Stock** — Use the search bar at the top to find any stock (e.g., `AAPL`, `RELIANCE.NS`, `GOOGL`)
2. **Dashboard** — View real-time price, candlestick chart, volume, key metrics, and technical indicators
3. **Analytics** — Dive into financial metrics: returns, risk ratios, price overview, MA signals
4. **Forecast** — Get ML-powered price predictions for 1, 7, and 30 days with confidence intervals
5. **Retrain Models** — Click the "Retraining..." button to force-retrain all models with the latest data
6. **Compare** — Enter up to 3 tickers to compare side-by-side across all metrics
7. **Watchlist** — Add stocks to your watchlist for quick access and tracking
8. **Export** — Download historical data as CSV from the Dashboard

---

## 📄 License

MIT

---

<p align="center">
  Built with ❤️ using React, Flask, PyTorch, and an RTX 5070 Ti
</p>
