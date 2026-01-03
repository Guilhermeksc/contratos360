import { BreakpointObserver } from '@angular/cdk/layout';
import { Component, ViewChild, computed, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenav, MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Router, RouterOutlet } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { SideMenu } from './side-menu/side-menu';
import { NgIf } from '@angular/common';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { AuthService } from '../../services/auth.service';

type DeviceType = 'mobile' | 'desktop';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    RouterOutlet,
    MatButtonModule,
    MatIconModule,
    MatSidenavModule,
    MatToolbarModule,
    SideMenu,
    NgIf
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
  animations: [
    trigger('topMenuCollapse', [
      state('collapsed', style({
        height: '0px',
        opacity: 0,
        overflow: 'hidden'
      })),
      state('expanded', style({
        height: '*',
        opacity: 1,
        overflow: 'visible'
      })),
      transition('collapsed <=> expanded', [
        animate('300ms ease-in-out')
      ])
    ])
  ]
})
export class HomeComponent {
  @ViewChild(MatSidenav) private readonly drawer?: MatSidenav;

  readonly deviceType = signal<DeviceType>('desktop');
  readonly isTopMenuExpanded = signal(false);
  
  readonly showSideMenu = computed(() => {
    return this.deviceType() === 'desktop';
  });

  readonly showTopMenu = computed(() => {
    return this.deviceType() === 'mobile';
  });

  constructor(
    private readonly breakpointObserver: BreakpointObserver,
    private readonly router: Router,
    private readonly authService: AuthService
  ) {
    // Observar breakpoint: Mobile/Tablet vs Desktop
    this.breakpointObserver
      .observe([
        '(max-width: 1023px)',   // Mobile/Tablet
        '(min-width: 1024px)'    // Desktop
      ])
      .pipe(takeUntilDestroyed())
      .subscribe((state) => {
        if (state.breakpoints['(max-width: 1023px)']) {
          this.deviceType.set('mobile');
          this.drawer?.close();
        } else {
          this.deviceType.set('desktop');
          this.isTopMenuExpanded.set(false);
        }
      });
  }

  toggleTopMenu(): void {
    this.isTopMenuExpanded.update(value => !value);
  }

  closeTopMenu(): void {
    this.isTopMenuExpanded.set(false);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  navigateHome(): void {
    this.router.navigate(['/home']);
  }
}
