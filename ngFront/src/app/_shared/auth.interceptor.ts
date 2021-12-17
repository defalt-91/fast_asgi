import { HttpErrorResponse, HttpHandler, HttpInterceptor, HttpRequest, } from "@angular/common/http";
import { Injectable }                                                    from "@angular/core";
import { Store }                                                         from "@ngrx/store";
import { throwError }                                                    from "rxjs";
import { catchError, shareReplay }                                       from "rxjs/operators";
import { AuthService }                                                   from "src/app/_services/auth.service";
import { clearStore }                                                    from "src/app/store/UserFeatureStore/actions/user-feature-store.actions";
import { State }                                                         from "src/app/store/UserFeatureStore/reducers/user-feature-store.reducer";
import { select_access_token }                                           from "src/app/store/UserFeatureStore/selectors/user-feature-store.selectors";


@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  idToken: string | undefined;

  constructor(private auth: AuthService, private store: Store<State>) {
    this.store
      .select( select_access_token )
      .subscribe( (x) => ( this.idToken = x ) );
  }

  intercept(req: HttpRequest<any>, next: HttpHandler) {
    req = req.clone( { withCredentials: true } );
    if (
      this.idToken
      // && this.auth.isLoggedIn()
    ) {
      const cloned = req.clone( {
        headers: req.headers.set(
          "Authorization",
          `Bearer ${this.idToken}`
        ),
      } );
      return next
        .handle( cloned )
        .pipe( catchError( this.errorHandler ), shareReplay() );
    } else {
      return next.handle( req ).pipe( catchError( this.errorHandler ) );
    }
  }

  errorHandler(error: HttpErrorResponse) {
    if ( error.status === 0 ) {
      throwError( {
        reason: error && error.error && error.error ? error.error : "",
        status: error.status,
      } );
    }
    if (
      error.error.detail ===
      "Authentication credentials were not provided."
    ) {
      throwError( error.error.detail );
    }
    if ( error.error.detail === "Given token not valid for any token type" ) {
      this.store.dispatch( clearStore() );
    }
    if ( error.status == 400 ) {
      let a = Object.keys( error.error )[0];
      return throwError( {
        reason:
          error.error.reason !== undefined ? error.error.reason : error.error[a][0],
        status: error.status,
      } );
    }

    let data = {
      reason:
        error && error.error && error.error.detail ? error.error : "",
      status: error.status,
    };
    return throwError( data );
  }
}
