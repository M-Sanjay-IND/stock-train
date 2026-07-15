"""
Stock Train - Data Preprocessing

Handles scaling, train/test splitting, and sequence creation
for both traditional ML and LSTM models.
"""

import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from typing import Tuple

logger = logging.getLogger("stockvision.ml.preprocessing")


def split_data(
    df: pd.DataFrame,
    target_col: str = "close",
    test_ratio: float = 0.2,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split data into train/test sets using random shuffling to allow
    models to interpolate across all historical price ranges.

    Returns:
        X_train, X_test, y_train, y_test
    """
    feature_cols = [c for c in df.columns if c != target_col]
    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_ratio, shuffle=False
    )

    logger.info(
        "Split data (chronological): train=%d, test=%d (%.0f%% test)",
        len(X_train), len(X_test), test_ratio * 100
    )
    return X_train, X_test, y_train, y_test

def scale_data(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray, RobustScaler]:
    """
    Apply RobustScaler to features.
    RobustScaler is more resilient to outliers in stock data
    (e.g. earnings jumps, flash crashes) compared to MinMaxScaler.

    Returns:
        scaled_X_train, scaled_X_test, fitted_scaler
    """
    scaler = RobustScaler()
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
    Uses MinMaxScaler for the target since LSTM output activation needs bounded range.

    Returns:
        scaled_y, target_scaler
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    y_scaled = scaler.fit_transform(y_train.values.reshape(-1, 1)).flatten()
    return y_scaled, scaler
