"""
StockVision AI - Technical Analysis Route
"""

import logging
from flask import Blueprint, jsonify, request
from app.services.data_service import DataService
from app.services.technical_service import TechnicalService

logger = logging.getLogger("stockvision.routes.technical")

technical_bp = Blueprint("technical", __name__)


@technical_bp.route("/technical/<ticker>", methods=["GET"])
def get_technical(ticker: str):
    """Get technical indicators for a stock."""
    try:
        df = DataService.fetch_history(ticker)
        if df.empty:
            return jsonify({"error": f"No data for '{ticker}'"}), 404

        limit = int(request.args.get("limit", 200))
        include_series = request.args.get("series", "true").lower() == "true"

        latest = TechnicalService.get_latest_indicators(df)

        result = {
            "ticker": ticker.upper(),
            "latest": latest,
        }

        if include_series:
            result["series"] = TechnicalService.get_full_indicators_series(df, limit=limit)

        return jsonify(result)

    except Exception as e:
        logger.error("Error computing technical indicators for %s: %s", ticker, str(e))
        return jsonify({"error": str(e)}), 500
