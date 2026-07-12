"""
StockVision AI - Feature Engineering

Builds feature matrices from raw OHLCV data combined with technical indicators
for use in ML model training and prediction.
"""

import logging
import numpy as np
import pandas as pd

from app.services.technical_service import TechnicalService

logger = logging.getLogger("stockvision.ml.features")


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a complete feature matrix from raw price data.

    Takes OHLCV DataFrame, computes all technical indicators,
    adds engineered features, and returns a clean DataFrame
    ready for model consumption.

    Args:
        df: DataFrame with columns [open, high, low, close, volume]

    Returns:
        DataFrame with all features, NaN rows dropped.
    """
    if df.empty or len(df) < 60:
        logger.warning("Insufficient data for feature engineering (%d rows)", len(df))
        return pd.DataFrame()

    # Compute all technical indicators
    featured = TechnicalService.compute_all_indicators(df)

    # Ensure lowercase
    featured.columns = [c.lower() for c in featured.columns]

    # Additional features for ML
    close = featured["close"]

    # Price ratios
    featured["close_to_sma20"] = close / featured["sma_20"].replace(0, np.nan)
    featured["close_to_sma50"] = close / featured["sma_50"].replace(0, np.nan)

    # Volume features
    if "volume" in featured.columns:
        featured["volume_sma_20"] = featured["volume"].rolling(20).mean()
        featured["volume_ratio"] = featured["volume"] / featured["volume_sma_20"].replace(0, np.nan)

    # Price range
    if "high" in featured.columns and "low" in featured.columns:
        featured["price_range"] = featured["high"] - featured["low"]
        featured["price_range_pct"] = featured["price_range"] / close.replace(0, np.nan)

    # Drop rows with NaN (from indicator warm-up period)
    featured.dropna(inplace=True)

    logger.info("Built features: %d rows, %d columns", len(featured), len(featured.columns))
    return featured


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """
    Get the list of feature columns to use for training.
    Excludes target and non-feature columns.
    """
    exclude = {"date", "adj_close", "dividends", "stock_splits", "stock splits"}
    return [c for c in df.columns if c.lower() not in exclude]


def get_target_column() -> str:
    """Return the target column name."""
    return "close"
