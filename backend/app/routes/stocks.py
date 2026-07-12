"""
StockVision AI - Stock Routes

Handles stock search, info, and historical data endpoints.
"""

import logging
from flask import Blueprint, jsonify, request
from app.services.data_service import DataService

logger = logging.getLogger("stockvision.routes.stocks")

stocks_bp = Blueprint("stocks", __name__)


@stocks_bp.route("/stocks/search", methods=["GET"])
def search_stocks():
    """Search for stocks by ticker or company name."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    results = DataService.search_tickers(query)
    return jsonify({"results": results, "count": len(results)})


@stocks_bp.route("/stocks/info/<ticker>", methods=["GET"])
def get_stock_info(ticker: str):
    """Get detailed stock information."""
    info = DataService.fetch_stock_info(ticker)
    if info is None:
        return jsonify({"error": f"Stock '{ticker}' not found"}), 404

    return jsonify({"data": info})


@stocks_bp.route("/history/<ticker>", methods=["GET"])
def get_history(ticker: str):
    """Get historical price data for a stock."""
    period = request.args.get("period", "2y")
    force = request.args.get("force", "false").lower() == "true"

    try:
        df = DataService.fetch_history(ticker, period=period, force_refresh=force)

        if df.empty:
            return jsonify({"error": f"No history data for '{ticker}'"}), 404

        # Convert to list of dicts
        records = []
        for idx, row in df.iterrows():
            records.append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(float(row.get("open", 0)), 2),
                "high": round(float(row.get("high", 0)), 2),
                "low": round(float(row.get("low", 0)), 2),
                "close": round(float(row.get("close", 0)), 2),
                "volume": int(row.get("volume", 0)),
            })

        return jsonify({
            "ticker": ticker.upper(),
            "period": period,
            "count": len(records),
            "data": records,
        })

    except Exception as e:
        logger.error("Error fetching history for %s: %s", ticker, str(e))
        return jsonify({"error": str(e)}), 500
