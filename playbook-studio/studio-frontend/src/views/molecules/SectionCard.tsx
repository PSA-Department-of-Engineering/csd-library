import type { RefSectionResponse } from '@/models';
import { Button } from '@/components/ui/button';

export interface SectionCardProps {
    section: RefSectionResponse;
    onEdit: (section: RefSectionResponse) => void;
}

export const SectionCard = ({ section, onEdit }: SectionCardProps) => (
    <div className="rounded-md border border-slate-200 p-3">
        <div className="flex items-center justify-between gap-2">
            <h3 className="text-sm font-semibold">
                §{section.number}. {section.title}
            </h3>
            {section.generated ? (
                <span className="rounded bg-slate-200 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-slate-600">
                    generated
                </span>
            ) : (
                <Button
                    variant="ghost"
                    className="h-6 px-2 text-xs"
                    onClick={() => onEdit(section)}
                >
                    Edit
                </Button>
            )}
        </div>
        <pre className="mt-2 max-h-56 overflow-auto whitespace-pre-wrap font-sans text-xs text-slate-700">
            {section.body}
        </pre>
    </div>
);
