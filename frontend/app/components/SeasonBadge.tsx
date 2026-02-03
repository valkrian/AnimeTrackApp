/**
 * Season Badge Component
 * Displays the current anime season with dynamic detection
 * Features glassmorphism design matching the overall theme
 * Requirements: 7.4
 */

'use client';

import { useEffect, useState } from 'react';
import { SeasonBadgeProps } from '../types/anime';

/**
 * Detect the current anime season based on the month
 * Winter: January-March (1-3)
 * Spring: April-June (4-6)
 * Summer: July-September (7-9)
 * Fall: October-December (10-12)
 */
export function detectCurrentSeason(): { season: string; year: number } {
  const now = new Date();
  const month = now.getMonth() + 1; // getMonth() returns 0-11
  const year = now.getFullYear();

  let season: string;
  if (month >= 1 && month <= 3) {
    season = 'Winter';
  } else if (month >= 4 && month <= 6) {
    season = 'Spring';
  } else if (month >= 7 && month <= 9) {
    season = 'Summer';
  } else {
    season = 'Fall';
  }

  return { season, year };
}

/**
 * Get season-specific styling
 */
function getSeasonStyles(season: string): {
  gradient: string;
  icon: string;
  iconColor: string;
} {
  switch (season.toLowerCase()) {
    case 'winter':
      return {
        gradient: 'from-blue-500/30 to-cyan-500/30',
        icon: '❄️',
        iconColor: 'text-cyan-300',
      };
    case 'spring':
      return {
        gradient: 'from-pink-500/30 to-green-500/30',
        icon: '🌸',
        iconColor: 'text-pink-300',
      };
    case 'summer':
      return {
        gradient: 'from-yellow-500/30 to-orange-500/30',
        icon: '☀️',
        iconColor: 'text-yellow-300',
      };
    case 'fall':
      return {
        gradient: 'from-orange-500/30 to-red-500/30',
        icon: '🍂',
        iconColor: 'text-orange-300',
      };
    default:
      return {
        gradient: 'from-purple-500/30 to-blue-500/30',
        icon: '📺',
        iconColor: 'text-purple-300',
      };
  }
}

export default function SeasonBadge({ season, year }: SeasonBadgeProps) {
  const [isClient, setIsClient] = useState(false);
  const styles = getSeasonStyles(season);

  // Ensure component only renders on client to avoid hydration mismatch
  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    return null;
  }

  return (
    <div
      className={`inline-flex items-center gap-3 px-6 py-3 rounded-full backdrop-blur-md bg-gradient-to-r ${styles.gradient} border border-white/30 shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-xl`}
      role="status"
      aria-label={`Current season: ${season} ${year}`}
    >
      {/* Season Icon */}
      <span className="text-2xl" aria-hidden="true">
        {styles.icon}
      </span>

      {/* Season Text */}
      <div className="flex flex-col">
        <span className="text-white/70 text-xs uppercase tracking-wider font-medium">
          Current Season
        </span>
        <span className={`text-white text-lg font-bold ${styles.iconColor}`}>
          {season} {year}
        </span>
      </div>

      {/* Animated pulse indicator */}
      <div className="relative">
        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
        <div className="absolute inset-0 w-2 h-2 bg-green-400 rounded-full animate-ping opacity-75" />
      </div>
    </div>
  );
}

/**
 * Auto-detecting Season Badge Component
 * Automatically detects and displays the current season
 */
export function AutoSeasonBadge() {
  const [seasonData, setSeasonData] = useState<{ season: string; year: number } | null>(null);

  useEffect(() => {
    // Detect season on mount
    const detected = detectCurrentSeason();
    setSeasonData(detected);

    // Update season every hour in case the season changes
    const interval = setInterval(() => {
      const updated = detectCurrentSeason();
      setSeasonData(updated);
    }, 60 * 60 * 1000); // 1 hour

    return () => clearInterval(interval);
  }, []);

  if (!seasonData) {
    return null;
  }

  return <SeasonBadge season={seasonData.season} year={seasonData.year} />;
}
