import { create } from 'zustand';

import type { PlaybookResponse } from '@/models';
import { apiFetch } from '@/utils';

import type { PlaybookState } from './playbook.state';

interface PlaybookActions {
    load: () => Promise<void>;
}

export const usePlaybook = create<PlaybookState & PlaybookActions>()((set, get) => ({
    doc: null,
    loading: false,
    error: null,

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
}));
