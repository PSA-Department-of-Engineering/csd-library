import type { PlaybookResponse, PlaybookSectionResponse } from '@/models';

/** The governance section every session must check; pinned first in the UI. */
export const selectViolationsSection = (
    doc: PlaybookResponse | null,
): PlaybookSectionResponse | null =>
    doc?.sections.find((s) => s.title.toLowerCase().startsWith('top violations')) ?? null;

export const selectOtherSections = (doc: PlaybookResponse | null): PlaybookSectionResponse[] =>
    doc?.sections.filter((s) => !s.title.toLowerCase().startsWith('top violations')) ?? [];
