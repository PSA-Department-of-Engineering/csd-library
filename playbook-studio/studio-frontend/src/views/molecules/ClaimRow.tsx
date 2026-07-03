import type { IntentClaimResponse } from '@/models';
import { cn } from '@/utils';

export interface ClaimRowProps {
    claim: IntentClaimResponse;
}

const CRITICALITY_CLASSES: Record<string, string> = {
    critical: 'bg-rose-100 text-rose-800',
    high: 'bg-amber-100 text-amber-800',
    medium: 'bg-sky-100 text-sky-800',
    low: 'bg-slate-100 text-slate-600',
};

export const ClaimRow = ({ claim }: ClaimRowProps) => (
    <li className="rounded-md border border-slate-200 p-2.5">
        <div className="flex items-center gap-2">
            <code className="text-xs font-semibold">{claim.claim_id}</code>
            <span
                className={cn(
                    'rounded px-1.5 py-0.5 text-[10px] font-medium uppercase',
                    CRITICALITY_CLASSES[claim.criticality] ?? CRITICALITY_CLASSES.low,
                )}
            >
                {claim.criticality}
            </span>
        </div>
        <p className="mt-1 text-xs text-slate-700">{claim.statement}</p>
    </li>
);
