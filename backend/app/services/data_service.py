"""
StockVision AI - Data Service

Fetches stock data from Yahoo Finance, caches in the database,
and provides a clean interface for other services.
"""

import logging
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional

import yfinance as yf
import pandas as pd

from app.repositories.stock_repository import StockRepository

logger = logging.getLogger("stockvision.data_service")

# In-memory cache for stock info (avoid hammering Yahoo Finance)
_info_cache: dict[str, dict] = {}
_cache_timestamps: dict[str, datetime] = {}
CACHE_TTL = timedelta(minutes=5)


class DataService:
    """Service for fetching and managing stock market data."""

    @staticmethod
    def fetch_stock_info(ticker: str) -> Optional[dict]:
        """
        Fetch stock metadata from Yahoo Finance.
        Uses in-memory cache to avoid repeated API calls.
        """
        ticker = ticker.upper()

        # Check cache
        if ticker in _info_cache:
            cache_age = datetime.now(timezone.utc) - _cache_timestamps.get(
                ticker, datetime.min.replace(tzinfo=timezone.utc)
            )
            if cache_age < CACHE_TTL:
                return _info_cache[ticker]

        try:
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info

            if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
                # Try fast_info as fallback
                fast = yf_ticker.fast_info
                if hasattr(fast, "last_price") and fast.last_price:
                    stock_info = {
                        "ticker": ticker,
                        "name": ticker,
                        "exchange": getattr(fast, "exchange", ""),
                        "sector": "",
                        "industry": "",
                        "market_cap": getattr(fast, "market_cap", None),
                        "current_price": float(fast.last_price),
                        "currency": getattr(fast, "currency", "USD"),
                        "previous_close": getattr(fast, "previous_close", None),
                        "day_high": getattr(fast, "day_high", None),
                        "day_low": getattr(fast, "day_low", None),
                        "fifty_two_week_high": getattr(fast, "year_high", None),
                        "fifty_two_week_low": getattr(fast, "year_low", None),
                        "average_volume": None,
                        "pe_ratio": None,
                        "dividend_yield": None,
                        "beta": None,
                    }
                else:
                    logger.warning("No data found for ticker: %s", ticker)
                    return None
            else:
                stock_info = {
                    "ticker": ticker,
                    "name": info.get("longName", info.get("shortName", ticker)),
                    "exchange": info.get("exchange", ""),
                    "sector": info.get("sector", ""),
                    "industry": info.get("industry", ""),
                    "market_cap": info.get("marketCap"),
                    "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
                    "currency": info.get("currency", "USD"),
                    "previous_close": info.get("previousClose"),
                    "day_high": info.get("dayHigh"),
                    "day_low": info.get("dayLow"),
                    "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                    "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                    "average_volume": info.get("averageVolume"),
                    "pe_ratio": info.get("trailingPE"),
                    "dividend_yield": info.get("dividendYield"),
                    "beta": info.get("beta"),
                }

            # Cache it
            _info_cache[ticker] = stock_info
            _cache_timestamps[ticker] = datetime.now(timezone.utc)

            # Persist to DB
            StockRepository.upsert_stock(ticker, stock_info)

            logger.info("Fetched info for %s: %s", ticker, stock_info.get("name"))
            return stock_info

        except Exception as e:
            logger.error("Error fetching info for %s: %s", ticker, str(e))
            return None

    @staticmethod
    def fetch_history(
        ticker: str, period: str = "2y", force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Fetch historical price data. First checks DB, then Yahoo Finance.
        Returns a pandas DataFrame with OHLCV columns.
        """
        ticker = ticker.upper()

        # Check existing data in DB
        existing_count = StockRepository.get_history_count(ticker)
        latest_date = StockRepository.get_latest_date(ticker)

        need_fetch = force_refresh or existing_count == 0

        if not need_fetch and latest_date:
            # Fetch only if we're missing recent data (> 1 business day)
            days_stale = (datetime.now(timezone.utc).date() - latest_date).days
            if days_stale > 3:  # account for weekends
                need_fetch = True

        if need_fetch:
            try:
                logger.info("Downloading history for %s (period=%s)", ticker, period)
                yf_ticker = yf.Ticker(ticker)
                df = yf_ticker.history(period=period, auto_adjust=False)

                if df.empty:
                    logger.warning("No history data for %s", ticker)
                else:
                    # Clean column names
                    df.columns = [c.replace(" ", "_") if " " in c else c for c in df.columns]
                    # Rename columns to match expected format
                    col_map = {}
                    for c in df.columns:
                        if c.lower() == "adj_close" or c == "Adj Close":
                            col_map[c] = "Adj Close"
                        elif c.lower() in ("open", "high", "low", "close", "volume"):
                            col_map[c] = c.capitalize()
                    if col_map:
                        df.rename(columns=col_map, inplace=True)

                    inserted = StockRepository.bulk_insert_history(ticker, df)
                    logger.info("Stored %d records for %s", inserted, ticker)

            except Exception as e:
                logger.error("Error downloading history for %s: %s", ticker, str(e))

        # Return from DB
        return StockRepository.get_history_as_dataframe(ticker)

    @staticmethod
    def compute_data_hash(df: pd.DataFrame) -> str:
        """Compute SHA-256 hash of DataFrame to detect data changes."""
        if df.empty:
            return ""
        content = pd.util.hash_pandas_object(df).values.tobytes()
        return hashlib.sha256(content).hexdigest()[:16]

    @staticmethod
    def search_tickers(query: str) -> list[dict]:
        """
        Search for tickers. First checks DB, then provides common suggestions.
        """
        # Common tickers for quick suggestions
        common_tickers = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "META": "Meta Platforms Inc.",
            "TSLA": "Tesla Inc.",
            "NVDA": "NVIDIA Corporation",
            "AMD": "Advanced Micro Devices",
            "NFLX": "Netflix Inc.",
            "INTC": "Intel Corporation",
            "RELIANCE.NS": "Reliance Industries Ltd.",
            "TCS.NS": "Tata Consultancy Services",
            "INFY.NS": "Infosys Ltd.",
            "HDFCBANK.NS": "HDFC Bank Ltd.",
            "ICICIBANK.NS": "ICICI Bank Ltd.",
            "SBIN.NS": "State Bank of India",
            "LT.NS": "Larsen & Toubro Ltd.",
            "ITC.NS": "ITC Ltd.",
        }

        query_upper = query.upper().strip()
        results = []

        # Search from common tickers
        for tick, name in common_tickers.items():
            if query_upper in tick.upper() or query_upper in name.upper():
                results.append({"ticker": tick, "name": name})

        # Search from DB
        db_stocks = StockRepository.search_stocks(query)
        for stock in db_stocks:
            if not any(r["ticker"] == stock.ticker for r in results):
                results.append({"ticker": stock.ticker, "name": stock.name or stock.ticker})

        return results[:15]
