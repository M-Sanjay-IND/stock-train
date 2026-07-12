"""
StockVision AI - Route Registration

Registers all API blueprints with the Flask application.
"""

from flask import Flask


def register_blueprints(app: Flask):
    """Register all route blueprints."""
    from app.routes.health import health_bp
    from app.routes.stocks import stocks_bp
    from app.routes.technical import technical_bp
    from app.routes.analytics import analytics_bp
    from app.routes.forecast import forecast_bp
    from app.routes.watchlist import watchlist_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(stocks_bp)
    app.register_blueprint(technical_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(forecast_bp)
    app.register_blueprint(watchlist_bp)
