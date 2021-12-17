import { NgModule }                 from '@angular/core';
import { MatButtonModule }          from "@angular/material/button";
import { MatCardModule }            from "@angular/material/card";
import { MatNativeDateModule, MatRippleModule }          from "@angular/material/core";
import { MatDividerModule }         from "@angular/material/divider";
import { MatExpansionModule }       from "@angular/material/expansion";
import { MatFormFieldModule }       from "@angular/material/form-field";
import { MatIconModule }            from "@angular/material/icon";
import { MatInputModule }           from "@angular/material/input";
import { MatListModule }            from "@angular/material/list";
import { MatMenuModule }            from '@angular/material/menu';
import { MatProgressBarModule }     from "@angular/material/progress-bar";
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSidenavModule }         from "@angular/material/sidenav";
import { MatSnackBarModule }        from "@angular/material/snack-bar";
import { MatToolbarModule }         from "@angular/material/toolbar";
import { MatTooltipModule }         from "@angular/material/tooltip";
import { MatTreeModule }  			from '@angular/material/tree';
import { MatTableModule } 			from '@angular/material/table';
import { MatPaginatorModule } 		from '@angular/material/paginator';
import { MatRadioModule } from '@angular/material/radio';
import { ScrollingModule } from '@angular/cdk/scrolling';
import { PortalModule } from '@angular/cdk/portal';
import { OverlayModule } from '@angular/cdk/overlay';
import { MatSortModule } from '@angular/material/sort';
import { MatSelectModule } from '@angular/material/select';
import { MatGridListModule } from '@angular/material/grid-list';
import {A11yModule} from '@angular/cdk/a11y';
import {CdkAccordionModule} from '@angular/cdk/accordion';
import {ClipboardModule} from '@angular/cdk/clipboard';
import {DragDropModule} from '@angular/cdk/drag-drop';
import {CdkStepperModule} from '@angular/cdk/stepper';
import {CdkTableModule} from '@angular/cdk/table';
import {CdkTreeModule} from '@angular/cdk/tree';
import {MatAutocompleteModule} from '@angular/material/autocomplete';
import {MatBadgeModule} from '@angular/material/badge';
import {MatBottomSheetModule} from '@angular/material/bottom-sheet';
import {MatButtonToggleModule} from '@angular/material/button-toggle';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatChipsModule} from '@angular/material/chips';
import {MatStepperModule} from '@angular/material/stepper';
import {MatDatepickerModule} from '@angular/material/datepicker';
import {MatDialogModule} from '@angular/material/dialog';
import {MatSliderModule} from '@angular/material/slider';
import {MatSlideToggleModule} from '@angular/material/slide-toggle';
import {MatTabsModule} from '@angular/material/tabs';

const Material = [
	A11yModule,
    CdkAccordionModule,
    ClipboardModule,
    CdkStepperModule,
    CdkTableModule,
    CdkTreeModule,
    DragDropModule,
    MatAutocompleteModule,
    MatBadgeModule,
    MatBottomSheetModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatCardModule,
    MatCheckboxModule,
    MatChipsModule,
    MatStepperModule,
    MatDatepickerModule,
    MatDialogModule,
    MatDividerModule,
    MatExpansionModule,
    MatGridListModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatMenuModule,
    MatNativeDateModule,
    MatPaginatorModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatRadioModule,
    MatRippleModule,
    MatSelectModule,
    MatSidenavModule,
    MatSliderModule,
    MatSlideToggleModule,
    MatSnackBarModule,
    MatSortModule,
    MatTableModule,
    MatTabsModule,
    MatToolbarModule,
    MatTooltipModule,
    MatTreeModule,
    OverlayModule,
    PortalModule,
    ScrollingModule,
	MatFormFieldModule,
];

@NgModule({imports:[...Material],exports: [...Material]})
export class MaterialModule{}