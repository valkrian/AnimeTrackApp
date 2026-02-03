/**
 * TypeScript interfaces for anime data structures
 * Matches the backend Pydantic models for type consistency
 */

export interface Studio {
  mal_id: number;
  name: string;
  url: string;
}

export interface Genre {
  mal_id: number;
  name: string;
  type: string;
  url: string;
}

export interface AnimeImages {
  jpg: {
    image_url: string;
    small_image_url: string;
    large_image_url: string;
  };
  webp: {
    image_url: string;
    small_image_url: string;
    large_image_url: string;
  };
}

export interface AnimeAired {
  from: string | null;
  to: string | null;
  prop: {
    from: {
      day: number | null;
      month: number | null;
      year: number | null;
    };
    to: {
      day: number | null;
      month: number | null;
      year: number | null;
    };
  };
  string: string;
}

export interface AnimeTrailer {
  youtube_id: string | null;
  url: string | null;
  embed_url: string | null;
  images: {
    image_url: string | null;
    small_image_url: string | null;
    medium_image_url: string | null;
    large_image_url: string | null;
    maximum_image_url: string | null;
  };
}

export interface AnimeItem {
  mal_id: number;
  title: string;
  title_english?: string | null;
  title_japanese?: string | null;
  synopsis?: string | null;
  score?: number | null;
  scored_by?: number | null;
  rank?: number | null;
  popularity?: number | null;
  members?: number | null;
  favorites?: number | null;
  status: string;
  airing: boolean;
  aired: AnimeAired;
  duration?: string | null;
  rating?: string | null;
  source: string;
  studios: Studio[];
  genres: Genre[];
  images: AnimeImages;
  trailer?: AnimeTrailer | null;
  url: string;
}

export interface Pagination {
  last_visible_page: number;
  has_next_page: boolean;
  current_page: number;
  items: {
    count: number;
    total: number;
    per_page: number;
  };
}

export interface SeasonalAnimeResponse {
  data: AnimeItem[];
  pagination: Pagination;
}

/**
 * API Error interface for error handling
 */
export interface ApiError {
  message: string;
  status: number;
  timestamp: string;
}

/**
 * Component Props Interfaces
 */

export interface AnimeCardProps {
  anime: AnimeItem;
  className?: string;
}

export interface AnimeGridProps {
  animes: AnimeItem[];
  isLoading: boolean;
  error: ApiError | null;
}

export interface LoadingSkeletonProps {
  count?: number;
  className?: string;
}

export interface ErrorToastProps {
  error: ApiError;
  onDismiss: () => void;
}

export interface SeasonBadgeProps {
  season: string;
  year: number;
}
