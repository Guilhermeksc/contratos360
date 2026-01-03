import { Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-home-landing',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule
  ],
  templateUrl: './home-landing.component.html',
  styleUrl: './home-landing.component.scss'
})
export class HomeLandingComponent {
  private authService = inject(AuthService);
  private currentUserSig = toSignal(this.authService.currentUser$, { initialValue: null });

  currentUsername = computed(() => this.currentUserSig()?.username || 'Usuário');
  isAdmin = computed(() => this.currentUserSig()?.perfil === 'admin' || false);

  constructor(private router: Router) {}

  navigateTo(path: string[]): void {
    this.router.navigate(['home', ...path]);
  }

  navigateBibliografiaId(): void {
    this.router.navigate(['/home/bibliografia-id']);
  }

  navigateCronograma(): void {
    this.router.navigate(['/home/cronograma']);
  }

  navigateEstatisticas(): void {
    this.router.navigate(['/home/estatisticas']);
  }
}
