import { create } from 'zustand';

import type { GraphResponse } from '@/models';
import { apiFetch } from '@/utils';

import type { GraphState } from './graph.state';

interface GraphActions {
    load: () => Promise<void>;
    select: (nodeId: string | null) => void;
    hover: (nodeId: string | null) => void;
}

export const useGraph = create<GraphState & GraphActions>()((set) => ({
    graph: null,
    loading: false,
    error: null,
    selectedRef: null,
    hoveredNode: null,

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
}));
