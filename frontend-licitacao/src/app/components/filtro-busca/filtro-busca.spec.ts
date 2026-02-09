import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FiltroBusca } from './filtro-busca';

describe('FiltroBusca', () => {
  let component: FiltroBusca;
  let fixture: ComponentFixture<FiltroBusca>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FiltroBusca]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FiltroBusca);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
