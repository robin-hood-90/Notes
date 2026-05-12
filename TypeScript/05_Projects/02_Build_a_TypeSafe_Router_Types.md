---
tags: [typescript, project, router, template-literal-types, satisfies, path-params]
aliases: ["TypeSafe Router", "Type-Level Router", "Route Typing"]
status: stable
updated: 2026-05-11
---

# Project: Build a TypeSafe Router Types

> [!summary] Goal
> Use template literal types + `infer` to extract `:param` from route strings at the type level. Combine with `satisfies` for endpoint validation and produce a fully typed client.

## Route Params Extraction

```typescript
// Core type: extract param names from route strings
type ExtractRouteParams<T extends string> =
    T extends `${string}:${infer Param}/${infer Rest}`
        ? { [K in Param | keyof ExtractRouteParams<Rest>]: string }
        : T extends `${string}:${infer Param}`
            ? { [K in Param]: string }
            : {};

// Examples:
type R1 = ExtractRouteParams<"/users/:id">;            // { id: string }
type R2 = ExtractRouteParams<"/users/:id/posts/:pid">; // { id: string; pid: string }
type R3 = ExtractRouteParams<"/health">;                // {}
```

## Router with `satisfies`

```typescript
// Step 1: Define the route config with satisfies validation
const routes = {
    "GET /users": {
        handler: () => ({ status: 200, body: [] as User[] }),
    },
    "GET /users/:id": {
        handler: ({ id }: { id: string }) => ({
            status: 200 as const,
            body: { id, name: "Alice" },
        }),
    },
    "POST /users": {
        handler: (body: { name: string; email: string }) => ({
            status: 201 as const,
            body: { id: crypto.randomUUID(), ...body },
        }),
    },
} satisfies Record<
    string,
    { handler: (...args: any[]) => { status: number; body: any } }
>;

// Step 2: Derive the route types
type RouteMap = typeof routes;
type RouteName = keyof RouteMap;

// Step 3: Typed request handler
type RouteHandler<R extends RouteName> = RouteMap[R]["handler"];
type RouteParams<R extends RouteName> =
    R extends `${string}:${infer _}` ? ExtractRouteParams<R & string> : {};
type RouteBody<R extends RouteName> =
    RouteHandler<R> extends (body: infer B) => any ? B : never;
```

## Generic Router Implementation

```typescript
class TypedRouter<T extends Record<string, { handler: (...args: any[]) => any }>> {
    private handlers = new Map<string, Function>();

    constructor(routes: T) {
        for (const [key, config] of Object.entries(routes)) {
            this.handlers.set(key, config.handler);
        }
    }

    // Typed dispatch — returns the exact type from each route's handler
    async dispatch<R extends keyof T & string>(
        method: R extends `${infer M} ${string}` ? M : never,
        path: string,
        body?: any,
    ): Promise<ReturnType<T[R]["handler"]>> {
        const handler = this.handlers.get(`${method} ${path}`);
        if (!handler) throw new Error(`No handler for ${method} ${path}`);
        return handler(body);
    }
}

// Usage:
const router = new TypedRouter(routes);
const result = await router.dispatch("GET", "/users");
// result is typed as:
// | { status: number; body: User[] }
// | { readonly status: 200; body: { id: string; name: string } }
// | { readonly status: 201; body: { id: string; name: string; email: string } }
```

## Client-Side Type Generation

```typescript
// From the same route map, generate a typed fetch client:

function createClient<T extends Record<string, { handler: (...args: any[]) => any }>>(
    baseUrl: string
) {
    return {
        get: async <R extends keyof T & string>(
            route: R,
            params?: RouteParams<R>
        ): Promise<ReturnType<T[R]["handler"]>> => {
            let url = `${baseUrl}${route}`;
            if (params) {
                for (const [k, v] of Object.entries(params)) {
                    url = url.replace(`:${k}`, encodeURIComponent(String(v)));
                }
            }
            const res = await fetch(url);
            return res.json();
        },
        post: async <R extends keyof T & string>(
            route: R,
            body: RouteBody<R>
        ): Promise<ReturnType<T[R]["handler"]>> => {
            const res = await fetch(`${baseUrl}${route}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            return res.json();
        },
    };
}

const client = createClient<typeof routes>("http://localhost:3000");
const users = await client.get("GET /users");
const user = await client.get("GET /users/:id", { id: "abc" });
```

---

## Cross-Links

- [[TypeScript/03_Advanced/03_Infer_and_Template_Literal_Types]] for template literal types
- [[TypeScript/03_Advanced/01_Conditional_Types]] for infer in conditional types
- [[TypeScript/03_Advanced/04_Typing_Patterns_for_APIs]] for satisfies and API patterns
