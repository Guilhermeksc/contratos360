import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DiarioOficial } from './diario-oficial';

describe('DiarioOficial', () => {
  let component: DiarioOficial;
  let fixture: ComponentFixture<DiarioOficial>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DiarioOficial]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DiarioOficial);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
