"""
Models package for the Seasonal Anime Tracker backend.
Exports all Pydantic models for data validation.
"""

from .anime import (
    AnimeItem,
    Studio,
    Genre,
    AnimeImages,
    AnimeTrailer,
    AnimeAired,
    AnimeBroadcast,
    SeasonalAnimeResponse,
    PaginationInfo,
    CacheEntry
)

__all__ = [
    "AnimeItem",
    "Studio", 
    "Genre",
    "AnimeImages",
    "AnimeTrailer",
    "AnimeAired",
    "AnimeBroadcast",
    "SeasonalAnimeResponse",
    "PaginationInfo",
    "CacheEntry"
]