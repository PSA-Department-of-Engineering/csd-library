import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { cn } from '@/utils';

export interface MarkdownProps {
    children: string;
    className?: string;
}

/** Playbook markdown, styled for the dark theme. */
export const Markdown = ({ children, className }: MarkdownProps) => (
    <div
        className={cn(
            'prose prose-sm prose-invert max-w-none',
            'prose-headings:text-foreground prose-p:text-muted-foreground',
            'prose-li:text-muted-foreground prose-strong:text-foreground',
            'prose-code:rounded prose-code:bg-secondary prose-code:px-1 prose-code:py-0.5',
            'prose-code:font-mono prose-code:text-[0.8em] prose-code:text-primary',
            'prose-code:before:content-none prose-code:after:content-none',
            'prose-pre:border prose-pre:bg-secondary/60',
            'prose-table:text-xs prose-th:text-foreground prose-td:text-muted-foreground',
            'prose-a:text-primary prose-blockquote:border-l-primary/50',
            'prose-blockquote:text-muted-foreground',
            className,
        )}
    >
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </div>
);
