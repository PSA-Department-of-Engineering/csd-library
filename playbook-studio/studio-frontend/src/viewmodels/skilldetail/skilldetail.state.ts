import type { SkillResponse, ValidationReportResponse } from '@/models';

export interface SkillDetailState {
    selectedSkill: string | null;
    skill: SkillResponse | null;
    loading: boolean;
    error: string | null;
    editing: boolean;
    draft: string;
    saving: boolean;
    saveError: string | null;
    lastReport: ValidationReportResponse | null;
}
