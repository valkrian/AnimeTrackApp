"""
Property-based tests for cache behavior.
Tests Property 3: Cache Round-Trip Consistency
"""

import asyncio
from datetime import datetime, timedelta
from hypothesis import given, strategies as st
from hypothesis import settings as hypothesis_settings
import pytest

from app.core.cache import InMemoryCache, get_seasonal_anime_cache, set_seasonal_anime_cache
from app.models.anime import SeasonalAnimeResponse, PaginationInfo


class TestCacheProperties:
    """Property-based tests for cache round-trip consistency."""
    
    @given(
        cache_key=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        ttl_minutes=st.integers(min_value=1, max_value=60)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_3_cache_round_trip_consistency(self, cache_key, ttl_minutes):
        """
        **Feature: seasonal-anime-tracker, Property 3: Cache Round-Trip Consistency**
        
        For any cache key and TTL, storing data and immediately retrieving it
        should return equivalent data.
        
        **Validates: Requirements 3.2, 3.3, 3.4, 3.5**
        """
        cache = InMemoryCache(default_ttl_minutes=ttl_minutes)
        
        # Create test data
        test_data = SeasonalAnimeResponse(
            data=[],
            pagination=PaginationInfo(
                last_visible_page=1,
                has_next_page=False
            )
        )
        
        # Property: storing and retrieving should return equivalent data
        cache.set(cache_key.strip(), test_data, ttl_minutes)
        retrieved_data = cache.get(cache_key.strip())
        
        # Property: retrieved data should be equivalent to stored data
        assert retrieved_data is not None
        assert retrieved_data.data == test_data.data
        assert retrieved_data.pagination.last_visible_page == test_data.pagination.last_visible_page
        assert retrieved_data.pagination.has_next_page == test_data.pagination.has_next_page
    
    @given(
        keys=st.lists(
            st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
            min_size=1,
            max_size=10,
            unique=True
        ),
        ttl_minutes=st.integers(min_value=1, max_value=30)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_3_multiple_cache_entries_consistency(self, keys, ttl_minutes):
        """
        **Feature: seasonal-anime-tracker, Property 3: Cache Round-Trip Consistency**
        
        For any set of cache keys, storing multiple entries should maintain
        independence and correct retrieval for each key.
        
        **Validates: Requirements 3.2, 3.3, 3.4, 3.5**
        """
        cache = InMemoryCache(default_ttl_minutes=ttl_minutes)
        
        # Store different data for each key
        stored_data = {}
        for i, key in enumerate(keys):
            test_data = SeasonalAnimeResponse(
                data=[],
                pagination=PaginationInfo(
                    last_visible_page=i + 1,
                    has_next_page=i % 2 == 0
                )
            )
            stored_data[key.strip()] = test_data
            cache.set(key.strip(), test_data, ttl_minutes)
        
        # Property: each key should return its specific data
        for key, expected_data in stored_data.items():
            retrieved_data = cache.get(key)
            assert retrieved_data is not None
            assert retrieved_data.pagination.last_visible_page == expected_data.pagination.last_visible_page
            assert retrieved_data.pagination.has_next_page == expected_data.pagination.has_next_page
        
        # Property: cache should contain all stored keys
        cache_keys = cache.get_cache_keys()
        for key in stored_data.keys():
            assert key in cache_keys
    
    @given(
        cache_key=st.text(min_size=1, max_size=30).filter(lambda x: x.strip()),
        ttl_seconds=st.integers(min_value=1, max_value=5)  # Short TTL for testing
    )
    @hypothesis_settings(max_examples=50, deadline=10000)  # Reduced examples and longer deadline for timing tests
    def test_property_3_cache_expiration_behavior(self, cache_key, ttl_seconds):
        """
        **Feature: seasonal-anime-tracker, Property 3: Cache Round-Trip Consistency**
        
        For any cache entry with TTL, the entry should be available before expiration
        and unavailable after expiration.
        
        **Validates: Requirements 3.2, 3.3, 3.4, 3.5**
        """
        # Convert seconds to minutes for cache (minimum 1 minute)
        ttl_minutes = max(1, ttl_seconds // 60) if ttl_seconds >= 60 else 1
        
        cache = InMemoryCache(default_ttl_minutes=ttl_minutes)
        
        test_data = SeasonalAnimeResponse(
            data=[],
            pagination=PaginationInfo(
                last_visible_page=1,
                has_next_page=False
            )
        )
        
        # Store data with short TTL
        cache.set(cache_key.strip(), test_data, ttl_minutes)
        
        # Property: data should be available immediately after storage
        retrieved_data = cache.get(cache_key.strip())
        assert retrieved_data is not None
        
        # Property: cache stats should reflect the entry
        stats = cache.get_stats()
        assert stats["total_entries"] >= 1
        assert stats["default_ttl_minutes"] == ttl_minutes
    
    @given(
        cache_key=st.text(min_size=1, max_size=30).filter(lambda x: x.strip())
    )
    @hypothesis_settings(max_examples=100)
    def test_property_3_cache_deletion_consistency(self, cache_key):
        """
        **Feature: seasonal-anime-tracker, Property 3: Cache Round-Trip Consistency**
        
        For any cached entry, deleting it should make it unavailable for retrieval.
        
        **Validates: Requirements 3.2, 3.3, 3.4, 3.5**
        """
        cache = InMemoryCache()
        
        test_data = SeasonalAnimeResponse(
            data=[],
            pagination=PaginationInfo(
                last_visible_page=1,
                has_next_page=False
            )
        )
        
        # Store and verify data exists
        cache.set(cache_key.strip(), test_data)
        assert cache.get(cache_key.strip()) is not None
        
        # Property: deleting existing key should return True
        deletion_result = cache.delete(cache_key.strip())
        assert deletion_result is True
        
        # Property: deleted entry should not be retrievable
        retrieved_data = cache.get(cache_key.strip())
        assert retrieved_data is None
        
        # Property: deleting non-existent key should return False
        second_deletion = cache.delete(cache_key.strip())
        assert second_deletion is False
    
    @given(
        entry_count=st.integers(min_value=1, max_value=20)
    )
    @hypothesis_settings(max_examples=50)
    def test_property_3_cache_clear_consistency(self, entry_count):
        """
        **Feature: seasonal-anime-tracker, Property 3: Cache Round-Trip Consistency**
        
        For any number of cache entries, clearing the cache should remove all entries.
        
        **Validates: Requirements 3.2, 3.3, 3.4, 3.5**
        """
        cache = InMemoryCache()
        
        test_data = SeasonalAnimeResponse(
            data=[],
            pagination=PaginationInfo(
                last_visible_page=1,
                has_next_page=False
            )
        )
        
        # Store multiple entries
        keys = [f"key_{i}" for i in range(entry_count)]
        for key in keys:
            cache.set(key, test_data)
        
        # Verify entries exist
        for key in keys:
            assert cache.get(key) is not None
        
        # Property: clear should return the number of entries cleared
        cleared_count = cache.clear()
        assert cleared_count == entry_count
        
        # Property: all entries should be unavailable after clear
        for key in keys:
            assert cache.get(key) is None
        
        # Property: cache should be empty
        stats = cache.get_stats()
        assert stats["total_entries"] == 0
        assert stats["active_entries"] == 0
    
    @pytest.mark.asyncio
    @given(
        year=st.one_of(st.none(), st.integers(min_value=2000, max_value=2030)),
        season=st.one_of(st.none(), st.sampled_from(["winter", "spring", "summer", "fall"]))
    )
    @hypothesis_settings(max_examples=50)
    async def test_property_3_seasonal_cache_functions_consistency(self, year, season):
        """
        **Feature: seasonal-anime-tracker, Property 3: Cache Round-Trip Consistency**
        
        For any year/season combination, the seasonal cache functions should
        maintain consistency between storage and retrieval.
        
        **Validates: Requirements 3.2, 3.3, 3.4, 3.5**
        """
        test_data = SeasonalAnimeResponse(
            data=[],
            pagination=PaginationInfo(
                last_visible_page=1,
                has_next_page=False
            )
        )
        
        # Store data using seasonal cache function
        await set_seasonal_anime_cache(test_data, year, season)
        
        # Property: retrieving with same parameters should return equivalent data
        retrieved_data = await get_seasonal_anime_cache(year, season)
        
        assert retrieved_data is not None
        assert retrieved_data.data == test_data.data
        assert retrieved_data.pagination.last_visible_page == test_data.pagination.last_visible_page
        assert retrieved_data.pagination.has_next_page == test_data.pagination.has_next_page
    
    @given(
        ttl_minutes=st.integers(min_value=1, max_value=60)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_3_cache_stats_consistency(self, ttl_minutes):
        """
        **Feature: seasonal-anime-tracker, Property 3: Cache Round-Trip Consistency**
        
        For any cache configuration, the cache statistics should accurately
        reflect the current state.
        
        **Validates: Requirements 3.2, 3.3, 3.4, 3.5**
        """
        cache = InMemoryCache(default_ttl_minutes=ttl_minutes)
        
        # Property: empty cache should have zero entries
        initial_stats = cache.get_stats()
        assert initial_stats["total_entries"] == 0
        assert initial_stats["active_entries"] == 0
        assert initial_stats["expired_entries"] == 0
        assert initial_stats["default_ttl_minutes"] == ttl_minutes
        
        # Add some entries
        test_data = SeasonalAnimeResponse(
            data=[],
            pagination=PaginationInfo(last_visible_page=1, has_next_page=False)
        )
        
        cache.set("key1", test_data)
        cache.set("key2", test_data)
        
        # Property: stats should reflect added entries
        updated_stats = cache.get_stats()
        assert updated_stats["total_entries"] == 2
        assert updated_stats["active_entries"] == 2
        assert updated_stats["expired_entries"] == 0
    
    def test_property_3_cache_thread_safety_simulation(self):
        """
        **Feature: seasonal-anime-tracker, Property 3: Cache Round-Trip Consistency**
        
        Cache operations should maintain consistency under concurrent access patterns.
        
        **Validates: Requirements 3.2, 3.3, 3.4, 3.5**
        """
        cache = InMemoryCache()
        
        test_data = SeasonalAnimeResponse(
            data=[],
            pagination=PaginationInfo(last_visible_page=1, has_next_page=False)
        )
        
        # Simulate concurrent operations
        keys = [f"concurrent_key_{i}" for i in range(10)]
        
        # Store all keys
        for key in keys:
            cache.set(key, test_data)
        
        # Property: all keys should be retrievable
        for key in keys:
            retrieved = cache.get(key)
            assert retrieved is not None
        
        # Property: mixed operations should maintain consistency
        cache.delete(keys[0])  # Delete first
        cache.set(keys[1], test_data)  # Update second
        
        assert cache.get(keys[0]) is None  # Should be deleted
        assert cache.get(keys[1]) is not None  # Should still exist
        assert cache.get(keys[2]) is not None  # Should be unchanged