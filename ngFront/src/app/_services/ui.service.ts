import { Injectable }                  from '@angular/core';
import { Store }                       from "@ngrx/store";
import { BehaviorSubject, Observable } from "rxjs";
import { AppState }                    from "src/app/store";
import { selectDarkTheme }             from "src/app/store/ui/ui.reducer";
import { Router, UrlTree }             from "@angular/router";


@Injectable({ providedIn: 'root' })
export class UIService {
  isLoading                   = new BehaviorSubject<boolean>(false);
  isDark: Observable<boolean> = this.store.select(selectDarkTheme);
  private bodyElement         = document.body;

  // isLoading$                  = this.isLoading.asObservable();

  constructor(private store: Store<AppState>, private router: Router){}

  ChangeTheme(){
    this.isDark.subscribe(
      (x) => !x ?
        this.bodyElement.classList.remove(`dark-theme`) :
        this.bodyElement.classList.add(`dark-theme`)
    )
  }

  // string_to_tree(stringUrl: string): UrlTree{return this.router.parseUrl(stringUrl)}

  goto(url: string | UrlTree): void{
    let urlTree = typeof url == "string" ? this.router.parseUrl(url) : url;
    this.router
        .navigateByUrl(urlTree)
    .then(_ => console.log(urlTree))
  }
}
