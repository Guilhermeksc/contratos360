import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HistoricoContrato } from './historico-contrato';

describe('HistoricoContrato', () => {
  let component: HistoricoContrato;
  let fixture: ComponentFixture<HistoricoContrato>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HistoricoContrato]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HistoricoContrato);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
