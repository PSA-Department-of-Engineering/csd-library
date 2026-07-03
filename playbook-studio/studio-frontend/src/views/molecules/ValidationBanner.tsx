import type { ValidationReportResponse } from '@/models';
import { cn } from '@/utils';

export interface ValidationBannerProps {
    report: ValidationReportResponse;
}

export const ValidationBanner = ({ report }: ValidationBannerProps) => (
    <div
        className={cn(
            'rounded-md border p-3 text-sm',
            report.ok
                ? 'border-emerald-300 bg-emerald-50 text-emerald-900'
                : 'border-rose-300 bg-rose-50 text-rose-900',
        )}
    >
        <p className="font-semibold">
            {report.ok ? 'Validation gates passed' : 'Validation gates failed'}
        </p>
        <p className="mt-1 text-xs">
            intent tests: {report.tests_passed ? 'pass' : 'FAIL'} · link check:{' '}
            {report.links_ok ? 'pass' : 'FAIL'}
        </p>
        {!report.ok && (
            <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap text-xs">
                {report.tests_passed ? report.links_output : report.tests_output}
            </pre>
        )}
    </div>
);
