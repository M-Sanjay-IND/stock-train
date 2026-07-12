"""
StockVision AI - Watchlist Routes
"""

import logging
from flask import Blueprint, jsonify, request
from app.repositories.stock_repository import StockRepository
from app.services.data_service import DataService

logger = logging.getLogger("stockvision.routes.watchlist")

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/watchlist", methods=["GET"])
def get_watchlist():
    """Get all watchlist entries."""
    try:
        entries = StockRepository.get_watchlist()
        return jsonify({
            "watchlist": [e.to_dict() for e in entries],
            "count": len(entries),
        })
    except Exception as e:
        logger.error("Error fetching watchlist: %s", str(e))
        return jsonify({"error": str(e)}), 500


@watchlist_bp.route("/watchlist", methods=["POST"])
def add_to_watchlist():
    """Add a stock to the watchlist."""
    try:
        data = request.get_json()
        if not data or "ticker" not in data:
            return jsonify({"error": "ticker is required"}), 400

        ticker = data["ticker"].upper()
        notes = data.get("notes", "")

        # Ensure stock exists in DB
        info = DataService.fetch_stock_info(ticker)
        if info is None:
            return jsonify({"error": f"Stock '{ticker}' not found"}), 404

        entry = StockRepository.add_to_watchlist(ticker, notes)
        return jsonify({"message": f"{ticker} added to watchlist", "entry": entry.to_dict()}), 201

    except Exception as e:
        logger.error("Error adding to watchlist: %s", str(e))
        return jsonify({"error": str(e)}), 500


@watchlist_bp.route("/watchlist/<ticker>", methods=["DELETE"])
def remove_from_watchlist(ticker: str):
    """Remove a stock from the watchlist."""
    try:
        removed = StockRepository.remove_from_watchlist(ticker)
        if removed:
            return jsonify({"message": f"{ticker.upper()} removed from watchlist"})
        else:
            return jsonify({"error": f"{ticker.upper()} not in watchlist"}), 404

    except Exception as e:
        logger.error("Error removing from watchlist: %s", str(e))
        return jsonify({"error": str(e)}), 500
