import { Component, OnInit } from '@angular/core';
import { MatBottomSheetRef} from '@angular/material/bottom-sheet';

@Component({
  selector: 'app-sheet-component',
  templateUrl: './sheet-component.component.html',
  styleUrls: ['./sheet-component.component.scss']
})
export class SheetComponentComponent {
  constructor(private _bottomSheetRef: MatBottomSheetRef<SheetComponentComponent>) {}

  openLink(event: MouseEvent): void {
    this._bottomSheetRef.dismiss();
    event.preventDefault();
  }
}