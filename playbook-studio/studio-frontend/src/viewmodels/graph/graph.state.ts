import type { GraphResponse } from '@/models';

export interface GraphState {
    graph: GraphResponse | null;
    loading: boolean;
    error: string | null;
    selectedRef: string | null;
    hoveredNode: string | null;
    hiddenDomains: string[];
    showSkills: boolean;
}
