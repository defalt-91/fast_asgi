import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {RouterModule} from "@angular/router";
import {NotFoundComponent} from './not-found.component';
import {OverlayModule} from "@angular/cdk/overlay";
import {_MatMenuDirectivesModule, MatMenuModule} from "@angular/material/menu";
import {MatButtonModule} from "@angular/material/button";
import {MatIconModule} from "@angular/material/icon";
import {MatListModule} from "@angular/material/list";

@NgModule({
  declarations: [NotFoundComponent],
	imports: [CommonModule, RouterModule.forChild([{
		path: '',
		component: NotFoundComponent
	}]), OverlayModule, _MatMenuDirectivesModule, MatMenuModule, MatButtonModule, MatIconModule, MatListModule]
})
export class NotFoundModule {
}
