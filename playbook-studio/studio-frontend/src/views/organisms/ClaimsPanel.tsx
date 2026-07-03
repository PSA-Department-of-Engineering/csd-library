import { useEffect } from 'react';

import { Button } from '@/components/ui/button';
import { useClaims } from '@/viewmodels/claims';
import { Spinner } from '@/views/atoms/Spinner';
import { ClaimRow } from '@/views/molecules/ClaimRow';
import { ValidationBanner } from '@/views/molecules/ValidationBanner';

export const ClaimsPanel = () => {
    const claims = useClaims((state) => state.claims);
    const loading = useClaims((state) => state.loading);
    const error = useClaims((state) => state.error);
    const validating = useClaims((state) => state.validating);
    const report = useClaims((state) => state.report);
    const load = useClaims((state) => state.load);
    const validate = useClaims((state) => state.validate);

    useEffect(() => {
        void load();
    }, [load]);

    return (
        <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
                <h2 className="text-base font-bold">Intent claims</h2>
                <Button disabled={validating} onClick={() => void validate()}>
                    {validating ? 'Running gates...' : 'Run validation'}
                </Button>
            </div>
            {report && <ValidationBanner report={report} />}
            {error && <p className="text-sm text-rose-700">{error}</p>}
            {loading ? (
                <Spinner />
            ) : (
                <ul className="flex flex-col gap-2">
                    {claims.map((claim) => (
                        <ClaimRow key={claim.claim_id} claim={claim} />
                    ))}
                </ul>
            )}
            <p className="text-xs text-slate-500">
                Select a REF in the graph to inspect and edit it. Edits only survive if the
                playbook's intent tests and link checker still pass.
            </p>
        </div>
    );
};
