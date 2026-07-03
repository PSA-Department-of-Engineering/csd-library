import type { ReactNode } from 'react';

import { useNav } from '@/viewmodels/nav';
import { cn } from '@/utils';

export interface MainLayoutProps {
    children: ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => {
    const view = useNav((state) => state.view);
    const setView = useNav((state) => state.setView);

    const tab = (target: 'library' | 'map' | 'playbook', label: string) => (
        <button
            onClick={() => setView(target)}
            className={cn(
                'rounded-md px-3 py-1 text-sm font-medium transition-colors',
                view === target
                    ? 'bg-secondary text-foreground'
                    : 'text-muted-foreground hover:text-foreground',
            )}
        >
            {label}
        </button>
    );

    return (
        <div className="flex min-h-screen flex-col">
            <header className="sticky top-0 z-10 border-b border-border/70 bg-background/85 backdrop-blur">
                <div className="flex items-center gap-4 px-5 py-2.5">
                    <div className="flex items-center gap-2.5">
                        <span className="relative flex h-2.5 w-2.5">
                            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-40" />
                            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-primary" />
                        </span>
                        <h1 className="text-base font-semibold tracking-tight">Playbook Studio</h1>
                    </div>
                    <nav className="flex items-center gap-1">
                        {tab('library', 'Library')}
                        {tab('map', 'Map')}
                        {tab('playbook', 'Playbook')}
                    </nav>
                    <p className="ml-auto hidden text-xs text-muted-foreground lg:block">
                        edits survive only if the intent gates pass
                    </p>
                </div>
            </header>
            <main className="flex-1 px-5 py-4">{children}</main>
        </div>
    );
};
