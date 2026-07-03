import { create } from 'zustand';

import type { SkillResponse, ValidationReportResponse } from '@/models';
import { apiFetch, gatedSend } from '@/utils';

import type { SkillDetailState } from './skilldetail.state';

interface SkillDetailActions {
    select: (name: string) => void;
    load: (name: string) => Promise<void>;
    startEdit: () => void;
    setDraft: (draft: string) => void;
    cancelEdit: () => void;
    save: () => Promise<void>;
}

export const useSkillDetail = create<SkillDetailState & SkillDetailActions>()((set, get) => ({
    selectedSkill: null,
    skill: null,
    loading: false,
    error: null,
    editing: false,
    draft: '',
    saving: false,
    saveError: null,
    lastReport: null,

    select: (name) => {
        set({ selectedSkill: name });
    },

    load: async (name) => {
        set({ loading: true, error: null, editing: false, saveError: null });
        try {
            const skill = await apiFetch<SkillResponse>(`/api/skills/${name}`);
            set({ skill });
        } catch (err) {
            set({ error: err instanceof Error ? err.message : 'Failed to load skill' });
        } finally {
            set({ loading: false });
        }
    },

    startEdit: () => {
        set({ editing: true, draft: get().skill?.raw ?? '', saveError: null });
    },

    setDraft: (draft) => {
        set({ draft });
    },

    cancelEdit: () => {
        set({ editing: false, draft: '', saveError: null });
    },

    save: async () => {
        const { skill, draft } = get();
        if (!skill) {
            return;
        }
        set({ saving: true, saveError: null });
        const result = await gatedSend<ValidationReportResponse>(
            `/api/skills/${skill.name}`,
            'PUT',
            { raw: draft },
        );
        set({
            saving: false,
            lastReport: (result.ok ?? result.report) as ValidationReportResponse | null,
        });
        if (result.error !== null) {
            set({ saveError: result.error });
            return;
        }
        set({ editing: false, draft: '' });
        await get().load(skill.name);
    },
}));
