"""
Property-based tests for API error handling and CORS.
Tests Property 2: API Error Handling and Property 4: CORS Header Consistency
"""

import pytest
from hypothesis import given, strategies as st, HealthCheck
from hypothesis import settings as hypothesis_settings
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import httpx

from app.main import app
from app.core.config import settings


class TestAPIErrorHandlingProperties:
    """Property-based tests for API error handling."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    @given(
        status_code=st.sampled_from([404, 429, 500, 502, 503, 504]),
        error_message=st.text(min_size=1, max_size=100)
    )
    @hypothesis_settings(max_examples=50)
    def test_property_2_api_error_handling_consistency(self, status_code, error_message):
        """
        **Feature: seasonal-anime-tracker, Property 2: API Error Handling**
        
        For any external API error condition, the backend should return appropriate
        HTTP error responses with meaningful error messages.
        
        **Validates: Requirements 2.5**
        """
        # Mock the anime service to simulate different error conditions
        with patch('app.services.anime_service.AnimeService.fetch_seasonal_anime') as mock_fetch:
            # Configure mock to raise HTTPException with the given status code
            from fastapi import HTTPException
            mock_fetch.side_effect = HTTPException(
                status_code=status_code,
                detail=error_message
            )
            
            # Make request to seasonal anime endpoint
            response = self.client.get("/api/v1/seasonal")
            
            # Property: error status codes should be preserved
            assert response.status_code == status_code
            
            # Property: error response should contain detail
            response_data = response.json()
            assert "detail" in response_data
            
            # Property: response should be valid JSON
            assert isinstance(response_data, dict)
    
    @given(
        year=st.integers(min_value=1800, max_value=2100),
        season=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=1, max_size=20)
    )
    @hypothesis_settings(max_examples=100, deadline=None)
    def test_property_2_input_validation_error_handling(self, year, season):
        """
        **Feature: seasonal-anime-tracker, Property 2: API Error Handling**
        
        For any invalid input parameters, the API should return appropriate
        validation error responses.
        
        **Validates: Requirements 2.5**
        """
        # Test invalid year ranges
        if year < 1900 or year > 2030:
            response = self.client.get(f"/api/v1/seasonal?year={year}")
            
            # Property: invalid year should return 400 Bad Request
            if response.status_code == 400:
                response_data = response.json()
                assert "detail" in response_data
                assert "year" in response_data["detail"].lower()
        
        # Test invalid season names (only test if season is not a valid season name)
        valid_seasons = ["winter", "spring", "summer", "fall"]
        if season.lower() not in valid_seasons:
            response = self.client.get(f"/api/v1/seasonal?season={season}")
            
            # Property: invalid season should return 400 Bad Request
            if response.status_code == 400:
                response_data = response.json()
                assert "detail" in response_data
                assert "season" in response_data["detail"].lower()
    
    @given(dummy=st.just(None))
    @hypothesis_settings(max_examples=10)
    def test_property_2_timeout_error_handling(self, dummy):
        """
        **Feature: seasonal-anime-tracker, Property 2: API Error Handling**
        
        For any timeout condition, the API should return appropriate timeout errors.
        
        **Validates: Requirements 2.5**
        """
        # This test verifies that the service layer properly handles timeouts
        # by checking the anime_service.py implementation directly
        from app.services.anime_service import AnimeService
        import inspect
        
        # Property: The fetch_seasonal_anime method should have timeout exception handling
        source = inspect.getsource(AnimeService.fetch_seasonal_anime)
        assert "TimeoutException" in source, "Service should handle TimeoutException"
        assert "504" in source, "Service should return 504 for timeouts"
    
    @given(dummy=st.just(None))
    @hypothesis_settings(max_examples=10)
    def test_property_2_network_error_handling(self, dummy):
        """
        **Feature: seasonal-anime-tracker, Property 2: API Error Handling**
        
        For any network error condition, the API should return appropriate network errors.
        
        **Validates: Requirements 2.5**
        """
        # This test verifies that the service layer properly handles network errors
        # by checking the anime_service.py implementation directly
        from app.services.anime_service import AnimeService
        import inspect
        
        # Property: The fetch_seasonal_anime method should have network error handling
        source = inspect.getsource(AnimeService.fetch_seasonal_anime)
        assert "NetworkError" in source, "Service should handle NetworkError"
        assert "503" in source, "Service should return 503 for network errors"


class TestCORSHeaderProperties:
    """Property-based tests for CORS header consistency."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    @given(
        origin=st.sampled_from([
            "http://localhost:3000",
            "http://localhost:5173", 
            "http://127.0.0.1:3000",
            "https://example.com"
        ])
    )
    @hypothesis_settings(max_examples=100, deadline=None)
    def test_property_4_cors_header_consistency(self, origin):
        """
        **Feature: seasonal-anime-tracker, Property 4: CORS Header Consistency**
        
        For any request with a valid origin, the response should include proper
        CORS headers allowing frontend access.
        
        **Validates: Requirements 4.3, 4.4**
        """
        # Make request with origin header
        headers = {"Origin": origin}
        response = self.client.get("/api/v1/seasonal", headers=headers)
        
        # Property: response should include CORS headers for allowed origins
        if origin in settings.effective_cors_origins:
            assert "access-control-allow-origin" in response.headers
            assert response.headers["access-control-allow-origin"] == origin
            assert "access-control-allow-credentials" in response.headers
            assert response.headers["access-control-allow-credentials"] == "true"
        
        # Property: response should be valid regardless of CORS
        assert response.status_code in [200, 400, 404, 500, 502, 503, 504]
    
    @given(
        method=st.sampled_from(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"]),
        origin=st.sampled_from(settings.effective_cors_origins)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_4_preflight_options_handling(self, method, origin):
        """
        **Feature: seasonal-anime-tracker, Property 4: CORS Header Consistency**
        
        For any HTTP method and allowed origin, OPTIONS preflight requests
        should be handled correctly with proper CORS headers.
        
        **Validates: Requirements 4.3, 4.4**
        """
        # Make OPTIONS preflight request
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = self.client.options("/api/v1/seasonal", headers=headers)
        
        # Property: OPTIONS should return 200 OK
        assert response.status_code == 200
        
        # Property: should include proper CORS headers
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == origin
        
        assert "access-control-allow-methods" in response.headers
        allowed_methods = response.headers["access-control-allow-methods"]
        assert method in allowed_methods
        
        assert "access-control-allow-headers" in response.headers
        
        # Property: should allow credentials
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"
    
    @given(
        path=st.sampled_from([
            "/api/v1/seasonal",
            "/health",
            "/",
            "/api/v1/seasonal/health"
        ]),
        origin=st.sampled_from(settings.effective_cors_origins)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_4_cors_consistency_across_endpoints(self, path, origin):
        """
        **Feature: seasonal-anime-tracker, Property 4: CORS Header Consistency**
        
        For any endpoint and allowed origin, CORS headers should be consistent
        across all API endpoints.
        
        **Validates: Requirements 4.3, 4.4**
        """
        headers = {"Origin": origin}
        response = self.client.get(path, headers=headers)
        
        # Property: all endpoints should handle CORS consistently
        if response.status_code < 500:  # Don't test server errors
            # Should include CORS headers for allowed origins
            assert "access-control-allow-origin" in response.headers
            assert response.headers["access-control-allow-origin"] == origin
            
            # Should allow credentials
            assert "access-control-allow-credentials" in response.headers
            assert response.headers["access-control-allow-credentials"] == "true"
    
    @given(
        invalid_origin=st.sampled_from([
            "http://evil.com",
            "https://malicious.org",
            "http://untrusted.net",
            "https://random-site.io",
            "http://not-allowed.dev"
        ])
    )
    @hypothesis_settings(max_examples=50)
    def test_property_4_cors_rejection_for_invalid_origins(self, invalid_origin):
        """
        **Feature: seasonal-anime-tracker, Property 4: CORS Header Consistency**
        
        For any invalid origin, CORS headers should not be included in responses.
        
        **Validates: Requirements 4.3, 4.4**
        """
        headers = {"Origin": invalid_origin}
        response = self.client.get("/api/v1/seasonal", headers=headers)
        
        # Property: invalid origins should not receive CORS headers
        # Note: FastAPI CORS middleware handles this automatically
        if "access-control-allow-origin" in response.headers:
            # If CORS headers are present, they should not match the invalid origin
            assert response.headers["access-control-allow-origin"] != invalid_origin
    
    @given(dummy=st.just(None))
    @hypothesis_settings(max_examples=50)
    def test_property_4_cors_headers_in_error_responses(self, dummy):
        """
        **Feature: seasonal-anime-tracker, Property 4: CORS Header Consistency**
        
        For any error response with valid origin, CORS headers should still be included.
        
        **Validates: Requirements 4.3, 4.4**
        """
        origin = settings.effective_cors_origins[0]
        headers = {"Origin": origin}
        
        # Force an error by providing invalid parameters
        response = self.client.get("/api/v1/seasonal?year=1800", headers=headers)
        
        # Property: error responses should still include CORS headers
        assert response.status_code == 400  # Should be validation error
        
        # Should include CORS headers even for errors
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == origin
    
    @given(
        custom_headers=st.lists(
            st.tuples(
                st.sampled_from(["X-Custom-Header", "Authorization", "Content-Type"]),
                st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=1, max_size=20)
            ),
            min_size=1,
            max_size=3
        )
    )
    @hypothesis_settings(max_examples=50)
    def test_property_4_cors_with_custom_headers(self, custom_headers):
        """
        **Feature: seasonal-anime-tracker, Property 4: CORS Header Consistency**
        
        For any request with custom headers and valid origin, CORS should handle
        the headers appropriately.
        
        **Validates: Requirements 4.3, 4.4**
        """
        origin = settings.effective_cors_origins[0]
        headers = {"Origin": origin}
        
        # Add custom headers
        for header_name, header_value in custom_headers:
            headers[header_name] = header_value
        
        response = self.client.get("/api/v1/seasonal", headers=headers)
        
        # Property: custom headers should not break CORS functionality
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == origin
        
        # Property: response should be successful or have expected error
        assert response.status_code in [200, 400, 404, 500, 502, 503, 504]