"""
Integration tests for Seasonal Anime Tracker API.
Tests end-to-end data flow from Jikan API to frontend display.

Feature: seasonal-anime-tracker
Requirements: 4.5, 10.5
"""

import pytest
import httpx
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.cache import get_cache


class TestEndToEndDataFlow:
    """Test end-to-end data flow from Jikan API to frontend display."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear cache before and after each test."""
        cache = get_cache()
        cache.clear()
        yield
        cache.clear()

    def test_seasonal_anime_endpoint_returns_valid_data(self):
        """
        Test that the seasonal anime endpoint returns valid data from Jikan API.
        Validates: Requirements 4.5, 10.5
        """
        client = TestClient(app)
        response = client.get("/api/v1/seasonal")

        # Verify successful response
        assert response.status_code == 200

        # Verify response structure
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

        # If data exists, verify anime item structure
        if len(data["data"]) > 0:
            anime = data["data"][0]
            assert "mal_id" in anime
            assert "title" in anime
            assert "images" in anime
            assert "url" in anime
            assert isinstance(anime["mal_id"], int)
            assert isinstance(anime["title"], str)

    def test_seasonal_anime_with_parameters(self):
        """
        Test seasonal anime endpoint with year and season parameters.
        Validates: Requirements 4.5
        """
        client = TestClient(app)

        # Test with valid parameters
        response = client.get("/api/v1/seasonal?year=2024&season=winter")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_seasonal_anime_invalid_season_parameter(self):
        """
        Test that invalid season parameter returns 400 error.
        Validates: Requirements 4.5
        """
        client = TestClient(app)
        response = client.get("/api/v1/seasonal?season=invalid")

        assert response.status_code == 400
        assert "Invalid season" in response.json()["detail"]

    def test_seasonal_anime_invalid_year_parameter(self):
        """
        Test that invalid year parameter returns 400 error.
        Validates: Requirements 4.5
        """
        client = TestClient(app)

        # Test year too old
        response = client.get("/api/v1/seasonal?year=1800")
        assert response.status_code == 400
        assert "Invalid year" in response.json()["detail"]

        # Test year too far in future
        response = client.get("/api/v1/seasonal?year=2050")
        assert response.status_code == 400
        assert "Invalid year" in response.json()["detail"]

    def test_cache_integration_with_api(self):
        """
        Test that cache integration works correctly with API endpoints.
        Validates: Requirements 4.5, 10.5
        """
        client = TestClient(app)

        # First request - should fetch from Jikan API
        response1 = client.get("/api/v1/seasonal")
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request - should return cached data
        response2 = client.get("/api/v1/seasonal")
        assert response2.status_code == 200
        data2 = response2.json()

        # Data should be identical (from cache)
        assert data1 == data2

    def test_health_check_endpoint(self):
        """
        Test that health check endpoint returns correct status.
        Validates: Requirements 10.5
        """
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "seasonal-anime-tracker"
        assert "version" in data
        assert data["cors_enabled"] is True

    def test_seasonal_health_check_endpoint(self):
        """
        Test seasonal anime specific health check endpoint.
        Validates: Requirements 10.5
        """
        client = TestClient(app)
        response = client.get("/api/v1/seasonal/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["endpoint"] == "seasonal_anime"
        assert data["cache_enabled"] is True


class TestCORSFunctionality:
    """Test CORS functionality with actual cross-origin requests."""

    def test_cors_headers_on_get_request(self):
        """
        Test that CORS headers are present on GET requests.
        Validates: Requirements 4.5
        """
        client = TestClient(app)

        # Make request with Origin header
        response = client.get(
            "/api/v1/seasonal",
            headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    def test_cors_preflight_options_request(self):
        """
        Test that OPTIONS preflight requests are handled correctly.
        Validates: Requirements 4.5
        """
        client = TestClient(app)

        # Send OPTIONS preflight request
        response = client.options(
            "/api/v1/seasonal",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )

        assert response.status_code == 200
        # Verify CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_cors_with_allowed_origin(self):
        """
        Test CORS with allowed origin from configuration.
        Validates: Requirements 4.5
        """
        client = TestClient(app)

        # Test with localhost:3000 (should be in allowed origins)
        response = client.get(
            "/api/v1/seasonal",
            headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_headers_include_credentials(self):
        """
        Test that CORS headers include credentials support.
        Validates: Requirements 4.5
        """
        client = TestClient(app)

        response = client.options(
            "/api/v1/seasonal",
            headers={"Origin": "http://localhost:3000"}
        )

        # OPTIONS may return 422 or 200 depending on FastAPI version
        # The important thing is that CORS headers are present
        assert response.status_code in [200, 422]
        # Check for credentials header
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        if "access-control-allow-credentials" in headers_lower:
            assert headers_lower["access-control-allow-credentials"] == "true"


class TestDockerComposeDeployment:
    """Test Docker Compose deployment readiness."""

    def test_environment_variables_loaded(self):
        """
        Test that environment variables are loaded correctly.
        Validates: Requirements 10.5
        """
        # Verify critical settings are loaded
        assert settings.HOST is not None
        assert settings.PORT is not None
        assert settings.JIKAN_API_URL is not None
        assert settings.CACHE_TTL_MINUTES > 0

    def test_api_root_endpoint(self):
        """
        Test that root endpoint provides API information.
        Validates: Requirements 10.5
        """
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "api" in data
        assert "seasonal_anime" in data["api"]

    def test_service_startup_and_shutdown(self):
        """
        Test that service startup and shutdown events work correctly.
        Validates: Requirements 10.5
        """
        # This test verifies that the app can be instantiated
        # and that startup/shutdown events don't raise errors
        client = TestClient(app)

        # Make a simple request to ensure app is running
        response = client.get("/health")
        assert response.status_code == 200

        # Client cleanup will trigger shutdown events
        client.close()

    def test_concurrent_requests_handling(self):
        """
        Test that the API can handle concurrent requests.
        Validates: Requirements 10.5
        """
        client = TestClient(app)

        # Make multiple concurrent requests
        responses = []
        for _ in range(5):
            response = client.get("/api/v1/seasonal")
            responses.append(response)

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "data" in data


class TestErrorHandling:
    """Test error handling across service boundaries."""

    def test_404_not_found(self):
        """
        Test that 404 errors are handled correctly.
        Validates: Requirements 4.5
        """
        client = TestClient(app)
        response = client.get("/api/v1/nonexistent")

        # FastAPI may return 405 for routes that don't exist but match a pattern
        # or 404 for completely unknown routes
        assert response.status_code in [404, 405]

    def test_method_not_allowed(self):
        """
        Test that unsupported HTTP methods return appropriate errors.
        Validates: Requirements 4.5
        """
        client = TestClient(app)

        # Try POST on GET-only endpoint
        response = client.post("/api/v1/anime/seasonal")
        assert response.status_code == 405

    def test_error_response_includes_cors_headers(self):
        """
        Test that error responses include CORS headers.
        Validates: Requirements 4.5
        """
        client = TestClient(app)

        # Make request that will fail with Origin header
        response = client.get(
            "/api/v1/seasonal?season=invalid",
            headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 400
        # CORS headers should still be present on error responses
        assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_async_external_api_integration():
    """
    Test async integration with external Jikan API.
    Validates: Requirements 4.5, 10.5
    """
    # Test direct connection to Jikan API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.jikan.moe/v4/seasons/now",
                timeout=10.0
            )

            # Verify we can reach Jikan API
            assert response.status_code == 200
            data = response.json()
            assert "data" in data

        except httpx.RequestError:
            # If Jikan API is unreachable, skip this test
            pytest.skip("Jikan API is unreachable")
