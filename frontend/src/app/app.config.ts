import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from '@angular/core';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withFetch, withInterceptors, HttpInterceptorFn, HttpErrorResponse, HTTP_INTERCEPTORS } from '@angular/common/http';
import { catchError, from, switchMap, throwError } from 'rxjs';

import { routes } from './app.routes';
import { environment } from './environments/environment';

// Functional interceptor para Angular standalone
// Nota: Como não podemos injetar serviços diretamente em interceptors funcionais,
// usamos localStorage diretamente e fetch para refresh token (evita dependência circular)
const authInterceptorFn: HttpInterceptorFn = (req, next) => {
  // Obtém token do localStorage diretamente
  const token = localStorage.getItem('accessToken');
  
  // Adiciona token de autenticação se disponível
  if (token) {
    req = req.clone({
      setHeaders: {
        'Authorization': `Bearer ${token}`
      }
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Se erro 401, tenta renovar token
      if (error.status === 401 && token) {
        const refreshToken = localStorage.getItem('refreshToken');
        
        if (!refreshToken) {
          // Se não tem refresh token, limpa dados e redireciona
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('currentUser');
          window.location.href = '/login';
          return throwError(() => error);
        }

        // Faz requisição para renovar token usando fetch (evita dependência circular com HttpClient)
        const apiUrl = environment.apiUrl.replace('/api', '');
        const refreshPromise = fetch(`${apiUrl}/auth/token/refresh/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ refresh: refreshToken })
        }).then(response => {
          if (!response.ok) {
            throw new Error('Failed to refresh token');
          }
          return response.json();
        });

        return from(refreshPromise).pipe(
          switchMap((response: { access: string }) => {
            // Atualiza token no localStorage (o AuthService será atualizado no próximo acesso)
            localStorage.setItem('accessToken', response.access);
            
            // Refaz requisição com novo token
            const newReq = req.clone({
              setHeaders: {
                'Authorization': `Bearer ${response.access}`
              }
            });
            
            return next(newReq);
          }),
          catchError(() => {
            // Se falha ao renovar, limpa dados e redireciona
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('currentUser');
            window.location.href = '/login';
            return throwError(() => error);
          })
        );
      }
      
      return throwError(() => error);
    })
  );
};

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideAnimations(),
    provideHttpClient(
      withFetch(),
      withInterceptors([authInterceptorFn])
    )
  ]
};
