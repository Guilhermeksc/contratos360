import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

/**
 * Guard funcional que protege rotas exigindo autenticação
 * Redireciona para /login se o usuário não estiver autenticado
 */
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  // Redireciona para login e salva a URL que o usuário tentou acessar
  router.navigate(['/login'], { 
    queryParams: { returnUrl: state.url } 
  });
  return false;
};
