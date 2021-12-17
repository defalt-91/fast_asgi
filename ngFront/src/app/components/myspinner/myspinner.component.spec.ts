import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyspinnerComponent } from './myspinner.component';

describe('MyspinnerComponent', () => {
  let component: MyspinnerComponent;
  let fixture: ComponentFixture<MyspinnerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MyspinnerComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MyspinnerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
