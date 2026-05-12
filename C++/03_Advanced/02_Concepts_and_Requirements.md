---
tags: [cpp, advanced, concepts, cpp20, requires, constraints, type-requirements, concepts-vs-sfinae]
aliases: ["Concepts", "C++20 Concepts", "requires", "Constraints", "Abbreviated Function Templates", "Standard Concepts"]
status: stable
updated: 2026-05-09
---

# Concepts and Requirements (C++20)

> [!summary] Goal
> Master C++20 concepts — define type requirements with `concept`, use `requires` expressions, apply constraints to templates, and understand standard concepts. Concepts replace 90% of SFINAE use cases with clear, readable, and fast-to-compile code.

## Table of Contents

1. [Concept Basics](#concept-basics)
2. [requires Expressions](#requires-expressions)
3. [Using Concepts with Templates](#using-concepts-with-templates)
4. [Standard Concepts](#standard-concepts)
5. [Concepts vs SFINAE](#concepts-vs-sfinae)
6. [Pitfalls](#pitfalls)

---

## Concept Basics

> [!info] Concept
> A concept is a named set of compile-time requirements on types. It defines what operations a type must support. If a type satisfies the concept, the template can be instantiated. If not, the compiler gives a clear error ("T does not satisfy Incrementable") instead of pages of template instantiation backtrace.

```cpp
#include <concepts>

// Define a concept: T must be incrementable with ++
template<typename T>
concept Incrementable = requires(T x) {
    ++x;
    x++;
};

// Use the concept to constrain a template
template<Incrementable T>
T advance(T value, int n) {
    for (int i = 0; i < n; ++i) ++value;
    return value;
}

// Concept with multiple requirements
template<typename T>
concept Printable = requires(T x, std::ostream& os) {
    { os << x } -> std::convertible_to<std::ostream&>;
};

template<Printable T>
void print(const T& value) {
    std::cout << value << '\n';
}
```

---

## requires Expressions

> [!info] requires expression
> A `requires` expression specifies a set of requirements that types must satisfy. Four kinds: simple (`++x`), type (`typename T::value_type`), compound (`{ expr } -> convertible_to<T>`), and nested (`requires OtherConcept<T>`).

```cpp
template<typename T>
concept Container = requires(T c) {
    // Type requirement — T must have a value_type member type
    typename T::value_type;
    
    // Simple requirement — must be pre-incrementable
    ++c;
    
    // Compound requirement — expression must compile and result must satisfy concept
    { c.begin() } -> std::same_as<typename T::iterator>;
    { c.end() } -> std::same_as<typename T::iterator>;
    
    // Nested requirement — additional concept check
    requires std::copyable<T>;
};

template<typename T>
concept Hashable = requires(T a, T b) {
    { std::hash<T>{}(a) } -> std::convertible_to<std::size_t>;
    { a == b } -> std::convertible_to<bool>;
};
```

### Parameterized requires expression

```cpp
template<typename T, typename U>
concept EqualityComparable = requires(T a, U b) {
    { a == b } -> std::convertible_to<bool>;
    { a != b } -> std::convertible_to<bool>;
};

// Different types can be compared
template<typename T, typename U>
    requires EqualityComparable<T, U>
bool check_equal(const T& a, const U& b) {
    return a == b;
}
```

---

## Using Concepts with Templates

### 1. Template parameter constrained with `requires`

```cpp
template<typename T>
    requires std::integral<T>
T half(T value) {
    return value / 2;
}
```

### 2. Abbreviated function template (C++20)

```cpp
// Equivalent to: template<typename T> requires std::integral<T>
void process(std::integral auto value) {
    std::cout << value << '\n';
}

// Multiple constrained parameters
auto add(std::integral auto a, std::integral auto b) {
    return a + b;
}
```

### 3. Class template with concepts

```cpp
template<typename T>
    requires std::regular<T>
class MyContainer {
    T data[100];
public:
    // Regular concept requires: default constructible, copyable, comparable
};

// Variable template with concept
template<typename T>
    requires std::integral<T>
constexpr double pi_for = 3.141592653589793;  // Not useful — just showing syntax
```

### 4. `auto` and concepts for functions

```cpp
// The function accepts any type that satisfies std::integral
std::integral auto square(std::integral auto x) {
    return x * x;
}

// Multiple type constraints
std::integral auto multiply(std::integral auto a, std::integral auto b) {
    return a * b;
}
```

---

## Standard Concepts

| Concept | Requires | Example |
|---------|----------|---------|
| `std::integral` | `T` is an integer type | `int`, `char`, `long` |
| `std::floating_point` | `T` is a floating-point type | `float`, `double` |
| `std::signed_integral` | `T` is a signed integer | `int`, `long` |
| `std::unsigned_integral` | `T` is an unsigned integer | `unsigned int`, `size_t` |
| `std::same_as<T, U>` | `T` and `U` are the same type | — |
| `std::convertible_to<T, U>` | `T` is convertible to `U` | `int` → `double` |
| `std::invocable<Fn, Args...>` | `Fn` can be called with `Args...` | — |
| `std::regular` | Copyable + default constructible + equality comparable | Most value types |
| `std::semiregular` | Copyable + default constructible | — |
| `std::totally_ordered` | Supports `==, !=, <, <=, >, >=` | — |
| `std::input_iterator` | Iterator that can be read once | `istream_iterator` |
| `std::forward_iterator` | Iterator that can be read multiple times | `forward_list` iterator |
| `std::range` | Something with `begin()` and `end()` | All containers |

```cpp
// Using standard concepts
template<std::input_iterator Iter, std::totally_ordered T>
Iter find(Iter first, Iter last, const T& value) {
    for (; first != last; ++first) {
        if (*first == value) return first;
    }
    return last;
}
```

---

## Concepts vs SFINAE

| Aspect | SFINAE | Concepts |
|--------|:------:|:--------:|
| **Error messages** | Pages of template backtrace | Clear "T does not satisfy concept" |
| **Readability** | Hard | Clear, intentional |
| **Compile speed** | Slower (heavy template matching) | Faster (earlier checking) |
| **Maintainability** | Fragile | Robust |
| **C++ version** | C++11 (enable_if), C++17 (if constexpr) | C++20 |
| **Type checking** | At instantiation time | At template definition time |
| **Requires clauses** | Possible but ugly | Clean syntax |

```cpp
// ❌ SFINAE (old way)
template<typename T>
std::enable_if_t<std::is_integral_v<T>, T> half(T value) {
    return value / 2;
}

// ✅ Concepts (C++20)
template<std::integral T>
T half(T value) {
    return value / 2;
}

// ✅ Even simpler with abbreviated syntax (C++20)
std::integral auto half(std::integral auto value) {
    return value / 2;
}
```

---

## Pitfalls

### requires clause placement

```cpp
// These are all equivalent:
template<typename T> requires Concept<T> void f();   // requires clause after template<>
template<Concept T> void f();                         // Concept in template parameter
void f(Concept auto);                                  // Abbreviated function template
```

### requires expression vs requires clause

```cpp
// requires CLAUSE — constrains a template
template<typename T> requires std::integral<T> T f(T x);

// requires EXPRESSION — checks compile-time properties
template<typename T>
concept MyConcept = requires(T x) {
    { x + 1 } -> std::convertible_to<T>;  // Compound requirement
};
```

### Both branches must compile with concepts

Concepts constrain which types can be used — they don't affect the instantiation of the function body. Use `if constexpr` inside concept-constrained templates for type-dependent behavior:

```cpp
template<std::integral T>
auto process(T value) {
    if constexpr (std::signed_integral<T>) {
        return -value;  // Works for signed ints
    } else {
        return value;   // For unsigned ints
    }
}
```

---

> [!question]- Interview Questions
>
> **Q: What are C++20 concepts and why are they better than SFINAE?**
> A: Concepts name and constrain template parameters. Error messages are clear ("T does not satisfy std::integral") instead of pages of template instantiation backtrace. Concepts are checked earlier (at definition, not instantiation) and compile faster. They use `concept`, `requires`, and abbreviated syntax for clean, readable code.
>
> **Q: What is the difference between a `requires` clause and a `requires` expression?**
> A: A `requires` CLAUSE constrains a template: `template<typename T> requires std::integral<T>`. A `requires` EXPRESSION defines what operations a type must support: `requires(T x) { ++x; }`. The clause says "this template only works with types that satisfy this." The expression defines "these are the requirements the type must meet."
>
> **Q: What are standard concepts in C++20?**
> A: Major ones include: `std::integral`, `std::floating_point`, `std::same_as`, `std::convertible_to`, `std::invocable`, `std::regular`, `std::totally_ordered`, `std::range`, `std::input_iterator`, `std::forward_iterator`, and `std::predicate`. The concepts library also provides comparison concepts and object concepts.
>
> **Q: How do you write a concept that checks for a member function?**
> A: Use a requires expression with a compound requirement: `concept HasSize = requires(T t) { { t.size() } -> std::convertible_to<std::size_t>; };`. The compound requirement checks both that `t.size()` is valid and that the return type is convertible to `std::size_t`.
>
> **Q: What is the difference between `std::same_as` and `std::convertible_to`?**
> A: `std::same_as<T, U>` requires T and U to be the EXACT same type (no conversions). `std::convertible_to<T, U>` allows implicit conversions. Example: `same_as<int, long>` is false, but `convertible_to<int, long>` is true (int converts to long).

---

## Cross-Links

- [[C++/01_Foundations/06_Templates_Basics_to_Variadic]] for template fundamentals
- [[C++/03_Advanced/01_Template_Metaprogramming_SFINAE_Type_Traits]] for SFINAE comparison
- [[C++/03_Advanced/04_CRTP_Mixins_and_Static_Polymorphism]] for CRTP with concepts
- [[C++/02_Core/02_STL_Containers_Deep_Dive]] for containers with standard concepts
- [[C++/02_Core/03_STL_Algorithms_and_Ranges]] for Ranges + Concepts integration
