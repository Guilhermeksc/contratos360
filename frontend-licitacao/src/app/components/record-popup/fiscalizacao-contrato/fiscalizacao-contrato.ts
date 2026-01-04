import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FiscalizacaoContrato } from '../../../interfaces/fiscalizacao.interface';

@Component({
  selector: 'app-fiscalizacao-contrato',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './fiscalizacao-contrato.html',
  styleUrl: './fiscalizacao-contrato.scss'
})
export class FiscalizacaoContratoComponent {
  @Input() fiscalizacao: FiscalizacaoContrato | null = null;
}
