"""
StockVision AI - Financial Analytics Service

Computes financial metrics: returns, risk ratios, drawdown, and more.
"""

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger("stockvision.analytics_service")


class AnalyticsService:
    """Compute financial analytics from price history."""

    @staticmethod
    def compute_analytics(df: pd.DataFrame) -> dict:
        """
        Compute comprehensive financial analytics from OHLCV DataFrame.
        Expects columns: close, high, low, volume (lowercase).
        """
        if df.empty or len(df) < 2:
            return {"error": "Insufficient data for analytics"}

        df = df.copy()
        df.columns = [c.lower() for c in df.columns]
        close = df["close"]
        volume = df["volume"]

        # --- Returns ---
        daily_returns = close.pct_change().dropna()
        total_days = len(close)

        # Latest price info
        current_price = float(close.iloc[-1])
        previous_close = float(close.iloc[-2]) if len(close) >= 2 else current_price

        # Daily return
        daily_return = (current_price - previous_close) / previous_close if previous_close else 0

        # Monthly return (last ~21 trading days)
        if len(close) >= 21:
            monthly_return = (current_price / float(close.iloc[-21]) - 1)
        else:
            monthly_return = None

        # Annual return (last ~252 trading days)
        if len(close) >= 252:
            annual_return = (current_price / float(close.iloc[-252]) - 1)
        else:
            annual_return = None

        # CAGR
        years = total_days / 252
        if years > 0 and float(close.iloc[0]) > 0:
            cagr = (current_price / float(close.iloc[0])) ** (1 / years) - 1
        else:
            cagr = None

        # --- Risk Metrics ---
        # Annualized Volatility
        volatility = float(daily_returns.std() * np.sqrt(252)) if len(daily_returns) > 1 else None

        # Sharpe Ratio (risk-free rate = 4%)
        risk_free_rate = 0.04
        if volatility and volatility > 0:
            annual_ret = float(daily_returns.mean() * 252)
            sharpe = (annual_ret - risk_free_rate) / volatility
        else:
            sharpe = None

        # Sortino Ratio (downside deviation)
        downside_returns = daily_returns[daily_returns < 0]
        if len(downside_returns) > 0:
            downside_std = float(downside_returns.std() * np.sqrt(252))
            if downside_std > 0:
                annual_ret = float(daily_returns.mean() * 252)
                sortino = (annual_ret - risk_free_rate) / downside_std
            else:
                sortino = None
        else:
            sortino = None

        # Maximum Drawdown
        cumulative = (1 + daily_returns).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = float(drawdown.min()) if len(drawdown) > 0 else None

        # --- Volume ---
        avg_volume = float(volume.mean()) if len(volume) > 0 else None
        avg_volume_10d = float(volume.tail(10).mean()) if len(volume) >= 10 else avg_volume

        # --- Price Extremes ---
        high_col = df["high"] if "high" in df.columns else close
        low_col = df["low"] if "low" in df.columns else close

        # 52-week (252 trading days)
        lookback_252 = min(252, len(df))
        fifty_two_week_high = float(high_col.tail(lookback_252).max())
        fifty_two_week_low = float(low_col.tail(lookback_252).min())

        # --- Moving Average Crossovers ---
        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean()
        crossovers = []

        if len(close) >= 50:
            current_sma20 = float(sma_20.iloc[-1])
            current_sma50 = float(sma_50.iloc[-1])
            prev_sma20 = float(sma_20.iloc[-2])
            prev_sma50 = float(sma_50.iloc[-2])

            if prev_sma20 <= prev_sma50 and current_sma20 > current_sma50:
                crossovers.append({
                    "type": "golden_cross",
                    "description": "SMA20 crossed above SMA50 (Bullish)",
                    "date": str(df.index[-1].date()) if hasattr(df.index[-1], "date") else str(df.index[-1]),
                })
            elif prev_sma20 >= prev_sma50 and current_sma20 < current_sma50:
                crossovers.append({
                    "type": "death_cross",
                    "description": "SMA20 crossed below SMA50 (Bearish)",
                    "date": str(df.index[-1].date()) if hasattr(df.index[-1], "date") else str(df.index[-1]),
                })

            # Current position
            if current_sma20 > current_sma50:
                crossovers.append({
                    "type": "bullish_position",
                    "description": "SMA20 is above SMA50 (Bullish trend)"
                })
            else:
                crossovers.append({
                    "type": "bearish_position",
                    "description": "SMA20 is below SMA50 (Bearish trend)"
                })

        def safe_round(val, decimals=4):
            if val is None or (isinstance(val, float) and np.isnan(val)):
                return None
            return round(float(val), decimals)

        return {
            "current_price": safe_round(current_price, 2),
            "previous_close": safe_round(previous_close, 2),
            "price_change": safe_round(current_price - previous_close, 2),
            "price_change_pct": safe_round(daily_return * 100, 2),
            "daily_return": safe_round(daily_return, 4),
            "monthly_return": safe_round(monthly_return, 4),
            "annual_return": safe_round(annual_return, 4),
            "cagr": safe_round(cagr, 4),
            "volatility": safe_round(volatility, 4),
            "sharpe_ratio": safe_round(sharpe, 4),
            "sortino_ratio": safe_round(sortino, 4),
            "max_drawdown": safe_round(max_drawdown, 4),
            "avg_daily_volume": safe_round(avg_volume, 0),
            "avg_volume_10d": safe_round(avg_volume_10d, 0),
            "fifty_two_week_high": safe_round(fifty_two_week_high, 2),
            "fifty_two_week_low": safe_round(fifty_two_week_low, 2),
            "total_trading_days": total_days,
            "crossovers": crossovers,
        }

    @staticmethod
    def compute_returns_series(df: pd.DataFrame, period: str = "daily") -> list[dict]:
        """Get returns as a time series for charting."""
        df = df.copy()
        df.columns = [c.lower() for c in df.columns]
        close = df["close"]

        if period == "daily":
            returns = close.pct_change().dropna()
        elif period == "weekly":
            returns = close.resample("W").last().pct_change().dropna()
        elif period == "monthly":
            returns = close.resample("ME").last().pct_change().dropna()
        else:
            returns = close.pct_change().dropna()

        result = []
        for idx, val in returns.items():
            if not np.isnan(val):
                result.append({
                    "date": str(idx.date()) if hasattr(idx, "date") else str(idx),
                    "return": round(float(val), 6),
                    "cumulative": round(float((1 + returns.loc[:idx]).prod() - 1), 6),
                })

        return result
