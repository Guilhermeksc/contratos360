import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-ccimar-contratos',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule],
  templateUrl: './ccimar-contratos.html',
  styleUrl: './ccimar-contratos.scss',
})
export class CcimarContratos {
  constructor() {}
}
