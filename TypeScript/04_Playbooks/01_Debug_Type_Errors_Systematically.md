---
tags: [typescript, playbook]
aliases: ["Debug TS Errors", "TypeScript Error Debugging"]
status: stable
updated: 2026-05-11
---

# Playbook: Debug Type Errors Systematically

> [!summary] Goal
> Reduce type errors to a minimal example and fix the root cause without fighting the compiler. Understand the most common error categories and their fixes.

## 1. Localize the Error

- Hover the type at the failing expression — the issue is often a step before the red underline.
- Examine: does one operand have a wider type than expected? Did inference widen a literal to `string`?

## 2. Reduce

- Inline generics and helper types.
- Replace complex values with simple literals.
- Isolate a single function signature from the chain.

## 3. Common Error Patterns

### Pattern A: Type widened (literal → primitive)

```typescript
// Problem:
const config = { port: 8080, host: "localhost" };
function setPort(p: number) {}
setPort(config.port);           // OK
// setPort(config.port + "bad"); // Error as expected — but sometimes inference widens

// Fix 1: use `as const`
const narrow = { port: 8080 } as const;  // port is 8080, not number

// Fix 2: const generic (TS 5.0+)
function get<const T>(x: T) { return x; }
const result = get({ port: 8080 });      // { readonly port: 8080 }
```

### Pattern B: Union narrowing fails

```typescript
type Shape =
    | { kind: "circle"; radius: number }
    | { kind: "rect"; width: number; height: number };

function area(s: Shape) {
    if (s.kind === "circle") return Math.PI * s.radius ** 2;
    // if (s.kind === "rect") return s.width * s.height;
    // Error?  Only if discriminant check is missing!
}

// Fix: ensure ALL discriminants are covered, or use exhaustive guard:
function assertNever(x: never): never { throw new Error("unreachable"); }
```

### Pattern C: Generic inference failure

```typescript
// Problem: T can't be inferred
function first<T>(arr: T[]): T | undefined { return arr[0]; }
first([]);                   // T = undefined — not useful

// Fix: provide better inference context or explicit type parameter:
const n = first([1, 2, 3]); // T = number — OK

// With NoInfer (TS 5.4):
function getOrDefault<T>(arr: T[], defaultValue: NoInfer<T>): T {
    return arr[0] ?? defaultValue;
}
```

### Pattern D: Excess property check on object literal

```typescript
interface Point { x: number; y: number; }
// const p: Point = { x: 1, y: 2, z: 3 };  // Error: excess property 'z'

// Fix: assign to variable first, then pass:
const pt = { x: 1, y: 2, z: 3 };
const p: Point = pt;  // OK (no excess check on non-literal)
```

### Pattern E: `.extends` mismatch on generic constraints

```typescript
function process<T extends { id: number }>(obj: T) { /* ... */ }
// process({ id: "abc" });  // Error: string != number
```

### Pattern F: `any` poisoning

```typescript
function evil(): any { return JSON.parse('"oops"'); }
const x: string = evil();   // OK — but x is any in disguise!
x.badMethod();               // No error! any suppresses all checks

// Fix: always type JSON.parse boundaries:
function safeJSON<T>(json: string): T { return JSON.parse(json) as T; }
```

## 4. Prefer Constraints Over Assertions

- Prefer `T extends Foo` over `as Foo`.
- If you must assert (`as`), add a `// SAFETY:` comment explaining why.
- Use `@ts-expect-error` (not `@ts-ignore`) when you deliberately bypass an error.

## 5. `typescript-eslint` Type-Checked Rules

```bash
# Enable these to catch common errors at lint time:
extends:
  - plugin:@typescript-eslint/recommended-type-checked
  - plugin:@typescript-eslint/strict-type-checked

# Key rules:
#   @typescript-eslint/no-unsafe-* — catches any poisoning
#   @typescript-eslint/strict-boolean-expressions — no implicit boolean coercion
#   @typescript-eslint/prefer-optional-chain — encourages ?. syntax
```

---

## Cross-Links

- [[TypeScript/01_Foundations/04_Narrowing_and_Type_Guards]] for narrowing patterns
- [[TypeScript/02_Core/02_Advanced_Generics]] for advanced generics
- [[TypeScript/02_Core/09_Utility_Types_Deep_Dive]] for NoInfer and other utilities
- [[TypeScript/04_Playbooks/04_Linting_and_Formatting]] for typescript-eslint config
