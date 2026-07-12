"""
StockVision AI - Forecast Service

Orchestrates the forecast workflow:
1. Fetch data
2. Check model freshness
3. Train if needed
4. Generate predictions
"""

import logging
from flask import current_app

from app.services.data_service import DataService
from app.ml.feature_engineering import build_features
from app.ml.model_manager import ModelManager
from app.ml.trainer import Trainer
from app.ml.predictor import Predictor

logger = logging.getLogger("stockvision.forecast_service")


class ForecastService:
    """Orchestrates the full forecast workflow."""

    @staticmethod
    def get_forecast(ticker: str) -> dict:
        """
        Get a forecast for a ticker. Trains models if needed.
        """
        ticker = ticker.upper()
        config = current_app.config
        saved_dir = config["SAVED_MODELS_DIR"]
        cache_hours = config["MODEL_CACHE_HOURS"]
        lookback = config["LSTM_LOOKBACK"]
        epochs = config["LSTM_EPOCHS"]

        # Step 1: Fetch latest data
        df = DataService.fetch_history(ticker)
        if df.empty:
            return {"error": f"No data available for {ticker}"}

        # Step 2: Check if we need training
        featured_df = build_features(df)
        if featured_df.empty:
            return {"error": f"Insufficient data for {ticker} (need >= 60 data points)"}

        data_hash = DataService.compute_data_hash(featured_df)
        manager = ModelManager(saved_dir, cache_hours=cache_hours)

        if manager.needs_training(ticker, data_hash):
            logger.info("Models need training for %s", ticker)
            trainer = Trainer(saved_dir)
            training_result = trainer.train_all_models(
                ticker, df, lookback=lookback, epochs=epochs
            )

            if "error" in training_result:
                return training_result

        # Step 3: Generate predictions
        predictor = Predictor(saved_dir, lookback=lookback)
        forecast = predictor.predict_with_best_model(ticker, df)

        # Step 4: Add model comparison data
        all_metrics = manager.get_all_metrics(ticker)
        forecast["all_models"] = all_metrics

        return forecast

    @staticmethod
    def force_train(ticker: str) -> dict:
        """Force retrain all models for a ticker."""
        ticker = ticker.upper()
        config = current_app.config
        saved_dir = config["SAVED_MODELS_DIR"]
        lookback = config["LSTM_LOOKBACK"]
        epochs = config["LSTM_EPOCHS"]

        df = DataService.fetch_history(ticker, force_refresh=True)
        if df.empty:
            return {"error": f"No data available for {ticker}"}

        trainer = Trainer(saved_dir)
        return trainer.train_all_models(ticker, df, lookback=lookback, epochs=epochs)
