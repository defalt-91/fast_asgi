import { routerReducer, RouterState }    from "@ngrx/router-store";
import { ActionReducerMap, MetaReducer } from '@ngrx/store';
import { storeFreeze }                   from 'ngrx-store-freeze';
import * as fromUI                       from "src/app/store/ui/ui.reducer";
import { environment }                   from 'src/environments/environment';

// import {userFeatureKey, userReducer} from "./UserFeatureStore/reducers/user-feature-store.reducer";
export interface AppState{
	router: RouterState;
	ui: fromUI.State;
}

export const reducers: ActionReducerMap<AppState> = {
	router: routerReducer,
	ui    : fromUI.reducer
};

export const metaReducers: MetaReducer<AppState>[] = !environment.production ? [storeFreeze] : [];