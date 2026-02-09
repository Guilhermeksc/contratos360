import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlanejamentoAnalises } from './planejamento-analises';

describe('PlanejamentoAnalises', () => {
  let component: PlanejamentoAnalises;
  let fixture: ComponentFixture<PlanejamentoAnalises>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PlanejamentoAnalises]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PlanejamentoAnalises);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
