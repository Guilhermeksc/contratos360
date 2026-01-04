import { Component, Input, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import { EmpenhosService } from '../../../services/empenhos.service';
import { Empenho } from '../../../interfaces/offline.interface';
import { formatCurrency } from '../../../utils/currency.utils';
import { formatDate } from '../../../utils/date.utils';

@Component({
  selector: 'app-empenhos-contrato',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatSelectModule,
    MatFormFieldModule,
    FormsModule
  ],
  templateUrl: './empenhos-contrato.html',
  styleUrl: './empenhos-contrato.scss'
})
export class EmpenhosContratoComponent implements OnInit {
  @Input() contratoId: string = '';

  empenhos = signal<Empenho[]>([]);
  loading = signal(false);
  selectedYear: string = 'Todos';
  availableYears: string[] = [];

  formatCurrency = formatCurrency;
  formatDate = formatDate;

  constructor(private empenhosService: EmpenhosService) {}

  ngOnInit(): void {
    if (this.contratoId) {
      this.loadEmpenhos();
    }
  }

  loadEmpenhos(): void {
    if (!this.contratoId || this.empenhos().length > 0) return;
    
    this.loading.set(true);
    this.empenhosService.list(this.contratoId).subscribe({
      next: (empenhos: Empenho[]) => {
        this.empenhos.set(Array.isArray(empenhos) ? empenhos : []);
        // Extrai anos únicos das datas de emissão
        const years = new Set<string>();
        empenhos.forEach(e => {
          if (e.data_emissao) {
            const year = e.data_emissao.substring(0, 4);
            if (year) years.add(year);
          }
        });
        this.availableYears = Array.from(years).sort().reverse();
        this.loading.set(false);
      },
      error: (err: any) => {
        console.error('EmpenhosContratoComponent: Erro ao carregar empenhos:', err);
        this.empenhos.set([]);
        this.loading.set(false);
      }
    });
  }

  getFilteredEmpenhos(): Empenho[] {
    if (this.selectedYear === 'Todos') {
      return this.empenhos();
    }
    return this.empenhos().filter(e => 
      e.data_emissao && e.data_emissao.startsWith(this.selectedYear)
    );
  }
}
