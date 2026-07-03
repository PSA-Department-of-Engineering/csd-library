import { Card, CardContent } from '@/components/ui/card';
import { DOMAIN_ORDER } from '@/viewmodels/graph';
import { useNav } from '@/viewmodels/nav';
import { DomainBadge } from '@/views/atoms/DomainBadge';
import { PlaybookGraph } from '@/views/organisms/PlaybookGraph';
import { PlaybookOverview } from '@/views/organisms/PlaybookOverview';
import { RefReader } from '@/views/organisms/RefReader';
import { SidebarNav } from '@/views/organisms/SidebarNav';

export const StudioPage = () => {
    const view = useNav((state) => state.view);

    return (
        <div className="grid h-[calc(100vh-7rem)] grid-cols-[240px_minmax(0,1fr)] gap-4">
            <Card className="overflow-hidden">
                <CardContent className="h-full p-3 pt-3">
                    <SidebarNav />
                </CardContent>
            </Card>
            <div className="overflow-y-auto pr-1">
                {view === 'overview' && <PlaybookOverview />}
                {view === 'ref' && <RefReader />}
                {view === 'map' && (
                    <Card className="relative h-full">
                        <CardContent className="h-full p-2 pt-2">
                            <div className="absolute left-4 top-3 z-10 flex flex-wrap gap-1.5">
                                {DOMAIN_ORDER.map((domain) => (
                                    <DomainBadge key={domain} domain={domain} />
                                ))}
                            </div>
                            <PlaybookGraph />
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
};
