import { Component, Input, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { ItensService } from '../../../services/itens.service';
import { ItemContrato } from '../../../interfaces/offline.interface';
import { formatCurrency } from '../../../utils/currency.utils';

@Component({
  selector: 'app-itens-contrato',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  templateUrl: './itens-contrato.html',
  styleUrl: './itens-contrato.scss'
})
export class ItensContratoComponent implements OnInit {
  @Input() contratoId: string = '';

  itens = signal<ItemContrato[]>([]);
  loading = signal(false);

  formatCurrency = formatCurrency;

  constructor(private itensService: ItensService) {}

  ngOnInit(): void {
    if (this.contratoId) {
      this.loadItens();
    }
  }

  loadItens(): void {
    if (!this.contratoId || this.itens().length > 0) return;
    
    this.loading.set(true);
    this.itensService.list(this.contratoId).subscribe({
      next: (itens: ItemContrato[]) => {
        this.itens.set(Array.isArray(itens) ? itens : []);
        this.loading.set(false);
      },
      error: (err: any) => {
        console.error('ItensContratoComponent: Erro ao carregar itens:', err);
        this.itens.set([]);
        this.loading.set(false);
      }
    });
  }
}
