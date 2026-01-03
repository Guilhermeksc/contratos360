import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { Router } from '@angular/router';

@Component({
  selector: 'app-cronograma',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatButtonModule],
  templateUrl: './cronograma.html',
  styleUrl: './cronograma.scss'
})
export class Cronograma {

  constructor(private router: Router) {}

  navigateHome(): void {
    this.router.navigate(['/home']);
  }
}
