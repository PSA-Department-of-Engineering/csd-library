import type { RefSectionResponse } from '@/models';
import { Button } from '@/components/ui/button';

export interface SectionCardProps {
    section: RefSectionResponse;
    onEdit: (section: RefSectionResponse) => void;
}

export const SectionCard = ({ section, onEdit }: SectionCardProps) => (
    <div className="rounded-lg border bg-secondary/40 p-3.5">
        <div className="flex items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-foreground">
                <span className="mr-1.5 text-primary">§{section.number}</span>
                {section.title}
            </h3>
            {section.generated ? (
                <span className="rounded-full border border-border px-2 py-0.5 text-[10px] uppercase tracking-wider text-muted-foreground">
                    generated
                </span>
            ) : (
                <Button
                    variant="ghost"
                    className="h-6 px-2 text-xs text-primary"
                    onClick={() => onEdit(section)}
                >
                    Edit
                </Button>
            )}
        </div>
        <pre className="mt-2 max-h-56 overflow-auto whitespace-pre-wrap font-sans text-xs leading-relaxed text-muted-foreground">
            {section.body}
        </pre>
    </div>
);
