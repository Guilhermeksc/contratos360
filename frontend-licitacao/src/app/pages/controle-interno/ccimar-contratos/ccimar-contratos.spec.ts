import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CcimarContratos } from './ccimar-contratos';

describe('CcimarContratos', () => {
  let component: CcimarContratos;
  let fixture: ComponentFixture<CcimarContratos>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CcimarContratos]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CcimarContratos);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
