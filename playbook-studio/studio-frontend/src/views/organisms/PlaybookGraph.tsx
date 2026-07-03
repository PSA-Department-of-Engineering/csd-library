import { useEffect, useMemo } from 'react';

import { computeDomainArcs, computeLayout, REF_RADIUS, useGraph } from '@/viewmodels/graph';
import { useNav } from '@/viewmodels/nav';
import { Spinner } from '@/views/atoms/Spinner';

const EDGE_COLORS: Record<string, string> = {
    'playbook-to-ref': '#3b4a6b',
    'ref-to-ref': '#4c5a7a',
    'skill-to-ref': '#6d5fd0',
};

const NODE_STROKE = '#0a0e1a';
const REF_LABEL = '#c7d2e4';
const SKILL_LABEL = '#8593ad';

const shortLabel = (id: string): string => id.replace(/^REF-/, '');

const truncated = (label: string): string => (label.length > 24 ? `${label.slice(0, 23)}…` : label);

const polarPoint = (radius: number, angle: number): [number, number] => [
    radius * Math.cos(angle),
    radius * Math.sin(angle),
];

/** Rotated so every label owns its own angular sector: no collisions. */
const radialLabel = (angle: number, radius: number) => {
    const [x, y] = polarPoint(radius, angle);
    const deg = (angle * 180) / Math.PI;
    const flip = Math.cos(angle) < 0;
    return {
        x,
        y,
        transform: `rotate(${flip ? deg + 180 : deg} ${x} ${y})`,
        textAnchor: flip ? ('end' as const) : ('start' as const),
    };
};

const arcPath = (radius: number, start: number, end: number): string => {
    const [x1, y1] = polarPoint(radius, start);
    const [x2, y2] = polarPoint(radius, end);
    const largeArc = end - start > Math.PI ? 1 : 0;
    return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`;
};

export const PlaybookGraph = () => {
    const graph = useGraph((state) => state.graph);
    const loading = useGraph((state) => state.loading);
    const error = useGraph((state) => state.error);
    const selectedRef = useGraph((state) => state.selectedRef);
    const hoveredNode = useGraph((state) => state.hoveredNode);
    const load = useGraph((state) => state.load);
    const select = useGraph((state) => state.select);
    const hover = useGraph((state) => state.hover);
    const setView = useNav((state) => state.setView);

    useEffect(() => {
        void load();
    }, [load]);

    const layout = useMemo(() => (graph ? computeLayout(graph) : []), [graph]);
    const arcs = useMemo(() => (graph ? computeDomainArcs(graph) : []), [graph]);
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

    const edgePath = (x1: number, y1: number, x2: number, y2: number): string => {
        // Chords curve gently toward the hub; spokes from the hub stay straight.
        if ((x1 === 0 && y1 === 0) || (x2 === 0 && y2 === 0)) {
            return `M ${x1} ${y1} L ${x2} ${y2}`;
        }
        const cx = ((x1 + x2) / 2) * 0.45;
        const cy = ((y1 + y2) / 2) * 0.45;
        return `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`;
    };

    return (
        <svg
            viewBox="-575 -575 1150 1150"
            className="h-full w-full"
            role="img"
            aria-label="Playbook reference graph"
            onClick={() => select(null)}
        >
            {arcs.map((arc) => (
                <path
                    key={arc.domain}
                    d={arcPath(REF_RADIUS - 24, arc.startAngle, arc.endAngle)}
                    fill="none"
                    stroke={arc.color}
                    strokeWidth={2.5}
                    strokeOpacity={0.55}
                    strokeLinecap="round"
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
                    <path
                        key={`${edge.source}->${edge.target}`}
                        d={edgePath(from.x, from.y, to.x, to.y)}
                        fill="none"
                        stroke={EDGE_COLORS[edge.kind] ?? '#334155'}
                        strokeWidth={isActive ? 1.8 : 0.7}
                        strokeOpacity={active === null ? 0.16 : isActive ? 0.95 : 0.04}
                    />
                );
            })}

            {layout.map(({ node, x, y, angle, color }) => {
                const isRef = node.kind === 'ref';
                const isPlaybook = node.kind === 'playbook';
                const isFocused = node.id === active || node.id === selectedRef;
                const radius = isPlaybook ? 26 : isRef ? (isFocused ? 11 : 9) : isFocused ? 6 : 4.5;
                const dimmed = active !== null && node.id !== active && !neighbourIds.has(node.id);
                const label = isPlaybook ? null : radialLabel(angle, Math.hypot(x, y) + radius + 8);
                return (
                    <g
                        key={node.id}
                        opacity={dimmed ? 0.22 : 1}
                        className="cursor-pointer"
                        onClick={(event) => {
                            event.stopPropagation();
                            if (isRef) {
                                select(node.id);
                                setView('ref');
                            }
                        }}
                        onMouseEnter={() => hover(node.id)}
                        onMouseLeave={() => hover(null)}
                    >
                        {isPlaybook && <circle r={44} fill="#6366f1" fillOpacity={0.12} />}
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
                                y={3.5}
                                textAnchor="middle"
                                fill="#eef2ff"
                                fontSize={10}
                                fontWeight={700}
                                letterSpacing="0.08em"
                            >
                                PLAYBOOK
                            </text>
                        ) : (
                            label && (
                                <text
                                    x={label.x}
                                    y={label.y}
                                    dy="0.32em"
                                    transform={label.transform}
                                    textAnchor={label.textAnchor}
                                    fill={isRef ? REF_LABEL : SKILL_LABEL}
                                    fontSize={isRef ? 12.5 : 10}
                                    fontWeight={isFocused ? 700 : isRef ? 500 : 400}
                                >
                                    <title>{node.id}</title>
                                    {truncated(shortLabel(node.id))}
                                </text>
                            )
                        )}
                    </g>
                );
            })}
        </svg>
    );
};
