---
tags: [javascript, core, proxy, reflect, intl, metaprogramming, traps, internationalization]
aliases: ["Proxy", "Reflect API", "Intl API", "JavaScript Metaprogramming", "Internationalization"]
status: stable
updated: 2026-05-11
---

# Proxy, Reflect, and `Intl`

> [!summary] Goal
> Master JavaScript metaprogramming: the `Proxy` object (13 traps), the `Reflect` API for default behavior, and the `Intl` API for internationalization (dates, numbers, lists, segments). Also covers `Intl.DateTimeFormat`, `NumberFormat`, `ListFormat`, and `Segmenter`.

## Table of Contents

1. [Proxy — 13 Traps](#proxy-13-traps)
2. [Reflect API](#reflect-api)
3. [Intl API](#intl-api)

---

## Proxy — 13 Traps

> [!info] Proxy
> `Proxy` lets you intercept fundamental operations on an object: property access, assignment, deletion, function calls, constructor calls, and more. Each interceptable operation is called a **trap**. `Proxy` is the foundation for: observability (Vue, MobX), validation, logging, caching, and virtual properties.

```javascript
const target = { message: 'hello' };
const handler = {
    get(obj, prop) {
        console.log(`GET ${String(prop)}`);
        return Reflect.get(obj, prop);
    }
};
const proxy = new Proxy(target, handler);
console.log(proxy.message);  // Logs: "GET message", then "hello"
```

### The 13 traps with examples

| Trap | Triggered by | Purpose |
|:----:|:-------------|---------|
| `get` | `proxy[prop]`, `proxy.prop` | Property read |
| `set` | `proxy[prop] = val` | Property write |
| `has` | `'prop' in proxy` | `in` operator |
| `deleteProperty` | `delete proxy.prop` | Property deletion |
| `apply` | `proxy(...args)` | Function call |
| `construct` | `new proxy(...args)` | Constructor call |
| `ownKeys` | `Object.keys(proxy)`, `for..in` | Enumerate keys |
| `getOwnPropertyDescriptor` | `Object.getOwnPropertyDescriptor(proxy, prop)` | Property descriptor |
| `defineProperty` | `Object.defineProperty(proxy, prop, desc)` | Define property |
| `getPrototypeOf` | `Object.getPrototypeOf(proxy)` | Prototype access |
| `setPrototypeOf` | `Object.setPrototypeOf(proxy, proto)` | Prototype mutation |
| `preventExtensions` | `Object.preventExtensions(proxy)` | Lock object |
| `isExtensible` | `Object.isExtensible(proxy)` | Check extensibility |

### `get` and `set` — most common

```javascript
const validator = {
    set(obj, prop, value) {
        if (prop === 'age') {
            if (!Number.isInteger(value)) throw new TypeError('Age must be an integer');
            if (value < 0 || value > 150) throw new RangeError('Age out of range');
        }
        return Reflect.set(obj, prop, value);  // Must return boolean
    },
    get(obj, prop) {
        if (prop === 'age') {
            return Reflect.get(obj, prop) ?? 0;
        }
        return Reflect.get(obj, prop);
    }
};

const user = new Proxy({}, validator);
user.age = 30;   // OK
// user.age = 200;  // RangeError
```

### `has` and `deleteProperty`

```javascript
const hiddenProps = new Set(['_secret', '_private']);

const secureStore = new Proxy({}, {
    has(target, prop) {
        if (hiddenProps.has(prop)) return false;
        return Reflect.has(target, prop);
    },
    deleteProperty(target, prop) {
        if (hiddenProps.has(prop)) throw new Error(`Cannot delete ${String(prop)}`);
        return Reflect.deleteProperty(target, prop);
    },
    ownKeys(target) {
        return Reflect.ownKeys(target).filter(k => !hiddenProps.has(k));
    }
});
```

### `apply` and `construct`

```javascript
// apply — intercept function calls
function sum(a, b) { return a + b; }

const loggingFn = new Proxy(sum, {
    apply(target, thisArg, args) {
        console.log(`Called sum(${args})`);
        return Reflect.apply(target, thisArg, args);
    }
});
console.log(loggingFn(3, 4));  // "Called sum(3,4)" → 7

// construct — intercept new calls
class User { constructor(name) { this.name = name; } }

const GuardedUser = new Proxy(User, {
    construct(target, args) {
        if (!args[0]) throw new Error('Name is required');
        return Reflect.construct(target, args);
    }
});
// new GuardedUser()      // Error: Name is required
// new GuardedUser('Bob') // OK
```

### Revocable Proxy

```javascript
// Proxy can be revoked — after revoke, any operation throws.

const { proxy, revoke } = Proxy.revocable(target, handler);
proxy.message;  // Works
revoke();
// proxy.message;  // TypeError: Cannot perform 'get' on a proxy that has been revoked

// Use case: granting temporary access and then revoking it
function grantAccess(resource, timeout) {
    const { proxy, revoke } = Proxy.revocable(resource, handler);
    setTimeout(revoke, timeout);
    return proxy;
}
```

---

## Reflect API

> [!info] Reflect
> `Reflect` is a built-in object with static methods that mirror every Proxy trap. It provides the **default behavior** for each operation. In a Proxy handler, always call `Reflect.*` for the default; this ensures correct `this` binding and proper behavior for built-in objects.

```javascript
// All Reflect methods — one-to-one with Proxy traps:
Reflect.get(target, prop, receiver)
Reflect.set(target, prop, value, receiver)
Reflect.has(target, prop)
Reflect.deleteProperty(target, prop)
Reflect.apply(target, thisArg, args)
Reflect.construct(target, args)
Reflect.ownKeys(target)
Reflect.getOwnPropertyDescriptor(target, prop)
Reflect.defineProperty(target, prop, descriptor)
Reflect.getPrototypeOf(target)
Reflect.setPrototypeOf(target, prototype)
Reflect.preventExtensions(target)
Reflect.isExtensible(target)
```

### Why use Reflect instead of direct operations

```javascript
// 1. Correct receiver in inheritance
const parent = { get value() { return this._val ?? 42; } };
const child = { _val: 100 };

// Without Reflect: inheritance broken in proxy
const handlerBad = {
    get(target, prop) { return target[prop]; }  // This returns 42 for 'value'!
};

// With Reflect: respects inheritance chain
const handlerGood = {
    get(target, prop, receiver) {
        return Reflect.get(target, prop, receiver);  // Uses receiver (child)
    }
};

// 2. Boolean return for set/deleteProperty
const success = Reflect.set(target, 'age', 30);  // Always returns boolean
// vs: target['age'] = 30;  // Still works but returns undefined

// 3. Apply with proper thisArg
const args = Reflect.apply(Math.max, null, [1, 5, 3]);
console.log(args);  // 5
```

---

## `Intl` API

> [!info] Intl
> The `Intl` object provides locale-aware formatting for dates, numbers, lists, collation, and text segmentation. All `Intl` constructors accept a `locale` string and an `options` object. If no locale is specified, the runtime default is used.

### `Intl.DateTimeFormat`

```javascript
const date = new Date('2026-05-11T15:30:00');

// Basic:
console.log(new Intl.DateTimeFormat('en-US').format(date));     // "5/11/2026"
console.log(new Intl.DateTimeFormat('de-DE').format(date));     // "11.5.2026"
console.log(new Intl.DateTimeFormat('ja-JP').format(date));     // "2026/5/11"

// With options:
const formatter = new Intl.DateTimeFormat('en-US', {
    dateStyle: 'full',          // 'full', 'long', 'medium', 'short'
    timeStyle: 'long',          // Same options
    // Or individually:
    // year: 'numeric', month: 'long', day: 'numeric',
    // hour: '2-digit', minute: '2-digit', second: '2-digit',
    timeZone: 'America/New_York',
    timeZoneName: 'short',
});
console.log(formatter.format(date));  // "Monday, May 11, 2026 at 11:30:00 AM EDT"

// Format range:
const start = new Date('2026-05-11');
const end = new Date('2026-05-15');
console.log(new Intl.DateTimeFormat('en-US').formatRange(start, end));
// "May 11 – May 15, 2026"
```

### `Intl.NumberFormat`

```javascript
const num = 1234567.89;

console.log(new Intl.NumberFormat('en-US').format(num));        // "1,234,567.89"
console.log(new Intl.NumberFormat('de-DE').format(num));        // "1.234.567,89"
console.log(new Intl.NumberFormat('en-IN').format(num));        // "12,34,567.89"

// Currency:
console.log(new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
}).format(num));  // "$1,234,567.89"

console.log(new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
}).format(num));  // "1.234.567,89 €"

// Compact notation (ES2020):
console.log(new Intl.NumberFormat('en-US', {
    notation: 'compact',
    compactDisplay: 'short',
}).format(1500000));  // "1.5M"

// Units:
console.log(new Intl.NumberFormat('en-US', {
    style: 'unit',
    unit: 'kilometer-per-hour',
}).format(100));  // "100 km/h"
```

### `Intl.ListFormat`

```javascript
const fruits = ['apples', 'bananas', 'cherries'];

console.log(new Intl.ListFormat('en-US', {
    type: 'conjunction',   // 'conjunction' (and), 'disjunction' (or), 'unit'
    style: 'long',         // 'long', 'short', 'narrow'
}).format(fruits));  // "apples, bananas, and cherries"

console.log(new Intl.ListFormat('en-US', {
    type: 'disjunction',
    style: 'short',
}).format(fruits));  // "apples, bananas, or cherries"

console.log(new Intl.ListFormat('de-DE', {
    type: 'conjunction',
}).format(fruits));  // "apples, bananas und cherries"
```

### `Intl.Segmenter` (ES2021)

```javascript
// Segment text by grapheme (visible characters), word, or sentence.
// Essential for correctly counting characters in Unicode strings.

// Grapheme segmentation (visible character boundaries):
const segmenter = new Intl.Segmenter('en', { granularity: 'grapheme' });
const text = '👨‍👩‍👧‍👦';  // Family emoji — 7 code points, 1 grapheme
const segments = [...segmenter.segment(text)];
console.log(segments.length);  // 1 (one visible character)

// Word segmentation:
const wordSeg = new Intl.Segmenter('en', { granularity: 'word' });
for (const { segment, isWordLike } of wordSeg.segment('Hello, world!')) {
    console.log(segment, isWordLike);
    // "Hello" true, "," false, " " false, "world!" true
}

// Sentence segmentation:
const sentSeg = new Intl.Segmenter('en', { granularity: 'sentence' });
for (const { segment } of sentSeg.segment('First sentence. Second! Third?')) {
    console.log(segment);
}
```

### `Intl.Collator` — locale-aware sorting

```javascript
const names = ['Zürich', 'Ägypten', 'Österreich'];

// Without collator: default JS sort is lexicographic by UTF-16 code unit
console.log(names.sort());  // ['Zürich', 'Ägypten', 'Österreich'] (wrong for German)

// With collator:
const collator = new Intl.Collator('de-DE', { sensitivity: 'base' });
console.log(names.sort(collator.compare));
// ['Ägypten', 'Österreich', 'Zürich'] (correct German phonebook order)
```

---

## Cross-Links

- [[JavaScript/01_Foundations/03_Objects_Prototypes_and_Classes]] for Object methods and property descriptors
- [[JavaScript/01_Foundations/05_ES2023_2024_Features_and_Symbol]] for Symbol used in custom traps
- [[JavaScript/02_Core/03_Performance_and_Memory]] for Proxy performance considerations
- [[JavaScript/03_Advanced/01_Closures_Scopes_and_Garbage_Collection]] for WeakRef with FinalizationRegistry
