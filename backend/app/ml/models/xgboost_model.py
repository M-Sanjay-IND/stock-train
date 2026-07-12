"""
StockVision AI - XGBoost Model Wrapper

Falls back to GradientBoosting if XGBoost is not installed.
"""

import logging
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

logger = logging.getLogger("stockvision.ml.xgboost")

try:
    from xgboost import XGBRegressor
    HAS_XGBOOST = True
except ImportError:
    from sklearn.ensemble import GradientBoostingRegressor
    HAS_XGBOOST = False
    logger.warning("XGBoost not available, falling back to GradientBoostingRegressor")


class XGBoostModel:
    """XGBoost model for stock price forecasting (with sklearn fallback)."""

    def __init__(self, n_estimators: int = 200, max_depth: int = 6, learning_rate: float = 0.1):
        if HAS_XGBOOST:
            self.model = XGBRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=learning_rate,
                random_state=42,
                verbosity=0,
            )
        else:
            self.model = GradientBoostingRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=learning_rate,
                random_state=42,
            )
        self.name = "xgboost"

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> dict:
        """Train the model."""
        logger.info(
            "Training %s (samples=%d, features=%d)",
            "XGBoost" if HAS_XGBOOST else "GradientBoosting",
            *X_train.shape
        )
        self.model.fit(X_train, y_train)
        return {"model_type": self.name, "status": "trained", "backend": "xgboost" if HAS_XGBOOST else "sklearn"}

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions."""
        return self.model.predict(X)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """Evaluate model and return metrics."""
        y_pred = self.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))

        mask = y_test != 0
        mape = float(np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100) if mask.any() else None

        metrics = {
            "model_type": self.name,
            "rmse": rmse,
            "mae": mae,
            "mape": mape,
            "r2_score": r2,
        }
        logger.info("XGBoost metrics: RMSE=%.4f, MAE=%.4f, R²=%.4f", rmse, mae, r2)
        return metrics
