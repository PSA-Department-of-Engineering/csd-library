import { useEffect } from 'react';

import { Button } from '@/components/ui/button';
import { useGraph } from '@/viewmodels/graph';
import { useNav } from '@/viewmodels/nav';
import { useSkillDetail } from '@/viewmodels/skilldetail';
import { Spinner } from '@/views/atoms/Spinner';
import { Markdown } from '@/views/molecules/Markdown';
import { ValidationBanner } from '@/views/molecules/ValidationBanner';

const shortName = (id: string): string => id.replace(/^REF-/, '');

export const SkillReader = () => {
    const selectedSkill = useSkillDetail((state) => state.selectedSkill);
    const skill = useSkillDetail((state) => state.skill);
    const loading = useSkillDetail((state) => state.loading);
    const error = useSkillDetail((state) => state.error);
    const editing = useSkillDetail((state) => state.editing);
    const draft = useSkillDetail((state) => state.draft);
    const saving = useSkillDetail((state) => state.saving);
    const saveError = useSkillDetail((state) => state.saveError);
    const lastReport = useSkillDetail((state) => state.lastReport);
    const load = useSkillDetail((state) => state.load);
    const startEdit = useSkillDetail((state) => state.startEdit);
    const setDraft = useSkillDetail((state) => state.setDraft);
    const cancelEdit = useSkillDetail((state) => state.cancelEdit);
    const save = useSkillDetail((state) => state.save);
    const selectRef = useGraph((state) => state.select);
    const setView = useNav((state) => state.setView);

    useEffect(() => {
        if (selectedSkill !== null) {
            void load(selectedSkill);
        }
    }, [selectedSkill, load]);

    if (selectedSkill === null) {
        return <p className="text-sm text-muted-foreground">Pick a skill from the sidebar.</p>;
    }
    if (loading) {
        return <Spinner />;
    }
    if (error) {
        return <p className="text-sm text-destructive">{error}</p>;
    }
    if (!skill) {
        return null;
    }

    if (editing) {
        return (
            <div className="mx-auto flex max-w-5xl flex-col gap-3">
                <div className="flex items-center gap-3">
                    <h2 className="font-mono text-xl font-bold tracking-tight">{skill.name}</h2>
                    <span className="text-xs text-muted-foreground">
                        whole SKILL.md, frontmatter included; the gates enforce table and back-link
                        consistency
                    </span>
                </div>
                {lastReport && !lastReport.ok && <ValidationBanner report={lastReport} />}
                <textarea
                    className="h-[65vh] w-full rounded-md border border-input bg-background/80 p-4 font-mono text-xs leading-relaxed text-foreground outline-none focus:ring-1 focus:ring-ring"
                    value={draft}
                    onChange={(event) => setDraft(event.target.value)}
                    spellCheck={false}
                />
                {saveError && <p className="text-xs text-destructive">{saveError}</p>}
                <div className="flex gap-2">
                    <Button disabled={saving} onClick={() => void save()}>
                        {saving ? 'Validating...' : 'Save (runs gates)'}
                    </Button>
                    <Button variant="outline" disabled={saving} onClick={cancelEdit}>
                        Cancel
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="mx-auto flex max-w-3xl flex-col gap-4">
            <div>
                <div className="flex items-center justify-between gap-3">
                    <h2 className="font-mono text-xl font-bold tracking-tight">{skill.name}</h2>
                    <Button variant="outline" onClick={startEdit}>
                        Edit SKILL.md
                    </Button>
                </div>
                <p className="mt-1.5 text-sm italic text-muted-foreground">{skill.description}</p>
                {skill.refs.length > 0 && (
                    <div className="mt-2 flex flex-wrap items-baseline gap-1.5">
                        <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground/70">
                            instantiates
                        </span>
                        {skill.refs.map((refId) => (
                            <button
                                key={refId}
                                onClick={() => {
                                    selectRef(refId);
                                    setView('ref');
                                }}
                                className="rounded-full border border-border bg-secondary/60 px-2 py-0.5 text-[11px] text-foreground hover:border-primary/60 hover:text-primary"
                            >
                                {shortName(refId)}
                            </button>
                        ))}
                    </div>
                )}
            </div>
            {lastReport && <ValidationBanner report={lastReport} />}
            <div className="rounded-lg border bg-card/60 p-4">
                <Markdown>{skill.body}</Markdown>
            </div>
        </div>
    );
};
