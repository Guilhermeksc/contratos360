import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { environment } from '../environments/environment';

export interface User {
  id: number;
  username: string;
  perfil: string;
  is_staff: boolean;
  is_active: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  private tokenSubject = new BehaviorSubject<string | null>(null);

  currentUser$ = this.currentUserSubject.asObservable();
  token$ = this.tokenSubject.asObservable();

  constructor(private http: HttpClient) {
    // Carrega token do localStorage se existir
    const token = localStorage.getItem('accessToken');
    const userStr = localStorage.getItem('currentUser');
    
    if (token) {
      this.tokenSubject.next(token);
    }
    
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        this.currentUserSubject.next(user);
      } catch (error) {
        console.warn('Erro ao carregar dados do usuário do localStorage:', error);
        localStorage.removeItem('currentUser');
      }
    }
  }

  /**
   * Realiza login do usuário
   */
  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login/`, credentials);
  }

  /**
   * Realiza logout do usuário
   */
  logout(): void {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
    this.tokenSubject.next(null);
  }

  /**
   * Salva tokens após login
   */
  setTokens(access: string, refresh: string, user?: User): void {
    localStorage.setItem('accessToken', access);
    localStorage.setItem('refreshToken', refresh);
    this.tokenSubject.next(access);
    
    if (user) {
      localStorage.setItem('currentUser', JSON.stringify(user));
      this.currentUserSubject.next(user);
    }
  }

  /**
   * Retorna o token atual
   */
  getToken(): string | null {
    return localStorage.getItem('accessToken');
  }

  /**
   * Verifica se o usuário está autenticado
   */
  isAuthenticated(): boolean {
    const token = this.getToken();
    return !!token; // TODO: Adicionar verificação de expiração
  }

  /**
   * Atualiza token usando refresh token
   */
  refreshToken(): Observable<{ access: string }> {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      return new Observable(observer => {
        observer.error(new Error('No refresh token available'));
      });
    }
    return this.http.post<{ access: string }>(`${this.apiUrl}/token/refresh/`, {
      refresh: refreshToken
    });
  }
}