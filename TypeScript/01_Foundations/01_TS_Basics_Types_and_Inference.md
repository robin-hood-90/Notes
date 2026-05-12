---
tags: [typescript, foundations]
aliases: ["TS Basics", "TypeScript Basics"]
status: stable
updated: 2026-05-03
---

# TypeScript Basics: Types and Inference

> [!summary] Goal
> Write TS that is type-safe without fighting the compiler: lean on inference, model data with unions, and avoid unsafe escapes.

## What TypeScript Actually Does

- TypeScript checks types at compile time.
- Generated JavaScript does not contain TS types.

```ts
type UserId = string;
const id: UserId = "u_123";
// At runtime, id is just a string.
```

## Inference First

Prefer letting TS infer when it produces the type you want.

```ts
const n = 123; // number
const ok = true; // boolean
const names = ["a", "b"]; // string[]

const user = {
  id: "u_1",
  email: "a@b.com",
};
// { id: string; email: string }
```

> [!tip] When to annotate
> Annotate function boundaries and public APIs. Inside implementations, inference is usually better.

## The Core Primitives

- `string`, `number`, `boolean`, `bigint`, `symbol`
- `null`, `undefined`
- `object` (rarely what you want)
- `unknown` (safe “I don't know yet”)
- `any` (turns off checking, avoid)
- `never` (impossible)

```ts
function fail(msg: string): never {
  throw new Error(msg);
}

function parseJson(s: string): unknown {
  return JSON.parse(s);
}
```

## Structural Typing (Duck Typing)

TypeScript is structural: if it has the required shape, it's assignable.

```ts
type HasId = { id: string };

const a = { id: "x", extra: 1 };
const b: HasId = a; // ok
```

## Union Types (Model Reality)

Most real data is "either/or".

```ts
type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: { message: string; code?: string } };
```

## Literal Types and `as const`

```ts
const role = "admin" as const; // type: "admin"

const routes = {
  home: "/",
  settings: "/settings",
} as const;
// values become literals instead of string
```

## `satisfies` (Keep Literals, Validate Shape)

`satisfies` checks a value conforms to a type without widening it.

```ts
type RouteMap = Record<string, `/${string}`>;

const ROUTES = {
  home: "/",
  settings: "/settings",
  // bad: "settings": "settings"
} as const satisfies RouteMap;
```

## Arrays vs Tuples

```ts
const a = [1, 2, 3]; // number[]
const t: [number, number] = [1, 2]; // tuple
```

## Common Pitfalls

- Prefer `unknown` over `any` at trust boundaries.
- Avoid type assertions (`as X`) unless you can justify runtime truth.
- Use unions + narrowing rather than optional fields everywhere.

## Cross-Links

- Next: [[TypeScript/01_Foundations/04_Narrowing_and_Type_Guards]]
- Used by: [[React/00_MOC/00_React_MOC]] | [[Angular/00_MOC/00_Angular_MOC]]

## References

- https://www.typescriptlang.org/docs/
