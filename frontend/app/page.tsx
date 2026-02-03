'use client';

import { useSeasonalAnime } from './hooks/useSeasonalAnime';
import AnimeGrid from './components/AnimeGrid';

export default function Home() {
  const { data, isLoading, error } = useSeasonalAnime();

  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            Seasonal Anime Tracker
          </h1>
          <p className="text-white/80 text-lg">
            Discover the latest anime of the season
          </p>
        </header>

        {/* Anime Grid */}
        <AnimeGrid 
          animes={data?.data || []} 
          isLoading={isLoading} 
          error={error || null} 
        />
      </div>
    </main>
  );
}
