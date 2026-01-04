import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FiscalizacaoContrato } from './fiscalizacao-contrato';

describe('FiscalizacaoContrato', () => {
  let component: FiscalizacaoContrato;
  let fixture: ComponentFixture<FiscalizacaoContrato>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FiscalizacaoContrato]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FiscalizacaoContrato);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
