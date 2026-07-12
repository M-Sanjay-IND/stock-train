"""
StockVision AI - Data Preprocessing

Handles scaling, train/test splitting, and sequence creation
for both traditional ML and LSTM models.
"""

import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple

logger = logging.getLogger("stockvision.ml.preprocessing")


def split_data(
    df: pd.DataFrame,
    target_col: str = "close",
    test_ratio: float = 0.2,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split data into train/test sets (chronological, no shuffle).

    Returns:
        X_train, X_test, y_train, y_test
    """
    feature_cols = [c for c in df.columns if c != target_col]
    X = df[feature_cols]
    y = df[target_col]

    split_idx = int(len(df) * (1 - test_ratio))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    logger.info(
        "Split data: train=%d, test=%d (%.0f%% test)",
        len(X_train), len(X_test), test_ratio * 100
    )
    return X_train, X_test, y_train, y_test


def scale_data(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray, MinMaxScaler]:
    """
    Apply MinMaxScaler to features.

    Returns:
        scaled_X_train, scaled_X_test, fitted_scaler
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, scaler


def create_sequences(
    data: np.ndarray,
    target: np.ndarray,
    lookback: int = 60,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create sequences for LSTM input.

    Args:
        data: Scaled feature array (n_samples, n_features)
        target: Target values array
        lookback: Number of past timesteps to use

    Returns:
        X: (n_sequences, lookback, n_features)
        y: (n_sequences,)
    """
    X, y = [], []
    for i in range(lookback, len(data)):
        X.append(data[i - lookback:i])
        y.append(target[i])

    X = np.array(X)
    y = np.array(y)

    logger.info("Created %d sequences with lookback=%d, shape=%s", len(X), lookback, X.shape)
    return X, y


def create_target_scaler(y_train: pd.Series) -> Tuple[np.ndarray, MinMaxScaler]:
    """
    Create a separate scaler for the target variable (for inverse transform on predictions).

    Returns:
        scaled_y, target_scaler
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    y_scaled = scaler.fit_transform(y_train.values.reshape(-1, 1)).flatten()
    return y_scaled, scaler
