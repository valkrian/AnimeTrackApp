/**
 * Anime Grid Layout Component
 * Displays anime cards in a responsive grid layout
 * Handles loading, error, and empty states
 */

'use client';

import AnimeCard from './AnimeCard';
import LoadingSkeleton from './LoadingSkeleton';
import { AnimeGridProps } from '../types/anime';

export default function AnimeGrid({ animes, isLoading, error }: AnimeGridProps) {
  // Loading State
  if (isLoading) {
    return (
      <section aria-label="Loading anime" role="status">
        <LoadingSkeleton count={12} />
      </section>
    );
  }

  // Error State
  if (error) {
    return (
      <section 
        className="flex flex-col items-center justify-center min-h-[400px] text-center px-4"
        role="alert"
        aria-live="polite"
      >
        <div className="backdrop-blur-md bg-red-500/20 border border-red-500/30 rounded-xl p-8 max-w-md">
          <svg
            className="w-16 h-16 text-red-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <h2 className="text-white text-xl font-bold mb-2">Failed to Load Anime</h2>
          <p className="text-white/80 mb-4">{error.message}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors backdrop-blur-sm border border-white/30"
            aria-label="Reload page"
          >
            Try Again
          </button>
        </div>
      </section>
    );
  }

  // Empty State
  if (!animes || animes.length === 0) {
    return (
      <section 
        className="flex flex-col items-center justify-center min-h-[400px] text-center px-4"
        role="status"
        aria-live="polite"
      >
        <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-xl p-8 max-w-md">
          <svg
            className="w-16 h-16 text-white/60 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
          <h2 className="text-white text-xl font-bold mb-2">No Anime Found</h2>
          <p className="text-white/80">
            There are no anime available for the current season.
          </p>
        </div>
      </section>
    );
  }

  // Success State - Display Grid
  return (
    <section aria-label="Seasonal anime grid">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {animes.map((anime) => (
          <AnimeCard key={anime.mal_id} anime={anime} />
        ))}
      </div>
      
      {/* Anime count indicator */}
      <div className="mt-8 text-center">
        <p className="text-white/60 text-sm">
          Showing {animes.length} {animes.length === 1 ? 'anime' : 'anime titles'}
        </p>
      </div>
    </section>
  );
}
