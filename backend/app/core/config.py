"""
Configuration management for the Seasonal Anime Tracker backend.
Handles environment variables with validation and defaults.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """
    
    # API Configuration
    JIKAN_API_URL: str = "https://api.jikan.moe/v4"
    
    # Cache Configuration
    CACHE_TTL_MINUTES: int = 60
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js development server
        "http://localhost:5173",  # Vite development server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @validator('CORS_ORIGINS', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable or use defaults."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator('CACHE_TTL_MINUTES')
    def validate_cache_ttl(cls, v):
        """Ensure cache TTL is positive."""
        if v <= 0:
            raise ValueError("Cache TTL must be positive")
        return v
    
    @validator('PORT')
    def validate_port(cls, v):
        """Ensure port is in valid range."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings instance.
    Useful for dependency injection in FastAPI.
    """
    return settings