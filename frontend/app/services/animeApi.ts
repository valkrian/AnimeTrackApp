/**
 * API Client Service for Anime Data
 * Handles all HTTP requests to the backend API
 */

import { SeasonalAnimeResponse, ApiError } from '../types/anime';

/**
 * Get the backend API URL from environment variables
 * Falls back to localhost:8000 for development
 */
const getApiUrl = (): string => {
  const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  return url;
};

/**
 * Custom error class for API errors
 */
export class AnimeApiError extends Error implements ApiError {
  status: number;
  timestamp: string;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'AnimeApiError';
    this.status = status;
    this.timestamp = new Date().toISOString();
  }
}

/**
 * Fetch seasonal anime data from the backend
 * @returns Promise<SeasonalAnimeResponse> - The seasonal anime data
 * @throws AnimeApiError - If the request fails
 */
export async function fetchSeasonalAnime(): Promise<SeasonalAnimeResponse> {
  const apiUrl = getApiUrl();
  const endpoint = `${apiUrl}/api/v1/anime/seasonal`;

  try {
    const response = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Handle non-OK responses
    if (!response.ok) {
      const errorMessage = await response.text().catch(() => 'Unknown error');
      throw new AnimeApiError(
        `Failed to fetch seasonal anime: ${errorMessage}`,
        response.status
      );
    }

    // Parse and validate response
    const data: SeasonalAnimeResponse = await response.json();

    // Basic validation
    if (!data || !Array.isArray(data.data)) {
      throw new AnimeApiError(
        'Invalid response format from backend',
        500
      );
    }

    return data;
  } catch (error) {
    // Re-throw AnimeApiError as-is
    if (error instanceof AnimeApiError) {
      throw error;
    }

    // Handle network errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new AnimeApiError(
        'Network error: Unable to connect to backend',
        0
      );
    }

    // Handle other errors
    throw new AnimeApiError(
      `Unexpected error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      500
    );
  }
}
