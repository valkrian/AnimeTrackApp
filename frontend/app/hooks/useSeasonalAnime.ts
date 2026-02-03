/**
 * TanStack Query Hook for Seasonal Anime Data
 * Provides data fetching, caching, and state management
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { SeasonalAnimeResponse } from '../types/anime';
import { fetchSeasonalAnime, AnimeApiError } from '../services/animeApi';

/**
 * Query key factory for seasonal anime
 * Helps with cache invalidation and organization
 */
export const seasonalAnimeKeys = {
  all: ['seasonal-anime'] as const,
  current: () => [...seasonalAnimeKeys.all, 'current'] as const,
};

/**
 * Hook for fetching seasonal anime data
 * 
 * Features:
 * - Automatic caching with 5-minute stale time
 * - Background refetch on window focus
 * - Automatic retry with exponential backoff
 * - Loading and error states
 * 
 * @returns UseQueryResult with seasonal anime data
 */
export function useSeasonalAnime(): UseQueryResult<SeasonalAnimeResponse, AnimeApiError> {
  return useQuery<SeasonalAnimeResponse, AnimeApiError>({
    queryKey: seasonalAnimeKeys.current(),
    queryFn: fetchSeasonalAnime,
    
    // Caching strategy: stale-while-revalidate
    staleTime: 5 * 60 * 1000, // 5 minutes - data is fresh for this duration
    gcTime: 10 * 60 * 1000, // 10 minutes - cache garbage collection time (formerly cacheTime)
    
    // Refetch configuration
    refetchOnWindowFocus: true, // Refetch when user returns to tab
    refetchOnReconnect: true, // Refetch when network reconnects
    refetchOnMount: false, // Don't refetch if data is fresh
    
    // Error handling with retry
    retry: (failureCount, error) => {
      // Don't retry on client errors (4xx)
      if (error.status >= 400 && error.status < 500) {
        return false;
      }
      // Retry up to 3 times for server errors (5xx) and network errors
      return failureCount < 3;
    },
    retryDelay: (attemptIndex) => {
      // Exponential backoff: 1s, 2s, 4s
      return Math.min(1000 * 2 ** attemptIndex, 30000);
    },
  });
}

/**
 * Helper hook to get just the loading state
 */
export function useSeasonalAnimeLoading(): boolean {
  const { isLoading } = useSeasonalAnime();
  return isLoading;
}

/**
 * Helper hook to get just the error state
 */
export function useSeasonalAnimeError(): AnimeApiError | null {
  const { error } = useSeasonalAnime();
  return error || null;
}

/**
 * Helper hook to get just the data
 */
export function useSeasonalAnimeData(): SeasonalAnimeResponse | undefined {
  const { data } = useSeasonalAnime();
  return data;
}
