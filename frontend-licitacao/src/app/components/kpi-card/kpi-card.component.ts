import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-kpi-card',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  templateUrl: './kpi-card.component.html',
  styleUrl: './kpi-card.component.scss'
})
export class KpiCardComponent {
  @Input() title: string = '';
  @Input() value: string = 'N/A';
  @Input() icon: string = 'info';
  @Input() color: 'blue' | 'green' | 'yellow' | 'red' | 'purple' = 'blue';

  getColorClass(): string {
    return `color-${this.color}`;
  }
}

