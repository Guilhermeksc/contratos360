import { Component } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { CommonModule } from '@angular/common';
import { AuthService, LoginRequest } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule, 
    MatCardModule, 
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatSnackBarModule
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  loginForm: FormGroup;
  isLoading = false;
  hidePassword = true;

  constructor(
    private readonly router: Router,
    private readonly route: ActivatedRoute,
    private readonly formBuilder: FormBuilder,
    private readonly authService: AuthService,
    private readonly snackBar: MatSnackBar
  ) {
    this.loginForm = this.formBuilder.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid && !this.isLoading) {
      this.isLoading = true;
      
      const credentials: LoginRequest = {
        username: this.loginForm.value.username,
        password: this.loginForm.value.password
      };

      this.authService.login(credentials).subscribe({
        next: (response) => {
          // Salva os tokens e dados do usuário
          this.authService.setTokens(response.access, response.refresh, response.user);
          
          // Mostra mensagem de sucesso
          this.snackBar.open('✅ Login realizado com sucesso!', 'Fechar', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          
          // Obtém a URL de retorno dos query params ou usa /home como padrão
          const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/home';
          
          // Navega para a URL de retorno ou home
          this.router.navigateByUrl(returnUrl);
        },
        error: (error) => {
          console.error('Erro no login:', error);
          let errorMessage = 'Erro no login. Verifique suas credenciais.';
          
          if (error.error?.detail) {
            errorMessage = error.error.detail;
          } else if (error.error?.non_field_errors) {
            errorMessage = error.error.non_field_errors[0];
          }
          
          this.snackBar.open(errorMessage, 'Fechar', {
            duration: 5000,
            panelClass: ['error-snackbar']
          });
          
          this.isLoading = false;
        }
      });
    } else {
      // Marca todos os campos como tocados para mostrar erros
      this.loginForm.markAllAsTouched();
    }
  }

  togglePasswordVisibility(): void {
    this.hidePassword = !this.hidePassword;
  }

  navigateToHome(): void {
    this.router.navigate(['/home']);
  }

  // Getters para facilitar acesso aos controles do formulário
  get username() {
    return this.loginForm.get('username');
  }

  get password() {
    return this.loginForm.get('password');
  }
}
