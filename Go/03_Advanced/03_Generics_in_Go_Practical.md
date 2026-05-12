---
tags: [go, advanced, generics, type-parameters, constraints]
aliases: ["Go Generics", "Type Parameters", "Generic Constraints"]
status: stable
updated: 2026-05-03
---

# Generics in Go (Practical)

> [!summary] Goal
> Use generics to remove duplication without creating unreadable type machinery. Understand type inference, constraints, and when generics are the right tool.

## Table of Contents

1. [Why Generics Matter](#why-generics-matter)
2. [Generic Functions](#generic-functions)
3. [Generic Types](#generic-types)
4. [Constraints Deep Dive](#constraints-deep-dive)
5. [When to Use Generics](#when-to-use-generics)
6. [Performance Considerations](#performance-considerations)
7. [Pitfalls](#pitfalls)

---

## Why Generics Matter

Before Go 1.18, you had to duplicate functions for every type or use `interface{}` with type assertions. Generics eliminate this boilerplate with **type parameters**.

```go
// Before generics — one version per type, or interface{} with casting
func SumInts(nums []int) int { /* ... */ }
func SumFloats(nums []float64) float64 { /* ... */ }

// With generics — one function for all
func Sum[T int | float64](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}
```

---

## Generic Functions

```go
// Basic type parameter
func Map[T any, U any](in []T, f func(T) U) []U {
    out := make([]U, 0, len(in))
    for _, v := range in {
        out = append(out, f(v))
    }
    return out
}

// Type inference — compiler deduces T and U from arguments
doubled := Map([]int{1, 2, 3}, func(x int) int { return x * 2 })

// Explicit type parameters (when inference is not possible)
var result = Map[int, string]([]int{1, 2}, func(x int) string {
    return fmt.Sprintf("%d", x)
})
```

---

## Generic Types

```go
// Generic struct
type Stack[T any] struct {
    items []T
}

func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item, true
}

// Usage
s := Stack[string]{}
s.Push("hello")
s.Push("world")
val, _ := s.Pop()  // "world"

// Generic map/reduce pattern
type Pair[K comparable, V any] struct {
    Key   K
    Value V
}
```

---

## Constraints Deep Dive

### Built-in constraints

```go
// any — accepts any type (equivalent to interface{})
func Print[T any](v T) { fmt.Println(v) }

// comparable — types that support == and !=
func Index[T comparable](s []T, v T) int {
    for i, item := range s {
        if item == v {
            return i
        }
    }
    return -1
}
```

### Custom constraints with unions

```go
// Numeric types union
type Number interface {
    ~int | ~int64 | ~float64
}

func Sum[T Number](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}

// Type approximation with ~
// ~int means "any type whose underlying type is int"
type Celsius int
Sum([]Celsius{10, 20})    // works — Celsius has underlying type int

// Without ~, this would not compile
```

### Constraint patterns

```go
// Orderable — types that support <, <=, >
type Ordered interface {
    ~int | ~int8 | ~int16 | ~int32 | ~int64 |
    ~uint | ~uint8 | ~uint16 | ~uint32 | ~uint64 |
    ~float32 | ~float64 | ~string
}

func Max[T Ordered](a, b T) T {
    if a > b {
        return a
    }
    return b
}

// Combining constraints
type Number interface {
    ~int | ~int64 | ~float64
}

type StringOrNumber interface {
    Number | ~string
}
```

---

## When to Use Generics

```mermaid
flowchart TD
    A[Need type-parametric code?] --> B{Operation on data structure?}
    B -->|Yes| C[Generics — Stack[T], BinaryTree[T]]
    B -->|No| D{Only one method needed?}
    D -->|Yes| E[Interface — io.Reader, error]
    D -->|No| F{Multiple implementations?}
    F -->|Yes| G[Interface — define contract]
    F -->|No| H{Utility function across types?}
    H -->|Yes| I[Generics — Map, Filter, Reduce]
    H -->|No| J[Concrete types only — no abstraction needed]
```

| Use generics for | Use interfaces for | Use neither for |
|-----------------|-------------------|-----------------|
| Data structures (Stack, Tree, List) | Behavioral contracts (Read, Write) | Single-type business logic |
| Utility functions (Map, Filter, Sum) | Dependency inversion (Repository, Service) | Application code |
| Container types (Pair, Result, Option) | Polymorphic behavior (Duck typing) | Simple CRUD |

---

## Performance Considerations

Generics are **monomorphized** — the compiler generates a separate copy of the function for each type parameter combination. This means:

- **Zero runtime overhead** — no boxing, no type assertions
- **Larger binary size** — more copies of the function
- **Compile time** — slight increase from generating copies
- **Same speed as hand-written code** — not slower, not faster

```go
// This generic function:
func Add[T int | float64](a, b T) T { return a + b }

// Generates at compile time:
func Add_int(a, b int) int { return a + b }
func Add_float64(a, b float64) float64 { return a + b }
```

---

## Pitfalls

### Cannot use methods on type parameters

```go
type Stringer interface { String() string }

func Print[T Stringer](v T) {
    fmt.Println(v.String())   // ERROR: T may have String, but compiler doesn't know
    fmt.Println(v)            // OK — works because v is still T
}
```

**Fix**: Use interface constraints instead of type parameters for methods.

### No generic methods — only generic functions or types

```go
type Container[T any] struct { val T }

// This is NOT allowed:
func (c Container[T]) Convert[U any]() U { /* ... */ }

// Workaround: define a top-level generic function
func Convert[T, U any](c Container[T], f func(T) U) U { return f(c.val) }
```

### Type inference won't always work

```go
func Parse[T any](raw string) (T, error) { ... }
val := Parse("42")              // ERROR: cannot infer T
val := Parse[int]("42")         // OK — explicit type argument
```

---

> [!question]- Interview Questions
>
> **Q: What is the difference between `any` and `comparable` constraints?**
> A: `any` accepts any type. `comparable` accepts only types that can be compared with `==` and `!=` (numeric, string, bool, pointer, channel, struct/array of comparable types).
>
> **Q: How does generic monomorphization affect performance?**
> A: The compiler generates a separate function copy per type parameter — zero runtime overhead, but larger binary size. Same performance as hand-written code.
>
> **Q: When should you use generics instead of interfaces?**
> A: Generics for data structures and utility functions that operate uniformly on values. Interfaces for behavioral polymorphism (multiple implementations of the same contract).

---

## Cross-Links

- [[Go/01_Foundations/03_Interfaces_and_Error_Handling]] for interface-based polymorphism
- [[Go/03_Advanced/05_Reflection_and_Unsafe]] for runtime type inspection
- [[Go/02_Core/02_Concurrency_Patterns_WorkerPools_FanInOut]] for generic concurrency helpers

---

## References

- [Go Blog: Generics](https://go.dev/blog/intro-generics)
- [Go 1.18 Generics](https://go.dev/doc/go1.18#generics)
- [Tutorial: Getting started with generics](https://go.dev/doc/tutorial/generics)
