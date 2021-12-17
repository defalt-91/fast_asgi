import { BreakpointObserver, Breakpoints } from "@angular/cdk/layout";
import { Component }                       from "@angular/core";
import { Title }                           from "@angular/platform-browser";
import { Router, RouterOutlet }            from "@angular/router";
import { Store,select }                           from "@ngrx/store";
import { Observable }                      from "rxjs";
import { map, share,take}                from "rxjs/operators";
import { AppState }                        from "src/app/store";
import { selectDarkTheme, selectLoading }  from "src/app/store/ui/ui.reducer";
import { AuthService }                     from "./_services/auth.service";
import { slideInAnimation }                from "./animations";
import { UI_Theme_Change,UI_Loading_True, UI_Loading_False }                 from "./store/ui/ui.actions";
import { clearStore }                      from "./store/UserFeatureStore/actions/user-feature-store.actions";


@Component(
	{
		selector     : "app-root",
		templateUrl  : "./app.component.html",
		styleUrls    : ["./app.component.scss"],
		animations   : [slideInAnimation],
		viewProviders: [Title]
	})
export class AppComponent{
	Title                           = 'Frontend';
	
	spin                            = false;
	loading$                        = this.store.pipe(select(selectLoading));
	isDark$: Observable<boolean>    = this.store.select(selectDarkTheme);
	// breakPoint
	isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Large).pipe(
		map((result) => result.matches)
	);
	step = 0;

	setStep(index: number) {
	  this.step = index;
	}
  
	nextStep() {
	  this.step++;
	}
  
	prevStep() {
	  this.step--;
	}
	constructor(
		private title: Title,
		private router: Router,
		private authService: AuthService,
		private store: Store<AppState>,
		private breakpointObserver: BreakpointObserver
	) {title.setTitle(this.Title)}
	
	getAnimationData(outlet: RouterOutlet):string|undefined { return outlet?.activatedRouteData?.animation}
	logout():void {this.authService.logout()};
	retttt():void  {this.store.dispatch(clearStore());};
	ChangeTheme():void  {this.store.dispatch(UI_Theme_Change())};
	spinner_change(){this.loading$.pipe(take(1)).subscribe(x=>{

		if (x) {this.store.dispatch(UI_Loading_False())
			
		} else {
			this.store.dispatch(UI_Loading_True())
		} 
		})};
}
