---
tags: [angular, core, pipes, custom-pipes, async-pipe, pure-impure, pipe-testing, i18n]
aliases: ["Angular Pipes Deep Dive", "Built-in Pipes", "Custom Pipes", "Pipe Transform", "async pipe"]
status: stable
updated: 2026-05-11
---

# Pipes: Built-In, Custom, and Deep Dive

> [!summary] Goal
> Master Angular pipes: all built-in pipes with format options, custom `@Pipe` with dependency injection, `| async` with `@let`, stateful vs stateless pipes, performance tuning, and pipe testing.

## Table of Contents

1. [Built-in Pipes Complete Reference](#built-in-pipes-complete-reference)
2. [Custom Pipes](#custom-pipes)
3. [Stateful and Impure Pipes](#stateful-and-impure-pipes)
4. [async Pipe and @let](#async-pipe-and-let)
5. [Pipes in TypeScript](#pipes-in-typescript)
6. [Pipe Testing](#pipe-testing)
7. [Performance Optimization](#performance-optimization)

---

## Built-in Pipes Complete Reference

> [!info] Built-in pipes
> Angular provides 15+ built-in pipes for common transformations. The most used ones are `date`, `currency`, `number`, `async`, `keyvalue`, `json`, `slice`, `i18nPlural`, and `i18nSelect`.

```html
<p>{{ today | date:'medium' }}</p>                    <!-- May 3, 2026, 2:30:00 PM -->
<p>{{ price | currency:'EUR':'symbol':'1.2-2' }}</p>  <!-- €42.99 -->
<p>{{ items | slice:0:3 }}</p>                        <!-- First 3 items -->
<p>{{ data$ | async }}</p>                            <!-- Subscribe to Observable -->
```

### Date formats

```text
Predefined formats:
  'short':    5/3/26, 2:30 PM
  'medium':   May 3, 2026, 2:30:00 PM
  'long':     May 3, 2026 at 2:30:00 PM GMT+5
  'full':     Monday, May 3, 2026 at 2:30:00 PM GMT+05:30
  'shortDate':    5/3/26
  'mediumDate':   May 3, 2026
  'longDate':     May 3, 2026
  'fullDate':     Monday, May 3, 2026
  'shortTime':    2:30 PM
  'mediumTime':   2:30:00 PM
  'longTime':     2:30:00 PM GMT+5
  'fullTime':     2:30:00 PM GMT+05:30

Custom formats:
  {{ today | date:'yyyy-MM-dd' }}        → 2026-05-03
  {{ today | date:'dd/MM/yyyy' }}        → 03/05/2026
  {{ today | date:'EEEE, MMMM d, y' }}   → Monday, May 3, 2026
  {{ today | date:'HH:mm:ss' }}           → 14:30:00

Locale-aware:
  {{ today | date:'medium':'':'fr' }}     → 3 mai 2026, 14:30:00
  {{ today | date:'fullDate':'':'de' }}   → Montag, 3. Mai 2026
```

### Currency and Number formats

```html
<!-- Currency -->
<p>{{ 42.99 | currency }}                      <!-- $42.99 -->
<p>{{ 42.99 | currency:'EUR' }}                <!-- €42.99 -->
<p>{{ 42.99 | currency:'EUR':'code' }}         <!-- EUR42.99 -->
<p>{{ 42.99 | currency:'EUR':'symbol':'1.2-2' }}  <!-- €42.99 -->
<p>{{ 42.99 | currency:'JPY':'symbol':'1.0-0' }}  <!-- ¥43 -->

<!-- Number / Decimal -->
<p>{{ 3.14159 | number:'1.2-2' }}              <!-- 3.14 -->
<p>{{ 0.5 | percent:'1.0-2' }}                 <!-- 50.00% -->
<p>{{ 1234567 | number:'1.0-0' }}              <!-- 1,234,567 -->

<!-- Percent -->
<p>{{ 0.856 | percent }}                        <!-- 85.6% -->
<p>{{ 0.856 | percent:'1.2-2' }}               <!-- 85.60% -->
```

### Other built-in pipes

```html
<!-- Async — subscribes to Observable/Promise -->
<p>{{ data$ | async }}</p>
<!-- Also emits on change detection — auto unsubscribes -->

<!-- Json — debugging -->
<pre>{{ user | json }}</pre>                     <!-- {"name":"Alice","age":30} -->

<!-- KeyValue — iterate objects -->
<div *ngFor="let entry of user | keyvalue">
  {{ entry.key }}: {{ entry.value }}
</div>

<!-- Slice — take subarrays/strings -->
<p>{{ items | slice:0:5 }}</p>                  <!-- First 5 items -->
<p>{{ 'hello world' | slice:0:5 }}</p>          <!-- 'hello' -->

<!-- I18nPlural — locale-aware pluralization -->
<p>{{ messages.length | i18nPlural:messageMapping }}</p>
<!-- messageMapping = { =0: 'No messages', =1: '1 message', other: '# messages' } -->

<!-- I18nSelect — string value → display mapping -->
<p>{{ user.gender | i18nSelect:genderMapping }}</p>
<!-- genderMapping = { male: 'He', female: 'She', other: 'They' } -->

<!-- TitleCase — capitalize words -->
<p>{{ 'hello world' | titlecase }}</p>           <!-- Hello World -->
```

---

## Custom Pipes

> [!info] Custom pipe
> Create a custom pipe with `@Pipe({ name: 'myPipe' })`. Implement `PipeTransform` with a `transform(value, ...args): returnType` method. Pipes can inject services via `inject()`.

```typescript
import { Pipe, PipeTransform, inject } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

// Simple pipe — no DI
@Pipe({ name: 'truncate', standalone: true })
export class TruncatePipe implements PipeTransform {
  transform(value: string, maxLength: number = 100, suffix: string = '...'): string {
    if (!value) return '';
    return value.length > maxLength ? value.substring(0, maxLength) + suffix : value;
  }
}
// Usage: {{ text | truncate:50:'. . .' }}

// Pipe with injection
@Pipe({ name: 'safeHtml', standalone: true })
export class SafeHtmlPipe implements PipeTransform {
  private sanitizer = inject(DomSanitizer);

  transform(value: string): SafeHtml {
    return this.sanitizer.bypassSecurityTrustHtml(value);
  }
}
// Usage: <div [innerHtml]="content | safeHtml"></div>

// Pipe with multiple arguments
@Pipe({ name: 'filterBy', standalone: true })
export class FilterByPipe implements PipeTransform {
  transform<T extends Record<string, any>>(items: T[], field: keyof T, value: any): T[] {
    if (!items || !field) return items;
    return items.filter(item => item[field] === value);
  }
}
// Usage: {{ users | filterBy:'role':'admin' }}
```

### Pipe transform signature

```typescript
interface PipeTransform {
  transform(value: T, ...args: any[]): R;
}
// value:     the input data (required)
// ...args:   optional parameters after the colon: | pipeName:arg1:arg2
// return:    the transformed output
```

---

## Stateful and Impure Pipes

> [!info] Pure vs impure
> By default, pipes are **pure** — they only re-evaluate when the input value reference changes. **Impure** pipes (`pure: false`) re-evaluate on every change detection cycle. Use pure by default; impure only when necessary (and understand the performance cost).

```typescript
// Pure pipe (default) — only runs when value reference changes
@Pipe({ name: 'pure', standalone: true })
// pure: true is the default — change detection does NOT re-evaluate

// Impure pipe — runs EVERY change detection cycle (expensive!)
@Pipe({ name: 'impure', pure: false, standalone: true })
export class ImpureExamplePipe implements PipeTransform {
  transform(value: any[]): any[] {
    console.log('Runs on every CD cycle!');
    return [...value].sort();
  }
}

// When impure is needed:
// 1. Array/object mutations (new reference not created)
// 2. Stateful pipes (maintain internal state)
// 3. Real-time data streams

// Stateful pipe example — keeps internal counter
@Pipe({ name: 'counter', pure: false, standalone: true })
export class CounterPipe implements PipeTransform {
  private count = 0;

  transform(value: any): string {
    return `${value} — called ${++this.count} times`;
  }
}

// ⚠️  Impure with no caching is expensive:
// Avoid: impure pipes that do heavy computation (sort, filter, API calls)
// Prefer: memoizing computed signals, pure pipes with new references
```

---

## `async` Pipe and `@let`

> [!info] async pipe
> The `| async` pipe subscribes to an `Observable` or `Promise`, returns the latest emitted value, and auto-unsubscribes when the component is destroyed. Combined with `@let` (Angular 18+), async data becomes reactive without `subscribe()`.

```typescript
import { Component, inject } from '@angular/core';
import { AsyncPipe, JsonPipe } from '@angular/common';
import { Observable } from 'rxjs';
import { UserService } from './user.service';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [AsyncPipe, JsonPipe],
  template: `
    <!-- Basic async — auto-subscribe + auto-unsubscribe -->
    <p>{{ users$ | async | json }}</p>

    <!-- Handling loading state with @let (Angular 18+) -->
    @let users = (users$ | async);
    @if (users) {
      <div *ngFor="let user of users">{{ user.name }}</div>
    } @else {
      <p>Loading...</p>
    }

    <!-- Multiple asyncs with object destructuring -->
    @let data = { user: (user$ | async), orders: (orders$ | async) };
    @if (data.user && data.orders) {
      <p>{{ data.user.name }} — {{ data.orders.length }} orders</p>
    }

    <!-- Default value with async -->
    <p>{{ (data$ | async) ?? 'Loading...' }}</p>

    <!-- Promise with async -->
    <p>{{ promiseData | async }}</p>
  `
})
export class UsersComponent {
  private userService = inject(UserService);
  users$: Observable<User[]> = this.userService.getUsers();
}
```

### `async` pipe and `*ngIf` pattern (pre-`@let`)

```html
<!-- Manual subscription variable (older pattern) -->
<div *ngIf="users$ | async as users">
  <p>{{ users.length }} users loaded</p>
</div>

<!-- With else block -->
<div *ngIf="users$ | async as users; else loading">
  <div *ngFor="let user of users">{{ user.name }}</div>
</div>
<ng-template #loading><p>Loading users...</p></ng-template>
```

---

## Pipes in TypeScript

```typescript
// Using pipes programmatically (not just templates):
import { DatePipe, CurrencyPipe } from '@angular/common';

@Component({ ... })
export class ReportService {
  private datePipe = inject(DatePipe);
  private currencyPipe = inject(CurrencyPipe);

  formatReport(date: Date, amount: number): string {
    const formattedDate = this.datePipe.transform(date, 'mediumDate');
    const formattedAmount = this.currencyPipe.transform(amount, 'USD', 'symbol', '1.2-2');
    return `${formattedDate}: ${formattedAmount}`;
  }
}

// Provide pipe at component level to make injectable
@Component({
  providers: [DatePipe, CurrencyPipe]
})
```

---

## Pipe Testing

```typescript
import { TruncatePipe } from './truncate.pipe';

describe('TruncatePipe', () => {
  const pipe = new TruncatePipe();

  it('should return empty string for null/undefined', () => {
    expect(pipe.transform('', 5)).toBe('');
    expect(pipe.transform(null as any, 5)).toBe('');
  });

  it('should not truncate short text', () => {
    expect(pipe.transform('hello', 10)).toBe('hello');
  });

  it('should truncate long text with default suffix', () => {
    expect(pipe.transform('hello world', 5)).toBe('hello...');
  });

  it('should truncate with custom suffix', () => {
    expect(pipe.transform('hello world', 5, '[...]')).toBe('hello[...]');
  });
});

// Testing pipe with DI (SafeHtmlPipe uses DomSanitizer):
import { SafeHtmlPipe } from './safe-html.pipe';
import { TestBed } from '@angular/core/testing';

describe('SafeHtmlPipe', () => {
  let pipe: SafeHtmlPipe;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    pipe = TestBed.runInInjectionContext(() => new SafeHtmlPipe());
  });

  it('should bypass HTML', () => {
    const result = pipe.transform('<script>alert("xss")</script>');
    expect(result).toBeDefined();
  });
});
```

---

## Performance Optimization

```text
Pipe performance rules:

1. Prefer PURE pipes (default). Only use impure when you must.
   Pure pipes run once per reference change. Impure run every CD cycle.

2. Avoid heavy computation in impure pipes.
   No sorting, filtering, or API calls in impure pipes. Use memoized
   computed() signals or transform data before passing to template.

3. Async pipe automatically handles subscription lifecycle.
   Never subscribe() inside a pipe — use inject() for services instead.

4. Pipe purity cheat sheet:
                                    Pure          Impure
   Re-evaluates on:              Reference change  Every CD cycle
   Array.sort() result           ❌ (same ref)      ✅
   Object mutation               ❌                 ✅
   Service.inject()              ✅                 ✅
   Performance                   Fast              Slow (avoid)
```

---

## Cross-Links

- [[Angular/02_Core/02_Signals_Essentials]] for `computed()` as an alternative to impure pipes
- [[Angular/02_Core/03_RxJS_in_Angular]] for async pipe with Observables
- [[Angular/03_Advanced/01_Change_Detection_and_Performance]] for change detection impact
- [[Angular/03_Advanced/02_Testing_Angular_Components]] for component-level testing
