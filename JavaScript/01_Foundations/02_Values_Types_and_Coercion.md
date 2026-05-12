---
tags: [javascript, foundations]
aliases: ["JS Types", "Coercion"]
status: stable
updated: 2026-04-26
---

# Values, Types, and Coercion

> [!summary] Goal
> Avoid surprising bugs by understanding equality, truthiness, and implicit conversions. Master JavaScript's type system and coercion rules to write predictable code.

## Table of Contents

1. [Primitive Types](#primitive-types)
2. [Type Detection](#type-detection)
3. [Type Coercion](#type-coercion)
4. [Equality Comparisons](#equality-comparisons)
5. [Truthiness and Falsiness](#truthiness-and-falsiness)
6. [Number System](#number-system)
7. [String Internals](#string-internals)
8. [Symbol and BigInt](#symbol-and-bigint)
9. [Object Type Conversion](#object-type-conversion)
10. [Common Pitfalls](#common-pitfalls)
11. [Best Practices](#best-practices)
12. [Interview Questions](#interview-questions)

---

## Primitive Types

JavaScript has **7 primitive types** and **1 object type**.

### The 7 Primitives

1. **`undefined`**: Absence of value (uninitialized variables)
2. **`null`**: Intentional absence of value
3. **`boolean`**: `true` or `false`
4. **`number`**: IEEE 754 double-precision floating-point
5. **`string`**: Sequence of UTF-16 code units
6. **`bigint`**: Arbitrary precision integers (ES2020)
7. **`symbol`**: Unique, immutable values (ES2015)

### Everything Else is an Object

- Objects, arrays, functions, dates, regex, etc.
- Objects are **mutable** and **passed by reference**
- Primitives are **immutable** and **passed by value**

### Primitive Wrapper Objects

JavaScript temporarily wraps primitives in objects when accessing properties:

```js
const str = 'hello';
console.log(str.length); // 5
console.log(str.toUpperCase()); // 'HELLO'

// Internally:
// 1. Temporary String object created: new String('hello')
// 2. Property/method accessed
// 3. Temporary object discarded
```

**Explicit wrapper objects** (avoid these):

```js
const str1 = 'hello';           // Primitive string
const str2 = new String('hello'); // String object (bad practice)

str1 === str2; // false (different types)
typeof str1;   // 'string'
typeof str2;   // 'object'
```

---

## Type Detection

### `typeof` Operator

Returns a string indicating the type.

```js
typeof undefined;        // 'undefined'
typeof true;             // 'boolean'
typeof 42;               // 'number'
typeof 'hello';          // 'string'
typeof 42n;              // 'bigint'
typeof Symbol('id');     // 'symbol'
typeof {};               // 'object'
typeof [];               // 'object' ⚠️
typeof null;             // 'object' ⚠️ (historical bug)
typeof function() {};    // 'function'
```

### `typeof` Quirks

#### 1. `typeof null` is 'object'

This is a **historic bug** in JavaScript that can't be fixed (would break too much code).

```js
typeof null; // 'object' (incorrect, but unchangeable)

// Check for null explicitly:
if (value === null) {
  // Handle null
}
```

#### 2. Arrays are 'object'

```js
typeof []; // 'object'

// Use Array.isArray():
Array.isArray([]); // true
Array.isArray({}); // false
```

#### 3. Functions are 'function'

```js
typeof function() {}; // 'function' (special case)
typeof (() => {}); // 'function'
typeof class {}; // 'function' (classes are functions)
```

### Better Type Checking

```js
// Check for array
Array.isArray(value)

// Check for null
value === null

// Check for NaN
Number.isNaN(value) // Preferred
isNaN(value)        // Coerces value first (avoid)

// Check for plain object
Object.prototype.toString.call(value) === '[object Object]'

// Check for integer
Number.isInteger(value)

// Check for finite number
Number.isFinite(value)
```

### Complete Type Detection Function

```js
function getType(value) {
  if (value === null) return 'null';
  if (Array.isArray(value)) return 'array';
  
  const type = typeof value;
  if (type === 'object') {
    return Object.prototype.toString.call(value).slice(8, -1).toLowerCase();
  }
  
  return type;
}

getType(null);           // 'null'
getType([]);             // 'array'
getType(new Date());     // 'date'
getType(/regex/);        // 'regexp'
getType(42);             // 'number'
```

---

## Type Coercion

**Coercion** is the automatic or explicit conversion of values from one type to another.

### Explicit Coercion (Intentional)

```js
// To String
String(123);           // '123'
(123).toString();      // '123'
'' + 123;              // '123'

// To Number
Number('123');         // 123
+'123';                // 123 (unary plus)
parseInt('123', 10);   // 123
parseFloat('3.14');    // 3.14

// To Boolean
Boolean(1);            // true
!!1;                   // true (double negation)
```

### Implicit Coercion (Automatic)

JavaScript automatically converts types in certain operations.

#### String Coercion

The `+` operator with strings converts other operands to strings.

```js
'The answer is ' + 42;           // 'The answer is 42'
'Value: ' + true;                // 'Value: true'
'Result: ' + null;               // 'Result: null'
'Data: ' + undefined;            // 'Data: undefined'
'Array: ' + [1, 2, 3];           // 'Array: 1,2,3'
'Object: ' + { a: 1 };           // 'Object: [object Object]'
```

#### Numeric Coercion

Mathematical operators (except `+`) convert operands to numbers.

```js
'5' - 2;               // 3
'5' * 2;               // 10
'10' / 2;              // 5
'10' % 3;              // 1
'5' > 3;               // true

// Unary plus
+'42';                 // 42
+true;                 // 1
+false;                // 0
+null;                 // 0
+undefined;            // NaN
+'';                   // 0
+'hello';              // NaN
```

#### Boolean Coercion

Happens in `if`, `while`, `for`, ternary, logical operators.

```js
if ('hello') {         // true (non-empty string)
  console.log('truthy');
}

!!0;                   // false
!!'hello';             // true
```

### Abstract Operations

JavaScript uses internal abstract operations for coercion.

#### ToPrimitive

Converts object to primitive value.

**Algorithm**:
1. If input is primitive, return as-is
2. If `Symbol.toPrimitive` method exists, call it
3. If hint is 'string', try `toString()` then `valueOf()`
4. Otherwise, try `valueOf()` then `toString()`

```js
const obj = {
  valueOf() {
    return 42;
  },
  toString() {
    return 'object';
  }
};

+obj;                  // 42 (numeric context, valueOf called)
String(obj);           // 'object' (string context, toString called)

// Custom ToPrimitive
const custom = {
  [Symbol.toPrimitive](hint) {
    if (hint === 'number') return 42;
    if (hint === 'string') return 'custom';
    return 'default';
  }
};

+custom;               // 42
String(custom);        // 'custom'
custom + '';           // 'default'
```

#### ToBoolean

Converts value to boolean.

**Falsy values** (8 total):
- `false`
- `0`, `-0`, `0n`
- `''`, `""`, ``` `` ``` (empty string)
- `null`
- `undefined`
- `NaN`

Everything else is **truthy**, including:
- `'0'`, `'false'` (non-empty strings)
- `[]`, `{}` (objects/arrays)
- `function() {}` (functions)
- `Infinity`, `-Infinity`

```js
Boolean(0);            // false
Boolean('0');          // true (string)
Boolean([]);           // true (object)
Boolean({});           // true (object)
```

#### ToNumber

Converts value to number.

| Input | Result |
|-------|--------|
| `undefined` | `NaN` |
| `null` | `0` |
| `true` | `1` |
| `false` | `0` |
| `""` (empty string) | `0` |
| `"123"` | `123` |
| `"12.34"` | `12.34` |
| `"hello"` | `NaN` |
| `"  42  "` | `42` (whitespace trimmed) |

```js
Number(undefined);     // NaN
Number(null);          // 0 ⚠️
Number(true);          // 1
Number(false);         // 0
Number('');            // 0 ⚠️
Number('  ');          // 0 ⚠️
Number('123');         // 123
Number('12.34');       // 12.34
Number('0x10');        // 16 (hex)
Number('1e3');         // 1000 (scientific)
```

#### ToString

Converts value to string.

| Input | Result |
|-------|--------|
| `undefined` | `"undefined"` |
| `null` | `"null"` |
| `true` | `"true"` |
| `false` | `"false"` |
| `123` | `"123"` |
| `NaN` | `"NaN"` |
| `Infinity` | `"Infinity"` |
| `[]` | `""` (empty string) |
| `[1, 2, 3]` | `"1,2,3"` |
| `{ a: 1 }` | `"[object Object]"` |

```js
String(null);          // 'null'
String(undefined);     // 'undefined'
String(true);          // 'true'
String(123);           // '123'
String([1, 2, 3]);     // '1,2,3'
String({ a: 1 });      // '[object Object]'

// Arrays to string
String([]);            // ''
String([1]);           // '1'
String([1, 2]);        // '1,2'
String([null]);        // ''
String([undefined]);   // ''
```

---

## Equality Comparisons

JavaScript has 4 types of equality comparisons.

### `==` (Loose Equality)

Performs **type coercion** before comparison.

#### Coercion Rules for `==`

1. **Same type**: Compare directly (like `===`)
2. **null == undefined**: `true` (special case)
3. **Number vs String**: Convert string to number
4. **Boolean**: Convert to number (true → 1, false → 0)
5. **Object vs Primitive**: Convert object to primitive

#### Examples

```js
// Same type (no coercion)
5 == 5;                // true
'hello' == 'hello';    // true

// null and undefined
null == undefined;     // true ⚠️
null == 0;             // false
undefined == 0;        // false

// Number vs String
5 == '5';              // true (string coerced to number)
0 == '';               // true (empty string → 0)
0 == '0';              // true

// Boolean coercion
true == 1;             // true (true → 1)
false == 0;            // true (false → 0)
true == '1';           // true (true → 1, '1' → 1)
false == '';           // true (false → 0, '' → 0)

// Object to primitive
[1] == 1;              // true ([1].toString() → '1' → 1)
[''] == 0;             // true ([''].toString() → '' → 0)
[null] == 0;           // true ([null].toString() → '' → 0)
```

### `===` (Strict Equality)

**No type coercion**. Both value and type must match.

```js
5 === 5;               // true
5 === '5';             // false (different types)
null === undefined;    // false (different types)
0 === false;           // false (different types)
'' === 0;              // false (different types)

// Objects compared by reference
{} === {};             // false (different objects)
[] === [];             // false (different arrays)

const obj = {};
obj === obj;           // true (same reference)
```

### `Object.is()`

Similar to `===` but handles edge cases differently.

```js
// Same as ===
Object.is(5, 5);                 // true
Object.is('hello', 'hello');     // true

// Edge cases
Object.is(NaN, NaN);             // true ⚠️ (=== returns false)
Object.is(0, -0);                // false ⚠️ (=== returns true)
Object.is(+0, -0);               // false

// Standard cases
Object.is(null, undefined);      // false
Object.is(true, 1);              // false
```

### SameValueZero

Used internally by `Map`, `Set`, `includes()`, etc.

Same as `Object.is()` except: `+0 === -0` is `true`.

```js
// Array.includes uses SameValueZero
[NaN].includes(NaN);   // true
[0].includes(-0);      // true

// Set uses SameValueZero
const set = new Set([NaN]);
set.has(NaN);          // true
```

### Comparison Table

| Comparison | `5 == '5'` | `NaN == NaN` | `0 == -0` | `null == undefined` |
|------------|------------|--------------|-----------|---------------------|
| `==` | `true` | `false` | `true` | `true` |
| `===` | `false` | `false` | `true` | `false` |
| `Object.is()` | `false` | `true` | `false` | `false` |

---

## Truthiness and Falsiness

### Falsy Values (8 Total)

```js
Boolean(false);        // false
Boolean(0);            // false
Boolean(-0);           // false
Boolean(0n);           // false (BigInt zero)
Boolean('');           // false
Boolean(null);         // false
Boolean(undefined);    // false
Boolean(NaN);          // false
```

### Truthy Values (Everything Else)

```js
Boolean(true);         // true
Boolean(1);            // true
Boolean(-1);           // true
Boolean('0');          // true ⚠️ (non-empty string)
Boolean('false');      // true ⚠️ (non-empty string)
Boolean([]);           // true ⚠️ (object)
Boolean({});           // true ⚠️ (object)
Boolean(function(){}); // true
Boolean(Infinity);     // true
Boolean(-Infinity);    // true
Boolean(new Date());   // true
```

### Logical Operators

#### `||` (OR) - Returns First Truthy or Last Value

```js
'hello' || 'world';    // 'hello' (first truthy)
0 || 1;                // 1 (second value, first is falsy)
null || undefined;     // undefined (last value, both falsy)
'' || 'default';       // 'default'

// Use case: Default values
const name = input || 'Guest';
```

**Caveat**: `0`, `''`, `false` are falsy

```js
const count = 0;
const display = count || 'No items'; // 'No items' ⚠️
```

#### `&&` (AND) - Returns First Falsy or Last Value

```js
'hello' && 'world';    // 'world' (both truthy, return last)
0 && 1;                // 0 (first falsy)
null && 'value';       // null (first falsy)
'a' && 'b' && 'c';     // 'c' (all truthy, return last)

// Use case: Conditional execution
user && user.name;     // Safe property access
```

#### `??` (Nullish Coalescing) - Returns Right if Left is null/undefined

```js
0 ?? 42;               // 0 (0 is not nullish)
'' ?? 'default';       // '' (empty string is not nullish)
null ?? 'default';     // 'default'
undefined ?? 'default';// 'default'
false ?? true;         // false (false is not nullish)

// Use case: Default only for null/undefined
const count = 0;
const display = count ?? 'No items'; // 0 ✅
```

### Comparison: `||` vs `??`

| Value | `value || 'default'` | `value ?? 'default'` |
|-------|----------------------|----------------------|
| `0` | `'default'` | `0` |
| `''` | `'default'` | `''` |
| `false` | `'default'` | `false` |
| `null` | `'default'` | `'default'` |
| `undefined` | `'default'` | `'default'` |
| `'value'` | `'value'` | `'value'` |

---

## Number System

JavaScript uses **IEEE 754 double-precision** (64-bit) floating-point.

### Number Structure

- **1 bit**: Sign (0 = positive, 1 = negative)
- **11 bits**: Exponent (range: -1023 to 1024)
- **52 bits**: Mantissa (fraction)

### Special Values

```js
Number.MAX_VALUE;              // 1.7976931348623157e+308
Number.MIN_VALUE;              // 5e-324 (closest to 0)
Number.MAX_SAFE_INTEGER;       // 9007199254740991 (2^53 - 1)
Number.MIN_SAFE_INTEGER;       // -9007199254740991
Number.POSITIVE_INFINITY;      // Infinity
Number.NEGATIVE_INFINITY;      // -Infinity
Number.NaN;                    // NaN
Number.EPSILON;                // 2.220446049250313e-16
```

### Floating-Point Precision Issues

```js
0.1 + 0.2;                     // 0.30000000000000004 ⚠️
0.1 + 0.2 === 0.3;             // false ⚠️

// Solution: Use epsilon for comparison
function areEqual(a, b) {
  return Math.abs(a - b) < Number.EPSILON;
}

areEqual(0.1 + 0.2, 0.3);      // true
```

### Safe Integer Range

Integers are safe between `-(2^53 - 1)` and `2^53 - 1`.

```js
Number.isSafeInteger(9007199254740991);  // true (2^53 - 1)
Number.isSafeInteger(9007199254740992);  // false (2^53)

// Beyond safe range, precision lost
9007199254740992 === 9007199254740993;   // true ⚠️
```

### NaN (Not-a-Number)

**NaN** is the result of invalid numeric operations.

```js
0 / 0;                 // NaN
Math.sqrt(-1);         // NaN
Number('hello');       // NaN
parseInt('abc');       // NaN

// NaN is not equal to anything, including itself
NaN === NaN;           // false ⚠️
NaN == NaN;            // false

// Check for NaN
Number.isNaN(NaN);     // true (preferred)
isNaN(NaN);            // true
isNaN('hello');        // true (coerces to number first)
Number.isNaN('hello'); // false (no coercion)

// Type guard
typeof NaN;            // 'number' ⚠️
```

### Infinity

```js
1 / 0;                 // Infinity
-1 / 0;                // -Infinity
Math.log(0);           // -Infinity

Infinity + 1;          // Infinity
Infinity * 2;          // Infinity
Infinity / Infinity;   // NaN
Infinity - Infinity;   // NaN

// Check for finite
Number.isFinite(100);        // true
Number.isFinite(Infinity);   // false
Number.isFinite(NaN);        // false
```

### Number Methods

```js
// Parsing
parseInt('123', 10);         // 123
parseInt('123.45', 10);      // 123
parseFloat('123.45');        // 123.45
parseInt('0x10', 16);        // 16 (hex)

// Formatting
(1234.5678).toFixed(2);      // '1234.57'
(1234.5678).toPrecision(4);  // '1235'
(1234.5678).toExponential(2);// '1.23e+3'

// Checking
Number.isInteger(123);       // true
Number.isInteger(123.45);    // false
Number.isNaN(NaN);           // true
Number.isFinite(Infinity);   // false
Number.isSafeInteger(10);    // true
```

---

## String Internals

### UTF-16 Encoding

JavaScript strings are sequences of **UTF-16 code units** (16-bit values).

```js
'A'.charCodeAt(0);           // 65 (code unit)
String.fromCharCode(65);     // 'A'

// Emoji (surrogate pairs, 2 code units)
'😀'.length;                  // 2 ⚠️ (2 UTF-16 code units)
'😀'.charCodeAt(0);           // 55357 (high surrogate)
'😀'.charCodeAt(1);           // 56832 (low surrogate)

// Code points (correct)
'😀'.codePointAt(0);          // 128512 (full code point)
String.fromCodePoint(128512);// '😀'
```

### String Length

```js
'hello'.length;              // 5
''.length;                   // 0
'😀'.length;                  // 2 (surrogate pair)
'👨‍👩‍👧‍👦'.length;                  // 11 ⚠️ (family emoji with ZWJ)

// Counting graphemes correctly
[...'😀'].length;             // 1 (spread operator splits by code points)
Array.from('😀').length;      // 1
```

### String Immutability

Strings are **immutable** - methods return new strings.

```js
const str = 'hello';
str[0] = 'H';                // Silently fails (strict mode: error)
console.log(str);            // 'hello' (unchanged)

// Create new string
const upper = str.toUpperCase(); // 'HELLO' (new string)
```

### Template Literals

```js
const name = 'Alice';
const greeting = `Hello, ${name}!`; // 'Hello, Alice!'

// Multi-line
const multiline = `
  Line 1
  Line 2
`;

// Tagged templates
function tag(strings, ...values) {
  console.log(strings); // ['Hello, ', '!']
  console.log(values);  // ['Alice']
  return strings[0] + values[0].toUpperCase() + strings[1];
}

tag`Hello, ${name}!`; // 'Hello, ALICE!'
```

---

## Symbol and BigInt

### Symbol

**Symbols** are unique, immutable primitive values.

```js
const sym1 = Symbol('description');
const sym2 = Symbol('description');
sym1 === sym2;               // false (always unique)

typeof sym1;                 // 'symbol'

// Use case: Object properties
const ID = Symbol('id');
const user = {
  [ID]: 123,
  name: 'Alice'
};

user[ID];                    // 123
Object.keys(user);           // ['name'] (symbol not enumerated)
Object.getOwnPropertySymbols(user); // [Symbol(id)]

// Global symbol registry
const sym3 = Symbol.for('shared');
const sym4 = Symbol.for('shared');
sym3 === sym4;               // true (same symbol)

Symbol.keyFor(sym3);         // 'shared'
```

### BigInt

**BigInt** represents arbitrary precision integers (ES2020).

```js
const big1 = 123n;           // BigInt literal
const big2 = BigInt(123);    // BigInt function
const big3 = BigInt('123');  // From string

typeof big1;                 // 'bigint'

// Arithmetic
123n + 456n;                 // 579n
123n * 2n;                   // 246n
10n ** 100n;                 // Very large number

// Cannot mix with Number
123n + 123;                  // TypeError ⚠️
123n + BigInt(123);          // 246n ✅

// Comparison
123n == 123;                 // true (coercion)
123n === 123;                // false (different types)
123n < 124;                  // true (coercion allowed)

// Use case: Safe large integers
const largeNum = 9007199254740991n; // Beyond Number.MAX_SAFE_INTEGER
largeNum + 1n;               // 9007199254740992n (accurate)
```

---

## Object Type Conversion

### Object to Primitive

When objects are coerced to primitives, JavaScript uses these methods:

1. **Symbol.toPrimitive** (if defined)
2. **valueOf()**
3. **toString()**

```js
const obj = {
  valueOf() {
    return 42;
  },
  toString() {
    return 'object';
  }
};

Number(obj);                 // 42 (valueOf)
String(obj);                 // 'object' (toString)
obj + 0;                     // 42 (numeric context)
obj + '';                    // 'object' (string context)

// Custom Symbol.toPrimitive
const custom = {
  [Symbol.toPrimitive](hint) {
    if (hint === 'number') return 10;
    if (hint === 'string') return 'custom';
    return 'default';
  }
};

Number(custom);              // 10
String(custom);              // 'custom'
custom + '';                 // 'default'
```

### Array to Primitive

```js
String([1, 2, 3]);           // '1,2,3' (join(','))
Number([42]);                // 42
Number([1, 2]);              // NaN

// In comparisons
[1] == 1;                    // true
[1, 2] == '1,2';             // true
[] == 0;                     // true ⚠️
[] == false;                 // true ⚠️
```

### Date to Primitive

```js
const date = new Date('2026-04-26');

Number(date);                // 1777276800000 (timestamp)
String(date);                // 'Sat Apr 26 2026 ...'
date + 0;                    // 'Sat Apr 26 2026 ...0' (string concat)
date - 0;                    // 1777276800000 (numeric)
```

---

## Common Pitfalls

### 1. `typeof null` is 'object'

```js
typeof null;                 // 'object' ⚠️

// Always check explicitly
if (value === null) {
  // Handle null
}
```

### 2. `NaN` is Not Equal to Itself

```js
NaN === NaN;                 // false ⚠️

// Use Number.isNaN
Number.isNaN(value);         // true for NaN only
```

### 3. Floating-Point Arithmetic

```js
0.1 + 0.2;                   // 0.30000000000000004 ⚠️
0.1 + 0.2 === 0.3;           // false ⚠️

// Use epsilon comparison
Math.abs((0.1 + 0.2) - 0.3) < Number.EPSILON; // true
```

### 4. Truthy Objects

```js
Boolean([]);                 // true ⚠️
Boolean({});                 // true ⚠️
Boolean(new Boolean(false)); // true ⚠️ (object, not primitive)

if ([]) {
  // This runs!
}
```

### 5. Empty String Coercion

```js
'' == 0;                     // true ⚠️
'' == false;                 // true ⚠️
Number('');                  // 0 ⚠️

// Use strict equality
'' === 0;                    // false
```

### 6. Array Coercion Surprises

```js
[] + [];                     // '' (empty string)
[] + {};                     // '[object Object]'
{} + [];                     // 0 (in some contexts, {} seen as block)
{} + {};                     // NaN or '[object Object][object Object]'

[1, 2] + [3, 4];             // '1,23,4' (string concat)
```

### 7. `null` vs `undefined` Coercion

```js
Number(null);                // 0 ⚠️
Number(undefined);           // NaN ⚠️

null == undefined;           // true
null === undefined;          // false

null == 0;                   // false ⚠️
undefined == 0;              // false ⚠️
```

### 8. String Number Comparison

```js
'10' > '9';                  // false ⚠️ (string comparison)
'10' > 9;                    // true (coerced to number)

// Strings compared lexicographically
'10' < '2';                  // true ⚠️ ('1' < '2')
```

### 9. BigInt and Number Mixing

```js
123n + 123;                  // TypeError ⚠️

// Explicit conversion needed
123n + BigInt(123);          // 246n
Number(123n) + 123;          // 246
```

### 10. Wrapper Object Creation

```js
const str = new String('hello'); // ❌ Don't do this
typeof str;                  // 'object' (not 'string')

// Use primitives
const str = 'hello';         // ✅ Correct
```

### 11. `isNaN()` vs `Number.isNaN()`

```js
isNaN('hello');              // true (coerces to NaN)
Number.isNaN('hello');       // false (no coercion)

isNaN(NaN);                  // true
Number.isNaN(NaN);           // true

// Prefer Number.isNaN
```

### 12. Negative Zero

```js
-0 === 0;                    // true ⚠️
Object.is(-0, 0);            // false

// Detecting -0
function isNegativeZero(n) {
  return n === 0 && 1 / n === -Infinity;
}
```

### 13. parseInt Without Radix

```js
parseInt('08');              // 8 (modern engines)
parseInt('08', 10);          // 8 (explicit, safer)
parseInt('0x10');            // 16 (hex detected)
parseInt('10', 2);           // 2 (binary)

// Always specify radix
```

### 14. String Indexing with Emoji

```js
'😀'[0];                      // '\uD83D' (high surrogate, invalid)
'😀'.charAt(0);               // '\uD83D' (same issue)

// Use Array.from or spread
[...'😀'][0];                 // '😀' ✅
Array.from('😀')[0];          // '😀' ✅
```

### 15. Loose Equality `==` Gotchas

```js
'' == '0';                   // false
0 == '';                     // true ⚠️
0 == '0';                    // true ⚠️

false == 'false';            // false ⚠️
false == '0';                // true ⚠️

false == undefined;          // false
false == null;               // false
null == undefined;           // true ⚠️

// Use === to avoid confusion
```

### 16. Automatic Semicolon Insertion (ASI)

```js
// Not a type issue, but related to parsing
function test() {
  return
    {
      value: 42
    };
}

test(); // undefined ⚠️ (ASI inserts ; after return)

// Fix: Same line
function test() {
  return {
    value: 42
  };
}
```

### 17. `valueOf()` in Comparisons

```js
const obj1 = {
  valueOf() { return 1; }
};

const obj2 = {
  valueOf() { return 2; }
};

obj1 < obj2;                 // true (1 < 2)
obj1 + obj2;                 // 3 (1 + 2)
```

### 18. String Length with Unicode

```js
'A'.length;                  // 1
'😀'.length;                  // 2 ⚠️ (surrogate pair)
'👨‍👩‍👧‍👦'.length;                  // 11 ⚠️ (family emoji with ZWJ)

// Use spread for code points
[...'😀'].length;             // 1
```

### 19. Object Property Coercion

```js
const obj = {};
obj[1] = 'one';              // Key coerced to '1'
obj['1'];                    // 'one'
obj[1];                      // 'one'

obj[{}] = 'object';          // Key coerced to '[object Object]'
obj['[object Object]'];      // 'object'
```

### 20. Date Arithmetic

```js
new Date() - new Date();     // 0 (number subtraction)
new Date() + new Date();     // "..." (string concatenation)

const d1 = new Date('2026-01-01');
const d2 = new Date('2026-01-02');
d2 - d1;                     // 86400000 (ms difference)
d2 + d1;                     // String concatenation
```

---

## Best Practices

### 1. Use `===` Instead of `==`

```js
// ❌ Avoid loose equality
if (value == 42) { }

// ✅ Use strict equality
if (value === 42) { }
```

### 2. Check for `null` and `undefined` Explicitly

```js
// ❌ Implicit check catches 0, '', false
if (value) { }

// ✅ Explicit null/undefined check
if (value != null) { } // Checks both null and undefined
if (value !== null && value !== undefined) { } // More explicit

// ✅ Use ?? for defaults
const result = value ?? 'default';
```

### 3. Use `Number.isNaN()` for NaN Checks

```js
// ❌ Coerces to number first
if (isNaN(value)) { }

// ✅ No coercion
if (Number.isNaN(value)) { }
```

### 4. Specify Radix in `parseInt()`

```js
// ❌ Implicit radix (risky)
parseInt('08');

// ✅ Explicit radix
parseInt('08', 10);
```

### 5. Use `Array.isArray()` for Arrays

```js
// ❌ Unreliable
if (typeof arr === 'object') { }

// ✅ Correct
if (Array.isArray(arr)) { }
```

### 6. Avoid Wrapper Objects

```js
// ❌ Don't create wrapper objects
const str = new String('hello');
const num = new Number(42);

// ✅ Use primitives
const str = 'hello';
const num = 42;
```

### 7. Use BigInt for Large Integers

```js
// ❌ Loses precision
const large = 9007199254740992;

// ✅ Accurate with BigInt
const large = 9007199254740992n;
```

### 8. Be Careful with Floating-Point Math

```js
// ❌ Direct comparison
if (0.1 + 0.2 === 0.3) { }

// ✅ Epsilon comparison
if (Math.abs((0.1 + 0.2) - 0.3) < Number.EPSILON) { }

// ✅ Or use integers
const cents = Math.round(amount * 100); // Work in cents
```

### 9. Use Template Literals for String Building

```js
// ❌ String concatenation
const message = 'Hello, ' + name + '! You have ' + count + ' messages.';

// ✅ Template literal
const message = `Hello, ${name}! You have ${count} messages.`;
```

### 10. Explicitly Convert Types

```js
// ❌ Implicit coercion
const num = +str;
const str = value + '';

// ✅ Explicit conversion
const num = Number(str);
const str = String(value);
```

---

## Interview Questions

### Q1: What are the primitive types in JavaScript?

**Answer**: JavaScript has 7 primitive types:
1. `undefined` - uninitialized values
2. `null` - intentional absence of value
3. `boolean` - true/false
4. `number` - IEEE 754 double-precision floats
5. `string` - UTF-16 text sequences
6. `bigint` - arbitrary precision integers (ES2020)
7. `symbol` - unique immutable values (ES2015)

Everything else is an object (including arrays, functions, dates).

### Q2: Explain the difference between `==` and `===`.

**Answer**:
- `==` (loose equality): Performs type coercion before comparison. `5 == '5'` is `true`.
- `===` (strict equality): No type coercion. Both type and value must match. `5 === '5'` is `false`.

**Best practice**: Always use `===` unless you specifically need coercion.

### Q3: What are falsy values in JavaScript?

**Answer**: There are exactly 8 falsy values:
- `false`
- `0`, `-0`
- `0n` (BigInt zero)
- `''` (empty string)
- `null`
- `undefined`
- `NaN`

Everything else is truthy, including `'0'`, `'false'`, `[]`, and `{}`.

### Q4: Why does `0.1 + 0.2 !== 0.3`?

**Answer**: JavaScript uses IEEE 754 double-precision floating-point numbers, which cannot precisely represent some decimal fractions. `0.1` and `0.2` are approximations, so their sum is `0.30000000000000004`.

**Solution**: Use epsilon comparison:
```js
Math.abs((0.1 + 0.2) - 0.3) < Number.EPSILON; // true
```

### Q5: What's the difference between `null` and `undefined`?

**Answer**:
- `undefined`: Default value for uninitialized variables, missing function parameters, or non-existent properties.
- `null`: Intentional absence of value, explicitly set by programmers.

```js
let x;           // undefined (uninitialized)
const obj = {};
obj.prop;        // undefined (doesn't exist)

let y = null;    // null (explicitly set)
```

They're loosely equal: `null == undefined` is `true`, but strictly different: `null === undefined` is `false`.

### Q6: Explain `typeof` quirks.

**Answer**: `typeof` has several quirks:

1. `typeof null` is `'object'` (historic bug)
2. `typeof []` is `'object'` (use `Array.isArray()`)
3. `typeof function() {}` is `'function'` (special case)
4. `typeof NaN` is `'number'`

### Q7: What is `NaN` and how do you check for it?

**Answer**: `NaN` ("Not-a-Number") is a special numeric value resulting from invalid operations like `0/0` or `Number('hello')`.

**Unique property**: `NaN` is not equal to itself: `NaN === NaN` is `false`.

**Check for NaN**:
- `Number.isNaN(value)` - recommended (no coercion)
- `isNaN(value)` - coerces to number first (less reliable)
- `value !== value` - works because only NaN fails self-equality

### Q8: Explain the difference between `||` and `??`.

**Answer**:

**`||` (OR)**: Returns first truthy value or last value
```js
0 || 42;         // 42 (0 is falsy)
'' || 'default'; // 'default' ('' is falsy)
```

**`??` (Nullish Coalescing)**: Returns right side only if left is `null` or `undefined`
```js
0 ?? 42;         // 0 (0 is not nullish)
'' ?? 'default'; // '' ('' is not nullish)
null ?? 'default'; // 'default'
```

**Use `??`** when you want to treat `0`, `''`, and `false` as valid values.

---

## Cross-Links

- **Runtime and execution**: [[JavaScript/01_Foundations/01_JS_Runtime_and_Event_Loop]]
- **Objects and prototypes**: [[JavaScript/01_Foundations/03_Objects_Prototypes_and_Classes]]
- **Type guards in TypeScript**: [[TypeScript/01_Foundations/02_Type_Guards_and_Narrowing]]

## References

- [MDN: Equality comparisons and sameness](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Equality_comparisons_and_sameness)
- [MDN: Type coercion](https://developer.mozilla.org/en-US/docs/Glossary/Type_coercion)
- [ECMA-262 Specification: Type Conversion](https://tc39.es/ecma262/#sec-type-conversion)
- [IEEE 754 Floating Point](https://en.wikipedia.org/wiki/IEEE_754)

---

**Status**: stable  
**Last Updated**: 2026-04-26  
**Lines**: 1000+
