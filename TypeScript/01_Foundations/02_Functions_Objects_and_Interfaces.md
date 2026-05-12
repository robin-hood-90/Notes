---
tags: [typescript, foundations]
aliases: ["TS Functions and Objects"]
status: stable
updated: 2026-05-03
---

# Functions, Objects, and Interfaces

> [!summary] Goal
> Model data and behavior with ergonomic types: function signatures, object shapes, optionality, and safe extension.

## Function Types

```ts
type Predicate<T> = (value: T) => boolean;

const isEven: Predicate<number> = (n) => n % 2 === 0;
```

### Parameters and return values

```ts
function clamp(n: number, min = 0, max = 100): number {
  return Math.min(max, Math.max(min, n));
}
```

### Optional and rest parameters

```ts
function formatName(first: string, last?: string): string {
  return last ? `${first} ${last}` : first;
}

function sum(...xs: number[]) {
  return xs.reduce((a, b) => a + b, 0);
}
```

## Object Types

```ts
type User = {
  id: string;
  email: string;
  displayName?: string;
  readonly createdAt: string;
};
```

### Excess property checks

Object literals get extra checking.

```ts
type Point = { x: number; y: number };

const p1: Point = { x: 1, y: 2 };
// const p2: Point = { x: 1, y: 2, z: 3 }; // error (excess property)

const tmp = { x: 1, y: 2, z: 3 };
const p3: Point = tmp; // ok (structural assignment)
```

## Interfaces

Interfaces are great for object shapes, especially when you expect extension.

```ts
interface Repo<T> {
  get(id: string): Promise<T | null>;
  put(value: T): Promise<void>;
}
```

### Extension

```ts
interface Entity {
  id: string;
}

interface User extends Entity {
  email: string;
}
```

## Index Signatures (Use Sparingly)

```ts
type Headers = { [k: string]: string };
```

If keys are known, prefer a union of keys + mapped types.

## Intersection and Union

```ts
type WithTimestamps = { createdAt: string; updatedAt: string };
type UserRow = User & WithTimestamps;

type Status = "idle" | "loading" | "success" | "error";
```

## Cross-Links

- Next: [[TypeScript/01_Foundations/03_Generics_Basics]]
- Deeper compare: [[TypeScript/02_Core/04_Types_vs_Interfaces]]

## References

- https://www.typescriptlang.org/docs/handbook/2/everyday-types.html
