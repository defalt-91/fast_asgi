import { Injectable }                                                                 from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree, } from '@angular/router';
import { select, Store }                                                              from "@ngrx/store";
import { Observable } from "rxjs";
import { map, take }  from "rxjs/operators";
import { AppState }   from "../store";
import { IsAuthenticated }                                                            from "../store/UserFeatureStore/selectors/user-feature-store.selectors";


@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate{
	constructor(
		private store: Store<AppState>,
		private router: Router
	) {}
	
	canActivate(
		route: ActivatedRouteSnapshot,
		state: RouterStateSnapshot
	): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
		return this.store.pipe(
			select(IsAuthenticated),
			take(1),
			map(value => {
				if(!value){
					return this.router.createUrlTree(['login'], {
						queryParams: { returnUrl: state.url },
					})
					// this.router.navigate(['/login'], { queryParams: { returnUrl: state.url }, })
				}
				return true
			})
		)
	}
}

//   canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
//   if (this.authService.isLoggedIn()) {
//     return true;
//   }
//   // not logged in so redirect to login page with the return url
//   return this.router.navigate(['/login'], {
//     queryParams: { returnUrl: state.url },
//   });
// }
