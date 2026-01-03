import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NotaTecnica } from './nota-tecnica';

describe('NotaTecnica', () => {
  let component: NotaTecnica;
  let fixture: ComponentFixture<NotaTecnica>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NotaTecnica]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NotaTecnica);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
