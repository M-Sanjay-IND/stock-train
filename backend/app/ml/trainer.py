"""
Stock Train - Model Trainer

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

# Minimum R² score for a model to be considered viable for best-model selection
MIN_R2_FOR_BEST = 0.5


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
        epochs: int = 100,
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

        sma_50_test = X_test["sma_50"].values

        for model_name, model in baseline_models:
            try:
                logger.info("Training %s for %s...", model_name, ticker)
                train_info = model.train(X_train_np, y_train_np)
                
                # Predict on detrended target
                y_pred_detrended = model.predict(X_test_np)
                
                # Reconstruct absolute price
                y_pred_real = y_pred_detrended + sma_50_test
                y_test_real = y_test_np + sma_50_test

                from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
                rmse = float(np.sqrt(mean_squared_error(y_test_real, y_pred_real)))
                mae = float(mean_absolute_error(y_test_real, y_pred_real))
                r2 = float(r2_score(y_test_real, y_pred_real))
                mask = y_test_real != 0
                mape = float(np.mean(np.abs((y_test_real[mask] - y_pred_real[mask]) / y_test_real[mask])) * 100) if mask.any() else None

                metrics = {
                    "rmse": rmse,
                    "mae": mae,
                    "mape": mape,
                    "r2_score": r2,
                }

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
                metrics["model_type"] = model_name

            except Exception as e:
                logger.error("Error training %s: %s", model_name, str(e))
                results["models"][model_name] = {"error": str(e)}

        # --- Train LSTM (needs sequences) ---
        try:
            logger.info("Training LSTM for %s...", ticker)
            from app.ml.models.lstm_model import LSTMModel

            # Validate minimum data for LSTM sequences
            min_lstm_samples = lookback + 20  # At least 20 sequences for meaningful training
            if len(X_train) < min_lstm_samples:
                raise ValueError(
                    f"Not enough training data for LSTM: {len(X_train)} rows, "
                    f"need at least {min_lstm_samples} (lookback={lookback} + 20 sequences)"
                )

            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import RobustScaler, MinMaxScaler

            # Scale entire chronological dataset first since X_train is already shuffled
            X_all = featured_df.drop(columns=[target_col])
            y_all = featured_df[target_col]

            feature_scaler = RobustScaler()
            X_all_scaled = feature_scaler.fit_transform(X_all)

            target_scaler = MinMaxScaler(feature_range=(0, 1))
            y_all_scaled = target_scaler.fit_transform(y_all.values.reshape(-1, 1)).flatten()

            # Create sequences from the chronological scaled data
            X_all_seq, y_all_seq = create_sequences(X_all_scaled, y_all_scaled, lookback)
            sma_50_all = featured_df["sma_50"].values[lookback:]

            # Chronological split the sequences
            X_train_seq, X_test_seq, y_train_seq, y_test_seq, sma_train, sma_test = train_test_split(
                X_all_seq, y_all_seq, sma_50_all, test_size=0.2, shuffle=False
            )

            if len(X_train_seq) < 30:
                raise ValueError(
                    f"Not enough LSTM training sequences: {len(X_train_seq)}, need at least 30"
                )
            if len(X_test_seq) < 5:
                raise ValueError(
                    f"Not enough LSTM test sequences: {len(X_test_seq)}, need at least 5"
                )

            # Split training for validation (85/15)
            val_split = int(len(X_train_seq) * 0.85)
            X_tr, X_vl = X_train_seq[:val_split], X_train_seq[val_split:]
            y_tr, y_vl = y_train_seq[:val_split], y_train_seq[val_split:]

            lstm = LSTMModel(lookback=lookback, epochs=epochs)
            train_info = lstm.train(X_tr, y_tr, X_vl, y_vl)

            # Evaluate on scaled test data, then inverse transform and reconstruct real prices
            y_pred_scaled = lstm.predict(X_test_seq)
            y_pred_real_detrended = target_scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
            y_test_real_detrended = target_scaler.inverse_transform(y_test_seq.reshape(-1, 1)).flatten()

            y_pred_real = y_pred_real_detrended + sma_test
            y_test_real = y_test_real_detrended + sma_test

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

            logger.info("LSTM evaluation: RMSE=%.4f, MAE=%.4f, R²=%.4f", rmse, mae, r2)

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
        # Only consider models with R² >= MIN_R2_FOR_BEST to prevent poorly-trained
        # models (especially LSTM) from hijacking predictions
        valid_metrics = [
            m for m in results["comparison"]
            if "rmse" in m and m["rmse"] is not None
            and "r2_score" in m and m["r2_score"] is not None
            and m["r2_score"] >= MIN_R2_FOR_BEST
        ]

        if valid_metrics:
            best = min(valid_metrics, key=lambda x: x["rmse"])
            results["best_model"] = best["model_type"]
            logger.info("Best model for %s: %s (RMSE=%.4f, R²=%.4f)",
                        ticker, best["model_type"], best["rmse"], best["r2_score"])
        else:
            # Fallback: if no model meets R² threshold, pick the best available
            all_valid = [m for m in results["comparison"] if "rmse" in m and m["rmse"] is not None]
            if all_valid:
                best = min(all_valid, key=lambda x: x["rmse"])
                results["best_model"] = best["model_type"]
                logger.warning(
                    "No model met R²>=%.2f threshold for %s, falling back to %s (R²=%.4f)",
                    MIN_R2_FOR_BEST, ticker, best["model_type"],
                    best.get("r2_score", 0)
                )

        # Save feature columns for prediction
        feature_cols_path = os.path.join(self.saved_models_dir, f"{ticker}_feature_columns.json")
        with open(feature_cols_path, "w") as f:
            json.dump(list(X_train.columns), f)

        logger.info("=== Training pipeline complete for %s ===", ticker)
        return results
