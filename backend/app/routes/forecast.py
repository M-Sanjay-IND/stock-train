"""
StockVision AI - Forecast & Metrics Routes
"""

import logging
from flask import Blueprint, jsonify
from app.services.forecast_service import ForecastService
from app.ml.model_manager import ModelManager
from flask import current_app

logger = logging.getLogger("stockvision.routes.forecast")

forecast_bp = Blueprint("forecast", __name__)


@forecast_bp.route("/forecast/<ticker>", methods=["GET"])
def get_forecast(ticker: str):
    """Get price forecast for a stock."""
    try:
        result = ForecastService.get_forecast(ticker)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result)

    except Exception as e:
        logger.error("Error generating forecast for %s: %s", ticker, str(e), exc_info=True)
        return jsonify({"error": str(e)}), 500


@forecast_bp.route("/train/<ticker>", methods=["POST"])
def train_models(ticker: str):
    """Force retrain all models for a stock."""
    try:
        result = ForecastService.force_train(ticker)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result)

    except Exception as e:
        logger.error("Error training models for %s: %s", ticker, str(e), exc_info=True)
        return jsonify({"error": str(e)}), 500


@forecast_bp.route("/metrics/<ticker>", methods=["GET"])
def get_metrics(ticker: str):
    """Get model metrics for a stock."""
    try:
        saved_dir = current_app.config["SAVED_MODELS_DIR"]
        cache_hours = current_app.config["MODEL_CACHE_HOURS"]
        manager = ModelManager(saved_dir, cache_hours=cache_hours)

        metrics = manager.get_all_metrics(ticker)
        best_type = manager.get_best_model_type(ticker)

        if not metrics:
            return jsonify({
                "ticker": ticker.upper(),
                "message": "No trained models found. Train models first.",
                "models": [],
            })

        return jsonify({
            "ticker": ticker.upper(),
            "best_model": best_type,
            "models": metrics,
        })

    except Exception as e:
        logger.error("Error fetching metrics for %s: %s", ticker, str(e))
        return jsonify({"error": str(e)}), 500
