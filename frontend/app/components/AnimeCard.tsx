/**
 * Anime Card Component
 * Displays individual anime information with glassmorphism design
 * Features hover effects revealing synopsis and studio information
 */

'use client';

import { useState } from 'react';
import { AnimeCardProps } from '../types/anime';

export default function AnimeCard({ anime, className = '' }: AnimeCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [imageError, setImageError] = useState(false);

  // Get the best available title
  const displayTitle = anime.title_english || anime.title || anime.title_japanese || 'Unknown Title';
  
  // Get image URL with fallback
  const imageUrl = imageError 
    ? '/placeholder-anime.jpg' 
    : anime.images?.jpg?.large_image_url || anime.images?.jpg?.image_url || '/placeholder-anime.jpg';

  // Format score display
  const scoreDisplay = anime.score ? anime.score.toFixed(2) : 'N/A';
  
  // Get studio names
  const studioNames = anime.studios?.length > 0 
    ? anime.studios.map(s => s.name).join(', ') 
    : 'Unknown Studio';

  // Truncate synopsis for display
  const truncatedSynopsis = anime.synopsis 
    ? anime.synopsis.length > 200 
      ? anime.synopsis.substring(0, 200) + '...' 
      : anime.synopsis
    : 'No synopsis available.';

  return (
    <article
      className={`group relative overflow-hidden rounded-xl backdrop-blur-md bg-white/10 border border-white/20 shadow-xl transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:bg-white/15 ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      role="article"
      aria-label={`Anime: ${displayTitle}`}
    >
      {/* Anime Image */}
      <div className="relative aspect-[3/4] overflow-hidden">
        <img
          src={imageUrl}
          alt={`${displayTitle} poster`}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
          onError={() => setImageError(true)}
          loading="lazy"
        />
        
        {/* Score Badge */}
        {anime.score && (
          <div 
            className="absolute top-2 right-2 backdrop-blur-md bg-black/50 text-white px-3 py-1 rounded-full text-sm font-bold flex items-center gap-1"
            aria-label={`Score: ${scoreDisplay}`}
          >
            <span className="text-yellow-400">★</span>
            {scoreDisplay}
          </div>
        )}

        {/* Airing Status Badge */}
        {anime.airing && (
          <div 
            className="absolute top-2 left-2 backdrop-blur-md bg-green-500/80 text-white px-3 py-1 rounded-full text-xs font-semibold uppercase"
            aria-label="Currently airing"
          >
            Airing
          </div>
        )}
      </div>

      {/* Card Content */}
      <div className="p-4 space-y-3">
        {/* Title */}
        <h3 className="text-white font-bold text-lg line-clamp-2 min-h-[3.5rem]" title={displayTitle}>
          {displayTitle}
        </h3>

        {/* Genres */}
        {anime.genres && anime.genres.length > 0 && (
          <div className="flex flex-wrap gap-2" role="list" aria-label="Genres">
            {anime.genres.slice(0, 3).map((genre) => (
              <span
                key={genre.mal_id}
                className="text-xs px-2 py-1 rounded-full bg-white/20 text-white/90 backdrop-blur-sm"
                role="listitem"
              >
                {genre.name}
              </span>
            ))}
            {anime.genres.length > 3 && (
              <span className="text-xs px-2 py-1 rounded-full bg-white/20 text-white/90 backdrop-blur-sm">
                +{anime.genres.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Source and Status */}
        <div className="flex items-center justify-between text-sm text-white/70">
          <span>{anime.source}</span>
          <span>{anime.status}</span>
        </div>
      </div>

      {/* Hover Overlay - Synopsis and Studio Info */}
      <div
        className={`absolute inset-0 backdrop-blur-lg bg-gradient-to-t from-black/95 via-black/85 to-black/75 p-6 flex flex-col justify-end transition-all duration-300 ${
          isHovered ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'
        }`}
        aria-hidden={!isHovered}
      >
        {/* Title in overlay */}
        <h4 className="text-white font-bold text-xl mb-3">{displayTitle}</h4>

        {/* Studio Information */}
        <div className="mb-3">
          <p className="text-white/60 text-xs uppercase tracking-wide mb-1">Studio</p>
          <p className="text-white text-sm font-medium">{studioNames}</p>
        </div>

        {/* Synopsis */}
        <div className="mb-4">
          <p className="text-white/60 text-xs uppercase tracking-wide mb-1">Synopsis</p>
          <p className="text-white/90 text-sm leading-relaxed line-clamp-6">
            {truncatedSynopsis}
          </p>
        </div>

        {/* View More Link */}
        <a
          href={anime.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
          aria-label={`View ${displayTitle} on MyAnimeList`}
        >
          View on MyAnimeList
          <svg 
            className="w-4 h-4" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </article>
  );
}
