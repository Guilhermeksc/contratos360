import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

export interface BotaoJanela {
  texto: string;
  tipo?: 'primary' | 'secondary' | 'danger' | 'success';
  disabled?: boolean;
  acao: () => void;
}

@Component({
  selector: 'app-janela-generica',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonModule],
  templateUrl: './janela-generica.html',
  styleUrl: './janela-generica.scss'
})
export class JanelaGenerica {
  @Input() titulo: string = '';
  @Input() mostrar: boolean = false;
  @Input() mostrarBotaoFechar: boolean = true;
  @Input() maxWidth: string = '600px';
  @Input() botoes: BotaoJanela[] = [];
  @Input() mostrarFooter: boolean = true;
  @Input() isLoading: boolean = false;

  @Output() fechar = new EventEmitter<void>();

  fecharJanela() {
    if (!this.isLoading) {
      this.fechar.emit();
    }
  }

  executarAcao(botao: BotaoJanela) {
    if (!botao.disabled && !this.isLoading) {
      botao.acao();
    }
  }

  fecharAoClicarOverlay(event: MouseEvent) {
    // Fecha apenas se clicar diretamente no overlay, não no conteúdo
    if (event.target === event.currentTarget && !this.isLoading) {
      this.fecharJanela();
    }
  }
}
