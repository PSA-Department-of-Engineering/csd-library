import { describe, expect, it } from 'vitest';

import type { GraphResponse } from '@/models';

import { computeLayout } from './graph.model';

const graph: GraphResponse = {
    nodes: [
        { id: 'AI-PLAYBOOK', kind: 'playbook', label: 'AI Playbook', domain: null },
        { id: 'REF-Alpha', kind: 'ref', label: 'Alpha', domain: 'language' },
        { id: 'REF-Beta', kind: 'ref', label: 'Beta', domain: 'meta' },
        { id: 'do-alpha', kind: 'skill', label: 'do-alpha', domain: null },
    ],
    edges: [{ source: 'do-alpha', target: 'REF-Alpha', kind: 'skill-to-ref' }],
};

describe('computeLayout', () => {
    it('puts the playbook at the origin', () => {
        const playbook = computeLayout(graph).find((l) => l.node.id === 'AI-PLAYBOOK');
        expect(playbook).toMatchObject({ x: 0, y: 0 });
    });

    it('places every node exactly once', () => {
        const ids = computeLayout(graph).map((l) => l.node.id);
        expect(ids.sort()).toEqual(['AI-PLAYBOOK', 'REF-Alpha', 'REF-Beta', 'do-alpha']);
    });

    it('puts skills on a wider ring than refs', () => {
        const layout = computeLayout(graph);
        const radius = (id: string) => {
            const l = layout.find((n) => n.node.id === id);
            return l ? Math.hypot(l.x, l.y) : 0;
        };
        expect(radius('do-alpha')).toBeGreaterThan(radius('REF-Alpha'));
    });

    it('colors refs by their domain', () => {
        const layout = computeLayout(graph);
        const alpha = layout.find((l) => l.node.id === 'REF-Alpha');
        const beta = layout.find((l) => l.node.id === 'REF-Beta');
        expect(alpha?.color).not.toEqual(beta?.color);
    });
});
