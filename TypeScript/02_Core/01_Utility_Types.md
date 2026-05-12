---
tags: [typescript, core]
aliases: ["TS Utility Types", "Utility Types Intro"]
status: stable
updated: 2026-05-03
---

# Utility Types

> [!summary] Goal
> Compose and transform object/function types instead of duplicating shapes.

## Object utilities

```ts
type User = { id: string; email: string; admin: boolean };

type UserPatch = Partial<User>;
type RequiredUser = Required<User>;
type ReadonlyUser = Readonly<User>;
type UserPublic = Pick<User, "id" | "email">;
type UserPrivate = Omit<User, "admin">;
type UserMap = Record<string, User>;
```

## Union utilities

```ts
type T = string | number | null;
type NonNull = NonNullable<T>; // string | number

type A = Exclude<"a" | "b" | "c", "b">; // "a" | "c"
type B = Extract<"a" | "b" | "c", "b" | "x">; // "b"
```

## Function utilities

```ts
type Fn = (a: number, b: string) => Promise<boolean>;

type P = Parameters<Fn>; // [number, string]
type R = ReturnType<Fn>; // Promise<boolean>
type AR = Awaited<R>; // boolean
```

## When to use

- `Partial` for patch/update APIs.
- `Pick`/`Omit` to control what crosses boundaries.
- `Record` for maps.
- `Awaited` for promise-heavy codebases.

## References

- https://www.typescriptlang.org/docs/handbook/utility-types.html
