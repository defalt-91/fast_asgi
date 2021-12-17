import { createReducer, on } from '@ngrx/store';
import * as UserActions      from '../actions/user-feature-store.actions';


export const userFeatureKey = 'user';

export interface State{
	IsAuthenticated: boolean;
	access_token?: string,
	access_token_expiration?: string
	refresh_token_expiration?: string;
	username: string;
	pk?: number;
	email?: string;
	first_name?: string;
	last_name?: string | null;
}

export const initialState: State = {
	username       : 'anonymous',
	IsAuthenticated: false,
	// access_token: '',
	// access_token_expiration: '',
	// refresh_token_expiration: '',
	// email: '',
	// first_name: '',
	// last_name: ''
};

export const userReducer = createReducer(
	initialState,

	on(UserActions.userAccessVerify, state => state),
	on(
		UserActions.userAccessVerifySuccess,
		(state, { data }) => ({ ...state, refresh_token_expiration: data.refresh_token_expiration })
	),
	on(UserActions.userAccessVerifyFailure, (state) => state),

	on(UserActions.userAccess, state => state),
	on(UserActions.userAccessSuccess, (state, { data }) => ({
		...state,
		access_token           : data.access,
		access_token_expiration: data.access_token_expiration,
		IsAuthenticated        : true
	})),
	on(UserActions.userAccessFailure, (state) => state),
	on(UserActions.getUser, state => state),
	on(UserActions.getUserSuccess, (state, action) => ({ ...state, ...action.data })),
	on(UserActions.getUserFailure, state => state),

	on(UserActions.clearStore, () => ({ ...initialState })),

	on(UserActions.userLogout, (state) => initialState),
	// on(UserActions.userLogoutSuccess,state  =>  state),
	// on(UserActions.userLogoutFailure,state  =>  state),
	on(UserActions.userLogin, state => state),
	on(UserActions.userLoginFailure, (state) => state),
	on(UserActions.userLoginSuccess, (state, {data}) => ({
		   ...state,
		   // ...action.data
		   IsAuthenticated         : true,
		   access_token            : data.access_token,
		   access_token_expiration : data.access_token_expiration,
		   refresh_token_expiration: data.refresh_token_expiration,
		   pk                      : data.user.pk,
		   username                : data.user.username,
		   email                   : data.user.email,
		   last_name               : data.user.last_name,
		   first_name              : data.user.first_name
	   })
	)
);
