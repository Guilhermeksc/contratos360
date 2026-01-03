import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatTabsModule } from '@angular/material/tabs';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ContractsService } from '../../../../../services/contracts.service';
import { ContratoDetail } from '../../../../../interfaces/contrato.interface';

@Component({
  selector: 'app-contract-details',
  standalone: true,
  imports: [CommonModule, MatTabsModule, MatButtonModule, MatIconModule],
  templateUrl: './contract-details.component.html',
  styleUrl: './contract-details.component.scss'
})
export class ContractDetailsComponent implements OnInit {
  contract = signal<ContratoDetail | null>(null);
  loading = signal(true);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private contractsService: ContractsService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadContract(id);
    }
  }

  loadContract(id: string): void {
    this.loading.set(true);
    this.contractsService.getDetails(id).subscribe({
      next: (contract: ContratoDetail) => {
        // Garante que registros_status e registros_mensagem sejam arrays
        if (contract) {
          contract.registros_status = Array.isArray(contract.registros_status) ? contract.registros_status : [];
          contract.registros_mensagem = Array.isArray(contract.registros_mensagem) ? contract.registros_mensagem : [];
        }
        this.contract.set(contract);
        this.loading.set(false);
      },
      error: (err: any) => {
        console.error('Erro ao carregar contrato:', err);
        this.loading.set(false);
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/contratos/lista']);
  }
}

