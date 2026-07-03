import type { GraphResponse } from '@/models';

export interface GraphState {
    graph: GraphResponse | null;
    loading: boolean;
    error: string | null;
    selectedRef: string | null;
    hoveredNode: string | null;
    /** null means every domain is visible; otherwise the focus set. */
    visibleDomains: string[] | null;
    showSkills: boolean;
}
