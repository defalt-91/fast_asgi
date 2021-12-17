import { createAction } from '@ngrx/store';

export enum UiActions{
	loadingTrue  = '[UI] Loading True',
	loadingFalse = '[UI] Loading False',
	Theme    	 = '[UI] Theme Change',
}

export const UI_Loading_True  = createAction(UiActions.loadingTrue);
export const UI_Loading_False = createAction(UiActions.loadingFalse);
export const UI_Theme_Change  = createAction(UiActions.Theme);
