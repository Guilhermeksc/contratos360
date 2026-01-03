import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BibliografiaId } from './bibliografia-id';

describe('BibliografiaId', () => {
  let component: BibliografiaId;
  let fixture: ComponentFixture<BibliografiaId>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BibliografiaId]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BibliografiaId);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
