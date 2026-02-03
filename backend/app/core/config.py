"""
Configuration management for the Seasonal Anime Tracker backend.
Handles environment variables with validation and defaults.
Supports both development and production environments.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    Automatically loads from .env file and environment variables.
    """

    # API Configuration
    JIKAN_API_URL: str = "https://api.jikan.moe/v4"

    # Cache Configuration
    CACHE_TTL_MINUTES: int = 60

    # CORS Configuration - Development defaults
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js development server
        "http://localhost:3001",  # Next.js development server (alternate port)
        "http://localhost:5173",  # Vite development server
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://127.0.0.1:3001",  # Alternative localhost (alternate port)
        "http://127.0.0.1:5173",  # Alternative localhost
        "http://localhost:4173",  # Vite preview server
        "http://127.0.0.1:4173",  # Alternative localhost preview
    ]

    # Production CORS origins (override via environment variable)
    PRODUCTION_CORS_ORIGINS: List[str] = []

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Environment Configuration
    ENVIRONMENT: str = "development"

    # Security Configuration
    ALLOWED_HOSTS: List[str] = ["*"]

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable or use defaults."""
        if isinstance(v, str):
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins if origins else cls.__fields__["CORS_ORIGINS"].default
        return v

    @validator("PRODUCTION_CORS_ORIGINS", pre=True)
    def parse_production_cors_origins(cls, v):
        """Parse production CORS origins from environment variable."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v or []

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from environment variable."""
        if isinstance(v, str):
            hosts = [host.strip() for host in v.split(",") if host.strip()]
            return hosts if hosts else ["*"]
        return v

    @validator("CACHE_TTL_MINUTES")
    def validate_cache_ttl(cls, v):
        """Ensure cache TTL is positive."""
        if v <= 0:
            raise ValueError("Cache TTL must be positive")
        return v

    @validator("PORT")
    def validate_port(cls, v):
        """Ensure port is in valid range."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment setting."""
        valid_environments = ["development", "production", "testing", "staging"]
        if v.lower() not in valid_environments:
            raise ValueError(
                f"Environment must be one of: {', '.join(valid_environments)}"
            )
        return v.lower()

    @property
    def effective_cors_origins(self) -> List[str]:
        """
        Get effective CORS origins based on environment.
        Uses production origins in production, development origins otherwise.
        """
        if self.ENVIRONMENT == "production" and self.PRODUCTION_CORS_ORIGINS:
            return self.PRODUCTION_CORS_ORIGINS
        return self.CORS_ORIGINS

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Allow extra fields for forward compatibility
        extra = "ignore"


# Global settings instance
settings = Settings()

# Update CORS origins based on environment
if settings.is_production and settings.PRODUCTION_CORS_ORIGINS:
    settings.CORS_ORIGINS = settings.PRODUCTION_CORS_ORIGINS


def get_settings() -> Settings:
    """
    Get application settings instance.
    Useful for dependency injection in FastAPI.

    Returns:
        Settings: Configured application settings
    """
    return settings


def get_cors_config() -> dict:
    """
    Get CORS configuration dictionary for middleware setup.

    Returns:
        dict: CORS configuration parameters
    """
    return {
        "allow_origins": settings.effective_cors_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        "allow_headers": [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "Cache-Control",
            "Pragma",
        ],
        "expose_headers": [
            "Content-Length",
            "Content-Type",
            "Cache-Control",
            "Expires",
            "Last-Modified",
            "ETag",
        ],
        "max_age": 86400,  # 24 hours
    }
