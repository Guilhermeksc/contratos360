import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Adiciona token de autenticação se disponível
    const token = this.authService.getToken();
    
    if (token) {
      req = req.clone({
        setHeaders: {
          'Authorization': `Bearer ${token}`
        }
      });
    }

    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        // Se erro 401, tenta renovar token
        if (error.status === 401 && token) {
          return this.authService.refreshToken().pipe(
            switchMap((response) => {
              // Atualiza token e refaz requisição
              this.authService.setTokens(response.access, localStorage.getItem('refreshToken') || '');
              
              const newReq = req.clone({
                setHeaders: {
                  'Authorization': `Bearer ${response.access}`
                }
              });
              
              return next.handle(newReq);
            }),
            catchError(() => {
              // Se falha ao renovar, desloga usuário
              this.authService.logout();
              return throwError(() => error);
            })
          );
        }
        
        return throwError(() => error);
      })
    );
  }
}