import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ItensContrato } from './itens-contrato';

describe('ItensContrato', () => {
  let component: ItensContrato;
  let fixture: ComponentFixture<ItensContrato>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ItensContrato]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ItensContrato);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
