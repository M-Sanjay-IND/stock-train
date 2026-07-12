"""
StockVision AI - Random Forest Regressor Model Wrapper
"""

import logging
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

logger = logging.getLogger("stockvision.ml.random_forest")


class RandomForestModel:
    """Random Forest model for stock price forecasting."""

    def __init__(self, n_estimators: int = 100, max_depth: int = 15, random_state: int = 42):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
        )
        self.name = "random_forest"

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> dict:
        """Train the model."""
        logger.info("Training Random Forest (samples=%d, features=%d)", *X_train.shape)
        self.model.fit(X_train, y_train)

        # Feature importance (top 10)
        importances = self.model.feature_importances_
        top_indices = np.argsort(importances)[-10:][::-1]

        return {
            "model_type": self.name,
            "status": "trained",
            "n_estimators": self.model.n_estimators,
            "feature_importance_indices": top_indices.tolist(),
        }

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
        logger.info("Random Forest metrics: RMSE=%.4f, MAE=%.4f, R²=%.4f", rmse, mae, r2)
        return metrics
