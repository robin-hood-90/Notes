---
tags: [typescript, project, event-emitter, generics, mapped-types]
aliases: ["Typed Event Emitter", "Type-Safe Event Emitter"]
status: stable
updated: 2026-05-11
---

# Project: Build a Typed Event Emitter

> [!summary] Goal
> Build a type-safe event emitter using generics and `keyof` to map event names to payload types. Extend with async events, wildcard listeners, and Node.js-style inheritance.

## Core Implementation

```typescript
// Step 1: Define event map type — a record of event name → payload
type Events = {
    ready: void;
    message: { from: string; body: string };
    error: { message: string; code?: number };
    disconnect: undefined;
};

// Step 2: Build the emitter with typed on/emit/off
class TypedEventEmitter<E extends Record<string, any>> {
    private listeners = new Map<keyof E, Set<(...args: any[]) => void>>();

    on<K extends keyof E>(event: K, cb: (payload: E[K]) => void): () => void {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event)!.add(cb as any);
        // Return unsubscribe function
        return () => this.off(event, cb as any);
    }

    off<K extends keyof E>(event: K, cb: (payload: E[K]) => void): void {
        this.listeners.get(event)?.delete(cb as any);
    }

    emit<K extends keyof E>(event: K, payload: E[K]): void {
        this.listeners.get(event)?.forEach(cb => (cb as any)(payload));
    }

    once<K extends keyof E>(event: K, cb: (payload: E[K]) => void): void {
        const wrapper = (payload: E[K]) => {
            cb(payload);
            this.off(event, wrapper as any);
        };
        this.on(event, wrapper as any);
    }

    removeAllListeners(event?: keyof E): void {
        if (event) this.listeners.delete(event);
        else this.listeners.clear();
    }

    listenerCount(event: keyof E): number {
        return this.listeners.get(event)?.size ?? 0;
    }
}

// Usage:
const emitter = new TypedEventEmitter<Events>();
const unsub = emitter.on("message", (payload) => {
    // payload is typed as { from: string; body: string }
    console.log(payload.from, payload.body);
});
emitter.emit("message", { from: "Alice", body: "Hello" });
unsub();  // Unsubscribe
emitter.emit("ready", undefined);  // OK — void
```

## Handling `void` vs `undefined` vs no payload

```typescript
// In the Events type above:
//   ready: void         → emit("ready")            — no arg
//   disconnect: undefined → emit("disconnect")      — no arg
//   message: { ... }    → emit("message", payload)  — with arg

// The void/undefined handling:
// emit<K>(event: K, payload: E[K]): the payload parameter is required
// BUT if E[K] is void, you can call emit("ready") because void allows undefined.
```

## Wildcard `"*"` listener

```typescript
type WildcardEvents = Events & { "*": Events[keyof Events] };

class WildcardEmitter<E extends Record<string, any>> extends TypedEventEmitter<E> {
    on(event: "*", cb: (event: keyof E, payload: E[keyof E]) => void): () => void;
    on<K extends keyof E>(event: K, cb: (payload: E[K]) => void): () => void;
    on(event: any, cb: any): () => void {
        if (event === "*") {
            // Store wildcard listeners separately
            return super.on(event, cb);
        }
        return super.on(event, cb);
    }
    // Override emit to also fire "*" listeners
    emit<K extends keyof E>(event: K, payload: E[K]): void {
        super.emit(event, payload);
        super.emit("*" as any, { event, payload } as any);
    }
}
```

## Node.js Inheritance Pattern

```typescript
// When your class extends EventEmitter, use the E key mapping:
interface MyServiceEvents {
    start: { pid: number };
    data: Buffer;
    error: Error;
    stop: void;
}

class MyService extends TypedEventEmitter<MyServiceEvents> {
    async run() {
        this.emit("start", { pid: process.pid });
        try {
            const data = await this.fetchData();
            this.emit("data", data);
        } catch (err) {
            this.emit("error", err as Error);
        }
        this.emit("stop", undefined);
    }
    private async fetchData(): Promise<Buffer> { return Buffer.from("data"); }
}

const svc = new MyService();
svc.on("data", (data) => console.log(data.byteLength));  // typed as Buffer
```

---

## Cross-Links

- [[TypeScript/02_Core/02_Advanced_Generics]] for advanced generics patterns
- [[TypeScript/02_Core/09_Utility_Types_Deep_Dive]] for utility types
- [[JavaScript/03_Advanced/06_Node_EventEmitter_Buffer_and_System_APIs]] for Node.js EventEmitter patterns
