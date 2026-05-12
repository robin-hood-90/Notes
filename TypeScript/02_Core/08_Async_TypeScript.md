---
tags: [typescript, core, async, promises, await, error-handling]
aliases: ["Async TypeScript", "Promises Typing", "Async/Await", "Async Error Handling"]
status: stable
updated: 2026-05-03
---

# Async TypeScript

> [!summary] Goal
> Type async code safely: understand `Promise<T>` generics, error handling with `unknown`, typing `Promise.all`/`allSettled`, and designing async APIs with proper type inference.

## Table of Contents

1. [Why Async Typing Matters](#why-async-typing-matters)
2. [`Promise<T>` Generics](#promiset-generics)
3. [`async`/`await` Type Inference](#async-await-type-inference)
4. [`Awaited<T>` Deep Dive](#awaitedt-deep-dive)
5. [Typing Async Error Handling](#typing-async-error-handling)
6. [Typing `Promise.all` and `Promise.allSettled`](#typing-promise-all-and-promise-allsettled)
7. [Typing Custom Async Functions](#typing-custom-async-functions)
8. [Observables and Streams](#observables-and-streams)
9. [Pitfalls](#pitfalls)

---

## Why Async Typing Matters

Async code is pervasive in TypeScript. Proper typing catches errors at compile time that would otherwise surface as runtime crashes.

```mermaid
flowchart LR
    A["async function fetchUser(id: string)"] --> B["return type: Promise<User>"]
    B --> C[Caller does: await fetchUser('123')]
    C --> D["Inferred type: User (not unknown)"]
    D --> E[Compile-time safety on returned data]
```

---

## `Promise<T>` Generics

`Promise<T>` is a generic type representing a value that will be available in the future:

```ts
type Promise<T> = {
  then<U>(onFulfilled?: (value: T) => U | Promise<U>): Promise<U>;
  catch<U>(onRejected?: (reason: unknown) => U | Promise<U>): Promise<U>;
};
```

### Creating typed promises

```ts
function fetchUser(id: string): Promise<User> {
  return fetch(`/users/${id}`).then(res => res.json());
}

// Or with the Promise constructor:
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

### The `T` in `Promise<T>` matters

```ts
// BAD: loses type information
async function getData(): Promise<any> { ... }

// GOOD: preserves type
async function getData(): Promise<{ id: string; email: string }> { ... }
```

---

## `async`/`await` Type Inference

`async` functions always return a `Promise`. TypeScript infers the wrapped type:

```ts
async function fetchUser(id: string): Promise<User> {
  const res = await fetch(`/users/${id}`);
  const data: User = await res.json();
  return data;
}

// Equivalent non-async:
function fetchUser(id: string): Promise<User> {
  return fetch(`/users/${id}`).then(res => res.json()) as Promise<User>;
}
```

### Inference from return expression

```ts
async function getNumber() {
  return 42;
}
// Return type inferred as Promise<number>

async function getStringOrNumber(b: boolean) {
  if (b) return 'hello';
  return 42;
}
// Return type inferred as Promise<string | number>
```

### Explicit return type

Always annotate the return type of public async functions:

```ts
// GOOD: explicit for callers
export async function lookupUser(id: string): Promise<User | null> {
  // ...
}
```

---

## `Awaited<T>` Deep Dive

`Awaited<T>` unwraps `Promise` types recursively:

```ts
type T1 = Awaited<Promise<string>>;        // string
type T2 = Awaited<Promise<Promise<number>>>;  // number
type T3 = Awaited<string | Promise<number>>;  // string | number
```

### How `Awaited` is defined

```ts
type Awaited<T> = T extends null | undefined
  ? T
  : T extends object & { then(onfulfilled: infer F): any }
    ? F extends ((value: infer V, ...args: any) => any)
      ? Awaited<V>
      : never
    : T;
```

### Real-world usage

```ts
async function fetchConfig(): Promise<{ debug: boolean }> {
  return { debug: true };
}

// With Awaited:
type Config = Awaited<ReturnType<typeof fetchConfig>>;
// type Config = { debug: boolean }
```

---

## Typing Async Error Handling

### `try`/`catch` with `unknown`

```ts
async function safeFetch(url: string): Promise<Result<unknown>> {
  try {
    const res = await fetch(url);
    const data = await res.json();
    return { ok: true, data };
  } catch (error) {
    // With useUnknownInCatchVariables: error is unknown
    if (error instanceof Error) {
      return { ok: false, error: error.message };
    }
    return { ok: false, error: String(error) };
  }
}
```

### Result type pattern for async

```ts
type AsyncResult<T, E = Error> =
  | { ok: true; data: T }
  | { ok: false; error: E };

async function divide(a: number, b: number): Promise<AsyncResult<number>> {
  if (b === 0) return { ok: false, error: new Error('Division by zero') };
  return { ok: true, data: a / b };
}

const result = await divide(10, 2);
if (result.ok) {
  console.log(result.data);  // typed as number
}
```

---

## Typing `Promise.all` and `Promise.allSettled`

### `Promise.all` — tuple inference

```ts
async function fetchUser(id: string): Promise<User> { /* ... */ }
async function fetchPosts(userId: string): Promise<Post[]> { /* ... */ }

const [user, posts] = await Promise.all([
  fetchUser('123'),
  fetchPosts('123'),
]);
// user: User
// posts: Post[]
```

TypeScript infers a tuple from the array literal:

```ts
type Result = Promise.AllResult<[Promise<User>, Promise<Post[]>]>;
// Result = [User, Post[]]
```

### `Promise.allSettled` — typed outcomes

```ts
const results = await Promise.allSettled([
  fetchUser('123'),
  fetchPosts('123'),
]);

for (const result of results) {
  if (result.status === 'fulfilled') {
    // result.value: User | Post[] — union of all resolved types
    console.log(result.value);
  } else {
    // result.reason: unknown
    console.error(result.reason);
  }
}
```

### Typed wrapper for allSettled

```ts
async function settledAll<T extends readonly unknown[]>(
  promises: { [K in keyof T]: Promise<T[K]> }
): Promise<{ [K in keyof T]: { ok: true; data: T[K] } | { ok: false; error: unknown } }> {
  const results = await Promise.allSettled(promises);
  return results.map(r =>
    r.status === 'fulfilled'
      ? { ok: true, data: r.value }
      : { ok: false, error: r.reason }
  ) as any;
}
```

---

## Typing Custom Async Functions

### Generic async functions

```ts
async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// Inferred correctly:
const user = await fetchJson<User>('/users/123');
// user: User
```

### Async function overloads

```ts
async function fetchItem(id: string): Promise<Item | null>;
async function fetchItem(ids: string[]): Promise<Item[]>;
async function fetchItem(arg: string | string[]): Promise<unknown> {
  if (Array.isArray(arg)) {
    return Promise.all(arg.map(id => fetchItem(id)));
  }
  const res = await fetch(`/items/${arg}`);
  if (!res.ok) return null;
  return res.json();
}
```

---

## Observables and Streams

```ts
// RxJS Observable typing
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

function fetchUsers$(): Observable<User[]> {
  return from(fetch('/users')).pipe(
    map(res => res.json()),
    catchError(err => of([] as User[]))
  );
}
```

| Pattern | Return type | When to use |
|---------|-------------|-------------|
| `async/await` | `Promise<T>` | Single async value |
| `Observable<T>` | Stream of values | Events, real-time data |
| `ReadableStream<T>` | Streaming response | Large payloads |

---

## Pitfalls

### Forgetting `await` inside async

```ts
async function process() {
  const data = fetchData();  // Promise<Data>, not Data!
  // Error: data.map is not a function at runtime
}
```

**Fix**: `const data = await fetchData();`

### Unhandled promise rejection

```ts
async function run() {
  throw new Error('fail');
}
run();  // Unhandled promise rejection!
```

**Fix**: Always `await` or `.catch()` promise-returning calls.

### `forEach` with async

```ts
async function processItems(items: Item[]) {
  items.forEach(async (item) => {
    await process(item);  // Fire-and-forget — errors not caught
  });
  console.log('done');  // Runs BEFORE all items processed
}
```

**Fix**: Use `for...of` or `Promise.all`:

```ts
for (const item of items) { await process(item); }
// Or: await Promise.all(items.map(i => process(i)));
```

### `catch` typing is `unknown`

With `useUnknownInCatchVariables`:

```ts
try { await risky(); }
catch (e) {
  console.log(e.message);  // Error: 'e' is unknown
}
```

**Fix**: Narrow with `instanceof` or type guard.

---

> [!question]- Interview Questions
>
> **Q: What type does an `async` function always return?**
> A: `Promise<T>`. The type parameter `T` is inferred from the return statement.
>
> **Q: What does `Awaited<T>` do?**
> A: Recursively unwraps `Promise` types. `Awaited<Promise<Promise<number>>>` becomes `number`.
>
> **Q: How does TypeScript infer types from `Promise.all`?**
> A: Array literals passed to `Promise.all` are inferred as tuples, preserving the individual types of each promise rather than merging them into a union.
>
> **Q: Why should you annotate async function return types?**
> A: Callers get precise types, and the compiler catches accidental return type mismatches.

---

## Cross-Links

- [[TypeScript/02_Core/01_Utility_Types]] for `Awaited`, `ReturnType`, `Parameters`
- [[TypeScript/01_Foundations/03_Generics_Basics]] for generic async patterns
- [[TypeScript/03_Advanced/04_Typing_Patterns_for_APIs]] for fetch wrapper patterns
- [[TypeScript/04_Playbooks/06_TypeScript_with_React]] for async hooks

---

## References

- [TypeScript Promise](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-5.html#the-awaited-type)
- [Promise.all Types](https://www.typescriptlang.org/play#example/async-await)
- [TypeScript Async Patterns](https://www.typescriptlang.org/docs/handbook/2/functions.html#async-functions)
