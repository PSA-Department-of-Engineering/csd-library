import { useEffect } from 'react';

import type { RefSectionResponse } from '@/models';
import { Button } from '@/components/ui/button';
import { useGraph } from '@/viewmodels/graph';
import { useRefDetail } from '@/viewmodels/refdetail';
import { DomainBadge } from '@/views/atoms/DomainBadge';
import { Spinner } from '@/views/atoms/Spinner';
import { SectionCard } from '@/views/molecules/SectionCard';
import { ValidationBanner } from '@/views/molecules/ValidationBanner';

export const RefDetailPanel = () => {
    const selectedRef = useGraph((state) => state.selectedRef);
    const ref = useRefDetail((state) => state.ref);
    const loading = useRefDetail((state) => state.loading);
    const error = useRefDetail((state) => state.error);
    const editingSection = useRefDetail((state) => state.editingSection);
    const draft = useRefDetail((state) => state.draft);
    const saving = useRefDetail((state) => state.saving);
    const saveError = useRefDetail((state) => state.saveError);
    const lastReport = useRefDetail((state) => state.lastReport);
    const load = useRefDetail((state) => state.load);
    const clear = useRefDetail((state) => state.clear);
    const startEdit = useRefDetail((state) => state.startEdit);
    const setDraft = useRefDetail((state) => state.setDraft);
    const cancelEdit = useRefDetail((state) => state.cancelEdit);
    const save = useRefDetail((state) => state.save);

    useEffect(() => {
        if (selectedRef !== null) {
            void load(selectedRef);
        } else {
            clear();
        }
    }, [selectedRef, load, clear]);

    if (loading) {
        return <Spinner />;
    }
    if (error) {
        return <p className="text-sm text-destructive">{error}</p>;
    }
    if (!ref) {
        return null;
    }

    const onEdit = (section: RefSectionResponse) => {
        startEdit(section.number, section.body);
    };

    return (
        <div className="flex flex-col gap-3">
            <div>
                <div className="flex items-center gap-2.5">
                    <h2 className="font-mono text-base font-bold tracking-tight">{ref.name}</h2>
                    <DomainBadge domain={ref.domain} />
                </div>
                <p className="mt-1.5 text-xs italic leading-relaxed text-muted-foreground">
                    {ref.summary}
                </p>
            </div>
            {lastReport && <ValidationBanner report={lastReport} />}
            {ref.sections.map((section) =>
                editingSection === section.number ? (
                    <div
                        key={section.number}
                        className="rounded-lg border border-primary/50 bg-secondary/40 p-3.5"
                    >
                        <h3 className="text-sm font-semibold">
                            <span className="mr-1.5 text-primary">§{section.number}</span>
                            {section.title}
                        </h3>
                        <textarea
                            className="mt-2 h-56 w-full rounded-md border border-input bg-background/80 p-2.5 font-mono text-xs leading-relaxed text-foreground outline-none focus:ring-1 focus:ring-ring"
                            value={draft}
                            onChange={(event) => setDraft(event.target.value)}
                        />
                        {saveError && <p className="mt-1 text-xs text-destructive">{saveError}</p>}
                        <div className="mt-2.5 flex gap-2">
                            <Button disabled={saving} onClick={() => void save()}>
                                {saving ? 'Validating...' : 'Save (runs gates)'}
                            </Button>
                            <Button variant="outline" disabled={saving} onClick={cancelEdit}>
                                Cancel
                            </Button>
                        </div>
                    </div>
                ) : (
                    <SectionCard key={section.number} section={section} onEdit={onEdit} />
                ),
            )}
        </div>
    );
};
