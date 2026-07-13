"""
StockVision AI - Stock Repository

Data access layer implementing the Repository Pattern for stock-related
database operations. Keeps SQL/ORM logic separate from business logic.
"""

import logging
from datetime import date, datetime, timezone
from typing import Optional

import pandas as pd
from sqlalchemy import desc

from app import db
from app.models.stock import Stock, StockHistory, Watchlist, TrainedModel

logger = logging.getLogger("stockvision.repository")


class StockRepository:
    """Repository for Stock and StockHistory CRUD operations."""

    # --- Stock Info ---

    @staticmethod
    def get_stock(ticker: str) -> Optional[Stock]:
        """Get stock by ticker."""
        return db.session.get(Stock, ticker.upper())

    @staticmethod
    def upsert_stock(ticker: str, info: dict) -> Stock:
        """Insert or update stock metadata."""
        ticker = ticker.upper()
        stock = db.session.get(Stock, ticker)
        if stock is None:
            stock = Stock(ticker=ticker)
            db.session.add(stock)

        stock.name = info.get("name", stock.name)
        stock.exchange = info.get("exchange", stock.exchange)
        stock.sector = info.get("sector", stock.sector)
        stock.industry = info.get("industry", stock.industry)
        stock.market_cap = info.get("market_cap", stock.market_cap)
        stock.current_price = info.get("current_price", stock.current_price)
        stock.currency = info.get("currency", stock.currency or "USD")
        stock.last_updated = datetime.now(timezone.utc)

        db.session.commit()
        logger.info("Upserted stock: %s (%s)", ticker, stock.name)
        return stock

    @staticmethod
    def search_stocks(query: str) -> list[Stock]:
        """Search stocks by ticker or name (prefix match)."""
        q = f"%{query.upper()}%"
        return Stock.query.filter(
            db.or_(
                Stock.ticker.ilike(q),
                Stock.name.ilike(q),
            )
        ).limit(20).all()

    # --- Price History ---

    @staticmethod
    def get_history(
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[StockHistory]:
        """Get price history for a ticker, optionally filtered by date range."""
        query = StockHistory.query.filter_by(ticker=ticker.upper()).order_by(StockHistory.date)
        if start_date:
            query = query.filter(StockHistory.date >= start_date)
        if end_date:
            query = query.filter(StockHistory.date <= end_date)
        return query.all()

    @staticmethod
    def get_history_as_dataframe(ticker: str) -> pd.DataFrame:
        """Get price history as a pandas DataFrame — used by ML pipeline."""
        records = StockHistory.query.filter_by(ticker=ticker.upper()).order_by(StockHistory.date).all()
        if not records:
            return pd.DataFrame()

        data = [r.to_dict() for r in records]
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        return df

    @staticmethod
    def get_latest_date(ticker: str) -> Optional[date]:
        """Get the most recent date in history for a ticker."""
        record = (
            StockHistory.query.filter_by(ticker=ticker.upper())
            .order_by(desc(StockHistory.date))
            .first()
        )
        return record.date if record else None

    @staticmethod
    def get_history_count(ticker: str) -> int:
        """Count history records for a ticker."""
        return StockHistory.query.filter_by(ticker=ticker.upper()).count()

    @staticmethod
    def bulk_insert_history(ticker: str, df: pd.DataFrame) -> int:
        """Bulk insert history from a DataFrame. Skips existing dates."""
        ticker = ticker.upper()
        existing_dates = {
            str(r[0]) if isinstance(r, tuple) else str(getattr(r, 'date', r))
            for r in StockHistory.query.filter_by(ticker=ticker)
            .with_entities(StockHistory.date)
            .all()
        }

        new_records = []
        for idx, row in df.iterrows():
            row_date = idx.date() if hasattr(idx, "date") else idx
            if str(row_date) in existing_dates:
                continue

            record = StockHistory(
                ticker=ticker,
                date=row_date,
                open=float(row.get("Open", 0)),
                high=float(row.get("High", 0)),
                low=float(row.get("Low", 0)),
                close=float(row.get("Close", 0)),
                adj_close=float(row.get("Adj Close", row.get("Close", 0))),
                volume=int(row.get("Volume", 0)),
            )
            new_records.append(record)

        if new_records:
            db.session.bulk_save_objects(new_records)
            db.session.commit()
            logger.info("Inserted %d new history records for %s", len(new_records), ticker)

        return len(new_records)

    # --- Watchlist ---

    @staticmethod
    def get_watchlist() -> list[Watchlist]:
        """Get all watchlist entries with stock info."""
        return Watchlist.query.order_by(desc(Watchlist.added_at)).all()

    @staticmethod
    def add_to_watchlist(ticker: str, notes: str = "") -> Watchlist:
        """Add a stock to the watchlist."""
        ticker = ticker.upper()
        existing = Watchlist.query.filter_by(ticker=ticker).first()
        if existing:
            return existing

        entry = Watchlist(ticker=ticker, notes=notes)
        db.session.add(entry)
        db.session.commit()
        logger.info("Added %s to watchlist", ticker)
        return entry

    @staticmethod
    def remove_from_watchlist(ticker: str) -> bool:
        """Remove a stock from the watchlist."""
        entry = Watchlist.query.filter_by(ticker=ticker.upper()).first()
        if entry:
            db.session.delete(entry)
            db.session.commit()
            logger.info("Removed %s from watchlist", ticker)
            return True
        return False

    # --- Trained Models ---

    @staticmethod
    def get_trained_model(ticker: str, model_type: str) -> Optional[TrainedModel]:
        """Get trained model metadata."""
        return TrainedModel.query.filter_by(
            ticker=ticker.upper(), model_type=model_type
        ).first()

    @staticmethod
    def get_all_trained_models(ticker: str) -> list[TrainedModel]:
        """Get all trained models for a ticker."""
        return TrainedModel.query.filter_by(ticker=ticker.upper()).all()

    @staticmethod
    def get_best_model(ticker: str) -> Optional[TrainedModel]:
        """Get the best-performing model for a ticker (lowest RMSE, with R² guard)."""
        # First try: models with R² >= 0.5 (prevents poorly-trained models from being selected)
        best = (
            TrainedModel.query.filter_by(ticker=ticker.upper())
            .filter(TrainedModel.rmse.isnot(None))
            .filter(TrainedModel.r2_score >= 0.5)
            .order_by(TrainedModel.rmse)
            .first()
        )
        if best:
            return best

        # Fallback: any model with valid RMSE
        return (
            TrainedModel.query.filter_by(ticker=ticker.upper())
            .filter(TrainedModel.rmse.isnot(None))
            .order_by(TrainedModel.rmse)
            .first()
        )

    @staticmethod
    def upsert_trained_model(ticker: str, model_type: str, data: dict) -> TrainedModel:
        """Insert or update trained model metadata."""
        import json
        ticker = ticker.upper()
        model = TrainedModel.query.filter_by(ticker=ticker, model_type=model_type).first()

        if model is None:
            model = TrainedModel(ticker=ticker, model_type=model_type)
            db.session.add(model)

        model.model_path = data.get("model_path", model.model_path)
        model.scaler_path = data.get("scaler_path", model.scaler_path)
        model.rmse = data.get("rmse", model.rmse)
        model.mae = data.get("mae", model.mae)
        model.mape = data.get("mape", model.mape)
        model.r2_score = data.get("r2_score", model.r2_score)
        model.data_hash = data.get("data_hash", model.data_hash)
        model.trained_at = datetime.now(timezone.utc)

        if "training_loss" in data:
            model.training_loss = json.dumps(data["training_loss"])
        if "validation_loss" in data:
            model.validation_loss = json.dumps(data["validation_loss"])

        db.session.commit()
        logger.info("Upserted model: %s/%s (RMSE: %s)", ticker, model_type, model.rmse)
        return model
