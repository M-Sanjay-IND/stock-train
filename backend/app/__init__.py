"""
StockVision AI - Flask Application Factory

Creates and configures the Flask application with extensions,
blueprints, error handlers, and logging.
"""

import os
import logging

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name: str | None = None):
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    from app.config import config_map
    app.config.from_object(config_map.get(config_name, config_map["development"]))

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("stockvision")
    logger.info("Starting StockVision AI (%s)", config_name)

    # Initialize extensions
    CORS(app, resources={r"/*": {"origins": "*"}})
    db.init_app(app)

    # Ensure saved_models directory exists
    os.makedirs(app.config.get("SAVED_MODELS_DIR", "saved_models"), exist_ok=True)

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # Create database tables
    with app.app_context():
        from app.models import stock  # noqa: F401 - Import to register models
        db.create_all()
        logger.info("Database tables created/verified")

    # --- Error Handlers ---

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": str(error.description) if hasattr(error, "description") else "Invalid request",
            "status": 400,
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found",
            "status": 404,
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status": 500,
        }), 500

    @app.after_request
    def add_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    return app
