import { describe, expect } from 'vitest';
import { intent } from 'vitest-intent';

import type { GraphResponse } from '@/models';

import { computeLayout } from './graph.model';

const graph: GraphResponse = {
    nodes: [
        { id: 'AI-PLAYBOOK', kind: 'playbook', label: 'AI Playbook', domain: null, summary: '' },
        { id: 'REF-Alpha', kind: 'ref', label: 'Alpha', domain: 'language', summary: 'Alpha.' },
        { id: 'REF-Beta', kind: 'ref', label: 'Beta', domain: 'meta', summary: 'Beta.' },
        { id: 'do-alpha', kind: 'skill', label: 'do-alpha', domain: null, summary: 'Does alpha.' },
    ],
    edges: [{ source: 'do-alpha', target: 'REF-Alpha', kind: 'skill-to-ref' }],
};

describe('computeLayout', () => {
    intent('INT-LAYOUT-001', 'puts the playbook at the origin', () => {
        const playbook = computeLayout(graph).find((l) => l.node.id === 'AI-PLAYBOOK');
        expect(playbook).toMatchObject({ x: 0, y: 0 });
    });

    intent('INT-LAYOUT-001', 'places every node exactly once', () => {
        const ids = computeLayout(graph).map((l) => l.node.id);
        expect(ids.sort()).toEqual(['AI-PLAYBOOK', 'REF-Alpha', 'REF-Beta', 'do-alpha']);
    });

    intent('INT-LAYOUT-001', 'puts skills on a wider ring than refs', () => {
        const layout = computeLayout(graph);
        const radius = (id: string) => {
            const l = layout.find((n) => n.node.id === id);
            return l ? Math.hypot(l.x, l.y) : 0;
        };
        expect(radius('do-alpha')).toBeGreaterThan(radius('REF-Alpha'));
    });

    intent('INT-LAYOUT-001', 'colors refs by their domain', () => {
        const layout = computeLayout(graph);
        const alpha = layout.find((l) => l.node.id === 'REF-Alpha');
        const beta = layout.find((l) => l.node.id === 'REF-Beta');
        expect(alpha?.color).not.toEqual(beta?.color);
    });
});
