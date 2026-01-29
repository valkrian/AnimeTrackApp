"""
Pydantic models for anime data validation.
Defines data structures for Jikan API responses with strict validation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, HttpUrl


class Studio(BaseModel):
    """Studio information model."""
    mal_id: int = Field(..., description="MyAnimeList ID for the studio")
    name: str = Field(..., description="Studio name")
    url: HttpUrl = Field(..., description="Studio URL on MyAnimeList")


class Genre(BaseModel):
    """Genre information model."""
    mal_id: int = Field(..., description="MyAnimeList ID for the genre")
    name: str = Field(..., description="Genre name")
    type: str = Field(..., description="Genre type (e.g., 'anime')")
    url: HttpUrl = Field(..., description="Genre URL on MyAnimeList")


class AnimeImages(BaseModel):
    """Anime image URLs model."""
    
    class ImageFormat(BaseModel):
        """Image format with different sizes."""
        image_url: Optional[HttpUrl] = Field(None, description="Standard image URL")
        small_image_url: Optional[HttpUrl] = Field(None, description="Small image URL")
        large_image_url: Optional[HttpUrl] = Field(None, description="Large image URL")
    
    jpg: Optional[ImageFormat] = Field(None, description="JPG format images")
    webp: Optional[ImageFormat] = Field(None, description="WebP format images")


class AnimeTrailer(BaseModel):
    """Anime trailer information model."""
    youtube_id: Optional[str] = Field(None, description="YouTube video ID")
    url: Optional[HttpUrl] = Field(None, description="Trailer URL")
    embed_url: Optional[HttpUrl] = Field(None, description="Embeddable trailer URL")


class AnimeAired(BaseModel):
    """Anime airing period model."""
    from_date: Optional[datetime] = Field(None, alias="from", description="Start date")
    to_date: Optional[datetime] = Field(None, alias="to", description="End date")
    prop: Optional[Dict[str, Any]] = Field(None, description="Additional properties")
    string: Optional[str] = Field(None, description="Human-readable airing period")


class AnimeBroadcast(BaseModel):
    """Anime broadcast information model."""
    day: Optional[str] = Field(None, description="Day of the week")
    time: Optional[str] = Field(None, description="Broadcast time")
    timezone: Optional[str] = Field(None, description="Timezone")
    string: Optional[str] = Field(None, description="Human-readable broadcast info")


class AnimeItem(BaseModel):
    """
    Main anime item model representing a single anime from Jikan API.
    Includes comprehensive validation for all fields.
    """
    
    # Core identification
    mal_id: int = Field(..., description="MyAnimeList ID")
    url: HttpUrl = Field(..., description="MyAnimeList URL")
    
    # Titles
    title: str = Field(..., description="Main title")
    title_english: Optional[str] = Field(None, description="English title")
    title_japanese: Optional[str] = Field(None, description="Japanese title")
    title_synonyms: List[str] = Field(default_factory=list, description="Alternative titles")
    
    # Content information
    synopsis: Optional[str] = Field(None, description="Anime synopsis")
    background: Optional[str] = Field(None, description="Background information")
    
    # Ratings and statistics
    score: Optional[float] = Field(None, ge=0, le=10, description="Average score (0-10)")
    scored_by: Optional[int] = Field(None, ge=0, description="Number of users who scored")
    rank: Optional[int] = Field(None, ge=1, description="Ranking position")
    popularity: Optional[int] = Field(None, ge=1, description="Popularity ranking")
    members: Optional[int] = Field(None, ge=0, description="Number of members")
    favorites: Optional[int] = Field(None, ge=0, description="Number of favorites")
    
    # Status and airing information
    status: str = Field(..., description="Airing status")
    airing: bool = Field(..., description="Currently airing flag")
    aired: Optional[AnimeAired] = Field(None, description="Airing period")
    broadcast: Optional[AnimeBroadcast] = Field(None, description="Broadcast information")
    
    # Content details
    type: Optional[str] = Field(None, description="Anime type (TV, Movie, etc.)")
    source: str = Field(..., description="Source material")
    episodes: Optional[int] = Field(None, ge=0, description="Number of episodes")
    duration: Optional[str] = Field(None, description="Episode duration")
    rating: Optional[str] = Field(None, description="Content rating")
    season: Optional[str] = Field(None, description="Season (winter/spring/summer/fall)")
    year: Optional[int] = Field(None, ge=1900, description="Year")
    
    # Related entities
    studios: List[Studio] = Field(default_factory=list, description="Animation studios")
    genres: List[Genre] = Field(default_factory=list, description="Genres")
    themes: List[Genre] = Field(default_factory=list, description="Themes")
    demographics: List[Genre] = Field(default_factory=list, description="Demographics")
    
    # Media
    images: Optional[AnimeImages] = Field(None, description="Anime images")
    trailer: Optional[AnimeTrailer] = Field(None, description="Trailer information")
    
    # Additional metadata
    approved: Optional[bool] = Field(None, description="Approval status")
    titles: List[Dict[str, str]] = Field(default_factory=list, description="All titles")
    
    @validator('score')
    def validate_score(cls, v):
        """Ensure score is within valid range if provided."""
        if v is not None and not (0 <= v <= 10):
            raise ValueError('Score must be between 0 and 10')
        return v
    
    @validator('title', 'status', 'source')
    def validate_required_strings(cls, v):
        """Ensure required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError('Required string field cannot be empty')
        return v.strip()
    
    @validator('synopsis', 'background', 'duration', 'rating')
    def validate_optional_strings(cls, v):
        """Clean optional string fields."""
        if v is not None:
            v = v.strip()
            return v if v else None
        return v


class PaginationInfo(BaseModel):
    """Pagination information model."""
    last_visible_page: int = Field(..., ge=1, description="Last visible page number")
    has_next_page: bool = Field(..., description="Whether there's a next page")
    current_page: int = Field(default=1, ge=1, description="Current page number")
    items: Optional[Dict[str, int]] = Field(None, description="Items count information")


class SeasonalAnimeResponse(BaseModel):
    """
    Complete response model for seasonal anime API endpoint.
    Validates the entire Jikan API response structure.
    """
    
    data: List[AnimeItem] = Field(..., description="List of anime items")
    pagination: PaginationInfo = Field(..., description="Pagination information")
    
    @validator('data')
    def validate_data_list(cls, v):
        """Ensure data list is valid."""
        if not isinstance(v, list):
            raise ValueError('Data must be a list')
        return v
    
    class Config:
        """Pydantic configuration."""
        # Allow population by field name or alias
        populate_by_name = True
        # Validate assignment to catch runtime changes
        validate_assignment = True
        # Use enum values instead of enum objects
        use_enum_values = True


class CacheEntry(BaseModel):
    """
    Cache entry model for storing API responses with metadata.
    """
    
    data: SeasonalAnimeResponse = Field(..., description="Cached anime data")
    timestamp: datetime = Field(..., description="Cache creation timestamp")
    expires_at: datetime = Field(..., description="Cache expiration timestamp")
    cache_key: str = Field(..., description="Cache key identifier")
    
    @validator('expires_at')
    def validate_expiration(cls, v, values):
        """Ensure expiration is after timestamp."""
        if 'timestamp' in values and v <= values['timestamp']:
            raise ValueError('Expiration must be after timestamp')
        return v
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.utcnow() >= self.expires_at
    
    def time_to_live(self) -> int:
        """Get remaining time to live in seconds."""
        if self.is_expired():
            return 0
        return int((self.expires_at - datetime.utcnow()).total_seconds())