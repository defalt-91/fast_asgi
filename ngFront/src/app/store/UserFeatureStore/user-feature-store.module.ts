import { NgModule }                    from '@angular/core';
import { EffectsModule }               from '@ngrx/effects';
import { StoreModule }                 from '@ngrx/store';
import { UserEffects }                 from './effects/user-feature-store.effects';
import { userFeatureKey, userReducer } from './reducers/user-feature-store.reducer';


@NgModule({
	imports: [
		StoreModule.forFeature(userFeatureKey, userReducer),
		EffectsModule.forFeature([UserEffects]),
	],
	exports: [StoreModule, EffectsModule]
})
export class UserFeatureStoreModule {}
