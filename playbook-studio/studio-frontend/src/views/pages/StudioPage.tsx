import { Card, CardContent } from '@/components/ui/card';
import { useNav } from '@/viewmodels/nav';
import { CreateRefForm } from '@/views/organisms/CreateRefForm';
import { GovernanceRail } from '@/views/organisms/GovernanceRail';
import { PlaybookGraph } from '@/views/organisms/PlaybookGraph';
import { PlaybookReader } from '@/views/organisms/PlaybookReader';
import { RefReader } from '@/views/organisms/RefReader';
import { SidebarNav } from '@/views/organisms/SidebarNav';

export const StudioPage = () => {
    const view = useNav((state) => state.view);

    return (
        <div className="grid h-[calc(100vh-6.5rem)] grid-cols-[230px_minmax(0,1fr)] grid-rows-[minmax(0,1fr)] gap-4">
            <Card className="min-h-0 overflow-hidden">
                <CardContent className="h-full p-3 pt-3">
                    <SidebarNav />
                </CardContent>
            </Card>

            {view === 'map' && (
                <div className="flex min-h-0 min-w-0 gap-4">
                    <Card className="relative min-w-0 flex-1 overflow-hidden">
                        <div className="absolute inset-0 p-1">
                            <PlaybookGraph />
                        </div>
                    </Card>
                    <div className="min-h-0 w-[360px] shrink-0">
                        <GovernanceRail />
                    </div>
                </div>
            )}
            {view === 'playbook' && (
                <div className="min-h-0 min-w-0 overflow-y-auto pr-1">
                    <PlaybookReader />
                </div>
            )}
            {view === 'ref' && (
                <div className="min-h-0 min-w-0 overflow-y-auto pr-1">
                    <RefReader />
                </div>
            )}
            {view === 'create' && (
                <div className="min-h-0 min-w-0 overflow-y-auto pr-1">
                    <CreateRefForm />
                </div>
            )}
        </div>
    );
};
