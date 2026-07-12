"""
StockVision AI - Analytics Tests

Tests for the financial analytics computation.
"""

import pytest
import pandas as pd
import numpy as np
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def sample_df():
    """Create a sample price DataFrame for testing."""
    dates = pd.date_range(start="2023-01-01", periods=300, freq="B")
    np.random.seed(42)

    # Generate realistic-looking price data
    base_price = 150
    returns = np.random.normal(0.0005, 0.02, 300)
    prices = base_price * np.cumprod(1 + returns)

    df = pd.DataFrame({
        "open": prices * (1 + np.random.uniform(-0.01, 0.01, 300)),
        "high": prices * (1 + np.abs(np.random.normal(0, 0.01, 300))),
        "low": prices * (1 - np.abs(np.random.normal(0, 0.01, 300))),
        "close": prices,
        "volume": np.random.randint(1000000, 50000000, 300),
    }, index=dates)

    return df


class TestAnalyticsService:
    """Tests for AnalyticsService."""

    def test_compute_analytics_returns_dict(self, sample_df):
        """Analytics computation should return a dictionary."""
        result = AnalyticsService.compute_analytics(sample_df)
        assert isinstance(result, dict)

    def test_analytics_has_required_fields(self, sample_df):
        """Result should contain all expected metrics."""
        result = AnalyticsService.compute_analytics(sample_df)
        required_fields = [
            "current_price", "daily_return", "volatility",
            "sharpe_ratio", "max_drawdown", "fifty_two_week_high",
            "fifty_two_week_low",
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_analytics_values_are_reasonable(self, sample_df):
        """Financial metrics should be within reasonable ranges."""
        result = AnalyticsService.compute_analytics(sample_df)
        assert result["current_price"] > 0
        assert -1 <= result["max_drawdown"] <= 0
        assert result["fifty_two_week_high"] >= result["fifty_two_week_low"]

    def test_empty_dataframe_returns_error(self):
        """Empty DataFrame should return error message."""
        result = AnalyticsService.compute_analytics(pd.DataFrame())
        assert "error" in result

    def test_crossovers_is_list(self, sample_df):
        """Crossovers should be a list."""
        result = AnalyticsService.compute_analytics(sample_df)
        assert isinstance(result["crossovers"], list)
