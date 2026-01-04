import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StatusContrato } from './status-contrato';

describe('StatusContrato', () => {
  let component: StatusContrato;
  let fixture: ComponentFixture<StatusContrato>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StatusContrato]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StatusContrato);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
