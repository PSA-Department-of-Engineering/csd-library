import type { ReactNode } from 'react';

export interface MainLayoutProps {
    children: ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => (
    <div className="min-h-screen">
        <header className="sticky top-0 z-10 border-b border-border/70 bg-background/80 backdrop-blur">
            <div className="mx-auto flex max-w-7xl items-center gap-3 px-6 py-3.5">
                <span className="relative flex h-2.5 w-2.5">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-40" />
                    <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-primary" />
                </span>
                <h1 className="text-base font-semibold tracking-tight">Playbook Studio</h1>
                <p className="ml-auto hidden text-xs text-muted-foreground sm:block">
                    edits survive only if the intent gates pass
                </p>
            </div>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-6">{children}</main>
    </div>
);
