import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PostDetailComponent } from './post-detail.component';
import {RouterModule} from "@angular/router";
import { DragDropComponent } from '../../../components/drag-drop/drag-drop.component';
import { DragDropModule } from '@angular/cdk/drag-drop';


@NgModule({
  declarations: [
    PostDetailComponent,
    DragDropComponent
  ],
  imports: [
    CommonModule,
      RouterModule.forChild([{ path: "", component: PostDetailComponent }]),
      DragDropModule,
]
})
export class PostDetailModule { }
