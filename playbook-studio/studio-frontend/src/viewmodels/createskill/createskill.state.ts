import type { ValidationReportResponse } from '@/models';

export interface CreateSkillState {
    name: string;
    description: string;
    refs: string[];
    submitting: boolean;
    error: string | null;
    report: ValidationReportResponse | null;
}
