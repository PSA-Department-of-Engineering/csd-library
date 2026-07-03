import type { PlaybookResponse } from '@/models';

export interface PlaybookState {
    doc: PlaybookResponse | null;
    loading: boolean;
    error: string | null;
}
