import { Component } from '@angular/core';
import { EstatisticasComponent } from '../../../../components/perguntas/estatisticas/estatisticas';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-estatistica-user',
  standalone: true,
  imports: [CommonModule, EstatisticasComponent],
  templateUrl: './estatistica-user.html',
  styleUrl: './estatistica-user.scss'
})
export class EstatisticaUser {
}
