---
tags: [typescript, advanced, using, disposable, variance, const-type-parameter, no-infer, isolated-declarations, erasable-syntax]
aliases: ["using declarations", "Disposable", "variance in/out", "const type parameters", "NoInfer", "isolatedDeclarations", "erasableSyntaxOnly", "A08"]
status: stable
updated: 2026-05-11
---

# `using`, Variance, `const` Parameters, `NoInfer`, and `--erasableSyntaxOnly`

> [!summary] Goal
> Master TypeScript's advanced type system features: `using`/`await using` declarations for explicit resource management, variance annotations (`in`/`out`), `const` type parameters, `NoInfer<T>`, `--isolatedDeclarations` for fast builds, and `--erasableSyntaxOnly` for clean emits.

## Table of Contents

1. [using and await using](#using-and-await-using)
2. [Variance Annotations (in/out)](#variance-annotations)
3. [const Type Parameters](#const-type-parameters)
4. [NoInfer\<T\>](#noinfert)
5. [--isolatedDeclarations and --erasableSyntaxOnly](#isolateddeclarations-and-erasablesyntaxonly)

---

## `using` and `await using`

> [!info] using declarations
> TypeScript 5.2 introduces `using` and `await using` declarations (targeting ES2023+). `using` provides **explicit resource management**: a block-scoped variable whose `[Symbol.dispose]()` method is called when the variable goes out of scope. This is the TypeScript version of C#'s `using` / Python's `with` / Java's `try-with-resources`.

### `Disposable` and `AsyncDisposable` interfaces

```typescript
// Built-in global types (TS 5.2+):
interface Disposable {
    [Symbol.dispose](): void;
}

interface AsyncDisposable {
    [Symbol.asyncDispose](): Promise<void>;
}
```

### `using` — synchronous disposal

```typescript
class FileHandle implements Disposable {
    constructor(private path: string) {
        console.log(`Opening ${path}`);
    }
    read(): string {
        return 'file content';
    }
    [Symbol.dispose](): void {
        console.log(`Closing ${this.path}`);
    }
}

// using declares a variable that is automatically disposed on scope exit:
function processFile() {
    using file = new FileHandle('/etc/config.json');
    const data = file.read();
    // file.[Symbol.dispose]() is called here (or on early return / throw)
    return JSON.parse(data);
}
// Output:
// Opening /etc/config.json
// Closing /etc/config.json

// Multiple declarations are disposed in reverse order:
using a = new ResourceA();
using b = new ResourceB();
// b is disposed first, then a
```

### `await using` — async disposal

```typescript
class DatabaseConnection implements AsyncDisposable {
    constructor(private url: string) {
        console.log(`Connecting to ${url}`);
    }
    async query(sql: string): Promise<any[]> {
        return [];
    }
    [Symbol.asyncDispose](): Promise<void> {
        console.log('Closing connection');
        return Promise.resolve();
    }
}

async function queryDatabase() {
    await using db = new DatabaseConnection('postgres://localhost:5432/mydb');
    const results = await db.query('SELECT * FROM users');
    // db.[Symbol.asyncDispose]() is awaited here
    return results;
}
```

### `DisposableStack` and `AsyncDisposableStack`

```typescript
// Programmatic composition of disposable resources:

function handleRequest() {
    using stack = new DisposableStack();

    const file = stack.use(new FileHandle('/tmp/data'));
    const lock = stack.use(new Mutex());  // Any Disposable

    // All resources are disposed in reverse order when scope exits,
    // even if an exception is thrown.
}

// Suppress disposal (take ownership):
using file = new FileHandle('/tmp/x');
const rawHandle = file[Symbol.dispose]();  // Prevent automatic disposal
stack.suppress(file);                       // Move disposal responsibility
```

---

## Variance Annotations (`in`/`out`)

> [!info] Variance annotations (TS 4.7+)
> TypeScript supports explicit variance markers `in` (contravariant) and `out` (covariant) on type parameters. They serve as documentation and enable the compiler to check that the type parameter is used consistently. Without annotations, TypeScript infers variance but is more permissive.

```typescript
// out — covariant: Producer<T> can be used where Producer<Supertype> is expected
interface Producer<out T> {
    produce(): T;           // T is only in output positions
}

// in — contravariant: Consumer<T> can be used where Consumer<Subtype> is expected
interface Consumer<in T> {
    consume(value: T): void;  // T is only in input positions
}

// Mixed:
interface Transformer<in T, out U> {
    transform(input: T): U;
}

// Without variance annotations, the compiler infers but is unsound:
interface BadProducer<T> {
    produce(): T;
    consume(value: T): void;  // violates the out annotation — error!
}
```

### Why use variance annotations

```typescript
// 1. Catch misuse at definition site:
interface SafeProducer<out T> {
    // produce(): T;       // OK
    // consume(v: T): void; // Error: T is in input position!
}

// 2. Documentation — readers know this type produces Ts, not consumes them

// 3. Enable more flexible assignments:
const stringProducer: Producer<string> = { produce: () => 'hello' };
const unknownProducer: Producer<unknown> = stringProducer;  // OK: covariant

// Without `out`, the compiler may reject this.
```

---

## `const` Type Parameters (TS 5.0)

> [!info] const type parameters
> `const` on a type parameter instructs TypeScript to infer the NARROWEST possible type — for literal values, infer the literal type; for arrays, infer a tuple type with literal elements. This eliminates the need to add `as const` at every call site.

```typescript
// Without const — inferred as string:
function identity<T>(value: T): T { return value; }
const result = identity("hello");  // type: string

// With const — inferred as "hello":
function identityConst<const T>(value: T): T { return value; }
const resultConst = identityConst("hello");  // type: "hello"

// Practical: tuple inference with const:
function merge<const T extends readonly any[], const U extends readonly any[]>(
  a: T, b: U
): [...T, ...U] {
  return [...a, ...b];
}

const merged = merge([1, 2] as const, ['a', 'b'] as const);
// type: [1, 2, "a", "b"]
// Without const: (number | string)[]

// Even better: with const T, the as const at the call site is optional:
const merged2 = merge([1, 2], ['a', 'b']);
// type: [1, 2, "a", "b"]  — inferred as const tuple!
```

---

## `NoInfer<T>` (TS 5.4)

> [!info] NoInfer
> `NoInfer<T>` marks a type parameter position where inference should NOT occur. The compiler uses it as a hint — it won't infer `T` from this position, but will check it against already-inferred types. This prevents unexpected widening of type parameters.

```typescript
// Problem: function where one parameter should determine T, and others should match:

// Without NoInfer — all positions contribute to inference:
function createRecord<T>(id: string, data: T): { id: string; data: T } {
    return { id, data };
}
const r = createRecord("x", "hello");  // T = string, but what if data is narrower?

// With NoInfer — T is only inferred from `data`, not from createRecord's usage:
function createRecordBetter<T>(
    id: string,
    data: NoInfer<T>  // Don't infer T from this position
): { id: string; data: T } {
    return { id, data };
}
// Now T is determined by the return context or explicit annotation.

// Practical: keyof + NoInfer for dictionary functions:
function getValue<T, K extends keyof T>(
    obj: T,
    key: K,
    defaultValue: NoInfer<T[K]>   // defaultValue must match value type at key K
): T[K] {
    return obj[key] ?? defaultValue;
}
const config = { port: 8080, host: "localhost" };
const port = getValue(config, "port", 3000);     // OK: number
// getValue(config, "port", "invalid"); // Error: string not assignable to number
```

---

## `--isolatedDeclarations` and `--erasableSyntaxOnly`

### `--isolatedDeclarations` (TS 5.5+)

```typescript
// Enables declaration-only build mode.
// Each file is compiled independently (no cross-file type inference for declarations).
// Benefits: fast parallel builds, supports project references, enables publishing .d.ts
// without fully type-checking downstream.

// When enabled, every exported function must have explicit return type:
// export function parseJSON<T>(json: string): T  // Error: return type inferred
export function parseJSON<T>(json: string): T {   // OK: explicit
    return JSON.parse(json) as T;
}
```

### `--erasableSyntaxOnly` (TS 5.8+)

```typescript
// Prevents TypeScript syntax that emits JavaScript code at runtime.
// Enums, namespaces, and parameter properties produce runtime code — these are banned.
// Keeps the emitted JS clean and standard-compliant.

// ❌ Error under --erasableSyntaxOnly:
// enum Color { Red, Green, Blue }         // Emits runtime IIFE
// namespace MyLib { export function x() {} }  // Emits object assignment
// class Foo { constructor(public x: number) {} }  // Emits this.x = x

// ✅ Allowed:
// type, interface, const, functions with type annotations, as, satisfies, using, etc.
type Color = "red" | "green" | "blue";      // Pure compile-time — OK
const Colors = { Red: "red", Green: "green" } as const;  // No runtime emit — OK
```

---

## Cross-Links

- [[TypeScript/01_Foundations/05_TS_Config_and_Compiler]] for all compiler options (targets, strict flags)
- [[TypeScript/02_Core/09_Utility_Types_Deep_Dive]] for NoInfer and utility types
- [[TypeScript/03_Advanced/01_Conditional_Types]] for extends-based type inference
- [[TypeScript/04_Playbooks/01_Debug_Type_Errors_Systematically]] for type error patterns
- [[JavaScript/01_Foundations/05_ES2023_2024_Features_and_Symbol]] for Symbol.dispose / Symbol.asyncDispose
