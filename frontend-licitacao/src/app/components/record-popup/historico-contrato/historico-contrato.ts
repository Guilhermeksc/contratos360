import { Component, Input, OnInit, OnChanges, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { HistoricoContrato } from '../../../interfaces/offline.interface';
import { formatCurrency } from '../../../utils/currency.utils';
import { formatDate } from '../../../utils/date.utils';

@Component({
  selector: 'app-historico-contrato',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  templateUrl: './historico-contrato.html',
  styleUrl: './historico-contrato.scss'
})
export class HistoricoContratoComponent implements OnInit {
  @Input() contratoId: string = '';
  @Input() historicos: HistoricoContrato[] = [];

  loading = signal(false);
  historicosSignal = signal<HistoricoContrato[]>([]);

  formatCurrency = formatCurrency;
  formatDate = formatDate;

  ngOnInit(): void {
    // Históricos são passados como Input
    this.historicosSignal.set(this.historicos || []);
    this.loading.set(false);
  }

  ngOnChanges(changes: any): void {
    if (changes.historicos) {
      this.historicosSignal.set(this.historicos || []);
    }
  }
}
