import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-ccimar-ata',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule],
  templateUrl: './ccimar-ata.html',
  styleUrl: './ccimar-ata.scss',
})
export class CcimarAta {
  constructor() {}
}
