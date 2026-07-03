import { create } from 'zustand';

import type { PlaybookResponse, ValidationReportResponse } from '@/models';
import { apiFetch, gatedSend } from '@/utils';

import type { PlaybookState } from './playbook.state';

interface PlaybookActions {
    load: () => Promise<void>;
    startEdit: () => void;
    setDraft: (draft: string) => void;
    cancelEdit: () => void;
    save: () => Promise<void>;
}

export const usePlaybook = create<PlaybookState & PlaybookActions>()((set, get) => ({
    doc: null,
    loading: false,
    error: null,
    editing: false,
    draft: '',
    saving: false,
    saveError: null,
    lastReport: null,

    load: async () => {
        if (get().doc !== null || get().loading) {
            return;
        }
        set({ loading: true, error: null });
        try {
            const doc = await apiFetch<PlaybookResponse>('/api/playbook');
            set({ doc });
        } catch (err) {
            set({ error: err instanceof Error ? err.message : 'Failed to load the playbook' });
        } finally {
            set({ loading: false });
        }
    },

    startEdit: () => {
        set({ editing: true, draft: get().doc?.raw ?? '', saveError: null });
    },

    setDraft: (draft) => {
        set({ draft });
    },

    cancelEdit: () => {
        set({ editing: false, draft: '', saveError: null });
    },

    save: async () => {
        const { draft } = get();
        set({ saving: true, saveError: null });
        const result = await gatedSend<ValidationReportResponse>('/api/playbook', 'PUT', {
            raw: draft,
        });
        set({
            saving: false,
            lastReport: (result.ok ?? result.report) as ValidationReportResponse | null,
        });
        if (result.error !== null) {
            set({ saveError: result.error });
            return;
        }
        set({ editing: false, draft: '', doc: null });
        await get().load();
    },
}));
