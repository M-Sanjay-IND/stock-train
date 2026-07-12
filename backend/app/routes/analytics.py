"""
StockVision AI - Analytics Route
"""

import logging
from flask import Blueprint, jsonify, request
from app.services.data_service import DataService
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger("stockvision.routes.analytics")

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics/<ticker>", methods=["GET"])
def get_analytics(ticker: str):
    """Get financial analytics for a stock."""
    try:
        df = DataService.fetch_history(ticker)
        if df.empty:
            return jsonify({"error": f"No data for '{ticker}'"}), 404

        analytics = AnalyticsService.compute_analytics(df)

        # Also fetch stock info for complete picture
        info = DataService.fetch_stock_info(ticker)

        result = {
            "ticker": ticker.upper(),
            "analytics": analytics,
        }

        if info:
            result["info"] = info

        # Optional returns series
        if request.args.get("returns", "false").lower() == "true":
            period = request.args.get("returns_period", "daily")
            result["returns_series"] = AnalyticsService.compute_returns_series(df, period)

        return jsonify(result)

    except Exception as e:
        logger.error("Error computing analytics for %s: %s", ticker, str(e))
        return jsonify({"error": str(e)}), 500
