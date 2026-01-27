"""
Anime API routes for seasonal anime data.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/seasonal")
async def get_seasonal_anime():
    """
    Get current seasonal anime data.
    This endpoint will be implemented in task 3.1.
    """
    return {"message": "Seasonal anime endpoint - to be implemented"}