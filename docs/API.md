# StockVision AI — API Documentation

## Base URL

**Development:** `http://localhost:5000`

---

## Endpoints

### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "StockVision AI",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

### Search Stocks

```
GET /stocks/search?q={query}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query (ticker or company name) |

**Response:**
```json
{
  "results": [
    { "ticker": "AAPL", "name": "Apple Inc." }
  ],
  "count": 1
}
```

---

### Stock Info

```
GET /stocks/info/{ticker}
```

**Response:**
```json
{
  "data": {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "exchange": "NMS",
    "sector": "Technology",
    "current_price": 195.50,
    "market_cap": 3000000000000,
    "fifty_two_week_high": 200.00,
    "fifty_two_week_low": 130.00
  }
}
```

---

### Historical Data

```
GET /history/{ticker}?period={period}&force={boolean}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | string | `2y` | Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max) |
| `force` | boolean | `false` | Force refresh from Yahoo Finance |

---

### Technical Indicators

```
GET /technical/{ticker}?limit={limit}&series={boolean}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | `200` | Number of data points |
| `series` | boolean | `true` | Include time series data |

**Computed Indicators:**
SMA 20/50, EMA 20/50, RSI, MACD, Signal, Histogram, Bollinger Bands, ATR, Momentum, Daily Return, Volatility, Lag 1/5/10/20

---

### Financial Analytics

```
GET /analytics/{ticker}?returns={boolean}&returns_period={period}
```

**Computed Metrics:**
Daily/Monthly/Annual Return, CAGR, Volatility, Sharpe Ratio, Sortino Ratio, Max Drawdown, 52W High/Low, MA Crossovers

---

### Forecast

```
GET /forecast/{ticker}
```

Returns predictions for 1-day, 7-day, and 30-day horizons with confidence intervals. Automatically trains models if none exist.

---

### Train Models

```
POST /train/{ticker}
```

Force retrain all ML models (Linear Regression, Random Forest, XGBoost, LSTM) for a given ticker.

---

### Model Metrics

```
GET /metrics/{ticker}
```

Returns evaluation metrics (RMSE, MAE, MAPE, R²) for all trained models.

---

### Watchlist

```
GET /watchlist                    # Get all watchlist entries
POST /watchlist                   # Add to watchlist (body: {"ticker": "AAPL"})
DELETE /watchlist/{ticker}        # Remove from watchlist
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "status": 400
}
```

| Status | Description |
|--------|-------------|
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |
