"""
FastAPI application entry point for Seasonal Anime Tracker.
Configures CORS, middleware, and API routes for the backend service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings, get_cors_config
from app.api.v1 import anime

# Create FastAPI application instance
app = FastAPI(
    title="Seasonal Anime Tracker API",
    description="A FastAPI backend for tracking seasonal anime releases with Jikan API integration",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# Configure trusted host middleware for production security
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with actual domains in production
    )

# Configure CORS middleware with comprehensive settings
cors_config = get_cors_config()
app.add_middleware(CORSMiddleware, **cors_config)

# Include API routes
app.include_router(anime.router, prefix="/api/v1", tags=["anime"])

# Global exception handler for CORS errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler that ensures CORS headers are included in error responses.
    """
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
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
        "cors_origins": len(settings.CORS_ORIGINS)
    }

# CORS preflight handler for complex requests
@app.options("/{path:path}")
async def options_handler(path: str):
    """
    Handle OPTIONS preflight requests for CORS.
    
    Args:
        path: The requested path
        
    Returns:
        JSONResponse: Empty response with CORS headers
    """
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH",
            "Access-Control-Allow-Headers": "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, X-CSRF-Token, Cache-Control, Pragma",
            "Access-Control-Max-Age": "86400"
        }
    )

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
        "api": {
            "seasonal_anime": "/api/v1/anime/seasonal"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )