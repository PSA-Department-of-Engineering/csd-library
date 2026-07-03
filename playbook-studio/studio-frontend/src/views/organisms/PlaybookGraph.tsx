import { useEffect, useMemo } from 'react';

import { Spinner } from '@/views/atoms/Spinner';
import { computeLayout, useGraph } from '@/viewmodels/graph';

const EDGE_COLORS: Record<string, string> = {
    'playbook-to-ref': '#3b4a6b',
    'ref-to-ref': '#4c5a7a',
    'skill-to-ref': '#6d5fd0',
};

const NODE_STROKE = '#0a0e1a';
const REF_LABEL = '#c7d2e4';
const SKILL_LABEL = '#5f6b82';
const RING_STROKE = '#1b2338';

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
        return <p className="text-sm text-destructive">{error}</p>;
    }
    if (!graph) {
        return null;
    }

    const active = hoveredNode ?? selectedRef;
    const activeEdges = graph.edges.filter((e) => e.source === active || e.target === active);
    const neighbourIds = new Set(activeEdges.flatMap((e) => [e.source, e.target]));

    return (
        <svg
            viewBox="-480 -480 960 960"
            className="h-full w-full"
            role="img"
            aria-label="Playbook reference graph"
            onClick={() => select(null)}
        >
            <defs>
                <radialGradient id="hub-glow">
                    <stop offset="0%" stopColor="#818cf8" stopOpacity="0.35" />
                    <stop offset="100%" stopColor="#818cf8" stopOpacity="0" />
                </radialGradient>
            </defs>

            {[250, 400].map((r) => (
                <circle
                    key={r}
                    r={r}
                    fill="none"
                    stroke={RING_STROKE}
                    strokeWidth={1}
                    strokeDasharray="2 6"
                />
            ))}

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
                        stroke={EDGE_COLORS[edge.kind] ?? '#334155'}
                        strokeWidth={isActive ? 1.8 : 0.7}
                        strokeOpacity={active === null ? 0.35 : isActive ? 0.95 : 0.08}
                    />
                );
            })}

            <circle r={70} fill="url(#hub-glow)" pointerEvents="none" />

            {layout.map(({ node, x, y, color }) => {
                const isRef = node.kind === 'ref';
                const isPlaybook = node.kind === 'playbook';
                const radius = isPlaybook ? 30 : isRef ? 9.5 : 5;
                const dimmed = active !== null && node.id !== active && !neighbourIds.has(node.id);
                const labelFactor = (Math.hypot(x, y) + radius + 11) / (Math.hypot(x, y) || 1);
                const lx = x * labelFactor;
                const ly = y * labelFactor;
                const isFocused = node.id === active || node.id === selectedRef;
                return (
                    <g
                        key={node.id}
                        opacity={dimmed ? 0.2 : 1}
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
                            fill={isPlaybook ? '#6366f1' : color}
                            stroke={node.id === selectedRef ? '#e2e8f0' : NODE_STROKE}
                            strokeWidth={node.id === selectedRef ? 2.5 : 1.5}
                        />
                        {isPlaybook ? (
                            <text
                                x={0}
                                y={4}
                                textAnchor="middle"
                                fill="#eef2ff"
                                fontSize={11}
                                fontWeight={700}
                                letterSpacing="0.08em"
                            >
                                PLAYBOOK
                            </text>
                        ) : (
                            <text
                                x={lx}
                                y={ly + 3.5}
                                textAnchor={lx > 20 ? 'start' : lx < -20 ? 'end' : 'middle'}
                                fill={isRef ? REF_LABEL : SKILL_LABEL}
                                fontSize={isRef ? 12 : 9}
                                fontWeight={isRef ? (isFocused ? 700 : 500) : 400}
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
