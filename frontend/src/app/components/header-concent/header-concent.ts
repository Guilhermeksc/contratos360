import { Component, Input, OnInit, inject, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ElementRef } from '@angular/core';

@Component({
  selector: 'app-header-concent',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header-concent.html',
  styleUrls: ['./header-concent.scss']
})
export class HeaderConcentComponent implements OnInit {
  @Input() moduleLabel: string = '';
  @Input() moduleEmoji: string = '';
  @Input() title: string = '';

  @Input() showBibliografia: boolean = true;
  @Input() showFlashcards: boolean = true;
  @Input() showMapaMental: boolean = true;
  @Input() showMedia: boolean = true;
  @Input() showPerguntas: boolean = true;
  @Input() showConceitos: boolean = true;

  private router = inject(Router);
  private host = inject(ElementRef);

  private moduleBasePath: string = '/home';
  isMenuOpen: boolean = false;

  ngOnInit() {
    this.computeModuleBase();
  }

  private computeModuleBase() {
    try {
      const url = this.router.url || '';
      const segments = url.split('/').filter(Boolean);
      const homeIndex = segments.indexOf('home');
      if (homeIndex >= 0 && segments.length > homeIndex + 1) {
        const moduleSeg = segments[homeIndex + 1];
        this.moduleBasePath = `/home/${moduleSeg}`;
      } else if (segments.length > 0) {
        this.moduleBasePath = `/${segments[0]}`;
      } else {
        this.moduleBasePath = '/home';
      }
    } catch {
      this.moduleBasePath = '/home';
    }
  }

  toggleMenu() {
    this.isMenuOpen = !this.isMenuOpen;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event) {
    // fecha o menu se o clique for fora do componente
    const target = event.target as Node;
    if (this.isMenuOpen && target && !this.host.nativeElement.contains(target)) {
      this.isMenuOpen = false;
    }
  }

  getPath(segment: string): string {
    if (!segment) return '';
    switch (segment) {
      case 'bibliografia': return `${this.moduleBasePath}/bibliografia`;
      case 'flash-cards': return `${this.moduleBasePath}/flash-cards`;
      case 'mapa-mental': return `${this.moduleBasePath}/mapa-mental`;
      case 'media': return `${this.moduleBasePath}/media`;
      case 'perguntas': return `${this.moduleBasePath}/perguntas`;
      case 'conceitos': return `${this.moduleBasePath}/conceitos`;
      default: return `${this.moduleBasePath}/${segment}`;
    }
  }

  navigateTo(path: string) {
    if (!path) return;
    const segments = path.startsWith('/') ? path.substring(1).split('/') : path.split('/');
    this.router.navigate(segments).catch(err => console.error('Erro ao navegar:', err));
    // fechar menu mobile ao navegar
    this.isMenuOpen = false;
  }
}
