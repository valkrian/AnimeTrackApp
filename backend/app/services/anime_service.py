"""
Anime service for fetching seasonal anime data from Jikan API.
Handles external API integration with proper error handling and timeout management.
Integrates with cache system for optimal performance.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.core.cache import get_seasonal_anime_cache, set_seasonal_anime_cache
from app.models.anime import SeasonalAnimeResponse

# Configure logging
logger = logging.getLogger(__name__)


class AnimeService:
    """
    Service class for interacting with the Jikan API.
    Provides methods to fetch seasonal anime data with proper error handling.
    """

    def __init__(self):
        """Initialize the anime service with HTTP client configuration."""
        self.base_url = settings.JIKAN_API_URL
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def fetch_seasonal_anime(
        self, year: Optional[int] = None, season: Optional[str] = None
    ) -> SeasonalAnimeResponse:
        """
        Fetch seasonal anime data from Jikan API with cache-first strategy.

        Args:
            year: Optional year for specific season (defaults to current)
            season: Optional season name (winter/spring/summer/fall, defaults to current)

        Returns:
            SeasonalAnimeResponse containing validated seasonal anime data

        Raises:
            HTTPException: For various API error conditions
        """
        # Try to get data from cache first
        cached_data = await get_seasonal_anime_cache(year, season)
        if cached_data is not None:
            logger.info("Returning cached seasonal anime data")
            return cached_data

        try:
            # Construct API endpoint URL
            if year and season:
                endpoint = f"{self.base_url}/seasons/{year}/{season.lower()}"
            else:
                endpoint = f"{self.base_url}/seasons/now"

            logger.info(f"Fetching seasonal anime from: {endpoint}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint)

                # Handle different HTTP status codes
                if response.status_code == 200:
                    raw_data = response.json()

                    # Validate data using Pydantic model
                    try:
                        validated_data = SeasonalAnimeResponse(**raw_data)
                        logger.info(
                            f"Successfully fetched and validated {len(validated_data.data)} anime items"
                        )

                        # Cache the validated data
                        await set_seasonal_anime_cache(validated_data, year, season)

                        return validated_data

                    except Exception as validation_error:
                        logger.error(f"Data validation failed: {validation_error}")
                        raise HTTPException(
                            status_code=502,
                            detail="Invalid data format received from external API",
                        )

                elif response.status_code == 404:
                    logger.warning(f"Season not found: {endpoint}")
                    raise HTTPException(
                        status_code=404,
                        detail=f"Season data not found for the requested period",
                    )

                elif response.status_code == 429:
                    logger.warning("Rate limit exceeded for Jikan API")
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Please try again later.",
                    )

                elif response.status_code >= 500:
                    logger.error(f"Jikan API server error: {response.status_code}")
                    raise HTTPException(
                        status_code=502,
                        detail="External API service temporarily unavailable",
                    )

                else:
                    logger.error(f"Unexpected API response: {response.status_code}")
                    raise HTTPException(
                        status_code=502,
                        detail=f"Unexpected response from external API: {response.status_code}",
                    )

        except httpx.TimeoutException as e:
            logger.error(f"Timeout while fetching seasonal anime: {e}")
            raise HTTPException(
                status_code=504,
                detail="Request timeout while fetching anime data. Please try again.",
            )

        except httpx.NetworkError as e:
            logger.error(f"Network error while fetching seasonal anime: {e}")
            raise HTTPException(
                status_code=503,
                detail="Network error occurred. Please check your connection and try again.",
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while fetching seasonal anime: {e}")
            raise HTTPException(
                status_code=502, detail="Error communicating with external API service"
            )

        except HTTPException:
            # Re-raise HTTPExceptions as-is
            raise

        except Exception as e:
            logger.error(f"Unexpected error while fetching seasonal anime: {e}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while fetching anime data",
            )


# Global service instance
anime_service = AnimeService()


def get_anime_service() -> AnimeService:
    """
    Get anime service instance.
    Useful for dependency injection in FastAPI.
    """
    return anime_service
