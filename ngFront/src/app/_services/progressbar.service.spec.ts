import { TestBed } from '@angular/core/testing';

import { UIService } from 'src/app/_services/ui.service';

describe('ProgressbarService', () => {
  let service: UIService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UIService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
