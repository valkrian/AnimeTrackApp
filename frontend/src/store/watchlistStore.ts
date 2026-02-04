import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { WatchlistItem } from '../types/common';

interface WatchlistState {
  items: WatchlistItem[];
  addToWatchlist: (animeId: number) => void;
  removeFromWatchlist: (animeId: number) => void;
  isInWatchlist: (animeId: number) => boolean;
  clearWatchlist: () => void;
}

export const useWatchlistStore = create<WatchlistState>()(
  persist(
    (set, get) => ({
      items: [],
      addToWatchlist: (animeId) => {
        const { items, isInWatchlist } = get();
        // Ensure idempotent operation - don't add duplicates
        if (!isInWatchlist(animeId)) {
          set({
            items: [
              ...items,
              { mal_id: animeId, addedAt: new Date().toISOString() },
            ],
          });
        }
      },
      removeFromWatchlist: (animeId) =>
        set((state) => ({
          items: state.items.filter((item) => item.mal_id !== animeId),
        })),
      isInWatchlist: (animeId) =>
        get().items.some((item) => item.mal_id === animeId),
      clearWatchlist: () => set({ items: [] }),
    }),
    {
      name: 'watchlist-storage',
    }
  )
);
