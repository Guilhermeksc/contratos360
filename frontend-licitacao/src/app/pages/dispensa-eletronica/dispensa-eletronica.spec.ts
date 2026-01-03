import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DispensaEletronica } from './dispensa-eletronica';

describe('DispensaEletronica', () => {
  let component: DispensaEletronica;
  let fixture: ComponentFixture<DispensaEletronica>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DispensaEletronica]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DispensaEletronica);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
