"""
StockVision AI - Linear Regression Model Wrapper
"""

import logging
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

logger = logging.getLogger("stockvision.ml.linear")


class LinearModel:
    """Linear Regression model for stock price forecasting (baseline)."""

    def __init__(self):
        self.model = LinearRegression()
        self.name = "linear_regression"

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> dict:
        """Train the model and return training info."""
        logger.info("Training Linear Regression (samples=%d, features=%d)", *X_train.shape)
        self.model.fit(X_train, y_train)
        return {"model_type": self.name, "status": "trained"}

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions."""
        return self.model.predict(X)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """Evaluate model and return metrics."""
        y_pred = self.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))

        # MAPE (avoid division by zero)
        mask = y_test != 0
        if mask.any():
            mape = float(np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100)
        else:
            mape = None

        metrics = {
            "model_type": self.name,
            "rmse": rmse,
            "mae": mae,
            "mape": mape,
            "r2_score": r2,
        }
        logger.info("Linear Regression metrics: RMSE=%.4f, MAE=%.4f, R²=%.4f", rmse, mae, r2)
        return metrics
