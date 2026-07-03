import { create } from 'zustand';

import type { GraphResponse } from '@/models';
import { apiFetch } from '@/utils';

import type { GraphState } from './graph.state';

interface GraphActions {
    load: () => Promise<void>;
    select: (nodeId: string | null) => void;
    hover: (nodeId: string | null) => void;
    toggleDomain: (domain: string) => void;
    toggleSkills: () => void;
    resetFilters: () => void;
}

export const useGraph = create<GraphState & GraphActions>()((set, get) => ({
    graph: null,
    loading: false,
    error: null,
    selectedRef: null,
    hoveredNode: null,
    hiddenDomains: [],
    showSkills: true,

    load: async () => {
        set({ loading: true, error: null });
        try {
            const graph = await apiFetch<GraphResponse>('/api/graph');
            set({ graph });
        } catch (err) {
            set({ error: err instanceof Error ? err.message : 'Failed to load graph' });
        } finally {
            set({ loading: false });
        }
    },

    select: (nodeId) => {
        set({ selectedRef: nodeId });
    },

    hover: (nodeId) => {
        set({ hoveredNode: nodeId });
    },

    toggleDomain: (domain) => {
        const hidden = get().hiddenDomains;
        set({
            hiddenDomains: hidden.includes(domain)
                ? hidden.filter((d) => d !== domain)
                : [...hidden, domain],
        });
    },

    toggleSkills: () => {
        set({ showSkills: !get().showSkills });
    },

    resetFilters: () => {
        set({ hiddenDomains: [], showSkills: true });
    },
}));
