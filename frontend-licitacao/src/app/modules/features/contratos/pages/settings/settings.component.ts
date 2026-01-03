import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SettingsService } from '../../../../../services/settings.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="settings-container">
      <h1>Configurações</h1>
      <p>Implementação em andamento</p>
    </div>
  `,
  styleUrl: './settings.component.scss'
})
export class SettingsComponent implements OnInit {
  mode = signal<'Online' | 'Offline'>('Online');

  constructor(private settingsService: SettingsService) {}

  ngOnInit(): void {
    this.settingsService.mode$.subscribe((mode: 'Online' | 'Offline') => this.mode.set(mode));
  }
}

