import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

/**
 * Guard funcional que redireciona usuários autenticados para home
 * Impede que usuários já logados acessem a página de login
 */
export const loginGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    // Se já está autenticado, redireciona para home
    router.navigate(['/home']);
    return false;
  }

  // Permite acesso à página de login se não estiver autenticado
  return true;
};
