"""
Stock Train - Predictor

Loads saved models and generates future price predictions
with confidence intervals.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import joblib
from datetime import timezone
from typing import Optional

from app.ml.feature_engineering import build_features, get_target_column

from app.repositories.stock_repository import StockRepository

logger = logging.getLogger("stockvision.ml.predictor")


class Predictor:
    """Loads saved models and generates forecasts."""

    def __init__(self, saved_models_dir: str, lookback: int = 60):
        self.saved_models_dir = saved_models_dir
        self.lookback = lookback

    def predict(
        self,
        ticker: str,
        df: pd.DataFrame,
        forecast_days: list[int] = None,
        model_type: Optional[str] = None,
    ) -> dict:
        """
        Generate predictions using a specific model or the best available.

        Args:
            ticker: Stock ticker
            df: Historical price DataFrame
            forecast_days: List of forecast horizons [1, 7, 30]
            model_type: Optional specific model type to use

        Returns:
            dict with predictions, confidence intervals, and metadata
        """
        if forecast_days is None:
            forecast_days = [1, 7, 30]

        ticker = ticker.upper()
        
        if model_type:
            model_record = StockRepository.get_trained_model(ticker, model_type)
            if not model_record:
                return {"error": f"Model {model_type} not found for {ticker}.", "ticker": ticker}
        else:
            # get_best_model already has R² >= 0.5 guard
            model_record = StockRepository.get_best_model(ticker)
            if not model_record:
                return {"error": "No trained models found. Please train models first.", "ticker": ticker}

        actual_model_type = model_record.model_type
        logger.info("Predicting %s with %s model (R²=%.4f, RMSE=%.4f)",
                     ticker, actual_model_type,
                     model_record.r2_score or 0, model_record.rmse or 0)

        if actual_model_type == "lstm":
            return self._predict_lstm(ticker, df, forecast_days, model_record)
        else:
            return self._predict_baseline(ticker, df, forecast_days, model_record)

    def _predict_baseline(
        self,
        ticker: str,
        df: pd.DataFrame,
        forecast_days: list[int],
        model_record,
    ) -> dict:
        """Generate predictions with a baseline model (Linear/RF/XGBoost)."""
        try:
            # Load model
            model = joblib.load(model_record.model_path)

            # Build features
            featured_df = build_features(df)
            if featured_df.empty:
                return {"error": "Insufficient data for prediction"}

            target_col = get_target_column()
            feature_cols = [c for c in featured_df.columns if c != target_col]
            X = featured_df[feature_cols].values

            # Predict on the existing data (for actual vs predicted chart)
            all_predictions_detrended = model.predict(X)
            actual_detrended = featured_df[target_col].values
            sma_50_values = featured_df["sma_50"].values

            all_predictions_real = all_predictions_detrended + sma_50_values
            actual_values_real = actual_detrended + sma_50_values

            # Create actual vs predicted series
            actual_vs_predicted = []
            for i in range(len(featured_df)):
                date_val = featured_df.index[i]
                actual_vs_predicted.append({
                    "date": str(date_val.date()) if hasattr(date_val, "date") else str(date_val),
                    "actual": round(float(actual_values_real[i]), 2),
                    "predicted": round(float(all_predictions_real[i]), 2),
                })

            # Future forecast using last known features with trend adjustment
            last_features = X[-1:]
            current_price = float(actual_values_real[-1])
            current_sma_50 = float(sma_50_values[-1])
            forecasts = {}

            for days in forecast_days:
                predicted_detrended = float(model.predict(last_features)[0])
                base_forecast_price = predicted_detrended + current_sma_50

                # Calculate daily change rate from recent absolute predictions
                if len(all_predictions_real) > 5:
                    recent_changes = np.diff(all_predictions_real[-10:]) / all_predictions_real[-10:-1]
                    avg_daily_change = float(np.mean(recent_changes))
                else:
                    avg_daily_change = 0

                # Project forward
                daily_predictions = []
                for d in range(1, days + 1):
                    daily_price = base_forecast_price * (1 + avg_daily_change * d)
                    daily_predictions.append(round(daily_price, 2))

                forecast_price = daily_predictions[-1]
                pct_change = ((forecast_price - current_price) / current_price) * 100

                # Confidence interval (based on model RMSE)
                rmse = model_record.rmse or 0
                confidence = rmse * np.sqrt(days)

                forecasts[f"{days}_day"] = {
                    "days": days,
                    "predicted_price": round(forecast_price, 2),
                    "current_price": round(current_price, 2),
                    "change_pct": round(pct_change, 2),
                    "trend": "bullish" if pct_change > 0 else "bearish",
                    "confidence_upper": round(forecast_price + confidence, 2),
                    "confidence_lower": round(max(0, forecast_price - confidence), 2),
                    "daily_predictions": daily_predictions,
                }

            return {
                "ticker": ticker,
                "model_type": model_record.model_type,
                "current_price": round(current_price, 2),
                "forecasts": forecasts,
                "actual_vs_predicted": actual_vs_predicted[-100:],  # Last 100 points
                "metrics": {
                    "rmse": model_record.rmse,
                    "mae": model_record.mae,
                    "mape": model_record.mape,
                    "r2_score": model_record.r2_score,
                },
                "trained_at": model_record.trained_at.replace(tzinfo=timezone.utc).isoformat() if model_record.trained_at else None,
            }

        except Exception as e:
            logger.error("Baseline prediction error: %s", str(e), exc_info=True)
            return {"error": str(e), "ticker": ticker}

    def _predict_lstm(
        self,
        ticker: str,
        df: pd.DataFrame,
        forecast_days: list[int],
        model_record,
    ) -> dict:
        """Generate predictions with LSTM model."""
        try:
            from app.ml.models.lstm_model import LSTMModel

            # Load model and scalers
            lstm = LSTMModel(lookback=self.lookback)
            lstm.load(model_record.model_path)

            feature_scaler_path = os.path.join(self.saved_models_dir, f"{ticker}_lstm_feature_scaler.joblib")
            target_scaler_path = os.path.join(self.saved_models_dir, f"{ticker}_lstm_target_scaler.joblib")

            feature_scaler = joblib.load(feature_scaler_path)
            target_scaler = joblib.load(target_scaler_path)

            # Build features
            featured_df = build_features(df)
            if featured_df.empty:
                return {"error": "Insufficient data for LSTM prediction"}

            target_col = get_target_column()
            feature_cols = [c for c in featured_df.columns if c != target_col]
            X_all = featured_df[feature_cols].values
            y_all = featured_df[target_col].values
            sma_50_values = featured_df["sma_50"].values

            # Scale
            X_scaled = feature_scaler.transform(X_all)

            # Create sequences for evaluation
            X_seq, y_seq_idx = [], []
            for i in range(self.lookback, len(X_scaled)):
                X_seq.append(X_scaled[i - self.lookback:i])
                y_seq_idx.append(i)
            X_seq = np.array(X_seq)

            # Predict on all sequences
            y_pred_scaled = lstm.predict(X_seq)
            y_pred_detrended = target_scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()

            # Actual vs predicted series
            actual_vs_predicted = []
            for i, idx in enumerate(y_seq_idx):
                date_val = featured_df.index[idx]
                sma_val = float(sma_50_values[idx])
                actual_vs_predicted.append({
                    "date": str(date_val.date()) if hasattr(date_val, "date") else str(date_val),
                    "actual": round(float(y_all[idx]) + sma_val, 2),
                    "predicted": round(float(y_pred_detrended[i]) + sma_val, 2),
                })

            # Future forecasts
            current_price = float(y_all[-1]) + float(sma_50_values[-1])
            current_sma_50 = float(sma_50_values[-1])
            last_sequence = X_scaled[-self.lookback:]  # (lookback, features)
            forecasts = {}

            for days in forecast_days:
                # Iterative prediction for multi-step
                seq = last_sequence.copy()
                predictions = []

                for d in range(days):
                    inp = seq.reshape(1, self.lookback, -1)
                    pred_scaled = lstm.predict(inp)
                    pred_detrended = float(target_scaler.inverse_transform(pred_scaled.reshape(-1, 1))[0, 0])
                    pred_price = pred_detrended + current_sma_50
                    predictions.append(pred_price)

                    # Roll the sequence forward (shift by 1, reuse last row features)
                    new_row = seq[-1].copy()
                    seq = np.roll(seq, -1, axis=0)
                    seq[-1] = new_row

                forecast_price = predictions[-1] if predictions else current_price
                pct_change = ((forecast_price - current_price) / current_price) * 100

                rmse = model_record.rmse or 0
                confidence = rmse * np.sqrt(days)

                forecasts[f"{days}_day"] = {
                    "days": days,
                    "predicted_price": round(forecast_price, 2),
                    "current_price": round(current_price, 2),
                    "change_pct": round(pct_change, 2),
                    "trend": "bullish" if pct_change > 0 else "bearish",
                    "confidence_upper": round(forecast_price + confidence, 2),
                    "confidence_lower": round(max(0, forecast_price - confidence), 2),
                    "daily_predictions": [round(p, 2) for p in predictions],
                }

            return {
                "ticker": ticker,
                "model_type": "lstm",
                "current_price": round(current_price, 2),
                "forecasts": forecasts,
                "actual_vs_predicted": actual_vs_predicted[-100:],
                "metrics": {
                    "rmse": model_record.rmse,
                    "mae": model_record.mae,
                    "mape": model_record.mape,
                    "r2_score": model_record.r2_score,
                },
                "training_loss": model_record.to_dict().get("training_loss"),
                "validation_loss": model_record.to_dict().get("validation_loss"),
                "trained_at": model_record.trained_at.replace(tzinfo=timezone.utc).isoformat() if model_record.trained_at else None,
            }

        except Exception as e:
            logger.error("LSTM prediction error: %s", str(e), exc_info=True)
            return {"error": str(e), "ticker": ticker}
