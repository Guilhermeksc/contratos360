import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTreeModule, MatTreeNestedDataSource } from '@angular/material/tree';
import { NestedTreeControl } from '@angular/cdk/tree';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { Router } from '@angular/router';
import { BibliografiaIdService, BibliografiaItem, MateriaBibliografia } from '../../../../services/bibliografia-id.service';

interface BibliografiaNode {
  name: string;
  id?: number;
  children?: BibliografiaNode[];
  count?: number; // Quantidade de bibliografias na matéria
}

@Component({
  selector: 'app-bibliografia-id',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTreeModule, MatIconModule, MatButtonModule],
  templateUrl: './bibliografia-id.html',
  styleUrl: './bibliografia-id.scss'
})
export class BibliografiaId implements OnInit {
  bibliografias: MateriaBibliografia[] = [];
  treeControl = new NestedTreeControl<BibliografiaNode>((node) => node.children || []);
  dataSource = new MatTreeNestedDataSource<BibliografiaNode>();
  isLoading = true;
  errorMessage = '';

  constructor(
    private bibliografiaIdService: BibliografiaIdService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.bibliografiaIdService.getBibliografiasGroupedByMateria().subscribe({
      next: (data: MateriaBibliografia[]) => {
        this.bibliografias = data;
        const treeData = this.bibliografias.map((mat: MateriaBibliografia) => ({
          name: mat.materia,
          count: mat.itens.length,
          children: mat.itens.map((item: BibliografiaItem) => ({
            name: `${item.titulo} — ${item.autor}`,
            id: item.id
          }))
        }));
        this.dataSource.data = treeData;
        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('Erro ao carregar bibliografias:', error);
        this.errorMessage = 'Não foi possível carregar a bibliografia.';
        this.isLoading = false;
      }
    });
  }

  hasChild = (_: number, node: BibliografiaNode) => !!node.children && node.children.length > 0;

  getBibliografiaCount(node: BibliografiaNode): number {
    return node.count || 0;
  }

  navigateHome(): void {
    this.router.navigate(['/home']);
  }
}
