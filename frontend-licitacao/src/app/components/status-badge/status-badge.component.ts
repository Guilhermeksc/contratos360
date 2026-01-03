import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { getStatusColor } from '../../utils/status.utils';

@Component({
  selector: 'app-status-badge',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './status-badge.component.html',
  styleUrl: './status-badge.component.scss'
})
export class StatusBadgeComponent {
  @Input() status: string = 'SEÇÃO CONTRATOS';

  getStatusColor(status: string): string {
    return getStatusColor(status);
  }
}

