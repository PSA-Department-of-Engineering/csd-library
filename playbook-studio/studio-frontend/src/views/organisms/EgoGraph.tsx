import { useMemo } from 'react';

import { DOMAIN_COLORS, SKILL_COLOR, useGraph } from '@/viewmodels/graph';
import { useNav } from '@/viewmodels/nav';

export interface EgoGraphProps {
    refName: string;
}

const shortLabel = (id: string): string => id.replace(/^REF-/, '');

interface Neighbour {
    id: string;
    kind: 'ref' | 'skill';
    inbound: boolean;
}

/** The selected REF and its direct connections, at a glance and clickable. */
export const EgoGraph = ({ refName }: EgoGraphProps) => {
    const graph = useGraph((state) => state.graph);
    const select = useGraph((state) => state.select);
    const setView = useNav((state) => state.setView);

    const neighbours = useMemo<Neighbour[]>(() => {
        if (!graph) {
            return [];
        }
        const out: Neighbour[] = [];
        const seen = new Set<string>();
        for (const e of graph.edges) {
            let other: Neighbour | null = null;
            if (e.source === refName && e.kind === 'ref-to-ref') {
                other = { id: e.target, kind: 'ref', inbound: false };
            } else if (e.target === refName && e.kind === 'ref-to-ref') {
                other = { id: e.source, kind: 'ref', inbound: true };
            } else if (e.target === refName && e.kind === 'skill-to-ref') {
                other = { id: e.source, kind: 'skill', inbound: true };
            }
            if (other && !seen.has(other.id)) {
                seen.add(other.id);
                out.push(other);
            }
        }
        return out;
    }, [graph, refName]);

    const domainOf = (id: string): string | null =>
        graph?.nodes.find((n) => n.id === id)?.domain ?? null;

    if (!graph || neighbours.length === 0) {
        return null;
    }

    const R = 92;
    const size = 300;
    const center = size / 2;
    const selfColor = DOMAIN_COLORS[domainOf(refName) ?? ''] ?? SKILL_COLOR;

    return (
        <svg viewBox={`0 0 ${size} ${size}`} className="w-full" role="img" aria-label="Connections">
            {neighbours.map((n, i) => {
                const angle = (2 * Math.PI * i) / neighbours.length - Math.PI / 2;
                const x = center + R * Math.cos(angle);
                const y = center + R * Math.sin(angle);
                const color =
                    n.kind === 'ref'
                        ? (DOMAIN_COLORS[domainOf(n.id) ?? ''] ?? SKILL_COLOR)
                        : SKILL_COLOR;
                const label = shortLabel(n.id);
                const flip = Math.cos(angle) < 0;
                const deg = (angle * 180) / Math.PI;
                const lx = center + (R + 10) * Math.cos(angle);
                const ly = center + (R + 10) * Math.sin(angle);
                return (
                    <g
                        key={n.id}
                        className={n.kind === 'ref' ? 'cursor-pointer' : undefined}
                        onClick={() => {
                            if (n.kind === 'ref') {
                                select(n.id);
                                setView('ref');
                            }
                        }}
                    >
                        <line
                            x1={center}
                            y1={center}
                            x2={x}
                            y2={y}
                            stroke={n.inbound ? '#6d5fd0' : '#4c5a7a'}
                            strokeWidth={1}
                            strokeOpacity={0.55}
                            strokeDasharray={n.kind === 'skill' ? '2 3' : undefined}
                        />
                        <circle cx={x} cy={y} r={n.kind === 'ref' ? 5 : 3.5} fill={color} />
                        <text
                            x={lx}
                            y={ly}
                            dy="0.32em"
                            transform={`rotate(${flip ? deg + 180 : deg} ${lx} ${ly})`}
                            textAnchor={flip ? 'end' : 'start'}
                            fill={n.kind === 'ref' ? '#c7d2e4' : '#8593ad'}
                            fontSize={8.5}
                        >
                            {label.length > 16 ? `${label.slice(0, 15)}…` : label}
                        </text>
                    </g>
                );
            })}
            <circle
                cx={center}
                cy={center}
                r={9}
                fill={selfColor}
                stroke="#0a0e1a"
                strokeWidth={1.5}
            />
        </svg>
    );
};
