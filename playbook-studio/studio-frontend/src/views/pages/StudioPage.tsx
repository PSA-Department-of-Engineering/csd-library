import { Card, CardContent } from '@/components/ui/card';
import { useNav } from '@/viewmodels/nav';
import { CreateRefForm } from '@/views/organisms/CreateRefForm';
import { CreateSkillForm } from '@/views/organisms/CreateSkillForm';
import { GovernanceRail } from '@/views/organisms/GovernanceRail';
import { MapFilters } from '@/views/molecules/MapFilters';
import { PlaybookGraph } from '@/views/organisms/PlaybookGraph';
import { PlaybookReader } from '@/views/organisms/PlaybookReader';
import { RefReader } from '@/views/organisms/RefReader';
import { SidebarNav } from '@/views/organisms/SidebarNav';
import { SkillReader } from '@/views/organisms/SkillReader';

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
                        <div className="absolute left-3 top-3 z-10 max-w-[70%]">
                            <MapFilters />
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
            {view === 'skill' && (
                <div className="min-h-0 min-w-0 overflow-y-auto pr-1">
                    <SkillReader />
                </div>
            )}
            {view === 'create' && (
                <div className="min-h-0 min-w-0 overflow-y-auto pr-1">
                    <CreateRefForm />
                </div>
            )}
            {view === 'createskill' && (
                <div className="min-h-0 min-w-0 overflow-y-auto pr-1">
                    <CreateSkillForm />
                </div>
            )}
        </div>
    );
};
