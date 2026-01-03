import { Component, Input, Output, EventEmitter, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Contrato } from '../../interfaces/contrato.interface';
import { calcularDiasRestantes, getDiasRestantesStyle } from '../../utils/date.utils';
import { formatCurrency } from '../../utils/currency.utils';
import { getStatusColor } from '../../utils/status.utils';
import { StatusBadgeComponent } from '../status-badge/status-badge.component';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
  selector: 'app-preview-table',
  standalone: true,
  imports: [CommonModule, StatusBadgeComponent, MatIconModule, MatTooltipModule],
  templateUrl: './preview-table.component.html',
  styleUrl: './preview-table.component.scss'
})
export class PreviewTableComponent {
  @Input() data: Contrato[] = [];
  @Output() rowClick = new EventEmitter<string>();

  calcularDiasRestantes = calcularDiasRestantes;
  getDiasRestantesStyle = getDiasRestantesStyle;
  formatCurrency = formatCurrency;
  getStatusColor = getStatusColor;

  copiedTooltips: Map<string, boolean> = new Map();

  constructor(private cdr: ChangeDetectorRef) {}

  onRowClick(contrato: Contrato): void {
    this.rowClick.emit(contrato.id);
  }

  getDiasIcon(dias: number | null): string {
    if (dias === null) return 'help_outline';
    if (dias < 0) return 'cancel';
    if (dias <= 30) return 'error';
    if (dias <= 90) return 'warning';
    if (dias <= 180) return 'info';
    if (dias <= 360) return 'check_circle';
    return 'check_circle_outline';
  }

  copiarValor(valor: string | null, event: Event, tooltipId: string): void {
    event.stopPropagation(); // Previne o clique na linha
    if (!valor) return;
    
    // Ativa o tooltip imediatamente
    this.copiedTooltips.set(tooltipId, true);
    requestAnimationFrame(() => {
      this.cdr.detectChanges();
    });
    
    navigator.clipboard.writeText(valor).then(() => {
      // Garante que o tooltip está visível após a cópia
      this.copiedTooltips.set(tooltipId, true);
      this.cdr.detectChanges();
      // Limpa o tooltip após 2 segundos
      setTimeout(() => {
        this.copiedTooltips.delete(tooltipId);
        this.cdr.detectChanges();
      }, 2000);
    }).catch(err => {
      console.error('Erro ao copiar:', err);
      this.copiedTooltips.delete(tooltipId);
      this.cdr.detectChanges();
    });
  }

  getTooltipMessage(valor: string | null, tooltipId: string): string {
    if (this.copiedTooltips.get(tooltipId)) {
      return `"${valor}" copiado para área de transferência`;
    }
    return 'Clique para copiar';
  }

  truncateText(text: string | null | undefined, maxLength: number): string {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }

  /**
   * Retorna o ícone de alerta para o contrato.
   * Lógica será implementada posteriormente.
   * @param contrato Contrato para verificar alertas
   * @returns Nome do ícone Material ou null se não houver alerta
   */
  getAlertaIcon(contrato: Contrato): string | null {
    // TODO: Implementar lógica de alertas
    // Exemplo de estrutura futura:
    // if (algumaCondicao) return 'warning';
    // if (outraCondicao) return 'error';
    // return null;
    return null;
  }

  /**
   * Retorna o tipo de alerta para aplicar classes CSS específicas.
   * Lógica será implementada posteriormente.
   * @param contrato Contrato para verificar alertas
   * @returns Tipo de alerta (ex: 'warning', 'error', 'info')
   */
  getAlertaType(contrato: Contrato): string {
    // TODO: Implementar lógica de tipos de alerta
    return 'default';
  }
}

