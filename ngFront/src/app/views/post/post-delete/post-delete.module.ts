import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PostDeleteComponent } from './post-delete.component';
import {RouterModule} from "@angular/router";


@NgModule({
  declarations: [
    PostDeleteComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild([{path:'',component:PostDeleteComponent}])
  ]
})
export class PostDeleteModule { }
