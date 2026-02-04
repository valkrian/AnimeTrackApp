import fc from 'fast-check';
import { WatchlistItem } from '../types/common';

/**
 * Generator for anime IDs (positive integers)
 */
export const animeIdGenerator = () => fc.integer({ min: 1, max: 100000 });

/**
 * Generator for ISO timestamp strings
 */
export const isoTimestampGenerator = () =>
  fc
    .date({ min: new Date('2020-01-01'), max: new Date('2025-12-31') })
    .map((date) => date.toISOString());

/**
 * Generator for WatchlistItem objects
 */
export const watchlistItemGenerator = (): fc.Arbitrary<WatchlistItem> =>
  fc.record({
    mal_id: animeIdGenerator(),
    addedAt: isoTimestampGenerator(),
  });

/**
 * Generator for arrays of unique anime IDs
 */
export const uniqueAnimeIdsGenerator = (minLength = 0, maxLength = 20) =>
  fc.uniqueArray(animeIdGenerator(), { minLength, maxLength });
