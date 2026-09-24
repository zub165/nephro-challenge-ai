import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { NotesReview } from '@/types';

interface NotesState {
  draftPaste: string;
  cachedReview: NotesReview | null;
  lastSyncedAt: string | null;
  setDraftPaste: (text: string) => void;
  setCachedReview: (review: NotesReview | null) => void;
  setLastSyncedAt: (iso: string) => void;
  clearDraft: () => void;
}

export const useNotesStore = create<NotesState>()(
  persist(
    (set) => ({
      draftPaste: '',
      cachedReview: null,
      lastSyncedAt: null,
      setDraftPaste: (draftPaste) => set({ draftPaste }),
      setCachedReview: (cachedReview) => set({ cachedReview }),
      setLastSyncedAt: (lastSyncedAt) => set({ lastSyncedAt }),
      clearDraft: () => set({ draftPaste: '' }),
    }),
    {
      name: 'nephro-study-notes',
      partialize: (state) => ({
        draftPaste: state.draftPaste,
        cachedReview: state.cachedReview,
        lastSyncedAt: state.lastSyncedAt,
      }),
    }
  )
);
