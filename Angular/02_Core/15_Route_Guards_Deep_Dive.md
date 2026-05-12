---
tags: [angular, core, routing, guards, can-activate, can-deactivate, can-match, route-guards, lazy-loading, resolvers]
aliases: ["Angular Route Guards", "CanActivateFn", "CanDeactivateFn", "CanMatchFn", "Route Resolvers", "Guard Testing"]
status: stable
updated: 2026-05-11
---

# Route Guards Deep Dive

> [!summary] Goal
> Master Angular route guards: `CanActivateFn` (route entry), `CanActivateChildFn` (child protection), `CanDeactivateFn` (unsaved changes), `CanMatchFn` (conditional lazy loading), guard composition, `inject()` inside guards, `UrlTree` redirects, and guard testing.

## Table of Contents

1. [Guard Types](#guard-types)
2. [Guard Composition and Execution Order](#guard-composition-and-execution-order)
3. [Functional Guards with inject()](#functional-guards-with-inject)
4. [Route Resolvers (ResolveFn)](#route-resolvers-resolvefn)
5. [Guard Testing](#guard-testing)

---

## Guard Types

> [!info] Route guard
> A route guard controls whether the router allows navigation to/from a route. Guards return `true` (allow), `false` (block), or `UrlTree` (redirect). Functional guards (`CanActivateFn`, etc.) are preferred over class-based guards.

### `CanActivateFn` — allow/deny route entry

```typescript
import { inject } from '@angular/core';
import { CanActivateFn, Router, UrlTree } from '@angular/router';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = (route, state): boolean | UrlTree => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isLoggedIn()) return true;

  // Redirect to login with return URL
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};

// In route config:
{
  path: 'dashboard',
  loadComponent: () => import('./dashboard/dashboard.component'),
  canActivate: [authGuard],
}
```

### `CanActivateChildFn` — protect child routes

```typescript
export const childGuard: CanActivateChildFn = (childRoute, state) => {
  const permissions = inject(PermissionsService);
  return permissions.hasAccess(childRoute.routeConfig?.path ?? '');
};

// In route config:
{
  path: 'admin',
  canActivateChild: [childGuard],
  children: [
    { path: 'users', component: UsersComponent },
    { path: 'settings', loadComponent: () => import('./settings.component') },
  ],
}
```

### `CanDeactivateFn` — confirm navigation away

```typescript
// Interface for the component to implement
export interface CanComponentDeactivate {
  canDeactivate: () => boolean | Observable<boolean> | Promise<boolean>;
}

export const unsavedChangesGuard: CanDeactivateFn<CanComponentDeactivate> = (
  component, currentRoute, currentState, nextState
) => {
  if (component.canDeactivate) {
    return component.canDeactivate();  // Component decides
  }
  return true;  // No guard method → allow navigation
};

// Component implements the interface:
@Component({ ... })
export class EditUserComponent implements CanComponentDeactivate {
  hasUnsavedChanges = false;

  canDeactivate(): boolean {
    if (!this.hasUnsavedChanges) return true;
    return confirm('You have unsaved changes. Discard them?');
  }
}

// Route config:
{
  path: 'users/:id/edit',
  component: EditUserComponent,
  canDeactivate: [unsavedChangesGuard],
}
```

### `CanMatchFn` — conditional lazy loading

```typescript
export const featureFlagGuard: CanMatchFn = (route, segments) => {
  const featureFlags = inject(FeatureFlagService);
  return featureFlags.isEnabled('new-dashboard');
};

// If the guard returns false, Angular tries the next route match.
// Use for: A/B testing, gradual rollout, feature-gated modules.

{
  // Tries this route first:
  path: 'dashboard',
  loadComponent: () => import('./new-dashboard/new-dashboard.component'),
  canMatch: [featureFlagGuard],   // Only matches if feature is ON
},
{
  // Falls back to this route:
  path: 'dashboard',
  loadComponent: () => import('./old-dashboard/old-dashboard.component'),
  // No canMatch — acts as default if the first doesn't match
}
```

---

## Guard Composition and Execution Order

> [!info] Guard composition
> Multiple guards can be specified for a single route. They run **in order** from left to right. If ANY guard returns `false` or `UrlTree`, the rest are skipped and navigation is cancelled/redirected.

```typescript
// Guards run in this order:
{
  path: 'admin',
  canActivate: [authGuard, adminGuard, auditLogGuard],
  // 1. authGuard — is the user logged in?
  // 2. adminGuard — does the user have admin role?
  // 3. auditLogGuard — log this access attempt
}
```

### Guard priority order (CanActivate + CanActivateChild)

```text
Root route → CanActivateChild (parent) → CanActivate (child) → Resolve
  1. The router checks parent's canActivateChild
  2. Then checks child's canActivate
  3. Then runs resolvers
  4. If all pass → activate route

Priority: CanMatch → CanActivateChild → CanActivate → CanDeactivate
  CanMatch is checked first (before loading a lazy module)
```

### `runGuardsAndResolvers` options

```typescript
{
  path: 'users/:id',
  component: UserComponent,
  runGuardsAndResolvers: 'paramsChange',
  // Options:
  //   'paramsChange'           — only when route params change (default)
  //   'paramsOrQueryParamsChange' — params or query params change
  //   'always'                 — always re-run guards/resolvers
  //   'pathParamsChange'       — only path parameters
  // 'pathParamsOrQueryParamsChange' — path or query params
}
```

---

## Functional Guards with `inject()`

> [!info] Injectable guards
> Functional guards (`CanActivateFn`, etc.) use `inject()` to access services. This is the recommended pattern over class-based guards. `inject()` works inside the guard's function body — it does NOT need to be called at the top level.

```typescript
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

// ✅ Correct — inject inside the function body:
export const myGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.isLoggedIn();
};

// ❌ Wrong — inject outside the guard function:
const auth = inject(AuthService);
export const brokenGuard: CanActivateFn = () => auth.isLoggedIn();
// This runs at module load time, not at guard execution time.
```

### Redirect with `UrlTree`

```typescript
export const roleGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isLoggedIn() && auth.hasRole('admin')) return true;

  // Standard redirect:
  if (!auth.isLoggedIn()) return router.parseUrl('/login');

  // Conditional redirect by role:
  if (auth.hasRole('editor')) return router.parseUrl('/editor/dashboard');
  if (auth.hasRole('viewer')) return router.parseUrl('/viewer/dashboard');

  return false;  // Block navigation (shows blank or error)
};
```

---

## Route Resolvers (`ResolveFn`)

> [!info] Resolver
> A resolver fetches data BEFORE the route activates. The resolved data is available via `ActivatedRoute.data`. Resolvers run after guards pass. To show a loading indicator while resolving, use `@defer` or a loading wrapper.

```typescript
import { ResolveFn, ActivatedRouteSnapshot } from '@angular/router';
import { inject } from '@angular/core';
import { UserService } from './user.service';
import { of } from 'rxjs';

export const userResolver: ResolveFn<User> = (route: ActivatedRouteSnapshot) => {
  const userService = inject(UserService);
  const id = route.paramMap.get('id')!;
  return userService.getUser(id);  // Returns Observable<User>
};

// Route config:
{
  path: 'users/:id',
  component: UserDetailComponent,
  resolve: { user: userResolver },
}

// In component — access resolved data:
@Component({ ... })
export class UserDetailComponent {
  private route = inject(ActivatedRoute);
  user = signal<User | null>(null);

  constructor() {
    this.route.data.subscribe(data => this.user.set(data['user']));
    // Or: const user = toSignal(this.route.data.pipe(map(d => d['user'])));
  }
}

// Multiple resolvers run in parallel:
{
  path: 'dashboard',
  component: DashboardComponent,
  resolve: { user: userResolver, orders: ordersResolver, stats: statsResolver },
}
```

---

## Guard Testing

```typescript
import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { Location } from '@angular/common';
import { Component } from '@angular/core';

import { authGuard } from './auth.guard';
import { AuthService } from './auth.service';

@Component({ standalone: true, template: '' })
class DummyComponent {}

describe('authGuard', () => {
  let authService: jasmine.SpyObj<AuthService>;
  let router: Router;
  let location: Location;

  beforeEach(() => {
    authService = jasmine.createSpyObj<AuthService>('AuthService', ['isLoggedIn']);

    TestBed.configureTestingModule({
      imports: [DummyComponent],
      providers: [
        provideRouter([
          { path: 'dashboard', canActivate: [authGuard], component: DummyComponent },
          { path: 'login', component: DummyComponent },
        ]),
        { provide: AuthService, useValue: authService },
      ],
    });

    router = TestBed.inject(Router);
    location = TestBed.inject(Location);
  });

  it('should allow navigation when logged in', async () => {
    authService.isLoggedIn.and.returnValue(true);
    await router.navigate(['/dashboard']);
    expect(location.path()).toBe('/dashboard');
  });

  it('should redirect to login when not logged in', async () => {
    authService.isLoggedIn.and.returnValue(false);
    await router.navigate(['/dashboard']);
    expect(location.path()).toBe('/login');
  });
});
```

---

## Cross-Links

- [[Angular/01_Foundations/04_Routing_Basics]] for routing fundamentals
- [[Angular/02_Core/01_Standalone_Components]] for standalone routing patterns
- [[Angular/02_Core/04_HttpClient_and_Interceptors]] for data fetching in resolvers
- [[Angular/03_Advanced/02_Testing_Angular_Components]] for component test setup
