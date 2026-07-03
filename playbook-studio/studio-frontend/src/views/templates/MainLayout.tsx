import type { ReactNode } from 'react';

export interface MainLayoutProps {
    children: ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => (
    <div className="min-h-screen bg-background text-foreground">
        <header className="border-b">
            <div className="mx-auto max-w-7xl px-4 py-3">
                <h1 className="text-lg font-semibold">Playbook Studio</h1>
            </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-4">{children}</main>
    </div>
);
