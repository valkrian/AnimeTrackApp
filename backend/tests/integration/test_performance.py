"""
Performance and validation tests for Seasonal Anime Tracker.
Tests cache performance, concurrent requests, and system optimization.

Feature: seasonal-anime-tracker
Requirements: 3.3, 7.5
"""

import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
from app.main import app
from app.core.cache import get_cache


class TestCachePerformance:
    """Test cache performance under concurrent requests."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear cache before and after each test."""
        cache = get_cache()
        cache.clear()
        yield
        cache.clear()

    def test_cache_improves_response_time(self):
        """
        Test that cache significantly improves response time.
        Validates: Requirements 3.3
        """
        client = TestClient(app)

        # First request - should fetch from Jikan API (slower)
        start_time = time.time()
        response1 = client.get("/api/v1/seasonal")
        first_request_time = time.time() - start_time

        assert response1.status_code == 200

        # Second request - should return from cache (faster)
        start_time = time.time()
        response2 = client.get("/api/v1/seasonal")
        cached_request_time = time.time() - start_time

        assert response2.status_code == 200

        # Cached request should be significantly faster
        # Allow some variance but cache should be at least 2x faster
        assert cached_request_time < first_request_time / 2, (
            f"Cached request ({cached_request_time:.3f}s) should be much faster "
            f"than first request ({first_request_time:.3f}s)"
        )

    def test_concurrent_requests_use_cache(self):
        """
        Test that concurrent requests properly utilize cache.
        Validates: Requirements 3.3
        """
        client = TestClient(app)

        # Prime the cache with first request
        response = client.get("/api/v1/seasonal")
        assert response.status_code == 200
        expected_data = response.json()

        # Make multiple concurrent requests
        num_requests = 10
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(client.get, "/api/v1/seasonal")
                for _ in range(num_requests)
            ]

            responses = [future.result() for future in as_completed(futures)]

        total_time = time.time() - start_time

        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)

        # All requests should return the same cached data
        for response in responses:
            assert response.json() == expected_data

        # Average time per request should be very low (< 100ms) due to caching
        avg_time = total_time / num_requests
        assert avg_time < 0.1, (
            f"Average cached request time ({avg_time:.3f}s) should be < 0.1s"
        )

    def test_cache_handles_high_load(self):
        """
        Test that cache performs well under high concurrent load.
        Validates: Requirements 3.3
        """
        client = TestClient(app)

        # Prime the cache
        response = client.get("/api/v1/seasonal")
        assert response.status_code == 200

        # Simulate high load with many concurrent requests
        num_requests = 50
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(client.get, "/api/v1/seasonal")
                for _ in range(num_requests)
            ]

            responses = [future.result() for future in as_completed(futures)]

        total_time = time.time() - start_time

        # All requests should succeed
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count == num_requests, (
            f"Expected {num_requests} successful requests, got {success_count}"
        )

        # Total time should be reasonable (< 5 seconds for 50 cached requests)
        assert total_time < 5.0, (
            f"High load test took {total_time:.2f}s, should be < 5s"
        )

    def test_cache_memory_efficiency(self):
        """
        Test that cache doesn't cause memory issues with multiple entries.
        Validates: Requirements 3.3
        """
        client = TestClient(app)
        cache = get_cache()

        # Make requests with different parameters to create multiple cache entries
        test_params = [
            {},
            {"year": 2024, "season": "winter"},
            {"year": 2023, "season": "fall"},
            {"year": 2023, "season": "summer"},
        ]

        for params in test_params:
            response = client.get("/api/v1/seasonal", params=params)
            assert response.status_code == 200

        # Verify cache has entries
        cache_size = len(cache._cache)
        assert cache_size > 0, "Cache should have entries"
        assert cache_size <= len(test_params), (
            f"Cache has {cache_size} entries, expected <= {len(test_params)}"
        )

    def test_cache_ttl_expiration(self):
        """
        Test that cache entries expire after TTL.
        Validates: Requirements 3.3
        """
        client = TestClient(app)
        cache = get_cache()

        # Make a request to populate cache
        response = client.get("/api/v1/seasonal")
        assert response.status_code == 200

        # Get cache entry - need to check internal cache structure
        # The cache key format may vary, so let's check if any entries exist
        assert len(cache._cache) > 0, "Cache should have at least one entry"

        # Get the first cache entry directly from internal cache
        cache_key = list(cache._cache.keys())[0]
        entry = cache._cache[cache_key]  # Access internal cache directly
        assert entry is not None, "Cache entry should exist"

        # Verify entry has TTL information
        assert hasattr(entry, "expires_at"), "Cache entry should have expiration"
        assert hasattr(entry, "timestamp"), "Cache entry should have timestamp"

        # Verify entry is not expired
        assert not entry.is_expired(), "Fresh cache entry should not be expired"

        # Verify TTL is reasonable (should be around 60 minutes)
        ttl_seconds = entry.time_to_live()
        assert 3500 < ttl_seconds <= 3600, (
            f"TTL should be around 3600 seconds, got {ttl_seconds}"
        )


class TestResponseTimeOptimization:
    """Test response time optimization across the system."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Clear cache before and after each test."""
        cache = get_cache()
        cache.clear()
        yield
        cache.clear()

    def test_health_check_response_time(self):
        """
        Test that health check endpoint responds quickly.
        Validates: Requirements 3.3
        """
        client = TestClient(app)

        # Health check should be very fast (< 50ms)
        start_time = time.time()
        response = client.get("/health")
        response_time = time.time() - start_time

        assert response.status_code == 200
        assert response_time < 0.05, (
            f"Health check took {response_time:.3f}s, should be < 0.05s"
        )

    def test_cached_endpoint_response_time(self):
        """
        Test that cached endpoints respond within acceptable time.
        Validates: Requirements 3.3
        """
        client = TestClient(app)

        # Prime the cache
        client.get("/api/v1/seasonal")

        # Cached request should be very fast (< 200ms)
        start_time = time.time()
        response = client.get("/api/v1/seasonal")
        response_time = time.time() - start_time

        assert response.status_code == 200
        assert response_time < 0.2, (
            f"Cached request took {response_time:.3f}s, should be < 0.2s"
        )

    def test_error_response_time(self):
        """
        Test that error responses are returned quickly.
        Validates: Requirements 3.3
        """
        client = TestClient(app)

        # Error responses should be fast (< 100ms)
        start_time = time.time()
        response = client.get("/api/v1/seasonal?season=invalid")
        response_time = time.time() - start_time

        assert response.status_code == 400
        assert response_time < 0.1, (
            f"Error response took {response_time:.3f}s, should be < 0.1s"
        )


class TestSystemValidation:
    """Test overall system validation and correctness."""

    def test_api_returns_valid_json(self):
        """
        Test that all API endpoints return valid JSON.
        Validates: Requirements 3.3
        """
        client = TestClient(app)

        endpoints = [
            "/",
            "/health",
            "/api/v1/seasonal",
            "/api/v1/seasonal/health",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, (
                f"Endpoint {endpoint} returned {response.status_code}"
            )

            # Verify response is valid JSON
            try:
                data = response.json()
                assert isinstance(data, dict), (
                    f"Endpoint {endpoint} should return a dict"
                )
            except Exception as e:
                pytest.fail(f"Endpoint {endpoint} returned invalid JSON: {e}")

    def test_api_handles_malformed_requests(self):
        """
        Test that API gracefully handles malformed requests.
        Validates: Requirements 3.3
        """
        client = TestClient(app)

        # Test various malformed requests
        # FastAPI returns 422 for validation errors, 400 for business logic errors
        malformed_requests = [
            ("/api/v1/seasonal?year=abc", 422),  # Invalid year type (validation error)
            ("/api/v1/seasonal?year=-1", 400),  # Invalid year value (business logic)
            ("/api/v1/seasonal?season=invalid", 400),  # Invalid season (business logic)
        ]

        for endpoint, expected_status in malformed_requests:
            response = client.get(endpoint)
            assert response.status_code == expected_status, (
                f"Endpoint {endpoint} returned {response.status_code}, "
                f"expected {expected_status}"
            )

            # Error responses should include detail
            data = response.json()
            assert "detail" in data, "Error response should include detail"

    def test_cors_headers_present_on_all_responses(self):
        """
        Test that CORS headers are present on all responses.
        Validates: Requirements 3.3
        """
        client = TestClient(app)

        endpoints = [
            "/",
            "/health",
            "/api/v1/seasonal",
        ]

        for endpoint in endpoints:
            response = client.get(
                endpoint,
                headers={"Origin": "http://localhost:3000"}
            )

            assert response.status_code == 200
            # CORS headers should be present
            assert "access-control-allow-origin" in response.headers

    def test_api_consistency_across_requests(self):
        """
        Test that API returns consistent data across multiple requests.
        Validates: Requirements 3.3
        """
        client = TestClient(app)

        # Make multiple requests
        responses = [client.get("/api/v1/seasonal") for _ in range(5)]

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

        # All should return the same data (from cache)
        first_data = responses[0].json()
        for response in responses[1:]:
            assert response.json() == first_data, (
                "Cached responses should be identical"
            )


@pytest.mark.asyncio
async def test_async_performance():
    """
    Test async performance characteristics.
    Validates: Requirements 3.3
    """
    from app.services.anime_service import AnimeService

    service = AnimeService()

    # Test that async operations don't block
    start_time = time.time()

    # Make multiple async requests
    tasks = [service.fetch_seasonal_anime() for _ in range(3)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    total_time = time.time() - start_time

    # At least some requests should succeed
    successful = [r for r in results if not isinstance(r, Exception)]
    assert len(successful) > 0, "At least one async request should succeed"

    # Async requests should complete in reasonable time
    assert total_time < 10.0, (
        f"Async requests took {total_time:.2f}s, should be < 10s"
    )
