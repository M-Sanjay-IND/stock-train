"""
StockVision AI - Configuration Module

Handles environment-based configuration for development, testing, and production.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, '..', 'stockvision.db')}"
    )

    # ML Configuration
    MODEL_CACHE_HOURS = int(os.getenv("MODEL_CACHE_HOURS", "24"))
    LSTM_EPOCHS = int(os.getenv("LSTM_EPOCHS", "100"))
    LSTM_LOOKBACK = int(os.getenv("LSTM_LOOKBACK", "60"))
    SAVED_MODELS_DIR = os.path.join(BASE_DIR, "..", "saved_models")

    # Data Configuration
    DEFAULT_HISTORY_PERIOD = "5y"
    MAX_HISTORY_PERIOD = "10y"

    # Cache Configuration
    CACHE_TIMEOUT = 300  # 5 minutes for in-memory cache


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
