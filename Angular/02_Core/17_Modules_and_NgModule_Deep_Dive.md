---
tags: [angular, core, modules, ngmodule, shared-module, feature-module, core-module, forRoot, lazy-loading, migration]
aliases: ["Angular Modules", "NgModule Deep Dive", "Module Types", "forRoot forChild", "Module to Standalone Migration"]
status: stable
updated: 2026-05-11
---

# Modules and `NgModule` Deep Dive

> [!summary] Goal
> Master Angular `NgModule` (legacy but widely used): `@NgModule` decorator API, module types (feature, shared, core, routing), `forRoot()`/`forChild()` pattern, lazy loading with `loadChildren`, providers scope, module vs standalone comparison, and step-by-step migration to standalone.

## Table of Contents

1. [NgModule API](#ngmodule-api)
2. [Module Types (Feature, Shared, Core, Routing)](#module-types-feature-shared-core-routing)
3. [forRoot and forChild Pattern](#forroot-and-forchild-pattern)
4. [Lazy Loading with NgModules](#lazy-loading-with-ngmodules)
5. [Module vs Standalone Comparison](#module-vs-standalone-comparison)
6. [Migration: Module to Standalone](#migration-module-to-standalone)

---

## `NgModule` API

> [!info] NgModule
> `@NgModule` is a decorator that organizes code into cohesive blocks. It declares components, pipes, and directives that belong together, and makes them available to other modules via imports/exports.

```typescript
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterModule, Routes } from '@angular/router';

import { UsersComponent } from './users.component';
import { UserDetailComponent } from './user-detail.component';
import { SharedModule } from '../shared/shared.module';
import { UppercasePipe } from './uppercase.pipe';
import { HighlightDirective } from './highlight.directive';

const routes: Routes = [
  { path: '', component: UsersComponent },
  { path: ':id', component: UserDetailComponent },
];

@NgModule({
  declarations: [
    UsersComponent,          // Components belonging to this module
    UserDetailComponent,      // (MUST be declared exactly once)
    UppercasePipe,            // Pipes
    HighlightDirective,       // Directives
  ],
  imports: [
    CommonModule,             // *ngIf, *ngFor, async, date, etc.
    ReactiveFormsModule,      // FormGroup, FormControl
    RouterModule.forChild(routes),  // Child routes
    SharedModule,             // Reusable shared components
  ],
  exports: [
    UsersComponent,           // Make available to importing modules
    UppercasePipe,            // Export pipe for use in other modules
  ],
  providers: [
    // Services scoped to this module (rare — prefer providedIn: 'root')
  ],
  bootstrap: [],             // Only in AppModule (root module)
})
export class UsersModule {}
```

### `@NgModule` properties

| Property | Purpose | Typically contains |
|:---------|:--------|:------------------|
| `declarations` | What belongs to this module | Components, directives, pipes (ONLY here) |
| `imports` | What this module needs | Other modules: `CommonModule`, `FormsModule`, `RouterModule.forChild()` |
| `exports` | What others can use | Components/pipes/directives that other modules need |
| `providers` | Services available to this module | `Injectable` services, `APP_INITIALIZER`, `HTTP_INTERCEPTORS` |
| `bootstrap` | Root component to launch | `AppComponent` (only in `AppModule`) |
| `schemas` | Shorthand for custom elements | `CUSTOM_ELEMENTS_SCHEMA`, `NO_ERRORS_SCHEMA` |

---

## Module Types (Feature, Shared, Core, Routing)

> [!info] Module organization
> Large Angular applications organize modules by type. Each type has a specific purpose and import/export pattern.

### Feature module

```typescript
@NgModule({
  declarations: [UsersComponent, UserListComponent],
  imports: [CommonModule, ReactiveFormsModule, SharedModule, RouterModule.forChild(routes)],
  exports: [],                       // Usually empty — feature is self-contained
})
export class UsersModule {}
// Loaded via lazy route: { path: 'users', loadChildren: () => import('./users/users.module').then(m => m.UsersModule) }
```

### Shared module

```typescript
@NgModule({
  declarations: [AvatarComponent, StatusBadgeComponent, TruncatePipe, HighlightDirective],
  imports: [CommonModule],
  exports: [
    // Re-export CommonModule so importers only need SharedModule:
    CommonModule,
    AvatarComponent, StatusBadgeComponent, TruncatePipe, HighlightDirective,
  ],
})
export class SharedModule {}
// Import in every feature module: imports: [SharedModule]
```

### Core module

```typescript
@NgModule({
  providers: [
    AuthService,
    LoggerService,
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
    { provide: APP_INITIALIZER, useFactory: appInitFactory, multi: true, deps: [ConfigService] },
  ],
  imports: [CommonModule],
  exports: [NavbarComponent, FooterComponent],  // Layout components used in AppModule
})
export class CoreModule {}
// Import ONCE in AppModule:
@NgModule({ imports: [CoreModule], bootstrap: [AppComponent] })
export class AppModule {}
```

### Routing module

```typescript
const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'users', loadChildren: () => import('./users/users.module').then(m => m.UsersModule) },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],   // forRoot in AppModule
  exports: [RouterModule],
})
export class AppRoutingModule {}
```

---

## `forRoot()` and `forChild()` Pattern

> [!info] forRoot/forChild
> `forRoot()` configures a module with app-wide singleton providers. `forChild()` adds routes/components without re-creating providers. `RouterModule.forRoot()` is the canonical example — `forRoot` registers the router service once, `forChild` only adds routes.

```typescript
// Custom module with forRoot/forChild:

// config.module.ts
@NgModule({})
export class ConfigModule {
  static forRoot(config: AppConfig): ModuleWithProviders<ConfigModule> {
    return {
      ngModule: ConfigModule,
      providers: [
        { provide: APP_CONFIG, useValue: config },
      ],
    };
  }

  static forChild(): ModuleWithProviders<ConfigModule> {
    return {
      ngModule: ConfigModule,
      providers: [],   // No singleton providers — just the module
    };
  }
}

// AppModule:
@NgModule({
  imports: [ConfigModule.forRoot({ apiUrl: 'https://api.example.com' })],
})
export class AppModule {}

// FeatureModule:
@NgModule({
  imports: [ConfigModule.forChild()],
})
export class FeatureModule {}
```

### `ModuleWithProviders<T>` — type-safe return

```typescript
import { ModuleWithProviders } from '@angular/core';

// ✅ Modern (Angular 15+):
static forRoot(): ModuleWithProviders<ConfigModule> { ... }

// ❌ Legacy (pre-15):
static forRoot(): ModuleWithProviders { ... }
```

---

## Lazy Loading with NgModules

```typescript
// App routing module:
const routes: Routes = [
  { path: '', component: HomeComponent },
  {
    path: 'users',
    loadChildren: () => import('./users/users.module').then(m => m.UsersModule),
    data: { preload: true },
  },
  {
    path: 'reports',
    loadChildren: () => import('./reports/reports.module').then(m => m.ReportsModule),
    canMatch: [featureFlagGuard],   // Only load if feature is enabled
  },
];

// Preloading strategy:
@NgModule({
  imports: [RouterModule.forRoot(routes, {
    preloadingStrategy: PreloadAllModules,   // Preload ALL lazy modules after initial load
    // Or: PreloadingStrategy: QuicklinkStrategy  // Preload based on links in viewport
  })],
  exports: [RouterModule],
})
export class AppRoutingModule {}
```

### `PreloadingStrategy` — custom preloading

```typescript
import { PreloadingStrategy, Route } from '@angular/router';
import { Observable, of, timer } from 'rxjs';

export class CustomPreloadingStrategy implements PreloadingStrategy {
  preload(route: Route, load: () => Observable<any>): Observable<any> {
    if (route.data?.['preload']) {
      return route.data?.['delay']
        ? timer(route.data['delay']).pipe(mergeMap(() => load()))
        : load();
    }
    return of(null);  // Don't preload
  }
}
```

---

## Module vs Standalone Comparison

| Aspect | NgModule | Standalone |
|:-------|:--------:|:----------:|
| **Boilerplate** | High (`@NgModule` needed for each set of components) | Low (no `@NgModule`) |
| **Lazy loading** | `loadChildren` with `NgModule` | `loadComponent` on each route |
| **Shared components** | `SharedModule` exports | Direct `imports` array per component |
| **Providers scope** | Module `providers` | `environmentInjector` via `provide` |
| **Tree-shaking** | Poor (module groups everything) | Good (only imported things bundled) |
| **Learning curve** | Steeper (concepts: declarations, imports, exports) | Gentler (just import what you use) |
| **Testing** | Need `TestBed.configureTestingModule` with module | Same, but simpler imports |
| **Migration path** | — | Use `ng generate @angular/core:standalone` |
| **Route guards** | Class-based (legacy) | Functional (`CanActivateFn`) |
| **Third-party libs** | Most use `NgModule` | Growing list of standalone libs |
| **When to use** | Existing projects, heavy module ecosystems | New projects (Angular 17+ default) |

---

## Migration: Module to Standalone

> [!info] Migration
> Angular provides `ng generate @angular/core:standalone` to convert the entire project. The migration runs component-by-component, pipe-by-pipe, and directive-by-directive.

```bash
# Step 1: Run the migration schematic (automatic):
ng generate @angular/core:standalone

# This will:
# - Convert all components/directives/pipes to standalone: true
# - Move declarations → imports into each component
# - Remove unused NgModules (unless referenced by 3rd-party libs)
# - Replace loadChildren + NgModule with loadComponent
```

### Manual migration — step by step

```typescript
// BEFORE (module-based):
// users.module.ts
@NgModule({
  declarations: [UsersComponent, UserListComponent],
  imports: [CommonModule, ReactiveFormsModule, SharedModule, RouterModule.forChild(routes)],
})
export class UsersModule {}

// AFTER (standalone):
// users.component.ts
@Component({
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, SharedModule, RouterModule],
  // Import directly — no NgModule wrapper needed
})
export class UsersComponent {}

// Route registration changes:
// BEFORE:
{ path: '', loadChildren: () => import('./users/users.module').then(m => m.UsersModule) }
// AFTER:
{ path: '', loadComponent: () => import('./users/users.component').then(c => c.UsersComponent) }

// Shared module replacement:
// BEFORE: imports: [SharedModule]
// AFTER: imports: [AvatarComponent, StatusBadgeComponent, ...]  // Import each component directly
```

---

## Cross-Links

- [[Angular/02_Core/01_Standalone_Components]] for standalone bootstrap pattern
- [[Angular/03_Advanced/07_Migration_Module_to_Standalone]] for full migration guide
- [[Angular/01_Foundations/01_Angular_App_Structure_and_Build]] for project structure
- [[Angular/03_Advanced/06_Angular_CLI_and_Configuration]] for `angular.json` module config
