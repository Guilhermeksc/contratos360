import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-ccimar-dash',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule],
  templateUrl: './ccimar-dash.html',
  styleUrl: './ccimar-dash.scss',
})
export class CcimarDash {
  constructor() {}
}
