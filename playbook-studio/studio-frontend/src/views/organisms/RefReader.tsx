import { useEffect } from 'react';

import type { RefSectionResponse } from '@/models';
import { Button } from '@/components/ui/button';
import { useGraph } from '@/viewmodels/graph';
import { useNav } from '@/viewmodels/nav';
import { useRefDetail } from '@/viewmodels/refdetail';
import { DomainBadge } from '@/views/atoms/DomainBadge';
import { Spinner } from '@/views/atoms/Spinner';
import { Markdown } from '@/views/molecules/Markdown';
import { ValidationBanner } from '@/views/molecules/ValidationBanner';

const shortName = (id: string): string => id.replace(/^REF-/, '');

interface ConnectionChipsProps {
    title: string;
    ids: string[];
    onOpen?: (id: string) => void;
}

const ConnectionChips = ({ title, ids, onOpen }: ConnectionChipsProps) => {
    if (ids.length === 0) {
        return null;
    }
    return (
        <div className="flex flex-wrap items-baseline gap-1.5">
            <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground/70">
                {title}
            </span>
            {ids.map((id) =>
                onOpen ? (
                    <button
                        key={id}
                        onClick={() => onOpen(id)}
                        className="rounded-full border border-border bg-secondary/60 px-2 py-0.5 text-[11px] text-foreground hover:border-primary/60 hover:text-primary"
                    >
                        {shortName(id)}
                    </button>
                ) : (
                    <span
                        key={id}
                        className="rounded-full border border-border px-2 py-0.5 text-[11px] text-muted-foreground"
                    >
                        {id}
                    </span>
                ),
            )}
        </div>
    );
};

export const RefReader = () => {
    const selectedRef = useGraph((state) => state.selectedRef);
    const graph = useGraph((state) => state.graph);
    const select = useGraph((state) => state.select);
    const setView = useNav((state) => state.setView);

    const ref = useRefDetail((state) => state.ref);
    const loading = useRefDetail((state) => state.loading);
    const error = useRefDetail((state) => state.error);
    const editingSection = useRefDetail((state) => state.editingSection);
    const draft = useRefDetail((state) => state.draft);
    const saving = useRefDetail((state) => state.saving);
    const saveError = useRefDetail((state) => state.saveError);
    const lastReport = useRefDetail((state) => state.lastReport);
    const load = useRefDetail((state) => state.load);
    const startEdit = useRefDetail((state) => state.startEdit);
    const setDraft = useRefDetail((state) => state.setDraft);
    const cancelEdit = useRefDetail((state) => state.cancelEdit);
    const save = useRefDetail((state) => state.save);

    useEffect(() => {
        if (selectedRef !== null) {
            void load(selectedRef);
        }
    }, [selectedRef, load]);

    if (selectedRef === null) {
        return <p className="text-sm text-muted-foreground">Pick a REF from the sidebar.</p>;
    }
    if (loading) {
        return <Spinner />;
    }
    if (error) {
        return <p className="text-sm text-destructive">{error}</p>;
    }
    if (!ref) {
        return null;
    }

    const edges = graph?.edges ?? [];
    const instantiatedBy = edges
        .filter((e) => e.kind === 'skill-to-ref' && e.target === ref.name)
        .map((e) => e.source);
    const references = edges
        .filter((e) => e.kind === 'ref-to-ref' && e.source === ref.name)
        .map((e) => e.target);
    const referencedBy = edges
        .filter((e) => e.kind === 'ref-to-ref' && e.target === ref.name)
        .map((e) => e.source);

    const openRef = (id: string) => {
        select(id);
        setView('ref');
    };

    const onEdit = (section: RefSectionResponse) => {
        startEdit(section.number, section.body);
    };

    return (
        <div className="mx-auto flex max-w-3xl flex-col gap-4">
            <div>
                <div className="flex items-center gap-3">
                    <h2 className="font-mono text-xl font-bold tracking-tight">{ref.name}</h2>
                    <DomainBadge domain={ref.domain} />
                </div>
                <p className="mt-1.5 text-sm italic text-muted-foreground">{ref.summary}</p>
                <div className="mt-3 flex flex-col gap-1.5">
                    <ConnectionChips title="references" ids={references} onOpen={openRef} />
                    <ConnectionChips title="referenced by" ids={referencedBy} onOpen={openRef} />
                    <ConnectionChips title="instantiated by" ids={instantiatedBy} />
                </div>
            </div>

            {lastReport && <ValidationBanner report={lastReport} />}

            {ref.sections.map((section) =>
                editingSection === section.number ? (
                    <section
                        key={section.number}
                        className="rounded-lg border border-primary/50 bg-secondary/30 p-4"
                    >
                        <h3 className="text-sm font-semibold">
                            <span className="mr-1.5 text-primary">§{section.number}</span>
                            {section.title}
                        </h3>
                        <textarea
                            className="mt-3 h-72 w-full rounded-md border border-input bg-background/80 p-3 font-mono text-xs leading-relaxed text-foreground outline-none focus:ring-1 focus:ring-ring"
                            value={draft}
                            onChange={(event) => setDraft(event.target.value)}
                        />
                        {saveError && <p className="mt-1 text-xs text-destructive">{saveError}</p>}
                        <div className="mt-3 flex gap-2">
                            <Button disabled={saving} onClick={() => void save()}>
                                {saving ? 'Validating...' : 'Save (runs gates)'}
                            </Button>
                            <Button variant="outline" disabled={saving} onClick={cancelEdit}>
                                Cancel
                            </Button>
                        </div>
                    </section>
                ) : (
                    <section
                        key={section.number}
                        className="group rounded-lg border bg-card/60 p-4"
                    >
                        <div className="flex items-center justify-between gap-2">
                            <h3 className="text-sm font-semibold">
                                <span className="mr-1.5 text-primary">§{section.number}</span>
                                {section.title}
                            </h3>
                            {section.generated ? (
                                <span
                                    className="rounded-full border border-border px-2 py-0.5 text-[10px] uppercase tracking-wider text-muted-foreground"
                                    title="Maintained by scripts/sync_backlinks.py; edit skill frontmatter instead."
                                >
                                    generated
                                </span>
                            ) : (
                                <Button
                                    variant="outline"
                                    className="h-6 px-2.5 text-xs opacity-0 transition-opacity group-hover:opacity-100"
                                    onClick={() => onEdit(section)}
                                >
                                    Edit
                                </Button>
                            )}
                        </div>
                        <div className="mt-2">
                            <Markdown>{section.body}</Markdown>
                        </div>
                    </section>
                ),
            )}
        </div>
    );
};
