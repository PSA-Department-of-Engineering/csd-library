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
        return <p className="text-sm text-rose-700">{error}</p>;
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
                <div className="flex items-center gap-2">
                    <h2 className="text-base font-bold">{ref.name}</h2>
                    <DomainBadge domain={ref.domain} />
                </div>
                <p className="mt-1 text-xs italic text-slate-600">{ref.summary}</p>
            </div>
            {lastReport && <ValidationBanner report={lastReport} />}
            {ref.sections.map((section) =>
                editingSection === section.number ? (
                    <div key={section.number} className="rounded-md border border-sky-300 p-3">
                        <h3 className="text-sm font-semibold">
                            §{section.number}. {section.title}
                        </h3>
                        <textarea
                            className="mt-2 h-56 w-full rounded border border-slate-300 p-2 font-mono text-xs"
                            value={draft}
                            onChange={(event) => setDraft(event.target.value)}
                        />
                        {saveError && <p className="mt-1 text-xs text-rose-700">{saveError}</p>}
                        <div className="mt-2 flex gap-2">
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
