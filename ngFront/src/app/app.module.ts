import { TreeComponent } from 'src/app/components/tree/tree.component';
import { CdkAccordionModule }                     from "@angular/cdk/accordion";
import { LayoutModule }                           from "@angular/cdk/layout";
import { HttpClientModule, HttpClientXsrfModule } from "@angular/common/http";
import { NgModule }                               from "@angular/core";
import { FormsModule, ReactiveFormsModule }       from "@angular/forms";
import { BrowserModule }                          from "@angular/platform-browser";
import { BrowserAnimationsModule }                from "@angular/platform-browser/animations";
import { EffectsModule }                          from "@ngrx/effects";
import { StoreRouterConnectingModule }            from "@ngrx/router-store";
import { StoreModule }                            from '@ngrx/store';
import { StoreDevtoolsModule }                    from "@ngrx/store-devtools";
import { MaterialModule }                         from "src/app/material.module";
import { environment }                            from "../environments/environment";
import { HttpInterceptorProviders }               from "./_shared";
import { ROUTER_STATE_SERIALIZER_PROVIDER }       from "./_shared/custom-serializer";
import { AppRoutingModule }                       from "./app-routing.module";
import { AppComponent }                           from "./app.component";
import { CarouselComponent }                      from './components/carousel/carousel.component';
import { LoaderComponent }                        from './components/loader/loader.component';
import { MyspinnerComponent }                     from './components/myspinner/myspinner.component';
import { SidebarComponent }                       from './components/sidebar/sidebar.component';
import { metaReducers, reducers }                 from "./store";
import { UiEffects }                              from './store/ui/ui.effects';
import { UserFeatureStoreModule }                 from "./store/UserFeatureStore/user-feature-store.module";
import { EllipsisComponent }                      from './components/ellipsis/ellipsis.component';
// import {UserEffects} from "./store/UserFeatureStore/effects/user-feature-store.effects";
// import {UserFeatureStoreModule} from "./store/UserFeatureStore/user-feature-store.module";

// import { RouterEffects } from './store/router.effects';

@NgModule(
  {
    declarations: [
      AppComponent,
      MyspinnerComponent,
      SidebarComponent,
      LoaderComponent,
      CarouselComponent,
      EllipsisComponent,
      TreeComponent,
    ],
    imports: [
      BrowserModule,
      BrowserAnimationsModule,
      HttpClientModule,
      MaterialModule,
      HttpClientXsrfModule.withOptions( { cookieName: "csrftoken", headerName: "X-CSRFTOKEN", } ),
      FormsModule,
      ReactiveFormsModule,
      LayoutModule,
      UserFeatureStoreModule,
      AppRoutingModule,
      StoreModule.forRoot( reducers, { metaReducers } ),
      EffectsModule.forRoot( [ UiEffects ] ),
      !environment.production ? StoreDevtoolsModule.instrument(
        { maxAge: 25, logOnly: environment.production } ) : [],
      StoreRouterConnectingModule.forRoot( { stateKey: 'router' } ),
      CdkAccordionModule,

    ],
    providers: [
      HttpInterceptorProviders,
      ROUTER_STATE_SERIALIZER_PROVIDER,
    ],
    bootstrap: [ AppComponent ],
  } )
export class AppModule {}
