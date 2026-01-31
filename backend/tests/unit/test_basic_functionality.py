"""
Basic unit tests for core functionality.
Complements property-based tests with specific examples.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.core.config import Settings
from app.core.cache import InMemoryCache
from app.models.anime import SeasonalAnimeResponse, PaginationInfo


class TestBasicFunctionality:
    """Basic unit tests for core functionality."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test that health endpoint returns expected response."""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "seasonal-anime-tracker"
        assert "version" in data
    
    def test_root_endpoint(self):
        """Test that root endpoint returns API information."""
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "api" in data
        assert "seasonal_anime" in data["api"]
    
    def test_seasonal_health_endpoint(self):
        """Test seasonal anime health check endpoint."""
        response = self.client.get("/api/v1/seasonal/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["endpoint"] == "seasonal_anime"
    
    def test_configuration_defaults(self):
        """Test that configuration has sensible defaults."""
        settings = Settings()
        
        assert settings.JIKAN_API_URL == "https://api.jikan.moe/v4"
        assert settings.CACHE_TTL_MINUTES == 60
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert len(settings.CORS_ORIGINS) > 0
    
    def test_cache_basic_operations(self):
        """Test basic cache operations work correctly."""
        cache = InMemoryCache()
        
        # Test empty cache
        assert cache.get("nonexistent") is None
        
        # Test storing and retrieving data
        test_data = SeasonalAnimeResponse(
            data=[],
            pagination=PaginationInfo(last_visible_page=1, has_next_page=False)
        )
        
        cache.set("test_key", test_data)
        retrieved = cache.get("test_key")
        
        assert retrieved is not None
        assert retrieved.data == test_data.data
        
        # Test deletion
        assert cache.delete("test_key") is True
        assert cache.get("test_key") is None
        assert cache.delete("test_key") is False
    
    @patch('app.services.anime_service.AnimeService.fetch_seasonal_anime')
    def test_seasonal_anime_endpoint_success(self, mock_fetch):
        """Test successful seasonal anime endpoint response."""
        # Mock successful response
        mock_data = SeasonalAnimeResponse(
            data=[],
            pagination=PaginationInfo(last_visible_page=1, has_next_page=False)
        )
        mock_fetch.return_value = mock_data
        
        response = self.client.get("/api/v1/seasonal")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "pagination" in data
    
    def test_seasonal_anime_invalid_parameters(self):
        """Test seasonal anime endpoint with invalid parameters."""
        # Invalid year
        response = self.client.get("/api/v1/seasonal?year=1800")
        assert response.status_code == 400
        
        # Invalid season
        response = self.client.get("/api/v1/seasonal?season=invalid")
        assert response.status_code == 400
    
    def test_cors_preflight_request(self):
        """Test CORS preflight OPTIONS request."""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = self.client.options("/api/v1/seasonal", headers=headers)
        assert response.status_code == 200
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers