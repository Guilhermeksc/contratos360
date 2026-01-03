import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-side-nav',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule],
  templateUrl: './side-nav.component.html',
  styleUrl: './side-nav.component.scss'
})
export class SideNavComponent implements OnInit {
  activeRoute = signal<string>('');

  navItems = [
    { icon: 'dashboard', label: 'Home', route: '/', tooltip: 'Home' },
    { icon: 'description', label: 'Contratos', route: '/contratos', tooltip: 'Contratos' },
    { icon: 'folder', label: 'Atas', route: '/atas', tooltip: 'Atas' }
  ];

  constructor(
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.router.events.subscribe(() => {
      this.activeRoute.set(this.router.url.split('?')[0]);
    });
    this.activeRoute.set(this.router.url.split('?')[0]);
  }

  navigate(route: string): void {
    this.router.navigate([route]);
  }

  isActive(route: string): boolean {
    if (route === '/') {
      return this.activeRoute() === '/' || this.activeRoute() === '/home';
    }
    return this.activeRoute().startsWith(route);
  }
}

