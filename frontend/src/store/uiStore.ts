import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Theme } from '../types/common';

interface UIState {
  theme: Theme;
  viewMode: 'grid' | 'list';
  filterPanelOpen: boolean;
  toggleTheme: () => void;
  setViewMode: (mode: 'grid' | 'list') => void;
  toggleFilterPanel: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      theme: 'dark',
      viewMode: 'grid',
      filterPanelOpen: false,
      toggleTheme: () =>
        set((state) => ({ theme: state.theme === 'dark' ? 'light' : 'dark' })),
      setViewMode: (mode) => set({ viewMode: mode }),
      toggleFilterPanel: () =>
        set((state) => ({ filterPanelOpen: !state.filterPanelOpen })),
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({ theme: state.theme, viewMode: state.viewMode }),
    }
  )
);
