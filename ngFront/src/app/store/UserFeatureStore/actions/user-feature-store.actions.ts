import { createAction, props } from '@ngrx/store';
import { ACCESS, VERIFY }      from 'src/app/_models/access';
import { LoginForm }           from 'src/app/_models/login-form';
import { LoginUser }           from 'src/app/_models/user';
import { USER }                from 'src/app/_models/users';


enum Auth{
	getUser                 = '[App] GetUser Success',
	getUserSuccess          = '[App] GetUser Success',
	getUserFailure          = '[App] GetUser Failure',
	userLogin               = '[User] Login',
	userLoginSuccess        = '[User] Login Success',
	userLoginFailure        = '[User] Login Failure',
	userLogout              = '[User] Logout',
	userLogoutSuccess       = '[User] Logout Success',
	userLogoutFailure       = '[User] Logout Failure',
	userAccess              = '[App] Refresh AccessT',
	userAccessSuccess       = '[App] Refresh AccessT Success',
	userAccessFailure       = '[App] Refresh AccessT Failure',
	userAccessVerify        = '[App] Verify AccessT',
	userAccessVerifySuccess = '[App] Verify AccessT Success',
	userAccessVerifyFailure = '[App] Verify AccessT Failure',
	clearStore              = '[initialState] Reset state',
}

export const getUser = createAction(Auth.getUser);
export const getUserSuccess = createAction(Auth.getUserSuccess, props<{ data: USER }>());
export const getUserFailure = createAction(Auth.getUserFailure, props<{ error: any }>());

export const userLogin = createAction(Auth.userLogin, props<{ formValue: LoginForm }>());
export const userLoginSuccess = createAction(Auth.userLoginSuccess, props<{ data: LoginUser }>());
export const userLoginFailure = createAction(Auth.userLoginFailure, props<{ error: any }>());

export const userLogout = createAction(Auth.userLogout);
export const userLogoutSuccess = createAction(Auth.userLogoutSuccess);
export const userLogoutFailure = createAction(Auth.userLogoutFailure, props<{ error: any }>());

export const userAccess = createAction(Auth.userAccess);
export const userAccessSuccess = createAction(Auth.userAccessSuccess, props<{ data: ACCESS }>());
export const userAccessFailure = createAction(Auth.userAccessFailure, props<{ error: any }>());

export const userAccessVerify = createAction(Auth.userAccessVerify);
export const userAccessVerifySuccess = createAction(Auth.userAccessVerifySuccess,props<{data:VERIFY}>());
export const userAccessVerifyFailure = createAction(Auth.userAccessVerifyFailure, props<{ error: any }>());

export const clearStore = createAction(Auth.clearStore);
