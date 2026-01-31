"""
Property-based tests for configuration management.
Tests Property 9: Configuration Management
"""

import os
import pytest
from hypothesis import given, strategies as st
from hypothesis import settings as hypothesis_settings
from pydantic import ValidationError

from app.core.config import Settings, get_cors_config


class TestConfigurationProperties:
    """Property-based tests for configuration management."""
    
    @given(
        cors_origins=st.lists(
            st.text(min_size=1, max_size=50).filter(lambda x: ',' not in x and x.strip()),
            min_size=1,
            max_size=10
        )
    )
    @hypothesis_settings(max_examples=100)
    def test_property_9_cors_origins_parsing(self, cors_origins):
        """
        **Feature: seasonal-anime-tracker, Property 9: Configuration Management**
        
        For any valid list of CORS origins, the configuration should parse them correctly
        and return the same origins when accessed.
        
        **Validates: Requirements 9.2**
        """
        # Convert list to comma-separated string
        cors_string = ",".join(cors_origins)
        
        # Create settings with the CORS origins
        settings = Settings(CORS_ORIGINS=cors_string)
        
        # Property: parsed origins should match input origins (after stripping)
        expected_origins = [origin.strip() for origin in cors_origins if origin.strip()]
        assert settings.CORS_ORIGINS == expected_origins
        
        # Property: effective CORS origins should be accessible
        effective_origins = settings.effective_cors_origins
        assert isinstance(effective_origins, list)
        assert len(effective_origins) > 0
    
    @given(
        cache_ttl=st.integers(min_value=1, max_value=1440)  # 1 minute to 24 hours
    )
    @hypothesis_settings(max_examples=100)
    def test_property_9_cache_ttl_validation(self, cache_ttl):
        """
        **Feature: seasonal-anime-tracker, Property 9: Configuration Management**
        
        For any positive cache TTL value, the configuration should accept and store it correctly.
        
        **Validates: Requirements 9.2**
        """
        settings = Settings(CACHE_TTL_MINUTES=cache_ttl)
        
        # Property: TTL should be stored exactly as provided
        assert settings.CACHE_TTL_MINUTES == cache_ttl
        
        # Property: TTL should be positive
        assert settings.CACHE_TTL_MINUTES > 0
    
    @given(
        port=st.integers(min_value=1, max_value=65535)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_9_port_validation(self, port):
        """
        **Feature: seasonal-anime-tracker, Property 9: Configuration Management**
        
        For any valid port number, the configuration should accept and store it correctly.
        
        **Validates: Requirements 9.2**
        """
        settings = Settings(PORT=port)
        
        # Property: port should be stored exactly as provided
        assert settings.PORT == port
        
        # Property: port should be in valid range
        assert 1 <= settings.PORT <= 65535
    
    @given(
        environment=st.sampled_from(["development", "production", "testing", "staging"])
    )
    @hypothesis_settings(max_examples=100)
    def test_property_9_environment_validation(self, environment):
        """
        **Feature: seasonal-anime-tracker, Property 9: Configuration Management**
        
        For any valid environment value, the configuration should normalize and store it correctly.
        
        **Validates: Requirements 9.2**
        """
        settings = Settings(ENVIRONMENT=environment)
        
        # Property: environment should be normalized to lowercase
        assert settings.ENVIRONMENT == environment.lower()
        
        # Property: environment properties should be consistent
        if environment.lower() == "development":
            assert settings.is_development is True
            assert settings.is_production is False
        elif environment.lower() == "production":
            assert settings.is_development is False
            assert settings.is_production is True
    
    @given(
        cors_origins=st.lists(st.text(min_size=1, max_size=30), min_size=1, max_size=5),
        production_origins=st.lists(st.text(min_size=1, max_size=30), min_size=1, max_size=5)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_9_effective_cors_origins(self, cors_origins, production_origins):
        """
        **Feature: seasonal-anime-tracker, Property 9: Configuration Management**
        
        For any combination of CORS origins and production origins, the effective origins
        should be determined correctly based on the environment.
        
        **Validates: Requirements 9.2**
        """
        # Test development environment
        dev_settings = Settings(
            ENVIRONMENT="development",
            CORS_ORIGINS=cors_origins,
            PRODUCTION_CORS_ORIGINS=production_origins
        )
        
        # Property: development should use CORS_ORIGINS
        assert dev_settings.effective_cors_origins == cors_origins
        
        # Test production environment with production origins
        prod_settings = Settings(
            ENVIRONMENT="production",
            CORS_ORIGINS=cors_origins,
            PRODUCTION_CORS_ORIGINS=production_origins
        )
        
        # Property: production should use PRODUCTION_CORS_ORIGINS when available
        assert prod_settings.effective_cors_origins == production_origins
    
    def test_property_9_cors_config_consistency(self):
        """
        **Feature: seasonal-anime-tracker, Property 9: Configuration Management**
        
        For any valid configuration, the CORS config should be consistent with settings.
        
        **Validates: Requirements 9.2**
        """
        settings = Settings()
        cors_config = get_cors_config()
        
        # Property: CORS config should include all effective origins
        assert cors_config["allow_origins"] == settings.effective_cors_origins
        
        # Property: CORS config should have required fields
        required_fields = ["allow_origins", "allow_credentials", "allow_methods", "allow_headers"]
        for field in required_fields:
            assert field in cors_config
        
        # Property: credentials should be enabled
        assert cors_config["allow_credentials"] is True
        
        # Property: methods should include common HTTP methods
        methods = cors_config["allow_methods"]
        assert "GET" in methods
        assert "POST" in methods
        assert "OPTIONS" in methods


# Test invalid configurations to ensure proper validation
class TestConfigurationValidation:
    """Test configuration validation for invalid inputs."""
    
    def test_invalid_cache_ttl(self):
        """Test that invalid cache TTL values are rejected."""
        with pytest.raises(ValidationError):
            Settings(CACHE_TTL_MINUTES=0)
        
        with pytest.raises(ValidationError):
            Settings(CACHE_TTL_MINUTES=-1)
    
    def test_invalid_port(self):
        """Test that invalid port values are rejected."""
        with pytest.raises(ValidationError):
            Settings(PORT=0)
        
        with pytest.raises(ValidationError):
            Settings(PORT=65536)
    
    def test_invalid_environment(self):
        """Test that invalid environment values are rejected."""
        with pytest.raises(ValidationError):
            Settings(ENVIRONMENT="invalid")