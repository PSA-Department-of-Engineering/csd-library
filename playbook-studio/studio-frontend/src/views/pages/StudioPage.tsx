import { Card, CardContent } from '@/components/ui/card';
import { useNav } from '@/viewmodels/nav';
import { GovernanceRail } from '@/views/organisms/GovernanceRail';
import { PlaybookGraph } from '@/views/organisms/PlaybookGraph';
import { PlaybookReader } from '@/views/organisms/PlaybookReader';
import { RefReader } from '@/views/organisms/RefReader';
import { SidebarNav } from '@/views/organisms/SidebarNav';

export const StudioPage = () => {
    const view = useNav((state) => state.view);

    return (
        <div className="grid h-[calc(100vh-6.5rem)] grid-cols-[230px_minmax(0,1fr)] gap-4">
            <Card className="overflow-hidden">
                <CardContent className="h-full p-3 pt-3">
                    <SidebarNav />
                </CardContent>
            </Card>

            {view === 'map' && (
                <div className="flex min-h-0 min-w-0 gap-4">
                    <Card className="relative min-w-0 flex-1 overflow-hidden">
                        <CardContent className="h-full p-1 pt-1">
                            <PlaybookGraph />
                        </CardContent>
                    </Card>
                    <div className="w-[360px] shrink-0">
                        <GovernanceRail />
                    </div>
                </div>
            )}
            {view === 'playbook' && (
                <div className="min-w-0 overflow-y-auto pr-1">
                    <PlaybookReader />
                </div>
            )}
            {view === 'ref' && (
                <div className="min-w-0 overflow-y-auto pr-1">
                    <RefReader />
                </div>
            )}
        </div>
    );
};
