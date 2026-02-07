import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CcimarDash } from './ccimar-dash';

describe('CcimarDash', () => {
  let component: CcimarDash;
  let fixture: ComponentFixture<CcimarDash>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CcimarDash]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CcimarDash);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
