import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-message-builder',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="message-builder-container">
      <h1>Gerador de Mensagem de Alerta</h1>
      <p>Implementação em andamento</p>
    </div>
  `,
  styleUrl: './message-builder.component.scss'
})
export class MessageBuilderComponent {}

