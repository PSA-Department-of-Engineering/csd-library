import { useEffect } from 'react';

import { Button } from '@/components/ui/button';
import { useClaims } from '@/viewmodels/claims';
import { DOMAIN_COLORS, DOMAIN_ORDER, useGraph } from '@/viewmodels/graph';
import { useNav } from '@/viewmodels/nav';
import { selectViolationsSection, usePlaybook } from '@/viewmodels/playbook';
import { Spinner } from '@/views/atoms/Spinner';
import { ValidationBanner } from '@/views/molecules/ValidationBanner';
import { ViolationsPanel } from '@/views/molecules/ViolationsPanel';

const shortName = (id: string): string => id.replace(/^REF-/, '');

/** Readable home: health, the five rules, and every REF/skill with its summary. */
export const LibraryPage = () => {
    const graph = useGraph((state) => state.graph);
    const graphLoad = useGraph((state) => state.load);
    const select = useGraph((state) => state.select);
    const doc = usePlaybook((state) => state.doc);
    const docLoad = usePlaybook((state) => state.load);
    const claims = useClaims((state) => state.claims);
    const claimsLoad = useClaims((state) => state.load);
    const validating = useClaims((state) => state.validating);
    const report = useClaims((state) => state.report);
    const validate = useClaims((state) => state.validate);
    const setView = useNav((state) => state.setView);

    useEffect(() => {
        void graphLoad();
        void docLoad();
        void claimsLoad();
    }, [graphLoad, docLoad, claimsLoad]);

    if (!graph) {
        return <Spinner />;
    }

    const refs = graph.nodes.filter((n) => n.kind === 'ref');
    const skills = graph.nodes.filter((n) => n.kind === 'skill');
    const violations = selectViolationsSection(doc);

    const openRef = (id: string) => {
        select(id);
        setView('ref');
    };

    return (
        <div className="mx-auto flex max-w-6xl flex-col gap-5">
            <div className="flex flex-wrap items-center gap-x-6 gap-y-2 rounded-lg border bg-card/60 px-4 py-3">
                <div className="flex items-baseline gap-4 text-sm">
                    <span>
                        <strong className="text-lg">{refs.length}</strong>{' '}
                        <span className="text-muted-foreground">REFs</span>
                    </span>
                    <span>
                        <strong className="text-lg">{skills.length}</strong>{' '}
                        <span className="text-muted-foreground">skills</span>
                    </span>
                    <span>
                        <strong className="text-lg">{claims.length}</strong>{' '}
                        <span className="text-muted-foreground">intent claims</span>
                    </span>
                </div>
                <div className="ml-auto flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">
                        intent tests + link checker gate every edit
                    </span>
                    <Button disabled={validating} onClick={() => void validate()}>
                        {validating ? 'Running...' : 'Run validation'}
                    </Button>
                </div>
            </div>
            {report && <ValidationBanner report={report} />}

            {violations && <ViolationsPanel body={violations.body} />}

            {DOMAIN_ORDER.map((domain) => {
                const group = refs
                    .filter((r) => r.domain === domain)
                    .sort((a, b) => a.id.localeCompare(b.id));
                if (group.length === 0) {
                    return null;
                }
                return (
                    <section key={domain}>
                        <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                            <span
                                className="h-2 w-2 rounded-full"
                                style={{ backgroundColor: DOMAIN_COLORS[domain] }}
                            />
                            {domain}
                            <span className="font-normal text-muted-foreground/60">
                                {group.length}
                            </span>
                        </h3>
                        <div className="grid grid-cols-1 gap-2 md:grid-cols-2 xl:grid-cols-3">
                            {group.map((ref) => (
                                <button
                                    key={ref.id}
                                    onClick={() => openRef(ref.id)}
                                    className="rounded-lg border bg-card/60 p-3 text-left transition-colors hover:border-primary/50 hover:bg-secondary/50"
                                >
                                    <p className="font-mono text-sm font-semibold text-foreground">
                                        {shortName(ref.id)}
                                    </p>
                                    <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-muted-foreground">
                                        {ref.summary}
                                    </p>
                                </button>
                            ))}
                        </div>
                    </section>
                );
            })}

            <section>
                <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                    <span className="h-2 w-2 rounded-full bg-slate-400" />
                    skills
                    <span className="font-normal text-muted-foreground/60">{skills.length}</span>
                </h3>
                <div className="grid grid-cols-1 gap-2 md:grid-cols-2 xl:grid-cols-3">
                    {skills
                        .sort((a, b) => a.id.localeCompare(b.id))
                        .map((skill) => {
                            const refChips = graph.edges
                                .filter((e) => e.kind === 'skill-to-ref' && e.source === skill.id)
                                .map((e) => e.target);
                            return (
                                <div key={skill.id} className="rounded-lg border bg-card/40 p-3">
                                    <p className="font-mono text-sm font-semibold text-foreground">
                                        {skill.id}
                                    </p>
                                    <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-muted-foreground">
                                        {skill.summary}
                                    </p>
                                    <div className="mt-2 flex flex-wrap gap-1">
                                        {refChips.map((refId) => (
                                            <button
                                                key={refId}
                                                onClick={() => openRef(refId)}
                                                className="rounded-full border border-border px-1.5 py-0.5 text-[10px] text-muted-foreground hover:border-primary/60 hover:text-primary"
                                            >
                                                {shortName(refId)}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            );
                        })}
                </div>
            </section>
        </div>
    );
};
