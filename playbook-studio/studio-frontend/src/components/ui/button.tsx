import type { ButtonHTMLAttributes } from 'react';

import { cn } from '@/utils';

export type ButtonVariant = 'default' | 'outline' | 'ghost';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: ButtonVariant;
}

const VARIANT_CLASSES: Record<ButtonVariant, string> = {
    default: 'bg-slate-900 text-white hover:bg-slate-700',
    outline: 'border border-slate-300 bg-white hover:bg-slate-100',
    ghost: 'hover:bg-slate-100',
};

export const Button = ({ className, variant = 'default', ...props }: ButtonProps) => (
    <button
        className={cn(
            'inline-flex items-center justify-center rounded-md px-3 py-1.5 text-sm font-medium',
            'transition-colors disabled:pointer-events-none disabled:opacity-50',
            VARIANT_CLASSES[variant],
            className,
        )}
        {...props}
    />
);
