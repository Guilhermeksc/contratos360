import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { DashboardService } from '../../../../../services/dashboard.service';
import { DashboardSummary } from '../../../../../interfaces/dashboard.interface';
import { KpiCardComponent } from '../../../../../components/kpi-card/kpi-card.component';
import { formatCurrency } from '../../../../../utils/currency.utils';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule, KpiCardComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  summary = signal<DashboardSummary | null>(null);
  loading = signal(true);
  formatCurrency = formatCurrency;

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.loadDashboard();
  }

  refreshDashboard(): void {
    this.loadDashboard();
  }

  private loadDashboard(): void {
    this.loading.set(true);
    this.dashboardService.getSummary().subscribe({
      next: (summary: DashboardSummary) => {
        this.summary.set(summary);
        this.loading.set(false);
      },
      error: (err: any) => {
        console.error('Erro ao carregar dashboard:', err);
        this.loading.set(false);
      }
    });
  }
}

