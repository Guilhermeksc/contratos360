import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-empresas-sancionadas',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './empresas-sancionadas.component.html',
  styleUrl: './empresas-sancionadas.component.scss'
})
export class EmpresasSancionadasComponent {
  constructor() {}
}

