"""
StockVision AI - Database Models

SQLAlchemy models for stocks, history, watchlist, and trained models.
Designed for SQLite with easy migration path to PostgreSQL.
"""

from datetime import datetime, timezone
from app import db


class Stock(db.Model):
    """Stock metadata — company info and current market snapshot."""

    __tablename__ = "stocks"

    ticker = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(200), nullable=True)
    exchange = db.Column(db.String(50), nullable=True)
    sector = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(200), nullable=True)
    market_cap = db.Column(db.Float, nullable=True)
    current_price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default="USD")
    last_updated = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    history = db.relationship(
        "StockHistory", backref="stock", lazy="dynamic", cascade="all, delete-orphan"
    )
    trained_models = db.relationship(
        "TrainedModel", backref="stock", lazy="dynamic", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "name": self.name,
            "exchange": self.exchange,
            "sector": self.sector,
            "industry": self.industry,
            "market_cap": self.market_cap,
            "current_price": self.current_price,
            "currency": self.currency,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


class StockHistory(db.Model):
    """Daily OHLCV price history."""

    __tablename__ = "stock_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticker = db.Column(
        db.String(20), db.ForeignKey("stocks.ticker"), nullable=False, index=True
    )
    date = db.Column(db.Date, nullable=False, index=True)
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    adj_close = db.Column(db.Float, nullable=True)
    volume = db.Column(db.BigInteger, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("ticker", "date", name="uq_ticker_date"),
    )

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "open": round(self.open, 2),
            "high": round(self.high, 2),
            "low": round(self.low, 2),
            "close": round(self.close, 2),
            "adj_close": round(self.adj_close, 2) if self.adj_close else None,
            "volume": self.volume,
        }


class Watchlist(db.Model):
    """User watchlist entries."""

    __tablename__ = "watchlist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticker = db.Column(
        db.String(20), db.ForeignKey("stocks.ticker"), nullable=False, unique=True
    )
    added_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    notes = db.Column(db.String(500), nullable=True)

    # Relationship to get stock info
    stock_info = db.relationship("Stock", backref="watchlist_entry", uselist=False)

    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "ticker": self.ticker,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "notes": self.notes,
        }
        if self.stock_info:
            result["stock"] = self.stock_info.to_dict()
        return result


class TrainedModel(db.Model):
    """Metadata for trained ML models — tracks file paths, metrics, and freshness."""

    __tablename__ = "trained_models"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticker = db.Column(
        db.String(20), db.ForeignKey("stocks.ticker"), nullable=False, index=True
    )
    model_type = db.Column(db.String(50), nullable=False)  # lstm, rf, xgboost, linear
    model_path = db.Column(db.String(500), nullable=False)
    scaler_path = db.Column(db.String(500), nullable=True)
    rmse = db.Column(db.Float, nullable=True)
    mae = db.Column(db.Float, nullable=True)
    mape = db.Column(db.Float, nullable=True)
    r2_score = db.Column(db.Float, nullable=True)
    data_hash = db.Column(db.String(64), nullable=True)  # SHA-256 of training data
    training_loss = db.Column(db.Text, nullable=True)  # JSON: list of loss values per epoch
    validation_loss = db.Column(db.Text, nullable=True)  # JSON: list of val_loss values
    trained_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        db.UniqueConstraint("ticker", "model_type", name="uq_ticker_model"),
    )

    def to_dict(self) -> dict:
        import json
        return {
            "id": self.id,
            "ticker": self.ticker,
            "model_type": self.model_type,
            "model_path": self.model_path,
            "scaler_path": self.scaler_path,
            "rmse": round(self.rmse, 4) if self.rmse else None,
            "mae": round(self.mae, 4) if self.mae else None,
            "mape": round(self.mape, 2) if self.mape else None,
            "r2_score": round(self.r2_score, 4) if self.r2_score else None,
            "training_loss": json.loads(self.training_loss) if self.training_loss else None,
            "validation_loss": json.loads(self.validation_loss) if self.validation_loss else None,
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
        }
