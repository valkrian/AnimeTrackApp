/**
 * Home Page - Main Page with Anime Grid
 * Integrates TanStack Query data fetching with anime grid display
 * Implements error boundaries and loading states
 * Requirements: 6.4, 7.1
 */

'use client';

import { useState, useEffect } from 'react';
import { useSeasonalAnime } from './hooks/useSeasonalAnime';
import AnimeGrid from './components/AnimeGrid';
import ErrorBoundary from './components/ErrorBoundary';
import { AutoSeasonBadge } from './components/SeasonBadge';
import ErrorToast from './components/ErrorToast';
import { ApiError } from './types/anime';

export default function Home() {
  const { data, isLoading, error } = useSeasonalAnime();
  const [showErrorToast, setShowErrorToast] = useState(false);
  const [toastError, setToastError] = useState<ApiError | null>(null);

  // Show error toast when query error occurs
  useEffect(() => {
    if (error) {
      setToastError(error);
      setShowErrorToast(true);
    }
  }, [error]);

  const handleDismissToast = () => {
    setShowErrorToast(false);
    setToastError(null);
  };

  return (
    <ErrorBoundary>
      <main className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <header className="text-center mb-8">
            <h1 className="text-5xl font-bold text-white mb-4">
              Seasonal Anime Tracker
            </h1>
            <p className="text-white/80 text-lg mb-6">
              Discover the latest anime of the season
            </p>
            
            {/* Season Badge */}
            <div className="flex justify-center">
              <AutoSeasonBadge />
            </div>
          </header>

          {/* Anime Grid with Error Handling */}
          <AnimeGrid 
            animes={data?.data || []} 
            isLoading={isLoading} 
            error={error || null} 
          />
        </div>

        {/* Error Toast Notification */}
        {showErrorToast && toastError && (
          <ErrorToast error={toastError} onDismiss={handleDismissToast} />
        )}
      </main>
    </ErrorBoundary>
  );
}
