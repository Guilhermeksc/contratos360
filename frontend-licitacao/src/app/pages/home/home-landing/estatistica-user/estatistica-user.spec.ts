import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EstatisticaUser } from './estatistica-user';

describe('EstatisticaUser', () => {
  let component: EstatisticaUser;
  let fixture: ComponentFixture<EstatisticaUser>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EstatisticaUser]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EstatisticaUser);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
