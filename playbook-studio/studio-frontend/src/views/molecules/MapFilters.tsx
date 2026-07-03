import { DOMAIN_COLORS, DOMAIN_ORDER, useGraph } from '@/viewmodels/graph';
import { cn } from '@/utils';

/** Interactive legend: click a domain to focus on it (solo), click more to
 *  widen the focus set, click an active chip to drop it. */
export const MapFilters = () => {
    const visibleDomains = useGraph((state) => state.visibleDomains);
    const showSkills = useGraph((state) => state.showSkills);
    const toggleDomain = useGraph((state) => state.toggleDomain);
    const toggleSkills = useGraph((state) => state.toggleSkills);
    const resetFilters = useGraph((state) => state.resetFilters);

    const filtered = visibleDomains !== null || !showSkills;

    return (
        <div className="flex flex-wrap items-center gap-1.5">
            {DOMAIN_ORDER.map((domain) => {
                const activeChip = visibleDomains === null || visibleDomains.includes(domain);
                const title =
                    visibleDomains === null
                        ? `Focus on ${domain}`
                        : activeChip
                          ? `Remove ${domain} from focus`
                          : `Add ${domain} to focus`;
                return (
                    <button
                        key={domain}
                        onClick={() => toggleDomain(domain)}
                        title={title}
                        className={cn(
                            'rounded-full px-2 py-0.5 text-[11px] font-medium transition-opacity',
                            activeChip
                                ? 'text-white'
                                : 'border border-border text-muted-foreground opacity-60 hover:opacity-100',
                        )}
                        style={activeChip ? { backgroundColor: DOMAIN_COLORS[domain] } : undefined}
                    >
                        {domain}
                    </button>
                );
            })}
            <button
                onClick={toggleSkills}
                title={showSkills ? 'Hide skills' : 'Show skills'}
                className={cn(
                    'rounded-full px-2 py-0.5 text-[11px] font-medium transition-opacity',
                    showSkills
                        ? 'bg-slate-500 text-white'
                        : 'border border-border text-muted-foreground opacity-60 hover:opacity-100',
                )}
            >
                skills
            </button>
            {filtered && (
                <button
                    onClick={resetFilters}
                    className="rounded-full border border-primary/50 px-2 py-0.5 text-[11px] font-medium text-primary hover:bg-primary/10"
                >
                    show all
                </button>
            )}
        </div>
    );
};
