import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PostCreateComponent } from './post-create.component';
import { RouterModule} from "@angular/router";
import { DragDropModule } from '@angular/cdk/drag-drop';
import { DashboardComponent } from '../../../components/dashboard/dashboard.component';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatCardModule } from '@angular/material/card';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { LayoutModule } from '@angular/cdk/layout';


@NgModule({
  declarations: [
    PostCreateComponent,
    DashboardComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild([{ path: '', component: PostCreateComponent }]),
    DragDropModule,
    MatGridListModule,
    MatCardModule,
    MatMenuModule,
    MatIconModule,
    MatButtonModule,
    LayoutModule
  ]
})
export class PostCreateModule { }
