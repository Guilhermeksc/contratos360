import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CcimarPncp } from './ccimar-pncp';

describe('CcimarPncp', () => {
  let component: CcimarPncp;
  let fixture: ComponentFixture<CcimarPncp>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CcimarPncp]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CcimarPncp);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
