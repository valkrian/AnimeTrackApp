"""
FastAPI application entry point for Seasonal Anime Tracker.
Configures CORS, middleware, and API routes for the backend service.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings, get_cors_config
from app.core.cache import get_cache
from app.api.v1 import anime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="Seasonal Anime Tracker API",
    description="A FastAPI backend for tracking seasonal anime releases with Jikan API integration",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Configure trusted host middleware for production security
if settings.ENVIRONMENT == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Configure CORS middleware with comprehensive settings
cors_config = get_cors_config()
app.add_middleware(CORSMiddleware, **cors_config)

# Include API routes
app.include_router(anime.router, prefix="/api/v1", tags=["anime"])


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Initialize background tasks and services.
    """
    # Start cache cleanup task
    cache = get_cache()
    cache.start_cleanup_task()
    logger.info("Application startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    Clean up background tasks and resources.
    """
    # Stop cache cleanup task
    cache = get_cache()
    cache.stop_cleanup_task()
    logger.info("Application shutdown completed")


# Global exception handler for CORS errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler that ensures proper CORS headers are included in error responses.
    """
    # Get the origin from the request
    origin = request.headers.get("origin")
    cors_headers = {}

    # Only add CORS headers if origin is in allowed origins
    if origin and origin in settings.effective_cors_origins:
        cors_headers.update(
            {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH",
                "Access-Control-Allow-Headers": "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, X-CSRF-Token, Cache-Control, Pragma",
            }
        )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=cors_headers,
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancer probes.

    Returns:
        dict: Service health status and configuration info
    """
    return {
        "status": "healthy",
        "service": "seasonal-anime-tracker",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "cors_enabled": True,
        "cors_origins": len(settings.CORS_ORIGINS),
    }


# CORS preflight handler for complex requests
@app.options("/{path:path}")
async def options_handler(request, path: str):
    """
    Handle OPTIONS preflight requests for CORS.

    Args:
        request: The incoming request
        path: The requested path

    Returns:
        JSONResponse: Empty response with proper CORS headers
    """
    # Get the origin from the request
    origin = request.headers.get("origin")
    cors_headers = {}

    # Only add CORS headers if origin is in allowed origins
    if origin and origin in settings.effective_cors_origins:
        cors_headers.update(
            {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH",
                "Access-Control-Allow-Headers": "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, X-CSRF-Token, Cache-Control, Pragma",
                "Access-Control-Max-Age": "86400",
            }
        )

    return JSONResponse(content={}, headers=cors_headers)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint providing API information.

    Returns:
        dict: API welcome message and available endpoints
    """
    return {
        "message": "Seasonal Anime Tracker API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "health": "/health",
        "api": {"seasonal_anime": "/api/v1/anime/seasonal"},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
