import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTreeModule, MatTreeNestedDataSource } from '@angular/material/tree';
import { NestedTreeControl } from '@angular/cdk/tree';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { Router } from '@angular/router';
// TODO: Implementar service quando necessário
// import { BibliografiaIdService, BibliografiaItem, MateriaBibliografia } from '../../../../services/bibliografia-id.service';

interface BibliografiaNode {
  name: string;
  id?: number;
  children?: BibliografiaNode[];
  count?: number;
}

@Component({
  selector: 'app-bibliografia-id',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTreeModule, MatIconModule, MatButtonModule],
  templateUrl: './bibliografia-id.html',
  styleUrl: './bibliografia-id.scss'
})
export class BibliografiaId implements OnInit {
  bibliografias: any[] = []; // MateriaBibliografia[] quando service estiver disponível
  treeControl = new NestedTreeControl<BibliografiaNode>((node) => node.children || []);
  dataSource = new MatTreeNestedDataSource<BibliografiaNode>();
  isLoading = true;
  errorMessage = '';

  constructor(
    // private bibliografiaIdService: BibliografiaIdService, // TODO: Implementar quando necessário
    private router: Router
  ) {}

  ngOnInit(): void {
    // TODO: Implementar quando service estiver disponível
    // this.bibliografiaIdService.getBibliografiasGroupedByMateria().subscribe({
    //   next: (data: MateriaBibliografia[]) => {
    //     this.bibliografias = data;
    //     this.buildTree(data);
    //     this.isLoading = false;
    //   },
    //   error: (error) => {
    //     this.errorMessage = 'Erro ao carregar bibliografias';
    //     this.isLoading = false;
    //   }
    // });
    this.isLoading = false;
  }

  hasChild = (_: number, node: BibliografiaNode) => !!node.children && node.children.length > 0;

  buildTree(data: any[]): void {
    const tree: BibliografiaNode[] = [];
    // TODO: Implementar lógica quando service estiver disponível
    this.dataSource.data = tree;
  }

  navigateToBibliografia(bibliografiaId: number): void {
    // TODO: Implementar navegação quando necessário
    console.log('Navegar para bibliografia:', bibliografiaId);
  }

  getBibliografiaCount(node: BibliografiaNode): number {
    // TODO: Implementar quando service estiver disponível
    return node.count || 0;
  }
}
