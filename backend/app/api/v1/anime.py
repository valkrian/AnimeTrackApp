"""
Anime API routes for seasonal anime data.
Provides endpoints for fetching current and historical seasonal anime information.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from app.services.anime_service import get_anime_service, AnimeService
from app.models.anime import SeasonalAnimeResponse

router = APIRouter()


@router.get("/seasonal", response_model=SeasonalAnimeResponse)
async def get_seasonal_anime(
    year: Optional[int] = Query(None, description="Year for specific season (e.g., 2024)"),
    season: Optional[str] = Query(None, description="Season name (winter, spring, summer, fall)"),
    anime_service: AnimeService = Depends(get_anime_service)
) -> SeasonalAnimeResponse:
    """
    Get seasonal anime data from Jikan API with cache-first strategy.
    
    Args:
        year: Optional year for specific season (defaults to current season)
        season: Optional season name (winter/spring/summer/fall, defaults to current)
        anime_service: Injected anime service dependency
        
    Returns:
        SeasonalAnimeResponse: Validated seasonal anime data
        
    Raises:
        HTTPException: Various error conditions with appropriate status codes
        
    Examples:
        - GET /api/v1/anime/seasonal - Current season
        - GET /api/v1/anime/seasonal?year=2024&season=winter - Winter 2024
        - GET /api/v1/anime/seasonal?year=2023 - Current season of 2023
    """
    try:
        # Validate season parameter if provided
        if season and season.lower() not in ["winter", "spring", "summer", "fall"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid season. Must be one of: winter, spring, summer, fall"
            )
        
        # Validate year parameter if provided
        if year and (year < 1900 or year > 2030):
            raise HTTPException(
                status_code=400,
                detail="Invalid year. Must be between 1900 and 2030"
            )
        
        # Fetch seasonal anime data using the service
        seasonal_data = await anime_service.fetch_seasonal_anime(year, season)
        
        return seasonal_data
        
    except HTTPException:
        # Re-raise HTTPExceptions from service layer
        raise
        
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the request"
        )


@router.get("/seasonal/health")
async def seasonal_health_check():
    """
    Health check endpoint specifically for the seasonal anime functionality.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "endpoint": "seasonal_anime",
        "cache_enabled": True,
        "external_api": "jikan.moe"
    }