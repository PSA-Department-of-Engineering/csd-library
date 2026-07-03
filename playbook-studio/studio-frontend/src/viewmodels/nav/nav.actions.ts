import { create } from 'zustand';

import type { NavState, StudioView } from './nav.state';

interface NavActions {
    setView: (view: StudioView) => void;
}

export const useNav = create<NavState & NavActions>()((set) => ({
    view: 'overview',

    setView: (view) => {
        set({ view });
    },
}));
