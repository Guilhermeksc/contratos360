import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JanelaGenerica } from './janela-generica';

describe('JanelaGenerica', () => {
  let component: JanelaGenerica;
  let fixture: ComponentFixture<JanelaGenerica>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JanelaGenerica]
    })
    .compileComponents();

    fixture = TestBed.createComponent(JanelaGenerica);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
