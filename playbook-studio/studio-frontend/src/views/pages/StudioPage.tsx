import { Card, CardContent } from '@/components/ui/card';
import { DOMAIN_ORDER, useGraph } from '@/viewmodels/graph';
import { DomainBadge } from '@/views/atoms/DomainBadge';
import { ClaimsPanel } from '@/views/organisms/ClaimsPanel';
import { PlaybookGraph } from '@/views/organisms/PlaybookGraph';
import { RefDetailPanel } from '@/views/organisms/RefDetailPanel';

export const StudioPage = () => {
    const selectedRef = useGraph((state) => state.selectedRef);

    return (
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
            <Card className="lg:col-span-2">
                <CardContent className="p-3">
                    <div className="flex flex-wrap gap-1.5 px-1.5 pt-1.5">
                        {DOMAIN_ORDER.map((domain) => (
                            <DomainBadge key={domain} domain={domain} />
                        ))}
                    </div>
                    <div className="aspect-square w-full">
                        <PlaybookGraph />
                    </div>
                </CardContent>
            </Card>
            <Card className="max-h-[85vh] overflow-y-auto">
                <CardContent className="p-4 pt-4">
                    {selectedRef ? <RefDetailPanel /> : <ClaimsPanel />}
                </CardContent>
            </Card>
        </div>
    );
};
