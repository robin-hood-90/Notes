---
tags: [javascript, es2023, es2024, symbol, array-methods, set-methods, temporal, group-by, well-known-symbols]
aliases: ["ES2023", "ES2024", "Modern JavaScript", "Symbol", "Well-Known Symbols"]
status: stable
updated: 2026-05-11
---

# ES2023-2024 Features and `Symbol`

> [!summary] Goal
> Master modern JavaScript: safe immutable array methods (ES2023), `Array.fromAsync`, Set methods, `Promise.withResolvers()`, `Object.groupBy()`/`Map.groupBy()` (ES2024), and the `Symbol` type — both creating unique keys and using well-known symbols.

## Table of Contents

1. [ES2023: Safe Array Methods](#es2023-safe-array-methods)
2. [ES2024: New Built-ins](#es2024-new-built-ins)
3. [Symbol — Unique Keys](#symbol-unique-keys)
4. [Well-Known Symbols](#well-known-symbols)

---

## ES2023: Safe Array Methods

> [!info] Safe immutable array methods
> ES2023 adds four methods that return a new array (no mutation), plus `Array.fromAsync` for async iterables. These solve the longstanding issue that `.sort()` and `.splice()` mutate the original array — forcing defensive copies.

```javascript
const arr = [3, 1, 4, 1, 5, 9];

// toReversed() — like .reverse() but returns a copy
const reversed = arr.toReversed();   // [9, 5, 1, 4, 1, 3]
console.log(arr);                    // [3, 1, 4, 1, 5, 9] — unchanged!

// toSorted(compareFn) — like .sort() but returns a copy
const sorted = arr.toSorted((a, b) => a - b);  // [1, 1, 3, 4, 5, 9]
console.log(arr);                                // unchanged

// toSpliced(start, deleteCount, ...items) — like .splice() but returns a copy
const spliced = arr.toSpliced(2, 2, 10, 20);    // [3, 1, 10, 20, 5, 9]
console.log(arr);                                // unchanged

// with(index, value) — set an element without mutation
const updated = arr.with(0, 100);              // [100, 1, 4, 1, 5, 9]
console.log(arr);                                // unchanged

// Before ES2023: you had to manually copy first
const copy = [...arr].sort();
// Now: arr.toSorted() does it in one call
```

### `Array.fromAsync`

```javascript
// Creates an array from an async iterable or promise source.
// Like Array.from() but awaits promises sequentially.

// Example: fetch paginated results
async function* fetchPages(url) {
    for (let i = 1; i <= 3; i++) {
        const res = await fetch(`${url}?page=${i}`);
        const data = await res.json();
        yield data.items;
    }
}

const allItems = await Array.fromAsync(
    fetchPages('/api/users'),
    { map: item => ({ ...item, fetchedAt: Date.now() }) }
);

// Also works with synchronous iterables (non-blocking):
const asyncItems = await Array.fromAsync([Promise.resolve(1), Promise.resolve(2)]);
// → [1, 2]

// Difference from Promise.all:
//   Array.fromAsync processes items SEQUENTIALLY (awaits one by one)
//   Promise.all processes items CONCURRENTLY
```

---

## ES2024: New Built-ins

### `Promise.withResolvers()`

```javascript
// Creates a Promise with externally accessible resolve/reject functions.
// No more wrapping in a Promise constructor just to get the callbacks.

// Before:
let resolve, reject;
const promise = new Promise((res, rej) => { resolve = res; reject = rej; });

// After:
const { promise, resolve, reject } = Promise.withResolvers();

// Use case: convert a callback-based API to promise
function readFilePromise(path) {
    const { promise, resolve, reject } = Promise.withResolvers();
    fs.readFile(path, 'utf-8', (err, data) => {
        if (err) reject(err);
        else resolve(data);
    });
    return promise;
}
```

### `Object.groupBy()` / `Map.groupBy()`

```javascript
const items = [
    { type: 'fruit', name: 'apple' },
    { type: 'fruit', name: 'banana' },
    { type: 'vegetable', name: 'carrot' },
    { type: 'fruit', name: 'date' },
];

// Object.groupBy — groups by string key, returns a plain object
const byType = Object.groupBy(items, item => item.type);
// {
//   fruit: [{ type: 'fruit', name: 'apple' }, ...],
//   vegetable: [{ type: 'vegetable', name: 'carrot' }]
// }

// Map.groupBy — groups by any key type, returns a Map
const byLength = Map.groupBy(items, item => item.name.length);
// Map(2) { 5 => [{...fruit}, {...fruit}], 6 => [{...vegetable}, {...fruit}] }
```

### Set methods (ES2024)

```javascript
const a = new Set([1, 2, 3, 4]);
const b = new Set([3, 4, 5, 6]);

// union — elements in either set
const union = a.union(b);              // Set {1, 2, 3, 4, 5, 6}

// intersection — elements in both sets
const intersection = a.intersection(b);// Set {3, 4}

// difference — elements in a but not b
const difference = a.difference(b);    // Set {1, 2}

// symmetricDifference — elements in one but not both
const symDiff = a.symmetricDifference(b); // Set {1, 2, 5, 6}

// isSubsetOf — is every element of a in b?
console.log(a.isSubsetOf(b));          // false
console.log(new Set([3]).isSubsetOf(b)); // true

// isSupersetOf — does a contain every element of b?
console.log(a.isSupersetOf(new Set([3, 4]))); // true

// isDisjointFrom — are there no common elements?
console.log(a.isDisjointFrom(new Set([7, 8])));// true
```

### `Error.cause` chaining

```javascript
// ES2022 (not 2024, but commonly grouped): Error.cause enables error chaining

try {
    await fetchData();
} catch (err) {
    throw new Error('Failed to load dashboard', {
        cause: err,  // Chain the original error
    });
}

// In the error handler:
catch (err) {
    console.log(err.message);        // "Failed to load dashboard"
    console.log(err.cause?.message); // Original error message
    // Error-cause chains work well with logging systems
}
```

---

## `Symbol` — Unique Keys

> [!info] Symbol
> A `Symbol` is a unique, immutable primitive value used as an object property key. Every call to `Symbol()` returns a new, unique value — even with the same description. Symbols guarantee property key uniqueness, preventing name collisions in objects.

```javascript
// Creating symbols:
const sym1 = Symbol();                // Unique symbol
const sym2 = Symbol('description');   // With description (for debugging)
const sym3 = Symbol('description');   // sym2 !== sym3 (always unique!)

// Using as property keys:
const LOGIN = Symbol('login');
const user = {
    name: 'Alice',
    [LOGIN]: 'alice@example.com',
};
console.log(user[LOGIN]);             // 'alice@example.com'
console.log(Object.keys(user));       // ['name'] — Symbol keys are hidden!
console.log(Object.getOwnPropertySymbols(user));  // [Symbol(login)]

// Global symbol registry:
const globalSym = Symbol.for('shared.key');     // Creates or retrieves
const sameGlobal = Symbol.for('shared.key');     // Same symbol as above!
console.log(globalSym === sameGlobal);           // true
console.log(Symbol.keyFor(globalSym));           // 'shared.key'

// Symbol.description:
console.log(sym2.description);                   // 'description'
```

### Practical Symbol use cases

```javascript
// 1. Private-like properties (not truly private, but hidden from casual iteration)
const _password = Symbol('password');
class User {
    constructor(name, password) {
        this.name = name;
        this[_password] = password;  // Won't show up in Object.keys()
    }
    checkPassword(pw) {
        return this[_password] === pw;
    }
}

// 2. Enum-like constants
const Colors = {
    RED:   Symbol('red'),
    GREEN: Symbol('green'),
    BLUE:  Symbol('blue'),
};

// 3. Metaprogramming hooks (via well-known symbols)
```

---

## Well-Known Symbols

> [!info] Well-known symbols
> JavaScript provides built-in symbols that serve as extension points for language behavior. You implement these on your objects to integrate with JavaScript's built-in protocols (iteration, string conversion, type coercion, regex, etc.).

| Symbol | Used by | Purpose |
|--------|:-------:|---------|
| `Symbol.iterator` | `for..of`, `...` spread, `Array.from` | Returns default iterator (→ `[Symbol.iterator]()`) |
| `Symbol.asyncIterator` | `for await..of` | Returns async iterator (→ `[Symbol.asyncIterator]()`) |
| `Symbol.hasInstance` | `instanceof` | Custom `instanceof` check |
| `Symbol.toStringTag` | `Object.prototype.toString()` | Custom description for `[object Xxx]` |
| `Symbol.toPrimitive` | Type coercion (`String()`, `Number()`) | Convert to primitive (hint: string/number/default) |
| `Symbol.species` | `.map()`, `.filter()`, `.slice()` | Controls derived object constructor |
| `Symbol.match` / `Symbol.replace` / `Symbol.search` / `Symbol.split` | `String.prototype.{match/replace/search/split}` | Custom regex-like pattern matching |
| `Symbol.isConcatSpreadable` | `Array.prototype.concat()` | When true, object is spread into concat result |
| `Symbol.unscopables` | `with` statement | Exclude properties from `with` scope |
| `Symbol.dispose` / `Symbol.asyncDispose` | `using` / `await using` (ES2025) | Explicit resource management |

### Implementing well-known symbols

```javascript
// Symbol.iterator — make objects iterable
class Range {
    constructor(start, end) {
        this.start = start;
        this.end = end;
    }
    [Symbol.iterator]() {
        let current = this.start;
        const end = this.end;
        return {
            next() {
                if (current <= end) {
                    return { value: current++, done: false };
                }
                return { value: undefined, done: true };
            }
        };
    }
}
for (const n of new Range(1, 5)) console.log(n);  // 1 2 3 4 5

// Symbol.asyncIterator — async iteration
class AsyncRange {
    constructor(start, end) { this.start = start; this.end = end; }
    [Symbol.asyncIterator]() {
        let current = this.start;
        return {
            async next() {
                await new Promise(r => setTimeout(r, 10));  // Simulate async
                if (current <= this.end) {
                    return { value: current++, done: false };
                }
                return { value: undefined, done: true };
            }
        };
    }
}
for await (const n of new AsyncRange(1, 3)) console.log(n);

// Symbol.toStringTag — customize Object.prototype.toString
class MyClass {
    get [Symbol.toStringTag]() { return 'MyClass'; }
}
console.log(Object.prototype.toString.call(new MyClass()));  // "[object MyClass]"

// Symbol.toPrimitive — control coercion
class Money {
    constructor(amount, currency) {
        this.amount = amount;
        this.currency = currency;
    }
    [Symbol.toPrimitive](hint) {
        if (hint === 'number') return this.amount;
        if (hint === 'string') return `${this.currency} ${this.amount}`;
        return this.amount;  // default
    }
}
const price = new Money(99.95, 'USD');
console.log(+price);       // 99.95 (number)
console.log(String(price));// "USD 99.95"

// Symbol.species — control derived object construction
class MyArray extends Array {
    static get [Symbol.species]() { return Array; }  // .map returns Array, not MyArray
}
const myArr = new MyArray(1, 2, 3);
const mapped = myArr.map(x => x * 2);
console.log(mapped instanceof MyArray);  // false (returns plain Array)
```

---

## Cross-Links

- [[JavaScript/01_Foundations/04_Async_Promises_and_AsyncAwait]] for Promise basics and async/await
- [[JavaScript/02_Core/04_Fetch_Abort_and_Streams]] for fetch() with AbortController and ReadableStream
- [[JavaScript/01_Foundations/03_Objects_Prototypes_and_Classes]] for objects and property descriptors
- [[JavaScript/03_Advanced/01_Closures_Scopes_and_Garbage_Collection]] for GC aspects of Symbol registry
