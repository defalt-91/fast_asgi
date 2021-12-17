import { createFeatureSelector, createReducer, createSelector, on } from '@ngrx/store';
import { AppState }                                                 from "src/app/store/index";
import * as UIActions                        from "src/app/store/ui/ui.actions"


export const uiFeatureKey = 'ui';

export interface State{
	Loading: boolean;
	Dark_Mode: boolean;
}

export const initialState: State = {
	Loading  : false,
	Dark_Mode: false,
};

export const reducer = createReducer(
	initialState,
	on(UIActions.UI_Loading_True,  (state) => ({ ...state, Loading: true })),
	on(UIActions.UI_Loading_False, (state) => ({ ...state, Loading: false })),
	on(UIActions.UI_Theme_Change,  (state) => ({ ...state, Dark_Mode: state.Dark_Mode !== true }))
);

// export const selectUI        = (state: AppState) => state.ui;
export const selectUI        = createFeatureSelector<State> (uiFeatureKey);
export const selectLoading   = createSelector(selectUI, (state: State) => state.Loading);
export const selectDarkTheme = createSelector(selectUI, (state: State) => state.Dark_Mode);
