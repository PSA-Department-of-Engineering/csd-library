import { useEffect, useMemo } from 'react';

import { Spinner } from '@/views/atoms/Spinner';
import { computeLayout, useGraph } from '@/viewmodels/graph';

const EDGE_COLORS: Record<string, string> = {
    'playbook-to-ref': '#cbd5e1',
    'ref-to-ref': '#94a3b8',
    'skill-to-ref': '#c4b5fd',
};

const shortLabel = (id: string): string => id.replace(/^REF-/, '');

export const PlaybookGraph = () => {
    const graph = useGraph((state) => state.graph);
    const loading = useGraph((state) => state.loading);
    const error = useGraph((state) => state.error);
    const selectedRef = useGraph((state) => state.selectedRef);
    const hoveredNode = useGraph((state) => state.hoveredNode);
    const load = useGraph((state) => state.load);
    const select = useGraph((state) => state.select);
    const hover = useGraph((state) => state.hover);

    useEffect(() => {
        void load();
    }, [load]);

    const layout = useMemo(() => (graph ? computeLayout(graph) : []), [graph]);
    const positions = useMemo(() => new Map(layout.map((l) => [l.node.id, l])), [layout]);

    if (loading && !graph) {
        return <Spinner />;
    }
    if (error) {
        return <p className="text-sm text-rose-700">{error}</p>;
    }
    if (!graph) {
        return null;
    }

    const active = hoveredNode ?? selectedRef;
    const activeEdges = graph.edges.filter((e) => e.source === active || e.target === active);
    const neighbourIds = new Set(activeEdges.flatMap((e) => [e.source, e.target]));

    return (
        <svg
            viewBox="-470 -470 940 940"
            className="h-full w-full"
            role="img"
            aria-label="Playbook reference graph"
            onClick={() => select(null)}
        >
            {graph.edges.map((edge) => {
                const from = positions.get(edge.source);
                const to = positions.get(edge.target);
                if (!from || !to) {
                    return null;
                }
                const isActive =
                    active !== null && (edge.source === active || edge.target === active);
                return (
                    <line
                        key={`${edge.source}->${edge.target}`}
                        x1={from.x}
                        y1={from.y}
                        x2={to.x}
                        y2={to.y}
                        stroke={EDGE_COLORS[edge.kind] ?? '#e2e8f0'}
                        strokeWidth={isActive ? 1.6 : 0.6}
                        strokeOpacity={active === null ? 0.25 : isActive ? 0.85 : 0.06}
                    />
                );
            })}
            {layout.map(({ node, x, y, color }) => {
                const isRef = node.kind === 'ref';
                const isPlaybook = node.kind === 'playbook';
                const radius = isPlaybook ? 26 : isRef ? 9 : 4.5;
                const dimmed = active !== null && node.id !== active && !neighbourIds.has(node.id);
                const labelFactor = (Math.hypot(x, y) + radius + 10) / (Math.hypot(x, y) || 1);
                const lx = x * labelFactor;
                const ly = y * labelFactor;
                return (
                    <g
                        key={node.id}
                        opacity={dimmed ? 0.25 : 1}
                        className="cursor-pointer"
                        onClick={(event) => {
                            event.stopPropagation();
                            select(isRef ? node.id : null);
                        }}
                        onMouseEnter={() => hover(node.id)}
                        onMouseLeave={() => hover(null)}
                    >
                        <circle
                            cx={x}
                            cy={y}
                            r={radius}
                            fill={color}
                            stroke={node.id === selectedRef ? '#0f172a' : 'white'}
                            strokeWidth={node.id === selectedRef ? 3 : 1.5}
                        />
                        {isPlaybook ? (
                            <text
                                x={0}
                                y={4}
                                textAnchor="middle"
                                className="fill-white text-[11px] font-bold"
                            >
                                PLAYBOOK
                            </text>
                        ) : (
                            <text
                                x={lx}
                                y={ly + 3}
                                textAnchor={lx > 20 ? 'start' : lx < -20 ? 'end' : 'middle'}
                                fill={isRef ? '#334155' : '#94a3b8'}
                                fontSize={isRef ? 11 : 8.5}
                            >
                                {shortLabel(node.id)}
                            </text>
                        )}
                    </g>
                );
            })}
        </svg>
    );
};
