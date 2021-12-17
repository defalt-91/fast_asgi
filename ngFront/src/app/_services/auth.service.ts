import { HttpClient }             from '@angular/common/http';
import { Injectable }             from '@angular/core';
import { MatSnackBar }            from '@angular/material/snack-bar';
import { Router }                 from '@angular/router';
import { Store }                  from '@ngrx/store';
import { Observable, throwError } from 'rxjs';
import { shareReplay, tap }       from 'rxjs/operators';
import { ACCESS, VERIFY }         from '../_models/access';
import { LoginForm }              from '../_models/login-form';
import { LoginUser }              from '../_models/user';
import { USER }                   from '../_models/users';
import { userLogout }             from '../store/UserFeatureStore/actions/user-feature-store.actions';
import {
	RefreshTokenExp, select_access_token, select_access_token_expiration
}                                 from '../store/UserFeatureStore/selectors/user-feature-store.selectors';
import { environment } from 'src/environments/environment';


@Injectable({ providedIn: 'root' })
export class AuthService{
	currentUser = {};
	endpoint    = `${environment.api_url}/auth`;
	Access?: string;
	AccessExpiration?: string;
	RefreshExpiration?: string;
	
	constructor(
		private store: Store,
		private http: HttpClient,
		public router: Router,
		private snack: MatSnackBar
	) {
		this.store.select(select_access_token).subscribe((x) => (this.Access = x));
		this.store
		    .select(select_access_token_expiration)
		    .subscribe((x) => (this.AccessExpiration = x));
		this.store.select(RefreshTokenExp).subscribe(x => this.RefreshExpiration = x);
	}
	
	getAccessChecked() {
		return this.http.post<VERIFY>(`${ this.endpoint }/token/verify/`, {});
	}
	
	getNewAccess(): Observable<ACCESS> {
		try{
			return this.http.post<ACCESS>(`${ this.endpoint }/token/refresh/`, {});
		} catch(e){
			return throwError(e);
		}
	}
	
	login(user: LoginForm): Observable<LoginUser> {
		// localStorage.clear()
		return this.http.post<LoginUser>(`${ this.endpoint }/login/`, user).pipe(
			tap((res) => {
				this.snack.open('You are Logged In ', 'close', { duration: 3001 });
				// this.setSessionFromLogin(res)
			}),
			shareReplay()
		);
	}
	
	getUser(): Observable<USER> {
		return this.http.get<USER>(`${ this.endpoint }/user/`);
	}
	
	logout() {
		this.store.dispatch(userLogout());
	}
	
	public isLoggedIn(): boolean {
		if(this.AccessExpiration && this.Access){
			return new Date(this.AccessExpiration) > new Date()
			
		} else{
			try{
				// this.getNewAccess();
				// return this.isLoggedIn();
				return false
			} catch(e){
				throwError(e);
				return false;
			}
		}
	}
	
	isLoggedOut() {
		return !this.isLoggedIn();
	}
}
