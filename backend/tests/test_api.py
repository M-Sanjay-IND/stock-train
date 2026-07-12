"""
StockVision AI - API Tests

Tests for REST API endpoints.
"""

import pytest
from app import create_app


@pytest.fixture
def app():
    """Create test application."""
    app = create_app("testing")
    yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 with status healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "StockVision AI"

    def test_health_has_version(self, client):
        """Health endpoint should include version."""
        response = client.get("/health")
        data = response.get_json()
        assert "version" in data


class TestStockSearchEndpoint:
    """Tests for the stock search endpoint."""

    def test_search_requires_query(self, client):
        """Search without query should return 400."""
        response = client.get("/stocks/search")
        assert response.status_code == 400

    def test_search_returns_results(self, client):
        """Search for known ticker should return results."""
        response = client.get("/stocks/search?q=AAPL")
        assert response.status_code == 200
        data = response.get_json()
        assert "results" in data
        assert len(data["results"]) > 0

    def test_search_result_has_ticker_and_name(self, client):
        """Search results should have ticker and name fields."""
        response = client.get("/stocks/search?q=AAPL")
        data = response.get_json()
        if data["results"]:
            result = data["results"][0]
            assert "ticker" in result
            assert "name" in result


class TestWatchlistEndpoint:
    """Tests for the watchlist endpoints."""

    def test_get_watchlist_returns_200(self, client):
        """Get watchlist should return 200."""
        response = client.get("/watchlist")
        assert response.status_code == 200
        data = response.get_json()
        assert "watchlist" in data

    def test_add_to_watchlist_requires_ticker(self, client):
        """Adding to watchlist without ticker should return 400."""
        response = client.post(
            "/watchlist",
            json={},
            content_type="application/json",
        )
        assert response.status_code == 400
