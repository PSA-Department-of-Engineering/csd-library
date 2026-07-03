import { useEffect } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useClaims } from '@/viewmodels/claims';
import { selectOtherSections, selectViolationsSection, usePlaybook } from '@/viewmodels/playbook';
import { Spinner } from '@/views/atoms/Spinner';
import { ClaimRow } from '@/views/molecules/ClaimRow';
import { Markdown } from '@/views/molecules/Markdown';
import { ValidationBanner } from '@/views/molecules/ValidationBanner';

export const PlaybookOverview = () => {
    const doc = usePlaybook((state) => state.doc);
    const loading = usePlaybook((state) => state.loading);
    const error = usePlaybook((state) => state.error);
    const load = usePlaybook((state) => state.load);
    const claims = useClaims((state) => state.claims);
    const claimsLoad = useClaims((state) => state.load);
    const validating = useClaims((state) => state.validating);
    const report = useClaims((state) => state.report);
    const validate = useClaims((state) => state.validate);

    useEffect(() => {
        void load();
        void claimsLoad();
    }, [load, claimsLoad]);

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
        <div className="mx-auto flex max-w-3xl flex-col gap-4">
            <Card>
                <CardContent className="flex items-center justify-between gap-4 p-4 pt-4">
                    <div>
                        <h2 className="text-lg font-bold tracking-tight">{doc.title}</h2>
                        <p className="mt-0.5 text-xs text-muted-foreground">
                            {claims.length} intent claims guard this playbook. Every edit made here
                            re-runs them.
                        </p>
                    </div>
                    <Button disabled={validating} onClick={() => void validate()}>
                        {validating ? 'Running gates...' : 'Run validation'}
                    </Button>
                </CardContent>
            </Card>
            {report && <ValidationBanner report={report} />}

            {violations && (
                <Card className="border-amber-500/40">
                    <CardContent className="p-4 pt-4">
                        <h3 className="mb-2 text-sm font-bold uppercase tracking-wider text-amber-300">
                            {violations.title}
                        </h3>
                        <Markdown>{violations.body}</Markdown>
                    </CardContent>
                </Card>
            )}

            {others.map((section) => (
                <Card key={section.title}>
                    <CardContent className="p-4 pt-4">
                        <details open={section.title.startsWith('Task Routing')}>
                            <summary className="cursor-pointer select-none text-sm font-semibold text-foreground marker:text-primary">
                                {section.title}
                            </summary>
                            <div className="mt-2">
                                <Markdown>{section.body}</Markdown>
                            </div>
                        </details>
                    </CardContent>
                </Card>
            ))}

            <Card>
                <CardContent className="p-4 pt-4">
                    <details>
                        <summary className="cursor-pointer select-none text-sm font-semibold text-foreground marker:text-primary">
                            Intent claims ({claims.length})
                        </summary>
                        <ul className="mt-3 flex flex-col gap-2">
                            {claims.map((claim) => (
                                <ClaimRow key={claim.claim_id} claim={claim} />
                            ))}
                        </ul>
                    </details>
                </CardContent>
            </Card>
        </div>
    );
};
