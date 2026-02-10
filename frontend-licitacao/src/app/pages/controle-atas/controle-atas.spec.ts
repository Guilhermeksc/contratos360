import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ControleAtas } from './controle-atas';

describe('ControleAtas', () => {
  let component: ControleAtas;
  let fixture: ComponentFixture<ControleAtas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ControleAtas]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ControleAtas);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
