"""
StockVision AI - LSTM Model

Deep learning model using Keras/TensorFlow for sequential stock price forecasting.
Architecture: 3 LSTM layers with Dropout + Dense output.
"""

import logging
import numpy as np
from typing import Optional

logger = logging.getLogger("stockvision.ml.lstm")


class LSTMModel:
    """LSTM neural network for time-series stock price forecasting."""

    def __init__(
        self,
        lookback: int = 60,
        epochs: int = 50,
        batch_size: int = 32,
        learning_rate: float = 0.001,
    ):
        self.lookback = lookback
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.model = None
        self.history = None
        self.name = "lstm"

    def build_model(self, input_shape: tuple) -> None:
        """
        Build the LSTM architecture.

        Architecture:
            LSTM(128) → Dropout(0.2) → LSTM(64) → Dropout(0.2)
            → LSTM(32) → Dropout(0.2) → Dense(16) → Dense(1)
        """
        import tensorflow as tf
        from tensorflow import keras
        from tensorflow.keras import layers

        model = keras.Sequential([
            layers.LSTM(128, return_sequences=True, input_shape=input_shape),
            layers.Dropout(0.2),
            layers.LSTM(64, return_sequences=True),
            layers.Dropout(0.2),
            layers.LSTM(32, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(16, activation="relu"),
            layers.Dense(1),
        ])

        optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)
        model.compile(optimizer=optimizer, loss="mse", metrics=["mae"])

        self.model = model
        logger.info("Built LSTM model: %s", model.summary(print_fn=lambda x: None) or "OK")

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
    ) -> dict:
        """
        Train the LSTM model with EarlyStopping.

        Args:
            X_train: Shape (n_samples, lookback, n_features)
            y_train: Shape (n_samples,)
            X_val: Optional validation data
            y_val: Optional validation targets
        """
        from tensorflow.keras.callbacks import EarlyStopping

        if self.model is None:
            self.build_model(input_shape=(X_train.shape[1], X_train.shape[2]))

        callbacks = [
            EarlyStopping(
                monitor="val_loss" if X_val is not None else "loss",
                patience=10,
                restore_best_weights=True,
                verbose=1,
            ),
        ]

        validation_data = (X_val, y_val) if X_val is not None else None

        logger.info(
            "Training LSTM: epochs=%d, batch=%d, samples=%d",
            self.epochs, self.batch_size, len(X_train)
        )

        self.history = self.model.fit(
            X_train,
            y_train,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_data=validation_data,
            callbacks=callbacks,
            verbose=1,
        )

        result = {
            "model_type": self.name,
            "status": "trained",
            "epochs_run": len(self.history.history["loss"]),
            "training_loss": [round(float(v), 6) for v in self.history.history["loss"]],
        }

        if "val_loss" in self.history.history:
            result["validation_loss"] = [round(float(v), 6) for v in self.history.history["val_loss"]]

        return result

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions."""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        predictions = self.model.predict(X, verbose=0)
        return predictions.flatten()

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """Evaluate model and return metrics."""
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

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
        logger.info("LSTM metrics: RMSE=%.4f, MAE=%.4f, R²=%.4f", rmse, mae, r2)
        return metrics

    def save(self, path: str) -> None:
        """Save model to .keras format."""
        if self.model is None:
            raise ValueError("No model to save")
        self.model.save(path)
        logger.info("LSTM model saved to %s", path)

    def load(self, path: str) -> None:
        """Load model from .keras format."""
        from tensorflow import keras
        self.model = keras.models.load_model(path)
        logger.info("LSTM model loaded from %s", path)
