"""
StockVision AI - Health Check Route
"""

from flask import Blueprint, jsonify
from datetime import datetime, timezone

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "StockVision AI",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
