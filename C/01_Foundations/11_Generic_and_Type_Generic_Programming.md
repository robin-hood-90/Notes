---
tags: [c, foundations, generic, type-generic, c11, typeof, auto_type, tgmath, dispatch]
aliases: ["_Generic", "Type-Generic Programming", "Generic Selection", "typeof", "tgmath.h"]
status: stable
updated: 2026-05-11
---

# `_Generic` and Type-Generic Programming

> [!summary] Goal
> Master C11's `_Generic` selection for type-generic macros and functions. Understand `typeof` (C23), `__auto_type` (GNU), and how to write type-safe generic code without C++ templates. Essential for writing math libraries, serialization frameworks, and cross-platform abstraction layers.

## Table of Contents

1. [Why _Generic Exists](#why-generic-exists)
2. [Syntax and Rules](#syntax-and-rules)
3. [Type-Generic Macro Patterns](#type-generic-macro-patterns)
4. [typeof and auto_type](#typeof-and-autotype)
5. [tgmath.h — Type-Generic Math](#tgmath-h-type-generic-math)
6. [Comparison: _Generic vs C++ Templates](#comparison-generic-vs-c-templates)
7. [Pitfalls](#pitfalls)

---

## Why `_Generic` Exists

> [!info] Generic selection
> C11 introduced `_Generic` to write macros that produce different code depending on the type of an expression. It's a compile-time dispatch mechanism — the selection is made at compile time based on the **type** of a controlling expression. Unlike C++ templates or overloading, `_Generic` is pure C: no new syntax for function definitions, just type-dispatch macros.

Before `_Generic`, C code used:
- Multiple differently-named functions (`fabs`, `fabsf`, `fabsl`)
- Ugly preprocessor tricks with `sizeof` and type names
- GNU `__builtin_types_compatible_p` extension

```c
// Without _Generic: three functions, three names
double abs_double(double x) { return x < 0 ? -x : x; }
float  abs_float(float x)   { return x < 0 ? -x : x; }
int    abs_int(int x)       { return x < 0 ? -x : x; }

// With _Generic: one macro, different implementations
#define ABS(x) _Generic((x), \
    int:    abs_int,    \
    float:  abs_float,  \
    double: abs_double, \
    default: abs_double \
)(x)
```

---

## Syntax and Rules

```c
_Generic(
    controlling_expression,
    type1: result_expression1,
    type2: result_expression2,
    ...
    default: result_expression_default   // optional
)
```

### How it works

```c
#include <stdio.h>

// 1. The controlling expression is NEVER evaluated.
//    Only its TYPE is examined.
//    `_Generic(42, ...)` has type `int`, regardless of its value.

// 2. Each association maps a TYPE to a RESULT.
//    The result can be a value, a function pointer, a compound literal — anything.

// 3. The match is exact: no implicit conversions are applied.
//    `int` does NOT match `long` or `short`.

// 4. `default:` is optional. If omitted and no type matches,
//    the program does not compile.

// Basic example:
#define DESCRIBE_TYPE(x) _Generic((x), \
    int:    "integer",      \
    double: "double",       \
    float:  "float",        \
    char:   "char",         \
    default: "unknown"      \
)

int main(void) {
    int a = 1;
    double b = 2.0;
    float c = 3.0f;
    char d = 'x';
    long e = 42L;

    printf("%s\n", DESCRIBE_TYPE(a));   // integer
    printf("%s\n", DESCRIBE_TYPE(b));   // double
    printf("%s\n", DESCRIBE_TYPE(c));   // float
    printf("%s\n", DESCRIBE_TYPE(d));   // char
    printf("%s\n", DESCRIBE_TYPE(e));   // unknown (long doesn't match int)
    return 0;
}
```

### Qualifiers matter

```c
// const, volatile, and restrict are PART of the type.

#define QUAL_CHECK(x) _Generic((x), \
    int:           "int",         \
    const int:     "const int",   \
    int *:         "int pointer", \
    const int *:   "const int pointer" \
)

int a;
const int b = 0;
int *c;
const int *d;

QUAL_CHECK(a);    // "int"
QUAL_CHECK(b);    // "const int"
QUAL_CHECK(c);    // "int pointer"
QUAL_CHECK(d);    // "const int pointer"
```

### Arrays and pointer decay

```c
// Arrays decay to pointers in the _Generic controlling expression.
// (The expression is an rvalue.)

int arr[10];
int *ptr = arr;

_Generic(arr, int *: "pointer", default: "not pointer");   // "pointer"
_Generic(ptr, int *: "pointer", default: "not pointer");   // "pointer"

// To distinguish arrays from pointers, don't let the array decay:
_Generic(&arr, int (*)[10]: "array pointer", default: "other");   // "array pointer"
_Generic(&ptr, int **: "ptr pointer", default: "other");          // "ptr pointer"
```

---

## Type-Generic Macro Patterns

### Pattern 1: Dispatch to type-specific functions

```c
#include <stdio.h>
#include <string.h>   // For size_t

// Type-specific implementations
static int to_int(int x)               { return x; }
static unsigned to_unsigned(unsigned x) { return x; }
static long to_long(long x)             { return x; }
static double to_double(double x)       { return x; }

// One macro that dispatches to the right function
#define TO_INTEGER(x) _Generic((x), \
    int:     to_int,      \
    unsigned: to_unsigned, \
    long:    to_long,     \
    double:  to_double,   \
    float:   to_double    \
)(x)
```

### Pattern 2: printf-style format specifier selection

```c
#include <inttypes.h>
#include <stdio.h>

// Choose the correct printf format for the type
#define PRINT_VALUE(x)                    \
    _Generic((x),                         \
        int:       printf("%d\n", x),     \
        long:      printf("%ld\n", x),    \
        long long: printf("%lld\n", x),   \
        unsigned:  printf("%u\n", x),     \
        double:    printf("%f\n", x),     \
        char *:    printf("%s\n", x)      \
    )

// PRI macros can be used inside _Generic:
#define FORMAT_UINT(x) _Generic((x),           \
    uint8_t:  PRIu8,                            \
    uint16_t: PRIu16,                           \
    uint32_t: PRIu32,                           \
    uint64_t: PRIu64                            \
)

uint32_t val = 42;
printf("val = %" FORMAT_UINT(val) "\n", val);
```

### Pattern 3: Type-generic math macros

```c
#include <math.h>

// One macro for square root across types
#define SQRT(x) _Generic((x), \
    float:      sqrtf,       \
    double:     sqrt,        \
    long double: sqrtl      \
)(x)

// One macro for absolute value
#define ABS(x) _Generic((x), \
    int:            abs,       \
    long:           labs,      \
    long long:      llabs,     \
    float:          fabsf,     \
    double:         fabs,      \
    long double:    fabsl      \
)(x)
```

### Pattern 4: Type-generic container

```c
#include <stdlib.h>
#include <string.h>

// Type-generic max function macro
#define MAX(a, b) _Generic((a),                         \
    int:           ({ int _a = (a); int _b = (b);       \
                      _a > _b ? _a : _b; }),            \
    unsigned:      ({ unsigned _a = (a); unsigned _b = (b); \
                      _a > _b ? _a : _b; }),             \
    double:        ({ double _a = (a); double _b = (b); \
                      _a > _b ? _a : _b; }),             \
    long:          ({ long _a = (a); long _b = (b);     \
                      _a > _b ? _a : _b; })             \
)

// ⚠️  Using statement expressions ({ }) inside _Generic
//    is a GNU extension. For strict C11, dispatch to a helper function.
```

### Pattern 5: Type dispatch via compound literals

```c
// Compound literals can be used in _Generic results.
// This embeds the type-specific value directly.

#define ZERO_FOR_TYPE(x) _Generic((x),      \
    int:         (int){0},                   \
    double:      (double){0.0},              \
    char *:      (char *){"(null)"},         \
    void *:      (void *){NULL}              \
)

int i = ZERO_FOR_TYPE(42);           // i = 0
double d = ZERO_FOR_TYPE(3.14);      // d = 0.0
```

---

## `typeof` and `__auto_type`

### `typeof` (C23, GNU extension)

```c
// typeof — determine the type of an expression at compile time.
// Standardized in C23. Available as GNU extension in C89–C17.

typeof(1 + 2) x = 42;          // x is int
typeof(x) y = 99;              // y is int

// Real use: declaring variables of the same type as a parameter
#define MAX_SAFE(a, b) ({                \
    typeof(a) _a = (a);                   \
    typeof(b) _b = (b);                   \
    _a > _b ? _a : _b;                    \
})

// C23 also adds typeof_unqual for unqualified types:
// typeof_unqual(x) — removes const, volatile, restrict.
const int *ptr;
typeof(ptr) p1;            // p1: const int *
typeof_unqual(ptr) p2;     // p2: int * (const removed)
```

### `__auto_type` (GNU C)

```c
// __auto_type — type deduction for variable declarations (GNU extension).
// Like C++ auto, but limited to declaration: __auto_type x = expr;

#define SWAP(a, b) do {                 \
    __auto_type _tmp = (a);             \
    (a) = (b);                          \
    (b) = _tmp;                         \
} while (0)

// typeof is preferred over __auto_type for new code:
//   - typeof is standardized in C23
//   - typeof works with _Generic for compile-time dispatch
//   - typeof can be used in more contexts (return types, cast targets)
```

---

## `<tgmath.h>` — Type-Generic Math (C99)

> [!info] tgmath.h
> The `<tgmath.h>` header redefines `<math.h>` and `<complex.h>` functions as type-generic macros using `_Generic`. It allows you to call `sqrt()` with `float`, `double`, or `long double` arguments and get the correct precision function.

```c
#include <tgmath.h>
#include <stdio.h>

// Instead of calling sqrt (double) or sqrtf (float) or sqrtl (long double):
float f = 4.0f;
double d = 4.0;
long double ld = 4.0L;

float sqrt_f = sqrt(f);        // Calls sqrtf
double sqrt_d = sqrt(d);       // Calls sqrt
long double sqrt_ld = sqrt(ld); // Calls sqrtl

// This works because <tgmath.h> macros use _Generic internally:
// #define sqrt(x) _Generic((x), \
//     float: sqrtf,              \
//     double: sqrt,              \
//     long double: sqrtl         \
// )(x)

// Other type-generic math functions:
//   sin, cos, tan, asin, acos, atan, atan2
//   sinh, cosh, tanh
//   exp, log, log10, log2, pow, sqrt, cbrt
//   floor, ceil, round, trunc, fabs, fmod
```

---

## Comparison: `_Generic` vs C++ Templates

```text
Feature              _Generic (C11)         C++ Templates
──────────────────────────────────────────────────────────────────
Compile-time         Yes                    Yes
Type dispatch        Exact match only       Pattern matching + SFINAE
Can generate types   No (only expressions)  Yes (entire type families)
Multiple arguments   One controlling expr   Multiple template params
Overloadable         Via macro dispatch     Native function overloading
Performance          Zero cost              Zero cost
Syntax complexity    Low (flat list)        High (primary + partial + explicit)
Debugging            Preprocessor output    Template error messages
Standard library     <tgmath.h> only        Full STL
```

`_Generic` is deliberately limited — it's for C's philosophy of "simple, predictable, no hidden dispatch."

---

## Pitfalls

### Controlling expression is NOT evaluated

```c
// ❌ COMMON MISTAKE: side effects in the controlling expression don't happen.
int x = 0;
_Generic(x++, int: "int", default: "other");
// x is STILL 0 — the expression is only type-checked.
```

### No implicit type promotion

```c
// ❌ short doesn't match int — _Generic wants exact types.
short s = 1;
_Generic(s, int: "int", short: "short");  // "short" (or default if omitted)

// const on the value matters:
const int ci = 1;
_Generic(ci, int: "int", const int: "const int");  // "const int"
```

### `_Generic` in return position does NOT change the return type

```c
// _Generic selects an expression, not a return type.
// The expression determines the type based on the CONTROLLING type, not vice versa.

// ❌ This DOES NOT change the result type:
// #define BAD_CAST(x) _Generic((x), int: (double)(x), double: (int)(x))
// The cast happens BEFORE _Generic, which already evaluated based on (x)'s type.
```

### `default:` hides missing type associations

If you use `default:`, the compiler won't warn you about missing type associations. For library interfaces, prefer listing ALL types explicitly and omitting `default` — the compiler will then tell you if a new type is introduced.

---

## Cross-Links

- [[C/01_Foundations/01_C_Basics_and_Pointers]] for base type system
- [[C/01_Foundations/10_Standard_Library_Utilities]] for `stdint.h` types used with _Generic
- [[C/03_Advanced/09_GNU_C_Extensions_and_Compiler_Attributes]] for `typeof` and `__auto_type`
- [[C/02_Core/05_Algorithms_and_Recursion]] for type-generic math algorithms
