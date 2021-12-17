import { Injectable }                                      from '@angular/core';
import { Actions, createEffect, ofType }                   from '@ngrx/effects';
import { ROUTER_CANCEL, ROUTER_NAVIGATED, ROUTER_REQUEST } from "@ngrx/router-store";
import { map, tap }                                        from "rxjs/operators";
import { UIService }                                       from "src/app/_services/ui.service";
import * as UIActions                                      from "src/app/store/ui/ui.actions";


@Injectable()
export class UiEffects{
	Loading$ = createEffect(
		() => this.actions$.pipe(
			ofType(ROUTER_REQUEST),
			map(() => UIActions.UI_Loading_True()),
		),
		{ dispatch: true }
	);
	
	Loading_end$ = createEffect(
		() => this.actions$.pipe(
			ofType(ROUTER_NAVIGATED, ROUTER_CANCEL),
			map(() => UIActions.UI_Loading_False())
	),
	{ dispatch: true });
	UI_Theme$    = createEffect(
		() => this.actions$.pipe(
			ofType(UIActions.UI_Theme_Change),
			tap(() => this.uiService.ChangeTheme())), 
			{ dispatch: false }
	);
	
	constructor(private actions$: Actions, private uiService: UIService) {}
}

// this.uiService.ChangeTheme()