import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmpenhosContrato } from './empenhos-contrato';

describe('EmpenhosContrato', () => {
  let component: EmpenhosContrato;
  let fixture: ComponentFixture<EmpenhosContrato>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EmpenhosContrato]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EmpenhosContrato);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
