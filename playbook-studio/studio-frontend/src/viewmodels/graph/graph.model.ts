import type { GraphNodeResponse, GraphResponse } from '@/models';

/** Fixed presentation order and color for each REF domain. */
export const DOMAIN_ORDER = [
    'meta',
    'architecture',
    'language',
    'framework',
    'practice',
    'methodology',
    'pkm',
] as const;

export const DOMAIN_COLORS: Record<string, string> = {
    meta: '#8b5cf6',
    architecture: '#0ea5e9',
    language: '#10b981',
    framework: '#f59e0b',
    practice: '#f43f5e',
    methodology: '#6366f1',
    pkm: '#14b8a6',
};

export const SKILL_COLOR = '#94a3b8';
export const PLAYBOOK_COLOR = '#0f172a';

export interface LaidOutNode {
    node: GraphNodeResponse;
    x: number;
    y: number;
    /** Angle in radians; NaN for the center node. Drives rotated labels. */
    angle: number;
    color: string;
}

export interface DomainArc {
    domain: string;
    startAngle: number;
    endAngle: number;
    color: string;
}

export const REF_RADIUS = 250;
export const SKILL_RADIUS = 390;

const polar = (radius: number, angle: number): { x: number; y: number } => ({
    x: Math.round(radius * Math.cos(angle) * 100) / 100,
    y: Math.round(radius * Math.sin(angle) * 100) / 100,
});

/**
 * Radial layout: playbook at the origin, REFs on an inner ring grouped by
 * domain (DOMAIN_ORDER), skills on an outer ring near the mean angle of the
 * REFs they instantiate.
 */
export function computeLayout(graph: GraphResponse): LaidOutNode[] {
    const refs = graph.nodes.filter((n) => n.kind === 'ref');
    const skills = graph.nodes.filter((n) => n.kind === 'skill');
    const playbook = graph.nodes.filter((n) => n.kind === 'playbook');

    const sortedRefs = sortRefsByDomain(refs);

    const refAngle = new Map<string, number>();
    const out: LaidOutNode[] = playbook.map((node) => ({
        node,
        x: 0,
        y: 0,
        angle: Number.NaN,
        color: PLAYBOOK_COLOR,
    }));

    sortedRefs.forEach((node, i) => {
        const angle = (2 * Math.PI * i) / sortedRefs.length - Math.PI / 2;
        refAngle.set(node.id, angle);
        out.push({
            node,
            ...polar(REF_RADIUS, angle),
            angle,
            color: DOMAIN_COLORS[node.domain ?? ''] ?? SKILL_COLOR,
        });
    });

    const desiredAngle = (skillId: string): number => {
        const targets = graph.edges
            .filter((e) => e.kind === 'skill-to-ref' && e.source === skillId)
            .map((e) => refAngle.get(e.target))
            .filter((a): a is number => a !== undefined);
        if (targets.length === 0) {
            return Math.PI / 2;
        }
        // Mean of unit vectors, so angles across the wrap point average correctly.
        const x = targets.reduce((acc, a) => acc + Math.cos(a), 0);
        const y = targets.reduce((acc, a) => acc + Math.sin(a), 0);
        return Math.atan2(y, x);
    };

    // Evenly spaced on the outer ring, ordered by where their REFs sit.
    const sortedSkills = [...skills].sort((a, b) => desiredAngle(a.id) - desiredAngle(b.id));
    sortedSkills.forEach((node, i) => {
        const angle = (2 * Math.PI * i) / sortedSkills.length - Math.PI / 2;
        out.push({ node, ...polar(SKILL_RADIUS, angle), angle, color: SKILL_COLOR });
    });

    return out;
}

/** One arc per contiguous domain group on the REF ring, for cluster accents. */
export function computeDomainArcs(graph: GraphResponse): DomainArc[] {
    const sortedRefs = sortRefsByDomain(graph.nodes.filter((n) => n.kind === 'ref'));
    if (sortedRefs.length === 0) {
        return [];
    }
    const slot = (2 * Math.PI) / sortedRefs.length;
    const arcs: DomainArc[] = [];
    let start = 0;
    for (let i = 1; i <= sortedRefs.length; i += 1) {
        const domain = sortedRefs[start].domain ?? 'practice';
        if (i === sortedRefs.length || (sortedRefs[i].domain ?? 'practice') !== domain) {
            arcs.push({
                domain,
                startAngle: start * slot - Math.PI / 2 - slot * 0.32,
                endAngle: (i - 1) * slot - Math.PI / 2 + slot * 0.32,
                color: DOMAIN_COLORS[domain] ?? SKILL_COLOR,
            });
            start = i;
        }
    }
    return arcs;
}

function sortRefsByDomain(refs: GraphNodeResponse[]): GraphNodeResponse[] {
    return [...refs].sort((a, b) => {
        const da = DOMAIN_ORDER.indexOf((a.domain ?? 'practice') as (typeof DOMAIN_ORDER)[number]);
        const db = DOMAIN_ORDER.indexOf((b.domain ?? 'practice') as (typeof DOMAIN_ORDER)[number]);
        return da === db ? a.id.localeCompare(b.id) : da - db;
    });
}

export const selectNodeCount = (state: { graph: GraphResponse | null }): number =>
    state.graph?.nodes.length ?? 0;
