'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';

/**
 * TanStack Query Provider with optimized configuration
 * 
 * Configuration:
 * - Stale-while-revalidate caching strategy
 * - 5-minute stale time for optimal UX
 * - Exponential backoff retry logic
 * - Background refetch on window focus
 */
export function QueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Stale-while-revalidate: data is considered fresh for 5 minutes
            staleTime: 5 * 60 * 1000, // 5 minutes
            
            // Cache data for 10 minutes
            gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
            
            // Retry failed requests with exponential backoff
            retry: (failureCount, error: any) => {
              // Don't retry on 4xx errors (client errors)
              if (error?.status >= 400 && error?.status < 500) {
                return false;
              }
              // Retry up to 3 times for other errors
              return failureCount < 3;
            },
            
            // Exponential backoff delay: 1s, 2s, 4s
            retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
            
            // Refetch on window focus to keep data fresh
            refetchOnWindowFocus: true,
            
            // Don't refetch on mount if data is still fresh
            refetchOnMount: false,
            
            // Refetch on reconnect
            refetchOnReconnect: true,
          },
          mutations: {
            // Retry mutations once on failure
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
