"""
StockVision AI - Technical Analysis Service

Computes technical indicators from OHLCV data using the `ta` library and pandas.
All indicators are computed on a DataFrame and returned as a dict for API response.
"""

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger("stockvision.technical_service")


class TechnicalService:
    """Compute technical indicators from price data."""

    @staticmethod
    def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all technical indicator columns to a price DataFrame.
        Expects columns: close, high, low, volume (lowercase).
        """
        if df.empty or len(df) < 20:
            return df

        df = df.copy()

        # Ensure lowercase columns
        df.columns = [c.lower() for c in df.columns]

        close = df["close"]
        high = df["high"]
        low = df["low"]

        # --- Moving Averages ---
        df["sma_20"] = close.rolling(window=20).mean()
        df["sma_50"] = close.rolling(window=50).mean()
        df["ema_20"] = close.ewm(span=20, adjust=False).mean()
        df["ema_50"] = close.ewm(span=50, adjust=False).mean()

        # --- RSI (14-period) ---
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["rsi"] = 100 - (100 / (1 + rs))

        # --- MACD ---
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        df["macd"] = ema_12 - ema_26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_histogram"] = df["macd"] - df["macd_signal"]

        # --- Bollinger Bands ---
        sma_20 = df["sma_20"]
        std_20 = close.rolling(window=20).std()
        df["bb_upper"] = sma_20 + (std_20 * 2)
        df["bb_middle"] = sma_20
        df["bb_lower"] = sma_20 - (std_20 * 2)
        df["bb_width"] = df["bb_upper"] - df["bb_lower"]

        # --- ATR (14-period) ---
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["atr"] = true_range.rolling(window=14).mean()

        # --- Momentum ---
        df["momentum"] = close - close.shift(10)

        # --- Daily Return ---
        df["daily_return"] = close.pct_change()

        # --- Volatility (20-day rolling std of returns) ---
        df["volatility"] = df["daily_return"].rolling(window=20).std()

        # --- Lag Features ---
        df["lag_1"] = close.shift(1)
        df["lag_5"] = close.shift(5)
        df["lag_10"] = close.shift(10)
        df["lag_20"] = close.shift(20)

        return df

    @staticmethod
    def get_latest_indicators(df: pd.DataFrame) -> dict:
        """Get the most recent values of all indicators."""
        if df.empty:
            return {}

        df = TechnicalService.compute_all_indicators(df)
        latest = df.iloc[-1]

        def safe_round(val, decimals=2):
            if pd.isna(val):
                return None
            return round(float(val), decimals)

        return {
            "date": str(df.index[-1].date()) if hasattr(df.index[-1], "date") else str(df.index[-1]),
            "close": safe_round(latest.get("close")),
            "sma_20": safe_round(latest.get("sma_20")),
            "sma_50": safe_round(latest.get("sma_50")),
            "ema_20": safe_round(latest.get("ema_20")),
            "ema_50": safe_round(latest.get("ema_50")),
            "rsi": safe_round(latest.get("rsi")),
            "macd": safe_round(latest.get("macd"), 4),
            "macd_signal": safe_round(latest.get("macd_signal"), 4),
            "macd_histogram": safe_round(latest.get("macd_histogram"), 4),
            "bb_upper": safe_round(latest.get("bb_upper")),
            "bb_middle": safe_round(latest.get("bb_middle")),
            "bb_lower": safe_round(latest.get("bb_lower")),
            "bb_width": safe_round(latest.get("bb_width")),
            "atr": safe_round(latest.get("atr")),
            "momentum": safe_round(latest.get("momentum")),
            "daily_return": safe_round(latest.get("daily_return"), 4),
            "volatility": safe_round(latest.get("volatility"), 4),
        }

    @staticmethod
    def get_indicator_series(df: pd.DataFrame, indicator: str, limit: int = 100) -> list[dict]:
        """Get a time series for a specific indicator."""
        df = TechnicalService.compute_all_indicators(df)

        if indicator not in df.columns:
            return []

        series = df[[indicator]].dropna().tail(limit)
        result = []
        for idx, row in series.iterrows():
            result.append({
                "date": str(idx.date()) if hasattr(idx, "date") else str(idx),
                "value": round(float(row[indicator]), 4),
            })
        return result

    @staticmethod
    def get_full_indicators_series(df: pd.DataFrame, limit: int = 200) -> list[dict]:
        """Get full technical indicators as time series for charting."""
        df = TechnicalService.compute_all_indicators(df)
        df = df.tail(limit)

        records = []
        for idx, row in df.iterrows():
            record = {
                "date": str(idx.date()) if hasattr(idx, "date") else str(idx),
            }
            for col in df.columns:
                val = row[col]
                if pd.isna(val):
                    record[col] = None
                elif isinstance(val, (int, np.integer)):
                    record[col] = int(val)
                else:
                    record[col] = round(float(val), 4)
            records.append(record)

        return records
