import { Injectable }       from '@angular/core';
import { CanLoad, UrlTree } from '@angular/router';
import { Observable }       from 'rxjs';
import { AuthService }      from "../_services/auth.service";


@Injectable({
	providedIn: 'root'
})
export class LogedinGuard implements CanLoad{
	constructor(private as: AuthService) {}
	
	canLoad(): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
		const { isLoggedOut } = this.as;
		return isLoggedOut()
	}
}
