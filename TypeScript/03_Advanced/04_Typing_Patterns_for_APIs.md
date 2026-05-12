---
tags: [typescript, advanced]
aliases: ["Typing Patterns for APIs"]
status: stable
updated: 2026-05-11
---

# Typing Patterns for APIs

> [!summary] Goal
> Type APIs so callers get correct inference and autocomplete, while implementation stays maintainable.

## Pattern 1: Model API results as discriminated unions

```ts
export type Result<T> =
  | { ok: true; data: T }
  | { ok: false; error: { message: string; code?: string } };

export async function getJson<T>(url: string): Promise<Result<T>> {
  try {
    const res = await fetch(url);
    if (!res.ok) {
      return { ok: false, error: { message: `HTTP ${res.status}` } };
    }
    return { ok: true, data: (await res.json()) as T };
  } catch (e) {
    return { ok: false, error: { message: e instanceof Error ? e.message : String(e) } };
  }
}
```

## Pattern 2: Use `satisfies` to keep literals

```ts
type Endpoint = {
  method: "GET" | "POST";
  path: `/${string}`;
};

export const ENDPOINTS = {
  getUser: { method: "GET", path: "/users/:id" },
  createUser: { method: "POST", path: "/users" },
} as const satisfies Record<string, Endpoint>;
```

## Pattern 3: Overloads for ergonomics

```ts
export function getItem(id: string): Promise<{ id: string } | null>;
export function getItem(ids: string[]): Promise<{ id: string }[]>;
export async function getItem(arg: string | string[]) {
  if (Array.isArray(arg)) return arg.map((id) => ({ id }));
  return { id: arg };
}
```

## Pattern 4: Generic functions should infer from parameters

```ts
export function mapById<T extends { id: string }>(items: T[]): Record<string, T> {
  return Object.fromEntries(items.map((x) => [x.id, x]));
}
```

## Pattern 5: "Opaque" ids (nominal-ish typing)

```ts
type Brand<T, B extends string> = T & { readonly __brand: B };

export type UserId = Brand<string, "UserId">;
export type OrderId = Brand<string, "OrderId">;

export function asUserId(x: string): UserId {
  return x as UserId;
}
```

> [!warning]
> Branding is compile-time only. Use runtime validation at trust boundaries.

## Cross-Links

- `satisfies`: [[TypeScript/01_Foundations/01_TS_Basics_Types_and_Inference]]
- Conditional types: [[TypeScript/03_Advanced/01_Conditional_Types]]

## References

- https://www.typescriptlang.org/docs/handbook/2/functions.html
