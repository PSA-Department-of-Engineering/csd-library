import { useEffect } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useClaims } from '@/viewmodels/claims';
import { selectViolationsSection, usePlaybook } from '@/viewmodels/playbook';
import { ClaimRow } from '@/views/molecules/ClaimRow';
import { Markdown } from '@/views/molecules/Markdown';
import { ValidationBanner } from '@/views/molecules/ValidationBanner';

/** Governance beside the map: health, top violations, claims. Always visible. */
export const GovernanceRail = () => {
    const doc = usePlaybook((state) => state.doc);
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

    const violations = selectViolationsSection(doc);

    return (
        <div className="flex h-full flex-col gap-3 overflow-y-auto pr-1">
            <Card>
                <CardContent className="flex items-center justify-between gap-3 p-3.5 pt-3.5">
                    <div>
                        <p className="text-sm font-semibold">Gates</p>
                        <p className="text-[11px] text-muted-foreground">
                            intent tests + link checker
                        </p>
                    </div>
                    <Button disabled={validating} onClick={() => void validate()}>
                        {validating ? 'Running...' : 'Run validation'}
                    </Button>
                </CardContent>
            </Card>
            {report && <ValidationBanner report={report} />}

            {violations && (
                <Card className="border-amber-500/40">
                    <CardContent className="p-3.5 pt-3.5">
                        <h3 className="mb-2 text-xs font-bold uppercase tracking-wider text-amber-300">
                            Top violations - check every change
                        </h3>
                        <Markdown className="prose-p:text-xs prose-li:text-xs">
                            {violations.body}
                        </Markdown>
                    </CardContent>
                </Card>
            )}

            <Card>
                <CardContent className="p-3.5 pt-3.5">
                    <details>
                        <summary className="cursor-pointer select-none text-sm font-semibold marker:text-primary">
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
