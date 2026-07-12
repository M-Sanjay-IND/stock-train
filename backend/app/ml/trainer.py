"""
StockVision AI - Model Trainer

Orchestrates training of all models, compares metrics,
and identifies the best-performing model for each ticker.
"""

import logging
import os
import json
import numpy as np
import pandas as pd
import joblib


from app.ml.feature_engineering import build_features, get_target_column
from app.ml.preprocessing import split_data, scale_data, create_sequences, create_target_scaler
from app.ml.models.linear_model import LinearModel
from app.ml.models.random_forest_model import RandomForestModel
from app.ml.models.xgboost_model import XGBoostModel

from app.repositories.stock_repository import StockRepository
from app.services.data_service import DataService

logger = logging.getLogger("stockvision.ml.trainer")


class Trainer:
    """Orchestrates training of all ML models for a given stock."""

    def __init__(self, saved_models_dir: str):
        self.saved_models_dir = saved_models_dir
        os.makedirs(saved_models_dir, exist_ok=True)

    def train_all_models(
        self,
        ticker: str,
        df: pd.DataFrame,
        lookback: int = 60,
        epochs: int = 50,
    ) -> dict:
        """
        Train all models (Linear, RF, XGBoost, LSTM) and compare.

        Returns:
            dict with model results, comparison, and best model info.
        """
        ticker = ticker.upper()
        logger.info("=== Starting full training pipeline for %s ===", ticker)

        # Build features
        featured_df = build_features(df)
        if featured_df.empty:
            return {"error": "Insufficient data for training", "ticker": ticker}

        target_col = get_target_column()

        # Data hash for cache invalidation
        data_hash = DataService.compute_data_hash(featured_df)

        # Split data
        X_train, X_test, y_train, y_test = split_data(featured_df, target_col=target_col)

        results = {
            "ticker": ticker,
            "data_points": len(featured_df),
            "train_size": len(X_train),
            "test_size": len(X_test),
            "features_count": len(X_train.columns),
            "models": {},
            "comparison": [],
            "best_model": None,
            "data_hash": data_hash,
        }

        # --- Train baseline models (on raw features) ---
        X_train_np = X_train.values
        X_test_np = X_test.values
        y_train_np = y_train.values
        y_test_np = y_test.values

        baseline_models = [
            ("linear_regression", LinearModel()),
            ("random_forest", RandomForestModel()),
            ("xgboost", XGBoostModel()),
        ]

        for model_name, model in baseline_models:
            try:
                logger.info("Training %s for %s...", model_name, ticker)
                train_info = model.train(X_train_np, y_train_np)
                metrics = model.evaluate(X_test_np, y_test_np)

                # Save model
                model_path = os.path.join(self.saved_models_dir, f"{ticker}_{model_name}.joblib")
                joblib.dump(model.model, model_path)

                # Save to DB
                StockRepository.upsert_trained_model(ticker, model_name, {
                    "model_path": model_path,
                    "rmse": metrics["rmse"],
                    "mae": metrics["mae"],
                    "mape": metrics["mape"],
                    "r2_score": metrics["r2_score"],
                    "data_hash": data_hash,
                })

                results["models"][model_name] = {**train_info, **metrics}
                results["comparison"].append(metrics)

            except Exception as e:
                logger.error("Error training %s: %s", model_name, str(e))
                results["models"][model_name] = {"error": str(e)}

        # --- Train LSTM (needs sequences) ---
        try:
            logger.info("Training LSTM for %s...", ticker)

            # Scale features
            from app.ml.models.lstm_model import LSTMModel
            X_train_scaled, X_test_scaled, feature_scaler = scale_data(X_train, X_test)

            # Scale target separately (for inverse transform)
            y_train_scaled, target_scaler = create_target_scaler(y_train)
            y_test_scaled = target_scaler.transform(y_test.values.reshape(-1, 1)).flatten()

            # Create sequences
            X_train_seq, y_train_seq = create_sequences(X_train_scaled, y_train_scaled, lookback)
            X_test_seq, y_test_seq = create_sequences(X_test_scaled, y_test_scaled, lookback)

            if len(X_train_seq) < 10 or len(X_test_seq) < 5:
                raise ValueError("Not enough data for LSTM sequences")

            # Split training for validation
            val_split = int(len(X_train_seq) * 0.85)
            X_tr, X_vl = X_train_seq[:val_split], X_train_seq[val_split:]
            y_tr, y_vl = y_train_seq[:val_split], y_train_seq[val_split:]

            lstm = LSTMModel(lookback=lookback, epochs=epochs)
            train_info = lstm.train(X_tr, y_tr, X_vl, y_vl)

            # Evaluate on scaled test data, then inverse transform for real metrics
            y_pred_scaled = lstm.predict(X_test_seq)
            y_pred_real = target_scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
            y_test_real = target_scaler.inverse_transform(y_test_seq.reshape(-1, 1)).flatten()

            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            rmse = float(np.sqrt(mean_squared_error(y_test_real, y_pred_real)))
            mae = float(mean_absolute_error(y_test_real, y_pred_real))
            r2 = float(r2_score(y_test_real, y_pred_real))
            mask = y_test_real != 0
            mape = float(np.mean(np.abs((y_test_real[mask] - y_pred_real[mask]) / y_test_real[mask])) * 100) if mask.any() else None

            lstm_metrics = {
                "model_type": "lstm",
                "rmse": rmse,
                "mae": mae,
                "mape": mape,
                "r2_score": r2,
            }

            # Save LSTM model + scalers
            model_path = os.path.join(self.saved_models_dir, f"{ticker}_lstm.keras")
            feature_scaler_path = os.path.join(self.saved_models_dir, f"{ticker}_lstm_feature_scaler.joblib")
            target_scaler_path = os.path.join(self.saved_models_dir, f"{ticker}_lstm_target_scaler.joblib")

            lstm.save(model_path)
            joblib.dump(feature_scaler, feature_scaler_path)
            joblib.dump(target_scaler, target_scaler_path)

            # Save to DB
            StockRepository.upsert_trained_model(ticker, "lstm", {
                "model_path": model_path,
                "scaler_path": feature_scaler_path,
                "rmse": rmse,
                "mae": mae,
                "mape": mape,
                "r2_score": r2,
                "data_hash": data_hash,
                "training_loss": train_info.get("training_loss"),
                "validation_loss": train_info.get("validation_loss"),
            })

            results["models"]["lstm"] = {**train_info, **lstm_metrics}
            results["comparison"].append(lstm_metrics)

        except Exception as e:
            logger.error("Error training LSTM: %s", str(e), exc_info=True)
            results["models"]["lstm"] = {"error": str(e)}

        # --- Determine best model ---
        valid_metrics = [m for m in results["comparison"] if "rmse" in m and m["rmse"] is not None]
        if valid_metrics:
            best = min(valid_metrics, key=lambda x: x["rmse"])
            results["best_model"] = best["model_type"]
            logger.info("Best model for %s: %s (RMSE=%.4f)", ticker, best["model_type"], best["rmse"])

        # Save feature columns for prediction
        feature_cols_path = os.path.join(self.saved_models_dir, f"{ticker}_feature_columns.json")
        with open(feature_cols_path, "w") as f:
            json.dump(list(X_train.columns), f)

        logger.info("=== Training pipeline complete for %s ===", ticker)
        return results
