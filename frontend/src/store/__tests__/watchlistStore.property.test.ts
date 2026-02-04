import { describe, it, expect, beforeEach } from 'vitest';
import fc from 'fast-check';
import { useWatchlistStore } from '../watchlistStore';
import { animeIdGenerator, uniqueAnimeIdsGenerator } from '../../test/generators';

describe('Watchlist Store - Property-Based Tests', () => {
  beforeEach(() => {
    // Reset the store before each test
    const { clearWatchlist } = useWatchlistStore.getState();
    clearWatchlist();
    localStorage.clear();
  });

  // Feature: frontend-rebuild, Property 15: Add to watchlist is idempotent
  describe('Property 15: Add to watchlist is idempotent', () => {
    it('should add an anime only once regardless of how many times addToWatchlist is called', () => {
      fc.assert(
        fc.property(
          animeIdGenerator(),
          fc.integer({ min: 1, max: 10 }), // Number of times to add
          (animeId, addCount) => {
            const { addToWatchlist, items, clearWatchlist } = useWatchlistStore.getState();
            
            // Clear before test
            clearWatchlist();
            
            // Add the same anime multiple times
            for (let i = 0; i < addCount; i++) {
              addToWatchlist(animeId);
            }
            
            const finalItems = useWatchlistStore.getState().items;
            
            // Property: The anime should appear exactly once
            const matchingItems = finalItems.filter(item => item.mal_id === animeId);
            expect(matchingItems.length).toBe(1);
            
            // Property: Total items should be 1
            expect(finalItems.length).toBe(1);
            
            return true;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should maintain idempotency when adding multiple different anime with duplicates', () => {
      fc.assert(
        fc.property(
          fc.array(animeIdGenerator(), { minLength: 1, maxLength: 20 }),
          (animeIds) => {
            const { addToWatchlist, items, clearWatchlist } = useWatchlistStore.getState();
            
            // Clear before test
            clearWatchlist();
            
            // Add all anime IDs (may contain duplicates)
            animeIds.forEach(id => addToWatchlist(id));
            
            const finalItems = useWatchlistStore.getState().items;
            
            // Property: Each unique anime ID should appear exactly once
            const uniqueIds = [...new Set(animeIds)];
            expect(finalItems.length).toBe(uniqueIds.length);
            
            // Property: All unique IDs should be present
            uniqueIds.forEach(id => {
              const matchingItems = finalItems.filter(item => item.mal_id === id);
              expect(matchingItems.length).toBe(1);
            });
            
            return true;
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  // Feature: frontend-rebuild, Property 16: Remove from watchlist works correctly
  describe('Property 16: Remove from watchlist works correctly', () => {
    it('should remove an anime from the watchlist when removeFromWatchlist is called', () => {
      fc.assert(
        fc.property(
          uniqueAnimeIdsGenerator(1, 20),
          fc.integer({ min: 0, max: 19 }), // Index to remove
          (animeIds, removeIndex) => {
            const { addToWatchlist, removeFromWatchlist, items, clearWatchlist } = 
              useWatchlistStore.getState();
            
            // Clear before test
            clearWatchlist();
            
            // Add all anime
            animeIds.forEach(id => addToWatchlist(id));
            
            // Remove one anime
            const idToRemove = animeIds[removeIndex % animeIds.length];
            removeFromWatchlist(idToRemove);
            
            const finalItems = useWatchlistStore.getState().items;
            
            // Property: The removed anime should not be in the watchlist
            const removedAnimeExists = finalItems.some(item => item.mal_id === idToRemove);
            expect(removedAnimeExists).toBe(false);
            
            // Property: The watchlist should have one less item
            expect(finalItems.length).toBe(animeIds.length - 1);
            
            // Property: All other anime should still be present
            animeIds.forEach((id, idx) => {
              if (idx !== removeIndex % animeIds.length) {
                const exists = finalItems.some(item => item.mal_id === id);
                expect(exists).toBe(true);
              }
            });
            
            return true;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should handle removing non-existent anime gracefully', () => {
      fc.assert(
        fc.property(
          uniqueAnimeIdsGenerator(1, 10),
          animeIdGenerator(),
          (existingIds, nonExistentId) => {
            // Ensure nonExistentId is not in existingIds
            fc.pre(!existingIds.includes(nonExistentId));
            
            const { addToWatchlist, removeFromWatchlist, clearWatchlist } = 
              useWatchlistStore.getState();
            
            // Clear before test
            clearWatchlist();
            
            // Add existing anime
            existingIds.forEach(id => addToWatchlist(id));
            
            const itemsBeforeRemove = useWatchlistStore.getState().items.length;
            
            // Try to remove non-existent anime
            removeFromWatchlist(nonExistentId);
            
            const itemsAfterRemove = useWatchlistStore.getState().items.length;
            
            // Property: Watchlist should remain unchanged
            expect(itemsAfterRemove).toBe(itemsBeforeRemove);
            expect(itemsAfterRemove).toBe(existingIds.length);
            
            return true;
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  // Feature: frontend-rebuild, Property 17: Watchlist persistence round-trip
  describe('Property 17: Watchlist persistence round-trip', () => {
    it('should persist watchlist to localStorage and restore it correctly', () => {
      fc.assert(
        fc.property(
          uniqueAnimeIdsGenerator(1, 20), // At least 1 item to ensure localStorage is set
          (animeIds) => {
            const { addToWatchlist, clearWatchlist } = useWatchlistStore.getState();
            
            // Clear before test
            clearWatchlist();
            localStorage.clear();
            
            // Add all anime
            animeIds.forEach(id => addToWatchlist(id));
            
            const itemsBeforePersist = useWatchlistStore.getState().items;
            
            // Simulate page reload by reading from localStorage
            const persistedData = localStorage.getItem('watchlist-storage');
            expect(persistedData).not.toBeNull();
            
            if (persistedData) {
              const parsed = JSON.parse(persistedData);
              
              // Property: Persisted data should contain the state
              expect(parsed.state).toBeDefined();
              expect(parsed.state.items).toBeDefined();
              
              // Property: All anime IDs should be persisted
              const persistedIds = parsed.state.items.map((item: any) => item.mal_id);
              expect(persistedIds.length).toBe(animeIds.length);
              
              animeIds.forEach(id => {
                expect(persistedIds).toContain(id);
              });
              
              // Property: Each item should have mal_id and addedAt
              parsed.state.items.forEach((item: any) => {
                expect(item.mal_id).toBeDefined();
                expect(item.addedAt).toBeDefined();
                expect(typeof item.mal_id).toBe('number');
                expect(typeof item.addedAt).toBe('string');
              });
            }
            
            return true;
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should restore watchlist state after simulated reload', () => {
      fc.assert(
        fc.property(
          uniqueAnimeIdsGenerator(1, 15),
          (animeIds) => {
            // Clear everything
            localStorage.clear();
            const { clearWatchlist } = useWatchlistStore.getState();
            clearWatchlist();
            
            // Add anime to watchlist
            const { addToWatchlist } = useWatchlistStore.getState();
            animeIds.forEach(id => addToWatchlist(id));
            
            const originalItems = useWatchlistStore.getState().items;
            
            // Get the persisted data
            const persistedData = localStorage.getItem('watchlist-storage');
            expect(persistedData).not.toBeNull();
            
            // Clear the store (simulating app restart)
            clearWatchlist();
            
            // Manually restore from localStorage (simulating Zustand's rehydration)
            if (persistedData) {
              const parsed = JSON.parse(persistedData);
              useWatchlistStore.setState({ items: parsed.state.items });
            }
            
            const restoredItems = useWatchlistStore.getState().items;
            
            // Property: Restored items should match original items
            expect(restoredItems.length).toBe(originalItems.length);
            
            // Property: All original anime IDs should be restored
            originalItems.forEach(originalItem => {
              const restored = restoredItems.find(item => item.mal_id === originalItem.mal_id);
              expect(restored).toBeDefined();
              expect(restored?.addedAt).toBe(originalItem.addedAt);
            });
            
            return true;
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  // Additional property: isInWatchlist should be consistent
  describe('Additional Property: isInWatchlist consistency', () => {
    it('should return true for added anime and false for non-added anime', () => {
      fc.assert(
        fc.property(
          uniqueAnimeIdsGenerator(1, 20),
          animeIdGenerator(),
          (addedIds, testId) => {
            const { addToWatchlist, isInWatchlist, clearWatchlist } = 
              useWatchlistStore.getState();
            
            // Clear before test
            clearWatchlist();
            
            // Add anime
            addedIds.forEach(id => addToWatchlist(id));
            
            // Property: isInWatchlist should return true for added anime
            addedIds.forEach(id => {
              expect(isInWatchlist(id)).toBe(true);
            });
            
            // Property: isInWatchlist should return false for non-added anime
            if (!addedIds.includes(testId)) {
              expect(isInWatchlist(testId)).toBe(false);
            }
            
            return true;
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
