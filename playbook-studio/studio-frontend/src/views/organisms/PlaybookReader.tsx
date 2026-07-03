import { useEffect } from 'react';

import { selectOtherSections, selectViolationsSection, usePlaybook } from '@/viewmodels/playbook';
import { Spinner } from '@/views/atoms/Spinner';
import { Markdown } from '@/views/molecules/Markdown';

/** The AI-PLAYBOOK.md document itself, violations pinned first. */
export const PlaybookReader = () => {
    const doc = usePlaybook((state) => state.doc);
    const loading = usePlaybook((state) => state.loading);
    const error = usePlaybook((state) => state.error);
    const load = usePlaybook((state) => state.load);

    useEffect(() => {
        void load();
    }, [load]);

    if (loading && !doc) {
        return <Spinner />;
    }
    if (error) {
        return <p className="text-sm text-destructive">{error}</p>;
    }
    if (!doc) {
        return null;
    }

    const violations = selectViolationsSection(doc);
    const others = selectOtherSections(doc);

    return (
        <div className="mx-auto flex max-w-4xl flex-col gap-4">
            <h2 className="text-xl font-bold tracking-tight">{doc.title}</h2>

            {violations && (
                <section className="rounded-lg border border-amber-500/40 bg-amber-500/5 p-4">
                    <h3 className="mb-2 text-sm font-bold uppercase tracking-wider text-amber-300">
                        {violations.title}
                    </h3>
                    <Markdown>{violations.body}</Markdown>
                </section>
            )}

            {others.map((section) => (
                <section key={section.title} className="rounded-lg border bg-card/60 p-4">
                    <h3 className="mb-2 text-sm font-semibold">{section.title}</h3>
                    <Markdown>{section.body}</Markdown>
                </section>
            ))}
        </div>
    );
};
