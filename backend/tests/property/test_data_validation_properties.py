"""
Property-based tests for data validation.
Tests Property 1: Data Validation Consistency
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis import settings as hypothesis_settings
from pydantic import ValidationError
from datetime import datetime, timedelta

from app.models.anime import (
    AnimeItem, Studio, Genre, AnimeImages, SeasonalAnimeResponse, 
    PaginationInfo, CacheEntry
)


class TestDataValidationProperties:
    """Property-based tests for data validation consistency."""
    
    @given(
        mal_id=st.integers(min_value=1, max_value=999999),
        title=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        status=st.sampled_from(["Finished Airing", "Currently Airing", "Not yet aired"]),
        source=st.sampled_from(["Manga", "Light novel", "Original", "Game", "Novel"]),
        airing=st.booleans()
    )
    @hypothesis_settings(max_examples=100)
    def test_property_1_anime_item_validation(self, mal_id, title, status, source, airing):
        """
        **Feature: seasonal-anime-tracker, Property 1: Data Validation Consistency**
        
        For any valid anime data, the AnimeItem model should successfully validate
        and preserve all required fields correctly.
        
        **Validates: Requirements 1.5, 2.4**
        """
        # Create minimal valid anime item
        anime_data = {
            "mal_id": mal_id,
            "url": f"https://myanimelist.net/anime/{mal_id}",
            "title": title.strip(),
            "status": status,
            "source": source,
            "airing": airing
        }
        
        # Property: valid data should create valid AnimeItem
        anime_item = AnimeItem(**anime_data)
        
        # Property: all required fields should be preserved exactly
        assert anime_item.mal_id == mal_id
        assert anime_item.title == title.strip()
        assert anime_item.status == status
        assert anime_item.source == source
        assert anime_item.airing == airing
        
        # Property: URL should be valid
        assert str(anime_item.url) == f"https://myanimelist.net/anime/{mal_id}"
    
    @given(
        mal_id=st.integers(min_value=1, max_value=999999),
        name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip())
    )
    @hypothesis_settings(max_examples=100)
    def test_property_1_studio_validation(self, mal_id, name):
        """
        **Feature: seasonal-anime-tracker, Property 1: Data Validation Consistency**
        
        For any valid studio data, the Studio model should validate correctly.
        
        **Validates: Requirements 1.5, 2.4**
        """
        studio_data = {
            "mal_id": mal_id,
            "name": name.strip(),
            "url": f"https://myanimelist.net/anime/producer/{mal_id}"
        }
        
        # Property: valid studio data should create valid Studio
        studio = Studio(**studio_data)
        
        # Property: all fields should be preserved exactly
        assert studio.mal_id == mal_id
        assert studio.name == name.strip()
        assert str(studio.url) == f"https://myanimelist.net/anime/producer/{mal_id}"
    
    @given(
        mal_id=st.integers(min_value=1, max_value=999999),
        name=st.text(min_size=1, max_size=30).filter(lambda x: x.strip()),
        genre_type=st.sampled_from(["anime", "manga"])
    )
    @hypothesis_settings(max_examples=100)
    def test_property_1_genre_validation(self, mal_id, name, genre_type):
        """
        **Feature: seasonal-anime-tracker, Property 1: Data Validation Consistency**
        
        For any valid genre data, the Genre model should validate correctly.
        
        **Validates: Requirements 1.5, 2.4**
        """
        genre_data = {
            "mal_id": mal_id,
            "name": name.strip(),
            "type": genre_type,
            "url": f"https://myanimelist.net/anime/genre/{mal_id}"
        }
        
        # Property: valid genre data should create valid Genre
        genre = Genre(**genre_data)
        
        # Property: all fields should be preserved exactly
        assert genre.mal_id == mal_id
        assert genre.name == name.strip()
        assert genre.type == genre_type
        assert str(genre.url) == f"https://myanimelist.net/anime/genre/{mal_id}"
    
    @given(
        score=st.one_of(st.none(), st.floats(min_value=0.0, max_value=10.0)),
        scored_by=st.one_of(st.none(), st.integers(min_value=0, max_value=1000000)),
        rank=st.one_of(st.none(), st.integers(min_value=1, max_value=50000)),
        episodes=st.one_of(st.none(), st.integers(min_value=0, max_value=5000))
    )
    @hypothesis_settings(max_examples=100)
    def test_property_1_optional_fields_validation(self, score, scored_by, rank, episodes):
        """
        **Feature: seasonal-anime-tracker, Property 1: Data Validation Consistency**
        
        For any combination of optional fields, the AnimeItem should handle them correctly.
        
        **Validates: Requirements 1.5, 2.4**
        """
        anime_data = {
            "mal_id": 12345,
            "url": "https://myanimelist.net/anime/12345",
            "title": "Test Anime",
            "status": "Finished Airing",
            "source": "Manga",
            "airing": False,
            "score": score,
            "scored_by": scored_by,
            "rank": rank,
            "episodes": episodes
        }
        
        # Property: optional fields should be handled correctly
        anime_item = AnimeItem(**anime_data)
        
        # Property: optional fields should preserve None or valid values
        assert anime_item.score == score
        assert anime_item.scored_by == scored_by
        assert anime_item.rank == rank
        assert anime_item.episodes == episodes
        
        # Property: if score is provided, it should be in valid range
        if anime_item.score is not None:
            assert 0.0 <= anime_item.score <= 10.0
    
    @given(
        anime_count=st.integers(min_value=0, max_value=100),
        last_page=st.integers(min_value=1, max_value=100),
        has_next=st.booleans()
    )
    @hypothesis_settings(max_examples=100)
    def test_property_1_seasonal_response_validation(self, anime_count, last_page, has_next):
        """
        **Feature: seasonal-anime-tracker, Property 1: Data Validation Consistency**
        
        For any valid seasonal anime response data, the SeasonalAnimeResponse should validate correctly.
        
        **Validates: Requirements 1.5, 2.4**
        """
        # Create anime items
        anime_items = []
        for i in range(anime_count):
            anime_data = {
                "mal_id": i + 1,
                "url": f"https://myanimelist.net/anime/{i + 1}",
                "title": f"Test Anime {i + 1}",
                "status": "Finished Airing",
                "source": "Manga",
                "airing": False
            }
            anime_items.append(anime_data)
        
        # Create pagination info
        pagination_data = {
            "last_visible_page": last_page,
            "has_next_page": has_next,
            "current_page": 1
        }
        
        response_data = {
            "data": anime_items,
            "pagination": pagination_data
        }
        
        # Property: valid response data should create valid SeasonalAnimeResponse
        response = SeasonalAnimeResponse(**response_data)
        
        # Property: data list should have correct length
        assert len(response.data) == anime_count
        
        # Property: pagination should be preserved
        assert response.pagination.last_visible_page == last_page
        assert response.pagination.has_next_page == has_next
        
        # Property: all anime items should be valid
        for i, anime in enumerate(response.data):
            assert anime.mal_id == i + 1
            assert anime.title == f"Test Anime {i + 1}"
    
    @given(
        ttl_minutes=st.integers(min_value=1, max_value=1440)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_1_cache_entry_validation(self, ttl_minutes):
        """
        **Feature: seasonal-anime-tracker, Property 1: Data Validation Consistency**
        
        For any valid cache entry data, the CacheEntry should validate time relationships correctly.
        
        **Validates: Requirements 1.5, 2.4**
        """
        # Create minimal seasonal response
        response_data = {
            "data": [],
            "pagination": {
                "last_visible_page": 1,
                "has_next_page": False
            }
        }
        seasonal_response = SeasonalAnimeResponse(**response_data)
        
        # Create cache entry with time relationships
        now = datetime.utcnow()
        expires_at = now.replace(microsecond=0).replace(second=0) + \
                    timedelta(minutes=ttl_minutes)
        
        cache_data = {
            "data": seasonal_response,
            "timestamp": now,
            "expires_at": expires_at,
            "cache_key": "test_key"
        }
        
        # Property: valid cache data should create valid CacheEntry
        cache_entry = CacheEntry(**cache_data)
        
        # Property: timestamps should be preserved
        assert cache_entry.timestamp == now
        assert cache_entry.expires_at == expires_at
        
        # Property: expiration should be after timestamp
        assert cache_entry.expires_at > cache_entry.timestamp
        
        # Property: TTL should be positive when not expired
        if not cache_entry.is_expired():
            assert cache_entry.time_to_live() > 0


class TestDataValidationErrors:
    """Test data validation error cases."""
    
    def test_invalid_anime_item_required_fields(self):
        """Test that missing required fields are rejected."""
        # Missing mal_id
        with pytest.raises(ValidationError):
            AnimeItem(
                url="https://myanimelist.net/anime/1",
                title="Test",
                status="Finished Airing",
                source="Manga",
                airing=False
            )
        
        # Empty title
        with pytest.raises(ValidationError):
            AnimeItem(
                mal_id=1,
                url="https://myanimelist.net/anime/1",
                title="",
                status="Finished Airing",
                source="Manga",
                airing=False
            )
    
    def test_invalid_score_range(self):
        """Test that invalid score values are rejected."""
        with pytest.raises(ValidationError):
            AnimeItem(
                mal_id=1,
                url="https://myanimelist.net/anime/1",
                title="Test",
                status="Finished Airing",
                source="Manga",
                airing=False,
                score=11.0  # Invalid: > 10
            )
        
        with pytest.raises(ValidationError):
            AnimeItem(
                mal_id=1,
                url="https://myanimelist.net/anime/1",
                title="Test",
                status="Finished Airing",
                source="Manga",
                airing=False,
                score=-1.0  # Invalid: < 0
            )
    
    def test_invalid_cache_entry_timestamps(self):
        """Test that invalid timestamp relationships are rejected."""
        response_data = {
            "data": [],
            "pagination": {"last_visible_page": 1, "has_next_page": False}
        }
        seasonal_response = SeasonalAnimeResponse(**response_data)
        
        now = datetime.utcnow()
        past = now - timedelta(minutes=10)
        
        # Expiration before timestamp should be invalid
        with pytest.raises(ValidationError):
            CacheEntry(
                data=seasonal_response,
                timestamp=now,
                expires_at=past,  # Invalid: before timestamp
                cache_key="test"
            )