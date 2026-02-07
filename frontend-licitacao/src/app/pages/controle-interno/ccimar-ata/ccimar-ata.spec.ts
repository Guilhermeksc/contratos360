import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CcimarAta } from './ccimar-ata';

describe('CcimarAta', () => {
  let component: CcimarAta;
  let fixture: ComponentFixture<CcimarAta>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CcimarAta]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CcimarAta);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
