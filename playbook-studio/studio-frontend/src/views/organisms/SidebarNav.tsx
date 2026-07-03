import { useEffect, useState } from 'react';

import { DOMAIN_COLORS, DOMAIN_ORDER, useGraph } from '@/viewmodels/graph';
import { useNav } from '@/viewmodels/nav';
import { cn } from '@/utils';

const shortName = (id: string): string => id.replace(/^REF-/, '');

export const SidebarNav = () => {
    const graph = useGraph((state) => state.graph);
    const load = useGraph((state) => state.load);
    const select = useGraph((state) => state.select);
    const selectedRef = useGraph((state) => state.selectedRef);
    const view = useNav((state) => state.view);
    const setView = useNav((state) => state.setView);
    const [query, setQuery] = useState('');

    useEffect(() => {
        void load();
    }, [load]);

    const refs = graph?.nodes.filter((n) => n.kind === 'ref') ?? [];
    const q = query.trim().toLowerCase();
    const visible = q ? refs.filter((r) => r.id.toLowerCase().includes(q)) : refs;

    const open = (id: string) => {
        select(id);
        setView('ref');
    };

    return (
        <nav className="flex h-full flex-col gap-3">
            <button
                onClick={() => setView('playbook')}
                className={cn(
                    'flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-[13px] font-semibold',
                    view === 'playbook'
                        ? 'bg-secondary text-foreground'
                        : 'text-foreground hover:bg-secondary/60',
                )}
            >
                <span className="h-2 w-2 shrink-0 rounded-full bg-primary" />
                AI-PLAYBOOK
            </button>
            <input
                type="search"
                placeholder="Find a REF..."
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className="w-full rounded-md border border-input bg-background/60 px-3 py-1.5 text-sm outline-none placeholder:text-muted-foreground/60 focus:ring-1 focus:ring-ring"
            />
            <div className="flex-1 overflow-y-auto pr-1">
                {DOMAIN_ORDER.map((domain) => {
                    const group = visible.filter((r) => r.domain === domain);
                    if (group.length === 0) {
                        return null;
                    }
                    return (
                        <div key={domain} className="mb-3">
                            <p className="mb-1 px-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/70">
                                {domain}
                            </p>
                            <ul>
                                {group.map((ref) => {
                                    const isActive = view === 'ref' && selectedRef === ref.id;
                                    return (
                                        <li key={ref.id}>
                                            <button
                                                onClick={() => open(ref.id)}
                                                className={cn(
                                                    'flex w-full items-center gap-2 rounded-md px-2 py-1 text-left text-[13px]',
                                                    isActive
                                                        ? 'bg-secondary font-semibold text-foreground'
                                                        : 'text-muted-foreground hover:bg-secondary/60 hover:text-foreground',
                                                )}
                                            >
                                                <span
                                                    className="h-2 w-2 shrink-0 rounded-full"
                                                    style={{
                                                        backgroundColor:
                                                            DOMAIN_COLORS[domain] ?? '#64748b',
                                                    }}
                                                />
                                                {shortName(ref.id)}
                                            </button>
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    );
                })}
                {visible.length === 0 && (
                    <p className="px-2 text-xs text-muted-foreground">No REF matches "{query}".</p>
                )}
            </div>
            <button
                onClick={() => setView('create')}
                className={cn(
                    'flex w-full items-center justify-center gap-1.5 rounded-md border border-dashed border-border px-2 py-1.5 text-xs font-medium',
                    view === 'create'
                        ? 'border-primary/60 text-primary'
                        : 'text-muted-foreground hover:border-primary/40 hover:text-foreground',
                )}
            >
                + New REF
            </button>
        </nav>
    );
};
