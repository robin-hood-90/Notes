---
tags: [cpp, foundations, lambdas, function, functional-programming, closures, captures]
aliases: ["Lambdas", "std::function", "Function Objects", "Closures", "Capture", "Functional C++"]
status: stable
updated: 2026-05-09
---

# Lambdas, std::function, and Functional Programming

> [!summary] Goal
> Master C++ lambdas — syntax, captures (by value/reference/init), mutable lambdas, generic lambdas (C++14), `std::function` type erasure, higher-order functions, and immediately invoked lambda expressions (IILE).

## Table of Contents

1. [Lambda Syntax](#lambda-syntax)
2. [Captures](#captures)
3. [Generic Lambdas (C++14)](#generic-lambdas)
4. [`std::function`](#stdfunction)
5. [Higher-Order Functions](#higher-order-functions)
6. [Immediately Invoked Lambda Expressions (IILE)](#immediately-invoked-lambda-expressions)
7. [Pitfalls](#pitfalls)

---

## Lambda Syntax

> [!info] Lambda expression
> A lambda is an anonymous function object (closure) created using the `[]` syntax. The compiler generates a unique, unnamed class with `operator()` and stores captures as member variables. Lambdas can be assigned to variables, passed to functions, and called like regular functions.

### What the compiler actually generates

When you write `[x](int y) { return x + y; }`, the compiler generates something equivalent to:

```cpp
class __Lambda_123ABC {   // Unique compiler-generated name
    int x;                // Captured variables become member variables
public:
    __Lambda_123ABC(int x_) : x(x_) {}   // Constructor initializes captures
    auto operator()(int y) const {       // operator() is const by default
        return x + y;
    }
};
auto lambda = __Lambda_123ABC(5);  // Equivalent to: [x=5](int y) { ... }
```

The capture storage layout depends on how you capture:

```cpp
int x = 5;
int* p = &x;
std::string s = "hello";

// Capture by value — copies stored inside the closure
auto a = [x, p, s] { /* x=5, p=0x..., s="hello" */ };
// Generated class holds: int x; int* p; std::string s; — ALL by value

// Capture by reference — pointers stored instead of copies
auto b = [&x, &p, &s] { /* x refers to outer x, s refers to outer s */ };
// Generated class holds: int* x_ref; int** p_ref; std::string* s_ref;
// Dereferences on each access

// Capture with initializer (C++14) — move-only types
auto c = [ptr = std::make_unique<int>(5)] { /* ptr is unique_ptr inside */ };
// Generated class holds: std::unique_ptr<int> ptr; — moved into closure
```

```cpp
// Basic lambda syntax:
// [captures](parameters) -> return_type { body }

auto square = [](int x) -> int { return x * x; };
int result = square(5);     // 25

// Return type deduction (C++14: auto deduction from return)
auto cube = [](int x) { return x * x * x; };

// Lambda with parameters
auto add = [](int a, int b) { return a + b; };

// Mutable lambda — can modify its captures
int counter = 0;
auto increment = [counter]() mutable { return ++counter; };
// mutable makes the captured counter modifiable inside the lambda
// Note: this modifies the LAMBDA's copy, not the original counter
```

### Lambda in STL algorithms

```cpp
std::vector<int> v = {1, 2, 3, 4, 5, 6, 7, 8};

// Filter with copy_if
std::vector<int> evens;
std::copy_if(v.begin(), v.end(), std::back_inserter(evens),
    [](int x) { return x % 2 == 0; });

// Transform (map)
std::transform(v.begin(), v.end(), v.begin(),
    [](int x) { return x * 2; });

// Sort with custom comparator
std::sort(v.begin(), v.end(),
    [](int a, int b) { return std::abs(a) < std::abs(b); });

// Find with condition
auto it = std::find_if(v.begin(), v.end(),
    [](int x) { return x > 10; });

// Accumulate with custom operation
int product = std::accumulate(v.begin(), v.end(), 1,
    [](int a, int b) { return a * b; });
```

---

## Captures

> [!info] Capture
> A lambda can capture variables from its surrounding scope. Captures can be by value (copy captured at lambda creation), by reference, or with an initializer (C++14). The default capture modes are `=` (by value) and `&` (by reference).

```cpp
int x = 42;
std::string msg = "Count: ";

// Capture by value (copy)
auto byValue = [x]() { return x; };           // Copies x at lambda creation
auto byDefaultValue = [=]() { return x; };     // Default capture by value

// Capture by reference
auto byRef = [&x]() { return x; };             // References x
auto byDefaultRef = [&]() { return x; };       // Default capture by reference

// Mixed captures
auto mixed = [=, &msg]() { return msg + std::to_string(x); };  // All by value except msg
auto mixed2 = [&, x]() { return x; };           // All by reference except x

// Init capture (C++14) — capture with an expression
auto init = [n = 42]() { return n; };           // Captures n = 42
auto moveOnly = [ptr = std::make_unique<int>(5)]() { return *ptr; };
// move-only types (unique_ptr, thread) can be init-captured

// Capture this (C++11)
class Widget {
    int value = 42;
public:
    auto getLambda() {
        return [this]() { return value; };       // Captures this pointer
    }
    // C++17: [*this] captures by value (a copy of the object)
    auto getSafeLambda() {
        return [*this]() mutable { return value++; };  // Copy of *this
    }
};
```

### Capture lifetime dangers

```cpp
// ❌ Dangling reference! Lambda outlives the captured-by-reference variable
auto createLambda() {
    int x = 42;
    return [&x]() { return x; };     // x is destroyed when createLambda returns!
}                                      // Using the returned lambda is UB

// ✅ Fix: capture by value, or use init capture
auto createSafeLambda(int x) {
    return [x]() { return x; };       // x is copied into the lambda
}
```

---

## Generic Lambdas (C++14)

> [!info] Generic lambda
> A generic lambda uses `auto` for its parameters, making it a template. The compiler generates a separate instantiation for each parameter type. This is equivalent to a function template but with more concise syntax.

```cpp
// Generic lambda — auto parameter makes it a template
auto add = [](auto a, auto b) { return a + b; };
// Equivalent to:
// template<typename T, typename U>
// auto add(T a, U b) { return a + b; }

std::cout << add(3, 4);                 // int + int
std::cout << add(3.14, 2.71);          // double + double
std::cout << add(std::string("a"), std::string("b"));  // string concatenation

// With vector of any type
auto print = [](const auto& container) {
    for (const auto& item : container) {
        std::cout << item << ' ';
    }
    std::cout << '\n';
};

std::vector<int> vi = {1, 2, 3};
std::vector<std::string> vs = {"a", "b", "c"};
print(vi);      // "1 2 3"
print(vs);      // "a b c"

// Return type deduction works: the return type is deduced from the body
auto transformPair = [](auto a, auto b) {
    if (a > b) return a;
    return b;           // Deduced as common type
};
```

---

## `std::function`

> [!info] std::function
> `std::function` is a type-erased wrapper for any callable — function pointers, lambdas, functors, and member function pointers. It can store, copy, and call any callable with a matching signature. It has a small overhead (heap allocation for larger lambdas) but provides runtime polymorphism for callables.

```cpp
#include <functional>

// Function that accepts any callable with int(int, int) signature
using BinaryOp = std::function<int(int, int)>;

void apply(const std::vector<int>& a, const std::vector<int>& b,
           BinaryOp op) {
    for (size_t i = 0; i < a.size() && i < b.size(); ++i) {
        std::cout << op(a[i], b[i]) << ' ';
    }
}

// All these can be passed to apply:
// 1. Lambda
auto add = [](int x, int y) { return x + y; };

// 2. Function pointer
int multiply(int x, int y) { return x * y; }

// 3. Functor
struct Subtract {
    int operator()(int x, int y) const { return x - y; }
};

// 4. std::function
BinaryOp customOp = [](int x, int y) { return x * x + y * y; };

apply(v1, v2, add);
apply(v1, v2, multiply);
apply(v1, v2, Subtract{});
apply(v1, v2, customOp);
```

### std::function performance considerations

```cpp
// std::function has a small-buffer optimization (SBO):
// Small lambdas (typically up to 2-4 pointers) are stored inline.
// Larger lambdas require heap allocation.

// If performance is critical, prefer:
// 1. Template parameter
template<typename F>
void callWith(F&& f) { f(); }     // No overhead — fully inlineable

// 2. auto lambda (for library code)
auto lambda = [](auto f) { return f(); };

// 3. Function pointer (for stateless lambdas)
void (*fp)() = [](){};            // Stateless lambda → function pointer
```

---

## Higher-Order Functions

```cpp
// A higher-order function takes a function as argument or returns one.

// Returning a lambda (C++14)
auto makeMultiplier(int factor) {
    return [factor](int x) { return x * factor; };
}

auto doubler = makeMultiplier(2);
auto tripler = makeMultiplier(3);
std::cout << doubler(5);    // 10
std::cout << tripler(5);    // 15

// Composing lambdas
auto compose = [](auto f, auto g) {
    return [f, g](auto x) { return f(g(x)); };
};

auto add1 = [](int x) { return x + 1; };
auto square = [](int x) { return x * x; };
auto add1ThenSquare = compose(square, add1);

std::cout << add1ThenSquare(5);    // (5+1)^2 = 36

// Pipeline (apply multiple functions in sequence)
template<typename... Fs>
auto pipeline(Fs... fs) {
    return [=](auto x) {
        return (fs(x), ...);  // C++17 fold — chain functions
    };
}
```

---

## Immediately Invoked Lambda Expressions (IILE)

> [!info] IILE
> An IILE is a lambda that's defined and immediately called in the same expression. Useful for: (a) initializing a `const` variable with complex logic, (b) isolating a series of operations in a scope without creating a named function, (c) creating complex initialization that needs local variables that shouldn't leak.

```cpp
// Complex initialization — make it const
const int value = []() -> int {
    std::ifstream file("config.txt");
    int val = 42;  // default
    if (file >> val) { /* ... */ }
    return val;
}();   // ← The lambda is called immediately!

// Alternative without IILE — requires a non-const variable or separate function
int value2;
{
    std::ifstream file("config.txt");
    if (file >> val) value2 = val;
    else value2 = 42;
}   // file is closed here
```

---

## Pitfalls

### Default capture by reference (`[&]`) in callbacks

```cpp
// ❌ Danger: capture by reference in async callback
void startAsync() {
    int result = 0;
    // Capture by reference — result will be destroyed before callback runs!
    doAsyncWork([&result]() { process(result); });
    // result is destroyed when startAsync returns
}   // ⚠️ result is gone; callback accesses dangling reference

// ✅ Fix: capture by value (C++14 init capture moves)
void startAsync() {
    doAsyncWork([result = int{0}]() mutable { process(result); });
}
```

### Lambda as default argument

```cpp
// ❌ Each call creates a different lambda with a different type
void process(std::function<void()> f = []() {}) { }

// Each instantiation of the default creates a unique lambda type
// This is OK for std::function, but problematic for templates

// ✅ Better: use a function pointer for stateless lambdas
void process2(void (*f)() = []() { }) { }
```

### Over-reliance on auto for parameters in generic lambdas

When you write `[](auto&& x)`, you get a forwarding reference (like a template with `T&&`). To preserve the value category:

```cpp
auto wrapper = [](auto&& x) {
    target(std::forward<decltype(x)>(x));   // Perfect forwarding inside lambda
};
```

### Lambda capture of structured bindings (pre-C++20)

Structured bindings (C++17) can't be captured by a lambda in C++17. They become captureable in C++20.

```cpp
auto [a, b] = getPair();
// auto lambda = [a]() { return a; };  // ❌ ERROR in C++17
// ✅ C++20 allows capturing structured bindings
```

---

> [!question]- Interview Questions
>
> **Q: What is a lambda expression and how does it work internally?**
> A: A lambda expression creates an anonymous function object (closure). The compiler generates a unique, unnamed class with `operator()`. Captured variables become member variables of this class. For `[x](int y) { return x + y; }`, the compiler generates something like a class with `int x` as a member and `int operator()(int y) const { return x + y; }`.
>
> **Q: What's the difference between capture by value and by reference?**
> A: By value (`[x]`) copies the variable into the lambda at creation time — modifications inside the lambda don't affect the original. By reference (`[&x]`) stores a reference — changes are visible to the original. The reference may dangle if the lambda outlives the captured variable. Use by value for safety, by reference for efficiency with large objects.
>
> **Q: What is a generic lambda?**
> A: A lambda with `auto` parameters — it's a template. `[](auto a, auto b) { return a + b; }` is equivalent to a function template. The compiler generates a separate instantiation for each parameter type. Generic lambdas (C++14) replace verbose template code with concise syntax.
>
> **Q: What is std::function and when should you use it?**
> A: std::function is a type-erased wrapper for any callable with a given signature. Use it when: (a) you need to store callables in a container (`std::vector<std::function<void()>>`), (b) you need runtime polymorphism (callbacks that can be lambdas, function pointers, or functors), (c) the callable type isn't known at compile time. Downside: small overhead (virtual dispatch or heap allocation).
>
> **Q: What is an IILE and when would you use it?**
> A: An Immediately Invoked Lambda Expression is a lambda defined and called in the same expression: `const int x = []{ return 42; }();`. Use it to: (a) initialize const variables with complex logic, (b) scope temporary variables without leaking them to the outer scope, (c) compute a value with early returns (cleaner than nested ternary operators).

---

## Cross-Links

- [[C++/01_Foundations/05_Move_Semantics_and_Value_Categories]] for std::move with lambdas and init capture
- [[C++/01_Foundations/06_Templates_Basics_to_Variadic]] for generic lambdas and auto parameters
- [[C++/02_Core/03_STL_Algorithms_and_Ranges]] for lambdas with algorithms
- [[C++/03_Advanced/05_Type_Erasure_and_Design_Patterns]] for std::function and type erasure
- [[C++/03_Advanced/03_Coroutines_C20]] for coroutines and lambda interaction
