export type StudioView = 'map' | 'playbook' | 'ref' | 'skill' | 'create' | 'createskill';

export interface NavState {
    view: StudioView;
}
