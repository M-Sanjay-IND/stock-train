"""
StockVision AI - Model Manager

Manages model lifecycle: checking freshness, loading saved models,
and deciding whether to retrain or serve cached predictions.
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.repositories.stock_repository import StockRepository
from app.services.data_service import DataService

logger = logging.getLogger("stockvision.ml.model_manager")


class ModelManager:
    """Manages ML model lifecycle and caching."""

    def __init__(self, saved_models_dir: str, cache_hours: int = 24):
        self.saved_models_dir = saved_models_dir
        self.cache_hours = cache_hours

    def is_model_fresh(self, ticker: str, model_type: str, current_data_hash: str) -> bool:
        """
        Check if a saved model is still fresh (recent + matching data).

        A model is considered fresh if:
        1. It exists in the database
        2. It was trained within the last cache_hours
        3. The training data hash matches current data
        """
        model_record = StockRepository.get_trained_model(ticker, model_type)

        if model_record is None:
            logger.info("No saved model for %s/%s", ticker, model_type)
            return False

        # Check file exists
        if not os.path.exists(model_record.model_path):
            logger.warning("Model file missing: %s", model_record.model_path)
            return False

        # Check age
        if model_record.trained_at:
            age = datetime.now(timezone.utc) - model_record.trained_at.replace(tzinfo=timezone.utc)
            if age > timedelta(hours=self.cache_hours):
                logger.info("Model %s/%s is stale (age: %s)", ticker, model_type, age)
                return False

        # Check data hash
        if model_record.data_hash and model_record.data_hash != current_data_hash:
            logger.info("Data hash changed for %s/%s", ticker, model_type)
            return False

        logger.info("Model %s/%s is fresh", ticker, model_type)
        return True

    def has_any_models(self, ticker: str) -> bool:
        """Check if any trained models exist for a ticker."""
        models = StockRepository.get_all_trained_models(ticker)
        return len(models) > 0

    def get_best_model_type(self, ticker: str) -> Optional[str]:
        """Get the type of the best model for a ticker."""
        best = StockRepository.get_best_model(ticker)
        return best.model_type if best else None

    def get_all_metrics(self, ticker: str) -> list[dict]:
        """Get metrics for all trained models."""
        models = StockRepository.get_all_trained_models(ticker)
        return [m.to_dict() for m in models]

    def needs_training(self, ticker: str, data_hash: str) -> bool:
        """Check if a ticker needs model training."""
        if not self.has_any_models(ticker):
            return True

        best_type = self.get_best_model_type(ticker)
        if best_type is None:
            return True

        return not self.is_model_fresh(ticker, best_type, data_hash)
