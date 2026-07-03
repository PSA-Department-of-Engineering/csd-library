import type { ReactNode } from 'react';

import { useNav } from '@/viewmodels/nav';
import { useTheme } from '@/viewmodels/theme';
import { cn } from '@/utils';

export interface MainLayoutProps {
    children: ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => {
    const view = useNav((state) => state.view);
    const setView = useNav((state) => state.setView);
    const mode = useTheme((state) => state.mode);
    const toggleTheme = useTheme((state) => state.toggle);

    const tab = (target: 'map' | 'playbook', label: string) => (
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
                        {tab('map', 'Map')}
                        {tab('playbook', 'Playbook')}
                    </nav>
                    <div className="ml-auto flex items-center gap-3">
                        <p className="hidden text-xs text-muted-foreground lg:block">
                            edits survive only if the intent gates pass
                        </p>
                        <button
                            onClick={toggleTheme}
                            title="Toggle light/dark theme"
                            className="rounded-md border border-border px-2 py-1 text-xs text-muted-foreground hover:text-foreground"
                        >
                            {mode === 'dark' ? 'Light' : 'Dark'}
                        </button>
                    </div>
                </div>
            </header>
            <main className="flex-1 px-5 py-4">{children}</main>
        </div>
    );
};
