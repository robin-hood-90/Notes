---
tags: [angular, core, directives, structural, attribute, custom, host-binding, host-listener, template-ref, view-container-ref, microsyntax, host-directives]
aliases: ["Angular Directives Deep Dive", "Structural Directives", "Attribute Directives", "Custom Directives", "Host Directives"]
status: stable
updated: 2026-05-11
---

# Directives: Structural, Attribute, and Advanced Patterns

> [!summary] Goal
> Master Angular directives: `@Directive` selector types, `@HostBinding`/`@HostListener` (decorator vs function form), structural directive microsyntax desugaring, `TemplateRef`+`ViewContainerRef` API, directive composition via `hostDirectives`, `@defer` triggers, and directive testing.

## Table of Contents

1. [@Directive Selector Types](#directive-selector-types)
2. [Attribute Directives — Deep Patterns](#attribute-directives--deep-patterns)
3. [Structural Directives — Microsyntax and Internals](#structural-directives--microsyntax-and-internals)
4. [Directive Composition (hostDirectives)](#directive-composition-hostdirectives)
5. [defer Triggers and Templates](#defer-triggers-and-templates)
6. [Directive Testing](#directive-testing)

---

## `@Directive` Selector Types

> [!info] Directive selector
> The `selector` defines which DOM elements the directive applies to. Selectors follow CSS selector syntax with extensions for attribute bindings.

| Selector | Matches | Example |
|:---------|:--------|:--------|
| `[appHighlight]` | Elements with attribute `appHighlight` | `<div appHighlight>` |
| `.my-class` | Elements with CSS class `my-class` | `<div class="my-class">` |
| `button[appConfirm]` | `<button>` elements with the attribute | `<button appConfirm>` |
| `:not(.ignore)` | Elements NOT matching `.ignore` | Bypass the directive |
| `[appColor="red"]` | Elements with exact attribute value | `<div appColor="red">` |
| `[dir]` | All elements (too broad — avoid) | Any element |

```typescript
@Directive({
  selector: '[appHighlight]',    // Attribute selector — most common
  standalone: true,
})
export class HighlightDirective { /* ... */ }
```

---

## Attribute Directives — Deep Patterns

### `@HostBinding` — decorator vs function form

```typescript
// Decorator form (simpler for common cases):
@Directive({ selector: '[appHighlight]', standalone: true })
export class HighlightDirective {
  @HostBinding('style.backgroundColor') bgColor?: string;
  @HostBinding('class.active') isActive = false;
  @HostBinding('attr.aria-label') label = 'highlighted element';
  @HostBinding('style.padding.px') padding = 8;          // Unit suffix
}

// Function form (more flexible — use when you need logic):
@Directive({ selector: '[appHighlight]', standalone: true })
export class HighlightDirective {
  private hostElement = inject(ElementRef).nativeElement as HTMLElement;

  constructor() {
    // @HostBinding function — can include conditions
    HostBinding('style.backgroundColor')
    get bgColor() { return this.isActive ? this.highlightColor : 'transparent'; }

    // Fallback: set directly on init
    setStyle();
  }
}
```

### `@HostListener` — event targets and `$event`

```typescript
@Directive({ selector: '[appHighlight]', standalone: true })
export class HighlightDirective {
  @HostListener('mouseenter', ['$event']) onMouseEnter(event: MouseEvent) { }
  @HostListener('mouseleave') onMouseLeave() { }
  @HostListener('window:keydown.escape') onEscape() { }     // Global keydown
  @HostListener('document:click', ['$event.target']) onDocClick(target: HTMLElement) { }
  @HostListener(':mouseenter') onSelfEnter() { }             // ':' = self
}
```

### `exportAs` — template variable access

```typescript
@Directive({
  selector: '[appCountdown]',
  exportAs: 'countdown',          // Makes directive accessible in template
  standalone: true,
})
export class CountdownDirective {
  secondsLeft = 10;
  start() { /* timer logic */ }
}
```
```html
<div appCountdown #timer="countdown">
  {{ timer.secondsLeft }}
  <button (click)="timer.start()">Start</button>
</div>
```

---

## Structural Directives — Microsyntax and Internals

> [!info] Structural directive
> Structural directives change the DOM layout by adding/removing elements. They use the `*` prefix, which is syntactic sugar for `<ng-template>` binding. The `*` desugars into an `<ng-template>` with the directive applied.

### Microsyntax desugaring

```html
<!-- Shorthand (what you write): -->
<div *ngFor="let user of users; trackBy: trackFn; index as i">{{ user.name }}</div>

<!-- Desugared (what Angular generates): -->
<ng-template ngFor [ngForOf]="users" [ngForTrackBy]="trackFn" let-user="$implicit" let-i="index">
  <div>{{ user.name }}</div>
</ng-template>
```

```html
<!-- *ngIf desugaring: -->
<div *ngIf="isVisible; else loading">Content</div>
<ng-template #loading>Loading...</ng-template>

<!-- Becomes: -->
<ng-template [ngIf]="isVisible" [ngIfElse]="loading">
  <div>Content</div>
</ng-template>
```

### `TemplateRef` and `ViewContainerRef` — custom structural directive

```typescript
import { Directive, Input, TemplateRef, ViewContainerRef, inject } from '@angular/core';

@Directive({
  selector: '[appIfNot]',
  standalone: true,
})
export class IfNotDirective {
  private templateRef = inject(TemplateRef<any>);
  private vcr = inject(ViewContainerRef);
  private hasView = false;

  @Input() set appIfNot(condition: boolean) {
    if (!condition && !this.hasView) {
      this.vcr.createEmbeddedView(this.templateRef);
      this.hasView = true;
    } else if (condition && this.hasView) {
      this.vcr.clear();
      this.hasView = false;
    }
  }

  // With context object (let-x pattern):
  @Input() set appIfNotElse(template: TemplateRef<any>) {
    // Store alternate template
  }
}
```
```html
<div *appIfNot="isDisabled">Shown when isDisabled is false</div>
```

### Context objects — `let-x` from directive

```typescript
@Directive({ selector: '[appRepeat]', standalone: true })
export class RepeatDirective {
  constructor(
    private templateRef: TemplateRef<{ $implicit: number; index: number }>,
    private vcr: ViewContainerRef,
  ) {}

  private _count = 0;
  @Input() set appRepeat(count: number) {
    this.vcr.clear();
    for (let i = 0; i < count; i++) {
      this.vcr.createEmbeddedView(this.templateRef, {
        $implicit: i + 1,      // let-value = $implicit
        index: i,              // let-idx = index
      });
    }
  }
}
```
```html
<div *appRepeat="5; let value; let idx = index">
  Item {{ idx }}: {{ value }}
</div>
<!-- Output: Item 0: 1, Item 1: 2, etc. -->
```

### `trackBy` deep

```typescript
// Without trackBy — re-renders ALL items on every change
<div *ngFor="let user of users">{{ user.id }}</div>

// With trackBy — only re-renders changed items
<div *ngFor="let user of users; trackBy: trackById">{{ user.id }}</div>

trackById(index: number, user: User): string {
  return user.id;   // Unique identifier
}
// Using a primitive ID lets Angular reuse DOM elements
// rather than destroying/recreating them — significant perf gain
```

---

## Directive Composition (`hostDirectives`)

> [!info] Host directives
> `hostDirectives` allows a component or directive to apply another directive to its host element. This is the Angular composition API — compose behavior from smaller directives without inheritance.

```typescript
// Composable behavior directives:
@Directive({ selector: '[appTooltip]', standalone: true })
export class TooltipDirective { /* tooltip logic */ }

@Directive({ selector: '[appClickOutside]', standalone: true })
export class ClickOutsideDirective { /* click outside logic */ }

// Compose both into a dropdown:
@Component({
  selector: 'app-dropdown',
  standalone: true,
  hostDirectives: [
    TooltipDirective,
    {
      directive: ClickOutsideDirective,
      inputs: ['appClickOutside: closeOnOutsideClick' ],
    },
  ],
  template: `...`
})
export class DropdownComponent { }

// Now <app-dropdown> has tooltip + click-outside behavior
```

---

## `@defer` Triggers and Templates

> [!info] Deferred loading
> `@defer` (Angular 17+) lazy-loads a block of templates. It supports triggers (`on viewport`, `on interaction`, `on idle`, `on immediate`, `on timer`) and placeholder/loading/error states.

```html
<!-- @defer with triggers -->
@defer (on viewport) {
  <heavy-component />
} @placeholder {
  <p>Scroll here to load</p>
}

@defer (on interaction) {
  <comment-section />
} @placeholder {
  <button>Load comments</button>
}

@defer (on timer(5s)) {
  <analytics-widget />
}

@defer (on immediate) {
  <above-the-fold-widget />
}

<!-- With loading and error states -->
@defer (on viewport; prefetch on idle) {
  <full-calendar />
} @loading {
  <spinner />
} @error {
  <p>Failed to load calendar</p>
}
```

---

## Directive Testing

```typescript
import { TestBed, ComponentFixture } from '@angular/core/testing';
import { Component, DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { HighlightDirective } from './highlight.directive';

// Test host component
@Component({
  standalone: true,
  imports: [HighlightDirective],
  template: `<p appHighlight="yellow" [class.active]="isActive">Test</p>`
})
class TestHostComponent { isActive = true; }

describe('HighlightDirective', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let pEl: DebugElement;

  beforeEach(() => {
    fixture = TestBed.configureTestingModule({
      imports: [HighlightDirective, TestHostComponent],
    }).createComponent(TestHostComponent);
    fixture.detectChanges();
    pEl = fixture.debugElement.query(By.css('[appHighlight]'));
  });

  it('should set background on mouseenter', () => {
    pEl.triggerEventHandler('mouseenter');
    fixture.detectChanges();
    expect(pEl.nativeElement.style.backgroundColor).toBe('yellow');
  });

  it('should clear background on mouseleave', () => {
    pEl.triggerEventHandler('mouseenter');
    fixture.detectChanges();
    pEl.triggerEventHandler('mouseleave');
    fixture.detectChanges();
    expect(pEl.nativeElement.style.backgroundColor).toBe('');
  });
});
```

---

## Cross-Links

- [[Angular/02_Core/05_Forms_Template_vs_Reactive]] for structural directives in forms
- [[Angular/03_Advanced/01_Change_Detection_and_Performance]] for change detection with trackBy
- [[Angular/03_Advanced/02_Testing_Angular_Components]] for component test setup
- [[Angular/01_Foundations/02_Components_Templates_and_Data_Binding]] for `@defer` and `ng-template`
