import { MaterialModule } from 'src/app/material.module';
import { MatFormFieldModule } from '@angular/material/form-field';
import { CommonModule }      	from "@angular/common";
import { NgModule }          	from "@angular/core";
import { MatPaginatorModule }	from "@angular/material/paginator";
import { MatTableModule } 	 	from "@angular/material/table";
import { RouterModule }      	from "@angular/router";
import { TableComponent } 	 	from "src/app/components/table/table.component";
import { PostListComponent } 	from "./post-list.component";
import { MatCardModule } from '@angular/material/card';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { ReactiveFormsModule } from '@angular/forms';
import { TestTableComponent } from '../../../components/test-table/test-table.component';
import { MatSortModule } from '@angular/material/sort';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';
import { LayoutModule } from '@angular/cdk/layout';


@NgModule({
		declarations: [
			PostListComponent,
			TableComponent,
			TestTableComponent
				],
		imports     : [
			CommonModule,
			RouterModule
				.forChild([{ path: "", component: PostListComponent }]),
			MatTableModule,
			MatPaginatorModule,
			MatFormFieldModule,
			MatCardModule,
			MatSelectModule,
			MatRadioModule,
			MatInputModule,
			MatButtonModule,
			ReactiveFormsModule,
			MatSortModule,
			MaterialModule,
			MatGridListModule,
			MatMenuModule,
			MatIconModule,
			LayoutModule
		
		],
	})
export class PostListModule{}
