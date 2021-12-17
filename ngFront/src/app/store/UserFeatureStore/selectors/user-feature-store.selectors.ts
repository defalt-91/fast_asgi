import { createFeatureSelector, createSelector } from '@ngrx/store';
import * as fromUser                             from '../reducers/user-feature-store.reducer';


export const selectUserState = createFeatureSelector<fromUser.State>(fromUser.userFeatureKey);
export const select_access_token_expiration = createSelector(
	selectUserState,
	(state) => state.access_token_expiration
);
export const select_access_token = createSelector(
	selectUserState,
	(state) => state.access_token
);
export const IsAuthenticated = createSelector(
	selectUserState,
	user => user.IsAuthenticated
);
export const isLoggedOut = createSelector(
	IsAuthenticated,
	loggedIn => !loggedIn
);
export const usernameSelector = createSelector(selectUserState, state => state.username);
export const RefreshTokenExp=createSelector(selectUserState,state=>state.refresh_token_expiration);