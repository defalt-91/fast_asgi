import {Component} from '@angular/core';
import {MatBottomSheet} from '@angular/material/bottom-sheet';
import { SheetComponentComponent } from '../sheet-component/sheet-component.component';

@Component({
  selector: 'sheets',
  templateUrl: './sheets.component.html',
})
export class SheetsComponent {
  constructor(private _bottomSheet: MatBottomSheet) {}

  openBottomSheet(): void {
    this._bottomSheet.open(SheetComponentComponent);
  }
}
