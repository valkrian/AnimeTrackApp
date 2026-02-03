/**
 * Loading Skeleton Component
 * Displays animated placeholder cards while anime data is loading
 * Uses glassmorphism styling to match the anime cards
 */

import { LoadingSkeletonProps } from '../types/anime';

export default function LoadingSkeleton({ count = 12, className = '' }: LoadingSkeletonProps) {
  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 ${className}`}>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className="relative overflow-hidden rounded-xl backdrop-blur-md bg-white/10 border border-white/20 shadow-xl"
          role="status"
          aria-label="Loading anime card"
        >
          {/* Image skeleton */}
          <div className="aspect-[3/4] bg-gradient-to-br from-white/20 to-white/5 animate-pulse" />
          
          {/* Content skeleton */}
          <div className="p-4 space-y-3">
            {/* Title skeleton */}
            <div className="h-6 bg-gradient-to-r from-white/30 to-white/10 rounded animate-pulse" />
            
            {/* Score skeleton */}
            <div className="flex items-center gap-2">
              <div className="h-4 w-16 bg-gradient-to-r from-white/30 to-white/10 rounded animate-pulse" />
            </div>
            
            {/* Genres skeleton */}
            <div className="flex flex-wrap gap-2">
              <div className="h-6 w-20 bg-gradient-to-r from-white/30 to-white/10 rounded-full animate-pulse" />
              <div className="h-6 w-24 bg-gradient-to-r from-white/30 to-white/10 rounded-full animate-pulse" />
            </div>
          </div>
          
          {/* Shimmer effect overlay */}
          <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        </div>
      ))}
      <span className="sr-only">Loading anime data...</span>
    </div>
  );
}
