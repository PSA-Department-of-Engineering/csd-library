import { create } from 'zustand';

import type { RefDetailResponse, ValidationReportResponse } from '@/models';
import { apiFetch } from '@/utils';

import type { RefDetailState } from './refdetail.state';

interface RefDetailActions {
    load: (name: string) => Promise<void>;
    clear: () => void;
    startEdit: (sectionNumber: number, body: string) => void;
    setDraft: (draft: string) => void;
    cancelEdit: () => void;
    save: () => Promise<void>;
}

interface GateRejection {
    detail?: string;
    report?: ValidationReportResponse;
}

/** PUT that surfaces the validation report carried by a 422 rejection. */
async function putSection(
    refName: string,
    sectionNumber: number,
    body: string,
): Promise<{ report: ValidationReportResponse | null; error: string | null }> {
    const response = await fetch(`/api/refs/${refName}/sections/${sectionNumber}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ body }),
    });
    if (response.ok) {
        return { report: (await response.json()) as ValidationReportResponse, error: null };
    }
    let rejection: GateRejection = {};
    try {
        rejection = (await response.json()) as GateRejection;
    } catch {
        // Non-JSON error body; fall through to the status text.
    }
    return {
        report: rejection.report ?? null,
        error: rejection.detail ?? `${response.status} ${response.statusText}`,
    };
}

export const useRefDetail = create<RefDetailState & RefDetailActions>()((set, get) => ({
    ref: null,
    loading: false,
    error: null,
    editingSection: null,
    draft: '',
    saving: false,
    saveError: null,
    lastReport: null,

    load: async (name) => {
        set({ loading: true, error: null, editingSection: null, saveError: null });
        try {
            const ref = await apiFetch<RefDetailResponse>(`/api/refs/${name}`);
            set({ ref });
        } catch (err) {
            set({ error: err instanceof Error ? err.message : 'Failed to load REF' });
        } finally {
            set({ loading: false });
        }
    },

    clear: () => {
        set({ ref: null, editingSection: null, saveError: null, lastReport: null });
    },

    startEdit: (sectionNumber, body) => {
        set({ editingSection: sectionNumber, draft: body, saveError: null });
    },

    setDraft: (draft) => {
        set({ draft });
    },

    cancelEdit: () => {
        set({ editingSection: null, draft: '', saveError: null });
    },

    save: async () => {
        const { ref, editingSection, draft } = get();
        if (ref === null || editingSection === null) {
            return;
        }
        set({ saving: true, saveError: null });
        const { report, error } = await putSection(ref.name, editingSection, draft);
        set({ lastReport: report, saving: false });
        if (error !== null) {
            set({ saveError: error });
            return;
        }
        set({ editingSection: null, draft: '' });
        await get().load(ref.name);
    },
}));
