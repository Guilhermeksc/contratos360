import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HomeLandingComponent } from './home-landing.component';
import { Router } from '@angular/router';

describe('HomeLandingComponent', () => {
  let component: HomeLandingComponent;
  let fixture: ComponentFixture<HomeLandingComponent>;
  let mockRouter: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    mockRouter = jasmine.createSpyObj('Router', ['navigate']);
    
    await TestBed.configureTestingModule({
      imports: [HomeLandingComponent],
      providers: [
        { provide: Router, useValue: mockRouter }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(HomeLandingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should navigate when navigateTo is called', () => {
    const path = ['app1-intendencia', 'bibliografia'];
    component.navigateTo(path);
    expect(mockRouter.navigate).toHaveBeenCalledWith(['home', ...path]);
  });
});

