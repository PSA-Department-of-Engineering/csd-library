import { DOMAIN_COLORS, DOMAIN_ORDER, useGraph } from '@/viewmodels/graph';
import { cn } from '@/utils';

/** Interactive legend: toggle domains and skills to focus the map. */
export const MapFilters = () => {
    const hiddenDomains = useGraph((state) => state.hiddenDomains);
    const showSkills = useGraph((state) => state.showSkills);
    const toggleDomain = useGraph((state) => state.toggleDomain);
    const toggleSkills = useGraph((state) => state.toggleSkills);
    const resetFilters = useGraph((state) => state.resetFilters);

    const filtered = hiddenDomains.length > 0 || !showSkills;

    return (
        <div className="flex flex-wrap items-center gap-1.5">
            {DOMAIN_ORDER.map((domain) => {
                const activeChip = !hiddenDomains.includes(domain);
                return (
                    <button
                        key={domain}
                        onClick={() => toggleDomain(domain)}
                        title={activeChip ? `Hide ${domain} REFs` : `Show ${domain} REFs`}
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
