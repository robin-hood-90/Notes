---
tags: [typescript, playbook, fetch, api, validation, zod, openapi]
aliases: ["Model API Types", "API Client Types", "Fetch Wrapper Types"]
status: stable
updated: 2026-05-11
---

# Playbook: Model API Types Safely

> [!summary] Goal
> Bridge the gap between runtime API responses (which arrive as `unknown`) and compile-time TypeScript types. Validate at the boundary, propagate typed errors, and integrate with schema validators.

## Rule: JSON is `unknown`

Every `res.json()` call returns `unknown` — the type system can't guarantee the shape.

```typescript
const data: unknown = await response.json();
```

## Generic Fetch Wrapper with Path/Query/Body Typing

```typescript
// A typed fetch wrapper that maps method + path to request/response types:

// Step 1: Define endpoint types
interface Endpoints {
    "GET /users": { response: User[] };
    "GET /users/:id": { params: { id: string }; response: User };
    "POST /users": { body: CreateUserDTO; response: User };
    "PATCH /users/:id": { params: { id: string }; body: Partial<CreateUserDTO>; response: User };
    "DELETE /users/:id": { params: { id: string }; response: void };
}

// Step 2: Generic client
async function apiClient<M extends keyof Endpoints & string>(
    method: M,
    ...args: Endpoints[M] extends { params: infer P } ? [path: string, p?: P] : [path?: string]
): Promise<Endpoints[M]["response"]> {
    const [path, params] = args;
    let url = path ?? "";
    if (params) {
        for (const [k, v] of Object.entries(params)) {
            url = url.replace(`:${k}`, encodeURIComponent(String(v)));
        }
    }
    const res = await fetch(url, { method: method.split(" ")[0] as any });
    if (!res.ok) throw new ApiError(res.status, await res.text());
    return res.json();
}

// Usage:
const users = await apiClient("GET /users");
const user = await apiClient("GET /users/:id", { id: "abc" });
```

## Validation at the Boundary

### Zod

```typescript
import { z } from "zod";

const UserSchema = z.object({
    id: z.string().uuid(),
    email: z.string().email(),
    age: z.number().int().positive().optional(),
});

type User = z.infer<typeof UserSchema>;

async function fetchUser(id: string): Promise<User> {
    const res = await fetch(`/api/users/${id}`);
    const json: unknown = await res.json();
    return UserSchema.parse(json);  // Throws ZodError on mismatch
}
```

### OpenAPI → TypeScript codegen

```bash
# Generate types from OpenAPI spec:
npx openapi-typescript ./schema.yaml -o ./types/api.ts

# Then use generated types directly:
import type { paths } from "./types/api";
type UserResponse = paths["/users/{id}"]["get"]["responses"][200]["content"]["application/json"];
```

## Error Boundary Pattern

```typescript
type ApiResult<T, E = string> =
    | { ok: true; data: T }
    | { ok: false; error: E };

async function apiCall<T>(url: string): Promise<ApiResult<T>> {
    try {
        const res = await fetch(url);
        if (!res.ok) {
            return { ok: false, error: `HTTP ${res.status}: ${res.statusText}` };
        }
        const data: T = await res.json();
        return { ok: true, data };
    } catch (err) {
        return { ok: false, error: String(err) };
    }
}

// Usage:
const result = await apiCall<User[]>("/api/users");
if (result.ok) {
    console.log(result.data.length);
} else {
    console.error(result.error);
}
```

---

## Cross-Links

- [[TypeScript/02_Core/03_Discriminated_Unions]] for ApiResult discriminated union
- [[TypeScript/03_Advanced/04_Typing_Patterns_for_APIs]] for API typing patterns
- [[TypeScript/04_Playbooks/06_TypeScript_with_React]] for React + API fetching
