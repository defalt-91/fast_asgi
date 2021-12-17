import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SheetComponentComponent } from './sheet-component.component';

describe('SheetComponentComponent', () => {
  let component: SheetComponentComponent;
  let fixture: ComponentFixture<SheetComponentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SheetComponentComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SheetComponentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
