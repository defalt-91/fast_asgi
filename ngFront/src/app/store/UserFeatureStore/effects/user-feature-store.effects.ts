import { Injectable }                                   from '@angular/core';
import { Actions, createEffect, ofType, OnInitEffects } from '@ngrx/effects';
import { Action }                                       from '@ngrx/store';
import { of }                                           from 'rxjs';
import { catchError, exhaustMap, map, tap }             from 'rxjs/operators';
import { AuthService }                                  from 'src/app/_services/auth.service';

import {
  getUser, getUserFailure, getUserSuccess, userAccess, userAccessFailure, userAccessSuccess, userAccessVerify,
  userAccessVerifyFailure, userAccessVerifySuccess, userLogin, userLoginFailure, userLoginSuccess
}                    from '../actions/user-feature-store.actions';
import { UIService } from "../../../_services/ui.service";


@Injectable()
export class UserEffects implements OnInitEffects {
  loginSuccess$      = createEffect(
    () => this.actions$.pipe(
      ofType(userLoginSuccess),
      tap(() => this.uiService.goto('post'))
    ), { dispatch: false }
  )
  logUser$           = createEffect(
    () => this.actions$.pipe(
      ofType(userLogin),
      exhaustMap(
        (action) => this.authService.login({ ...action.formValue }).pipe(
          map((data) => userLoginSuccess({ data })),
          catchError((error) => of(userLoginFailure({ error })))
        )
      )
    )
    // { dispatch: false }
  );
  GetNewAccessToken$ = createEffect(
    () => this.actions$.pipe(
      ofType(userAccess),
      exhaustMap(
        (action) => this.authService.getNewAccess().pipe(
          map((data) => userAccessSuccess({ data })),
          catchError((error) => of(userAccessFailure({ error })))
        )
      )
    )
    // { dispatch: false }
  );
  CheckAccessT$      = createEffect(
    () => this.actions$.pipe(
      ofType(userAccessVerify),
      // map(() => userAccess()),
      exhaustMap(
        () => this.authService.getAccessChecked().pipe(
          // tap(()=>userAccess()),
          map((data) => userAccessVerifySuccess({ data })),
          catchError((error) => of(userAccessVerifyFailure({ error })))
        )
      )
    )
    // { dispatch: false }
  );
  CheckAccessT2$     = createEffect(
    () => this.actions$.pipe(
      ofType(userAccessVerifySuccess),
      map(() => userAccess())
    )
  );

  loadUser$           = createEffect(
    () => this.actions$.pipe(
      ofType(getUser),
      exhaustMap(
        () => this.authService.getUser().pipe(
          map((data) => getUserSuccess({ data })),
          catchError((error) => of(getUserFailure({ error })))
        )
      )
    )
  );
  loadUserFromEffect$ = createEffect(
    () => this.actions$.pipe(
      ofType(userAccessSuccess),
      exhaustMap(
        () => this.authService.getUser().pipe(
          map((data) => getUserSuccess({ data })),
          catchError((error) => of(getUserFailure({ error })))
        )
      )
    )
  );

  constructor(
    private actions$: Actions,
    private authService: AuthService,
    private uiService: UIService
  ) {
  }

  ngrxOnInitEffects = (): Action => ({ type: '[App] Verify AccessT' });
}

// userAccessSuccess;
