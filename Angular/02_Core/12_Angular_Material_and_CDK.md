---
tags: [angular, core, material, cdk, ui-components, theming, overlay, a11y]
aliases: ["Angular Material", "Material Design", "CDK", "Component Dev Kit", "MatTable", "MatDialog"]
status: stable
updated: 2026-05-09
---

# Angular Material and CDK

> [!summary] Goal
> Build professional UIs with Angular Material components and the Component Dev Kit (CDK). Cover theming, common components, overlays, accessibility, drag-and-drop, and virtual scrolling.

## Table of Contents

1. [Setup](#setup)
2. [Component Families](#component-families)
3. [Theming](#theming)
4. [CDK Utilities](#cdk-utilities)
5. [Pitfalls](#pitfalls)

---

## Setup

```bash
ng add @angular/material

# Or manually:
npm install @angular/material @angular/cdk @angular/animations
```

```typescript
// app.config.ts
import { provideAnimations } from '@angular/platform-browser/animations';

export const appConfig: ApplicationConfig = {
  providers: [
    provideAnimations(),
    // provideNoopAnimations() for tests or SSR without animations
  ],
};
```

```typescript
// Import individual components (tree-shakeable)
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTableModule } from '@angular/material/table';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
```

---

## Component Families

### Form Controls

| Component | Purpose | Key directives/properties |
|-----------|---------|--------------------------|
| `MatFormField` | Container for input controls | `appearance="fill"` / `"outline"`, `floatLabel` |
| `MatInput` | Text input | `type`, `matInput` directive |
| `MatSelect` | Dropdown select | `multiple`, `value`, `compareWith` |
| `MatCheckbox` | Boolean checkbox | `indeterminate`, `labelPosition` |
| `MatRadioGroup` / `MatRadioButton` | Radio selection | `color`, `labelPosition` |
| `MatSlideToggle` | On/off toggle | `color`, `labelPosition` |
| `MatSlider` | Range slider | `min`, `max`, `step`, `discrete` |
| `MatDatepicker` | Date picker | Requires `MatDatepickerModule` + `MatNativeDateModule` |

```html
<form [formGroup]="profileForm">
  <mat-form-field appearance="outline">
    <mat-label>Email</mat-label>
    <input matInput formControlName="email" type="email" placeholder="user@example.com">
    <mat-icon matSuffix>email</mat-icon>
    <mat-hint>We'll never share your email</mat-hint>
    <mat-error *ngIf="profileForm.get('email')?.hasError('email')">Invalid email</mat-error>
  </mat-form-field>

  <mat-form-field appearance="fill">
    <mat-label>Role</mat-label>
    <mat-select formControlName="role">
      <mat-option value="admin">Admin</mat-option>
      <mat-option value="user">User</mat-option>
      <mat-option value="viewer">Viewer</mat-option>
    </mat-select>
  </mat-form-field>
</form>
```

### Navigation and Layout

| Component | Purpose |
|-----------|---------|
| `MatSidenav` / `MatSidenavContainer` | Side navigation drawer |
| `MatToolbar` | Top app bar |
| `MatMenu` | Dropdown menus |
| `MatTabs` / `MatTabGroup` | Tabbed navigation |
| `MatExpansionPanel` | Accordion sections |
| `MatStepper` | Multi-step flow (horizontal or vertical) |

### Data Display

| Component | Purpose | Key features |
|-----------|---------|-------------|
| `MatTable` | Tabular data | Columns, sorting (`MatSort`), pagination (`MatPaginator`), filtering |
| `MatTree` | Tree data structure | Nested nodes, expandable |
| `MatCard` | Content card | Header, content, actions, footer |
| `MatList` | Lists of items | Single/multi select, nav lists |
| `MatGridList` | Grid layout | Tile sizing, row/column count |
| `MatBadge` | Badge overlay | Position, color, overlap |

```html
<!-- MatTable with sorting and pagination -->
<table mat-table [dataSource]="dataSource" matSort class="mat-elevation-z2">
  <ng-container matColumnDef="name">
    <th mat-header-cell *matHeaderCellDef mat-sort-header>Name</th>
    <td mat-cell *matCellDef="let user">{{ user.name }}</td>
  </ng-container>

  <ng-container matColumnDef="email">
    <th mat-header-cell *matHeaderCellDef>Email</th>
    <td mat-cell *matCellDef="let user">{{ user.email }}</td>
  </ng-container>

  <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
  <tr mat-row *matRowDef="let row; columns: displayedColumns"></tr>
</table>

<mat-paginator [pageSize]="20" [pageSizeOptions]="[10, 20, 50]" showFirstLastButtons>
</mat-paginator>
```

### Feedback and Overlays

| Component | Purpose | API |
|-----------|---------|-----|
| `MatDialog` | Modal dialogs | `MatDialog.open(Component, { data, width, disableClose })` |
| `MatSnackBar` | Toast notifications | `MatSnackBar.open(message, action, { duration, panelClass })` |
| `MatBottomSheet` | Mobile bottom sheet | `MatBottomSheet.open(Component)` |
| `MatTooltip` | Hover tooltip | `matTooltip="text"`, `matTooltipPosition` |
| `MatProgressSpinner` / `MatProgressBar` | Loading indicators | `mode="indeterminate"`, `diameter`, `color` |

```typescript
// MatDialog
const dialogRef = this.dialog.open(ConfirmDialogComponent, {
  width: '400px',
  data: { title: 'Delete user?', message: 'This action cannot be undone.' },
});

dialogRef.afterClosed().subscribe(result => {
  if (result) this.userService.delete(id);
});

// MatSnackBar
this.snackBar.open('User saved', 'Undo', { duration: 3000 })
  .onAction().subscribe(() => this.userService.undoDelete());
```

---

## Theming

### Pre-built themes

```scss
// styles.scss
@use '@angular/material' as mat;

// Choose a pre-built theme
@include mat.core();
@include mat.all-component-themes(mat.$indigo-pink-theme);
// Alternatives: $deeppurple-amber-theme, $pink-bluegrey-theme, $purple-green-theme
```

### Custom theme

```scss
@use '@angular/material' as mat;

@include mat.core();

// Define palettes
$my-primary: mat.define-palette(mat.$indigo-palette, 500);
$my-accent: mat.define-palette(mat.$pink-palette, A200, A100, A400);
$my-warn: mat.define-palette(mat.$red-palette);

// Define theme
$my-theme: mat.define-light-theme((
  color: (primary: $my-primary, accent: $my-accent, warn: $my-warn),
  typography: mat.define-typography-config(),
  density: 0,
));

// Apply
@include mat.all-component-themes($my-theme);
```

### Dark theme

```scss
$my-dark-theme: mat.define-dark-theme((
  color: (primary: $my-primary, accent: $my-accent, warn: $my-warn),
));

.dark-theme {
  @include mat.all-component-colors($my-dark-theme);
}
```

```html
<body [class.dark-theme]="isDarkMode">
  <app-root></app-root>
</body>
```

### Form field appearance comparison

| `appearance` | Look | Style |
|-------------|------|-------|
| `"fill"` | Filled background, border bottom | Default — Material Design standard |
| `"outline"` | Outlined border | Modern, preferred for most apps |

---

## CDK Utilities

The Component Dev Kit provides behavior without Material's visual styling:

### Overlay

```typescript
import { Overlay, OverlayRef } from '@angular/cdk/overlay';
import { ComponentPortal } from '@angular/cdk/portal';

@Component({...})
export class OverlayExample {
  private overlay = inject(Overlay);
  private overlayRef: OverlayRef | null = null;

  openOverlay() {
    const positionStrategy = this.overlay.position()
      .global()
      .centerHorizontally()
      .centerVertically();

    this.overlayRef = this.overlay.create({
      positionStrategy,
      hasBackdrop: true,
      backdropClass: 'cdk-overlay-dark-backdrop',
    });

    const portal = new ComponentPortal(MyOverlayComponent);
    this.overlayRef.attach(portal);
  }

  close() {
    this.overlayRef?.detach();
  }
}
```

### Accessibility (A11y)

```typescript
import { A11yModule, LiveAnnouncer } from '@angular/cdk/a11y';
import { FocusMonitor } from '@angular/cdk/a11y';

@Component({...})
export class A11yExample {
  private liveAnnouncer = inject(LiveAnnouncer);
  private focusMonitor = inject(FocusMonitor);

  announceMessage(msg: string) {
    this.liveAnnouncer.announce(msg, 'polite');
    // 'polite' — waits for current speech to finish
    // 'assertive' — interrupts current speech
  }

  ngAfterViewInit() {
    // Monitor focus on an element
    this.focusMonitor.monitor(this.myElement)
      .subscribe(origin => console.log('Focus origin:', origin));
  }
}
```

### Clipboard

```typescript
import { Clipboard } from '@angular/cdk/clipboard';

@Component({...})
export class CopyExample {
  private clipboard = inject(Clipboard);

  copyText(text: string) {
    this.clipboard.copy(text);
    // Returns true/false based on success
  }
}
```

### Drag and Drop

```typescript
import { DragDropModule } from '@angular/cdk/drag-drop';

@Component({
  template: `
    <div cdkDropList (cdkDropListDropped)="drop($event)" class="list">
      <div *ngFor="let item of items" cdkDrag>{{ item }}</div>
    </div>
  `,
  imports: [DragDropModule],
})
export class DragExample {
  items = ['Item 1', 'Item 2', 'Item 3'];

  drop(event: CdkDragDrop<string[]>) {
    moveItemInArray(this.items, event.previousIndex, event.currentIndex);
  }
}
```

| CDK Feature | Module | Use case |
|-------------|--------|---------|
| **Overlay** | `OverlayModule` | Custom modals, dropdowns, tooltips, context menus |
| **A11y** | `A11yModule` | Live announcer, focus monitoring, FocusTrap |
| **Clipboard** | `ClipboardModule` | Copy to clipboard |
| **DragDrop** | `DragDropModule` | Reorderable lists, drag-to-reorder tables |
| **Layout** | `LayoutModule` | `BreakpointObserver` for responsive design |
| **Stepper** | `StepperModule` | Custom multi-step flows (without Material styling) |
| **Tree** | `TreeModule` | Nested tree data structures |
| **Table** | `TableModule` | Low-level table (without Material styling) |
| **Text field** | `TextFieldModule` | Auto-resize textareas |
| **Portal** | `PortalModule` | Dynamic component rendering in templates |
| **Scrolling** | `ScrollingModule` | Virtual scrolling (`cdk-virtual-scroll-viewport`) |
| **Platform** | `PlatformModule` | Detect browser/platform info |

### Virtual scrolling

```html
<cdk-virtual-scroll-viewport itemSize="50" class="viewport" minBufferPx="200" maxBufferPx="400">
  <div *cdkVirtualFor="let item of largeList" class="item">
    {{ item.name }}
  </div>
</cdk-virtual-scroll-viewport>
```

```scss
.viewport {
  height: 400px;
  border: 1px solid #ccc;
}
```

---

## Pitfalls

### Importing entire module instead of individual ones

```typescript
// ❌ Bad — imports ALL Material components
import { MatComponentsModule } from './mat-components.module';

// ✅ Good — tree-shakeable individual imports
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
```

**Fix**: Always import individual `Mat*Module` for each component you use. Angular CLI's `ng generate @angular/material:material-nav --name nav` auto-imports only what's needed.

### Forgetting `MatFormField` wraps `MatInput`

```html
<!-- ❌ Won't work — matInput needs mat-form-field parent -->
<input matInput placeholder="Name" />

<!-- ✅ Correct -->
<mat-form-field>
  <mat-label>Name</mat-label>
  <input matInput />
</mat-form-field>
```

### Not providing MatNativeDateModule for datepicker

```typescript
// ❌ Missing — datepicker won't open
import { MatDatepickerModule } from '@angular/material/datepicker';

// ✅ Need MatNativeDateModule (or custom DateAdapter)
import { MatNativeDateModule } from '@angular/material/core';
```

### CDK overlay stacking issues

Multiple overlays (dialog + snackbar + tooltip) can stack in unexpected order. Use `OverlayRef.setProperty('z-index', value)` or configure stacking order in the global overlay config.

---

> [!question]- Interview Questions
>
> **Q: What is the difference between Angular Material and the CDK?**
> A: Angular Material provides styled components following Material Design. The CDK provides behavior primitives (overlay, drag-drop, a11y, virtual scroll) without any styling — you can build custom components with CDK behaviors.
>
> **Q: How do you create a custom theme in Angular Material?**
> A: Use `mat.define-palette()` to define primary/accent/warn palettes, pass them to `mat.define-light-theme()` or `mat.define-dark-theme()`, then call `@include mat.all-component-themes($theme)`.
>
> **Q: How do you handle drag-and-drop with the CDK?**
> A: Add `cdkDropList` to the container and `cdkDrag` to each draggable item. Handle the `(cdkDropListDropped)` event to update the array with `moveItemInArray()` or `transferArrayItem()`.
>
> **Q: What is the purpose of the Overlay CDK?**
> A: The Overlay CDK creates floating elements (modals, dropdowns, tooltips, menus) that are positioned relative to a trigger element or globally. It handles scroll blocking, backdrop, and z-index stacking. Material's `MatDialog`, `MatSnackBar`, and `MatMenu` all use the Overlay CDK internally.
>
> **Q: How do you make a Material table sortable?**
> A: Add `matSort` directive to the table, `mat-sort-header` to each sortable column header, and set `MatSort` as the `sort` property of the `MatTableDataSource`.

---

## Cross-Links

- [[Angular/02_Core/05_Forms_Template_vs_Reactive]] for integrating Material form controls with reactive forms
- [[Angular/02_Core/08_Styling_and_View_Encapsulation]] for theme SCSS configuration
- [[Angular/03_Advanced/02_Testing_Angular_Components]] for testing Material components with harnesses
- [[Angular/01_Foundations/02_Components_Templates_and_Data_Binding]] for template rendering contexts
