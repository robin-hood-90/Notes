---
tags: [cpp, foundations, cpp-vs-c, compilation, namespaces, iostream, overloading]
aliases: ["C++ vs C", "C++ Syntax", "Function Overloading", "Namespace", "C++ Compilation"]
status: stable
updated: 2026-05-09
---

# C++ vs C: Syntax, Compilation, and Core Differences

> [!summary] Goal
> Understand C++ as a superset of C — what it adds, how compilation differs, the new type system features, and the core vocabulary every C++ developer needs. This is the foundation for everything that follows.

## Table of Contents

1. [C++ as a Superset of C](#c-as-a-superset-of-c)
2. [Compilation: g++ vs gcc](#compilation-g-vs-gcc)
3. [References vs Pointers](#references-vs-pointers)
4. [Basic I/O: iostream](#basic-i-o-iostream)
5. [Function Overloading](#function-overloading)
6. [Default Arguments](#default-arguments)
7. [Namespaces](#namespaces)
8. [The `auto` Keyword](#the-auto-keyword)
9. [Pitfalls](#pitfalls)

---

## C++ as a Superset of C

> [!info] C++ is (mostly) a superset of C
> Almost all valid C code is valid C++ code. C++ adds: classes with encapsulation, inheritance and polymorphism, templates, exceptions, operator overloading, references (vs pointers only), a richer standard library (STL), and RAII (Resource Acquisition Is Initialization). The main C features that differ: `malloc`/`free` are replaced by `new`/`delete`, C-style casts are replaced by safer C++ casts, and C strings (`char*`) are supplemented by `std::string`.

### Quick comparison

| Aspect | C | C++ |
|--------|:--:|:---:|
| **File extension** | `.c` | `.cpp` |
| **Compiler** | `gcc` | `g++` |
| **Memory alloc** | `malloc`/`free` | `new`/`delete`, smart pointers |
| **I/O** | `printf`/`scanf` | `std::cout`/`std::cin` |
| **Strings** | `char*` + `string.h` | `std::string` |
| **Arrays** | Raw arrays | `std::vector`, `std::array` |
| **Bool type** | `_Bool` (C99) | `bool` keyword |
| **Function overloading** | ❌ | ✅ |
| **References** | ❌ | ✅ |
| **Templates** | ❌ | ✅ |
| **Exceptions** | ❌ | ✅ |
| **RAII** | ❌ | ✅ |

### Minimal C++ program

```cpp
#include <iostream>
#include <string>

int main() {
    std::string name;
    std::cout << "Enter name: ";
    std::cin >> name;
    std::cout << "Hello, " << name << "!" << std::endl;
    return 0;
}
```

---

## Compilation: g++ vs gcc

```bash
# Compile a C++ program
g++ -std=c++20 -Wall -Wextra -O2 program.cpp -o program

# Common compiler flags for C++
g++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -O2 -g program.cpp -o program

# Compile multiple files
g++ -std=c++20 -c file1.cpp -o file1.o
g++ -std=c++20 -c file2.cpp -o file2.o
g++ file1.o file2.o -o program

# Link a C library
g++ main.cpp -lm -lpthread

# Show what C++ standard version you're using
g++ -dM -E -x c++ /dev/null | grep __cplusplus
# C++11: 201103L, C++14: 201402L, C++17: 201703L, C++20: 202002L, C++23: 202302L
```

| Flag | Meaning |
|------|---------|
| `-std=c++20` | Use the C++20 standard |
| `-Wall -Wextra -Wpedantic` | Enable all warnings |
| `-Werror` | Treat warnings as errors (CI) |
| `-O2` | Optimize (level 2) |
| `-g` | Debug symbols |
| `-fno-exceptions` | Disable exceptions (embedded/games) |
| `-fno-rtti` | Disable RTTI (embedded, smaller binary) |

---

## References vs Pointers

> [!info] Reference
> A reference is an alias for an existing variable. It must be initialized at declaration and cannot be changed to refer to another variable. Unlike a pointer, it's not nullable and doesn't require `*` for dereferencing. References are the C++ way to pass parameters by reference without pointer syntax.

```cpp
// Pointers (C style)
void swap_c(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

// References (C++ style) — cleaner syntax, no null check needed
void swap_cpp(int &a, int &b) {
    int temp = a;
    a = b;
    b = temp;
}

// Usage
int x = 10, y = 20;
swap_c(&x, &y);     // pointers: must take address
swap_cpp(x, y);     // references: just pass variables
```

| Aspect | Pointers | References |
|--------|:--------:|:----------:|
| **Can be null** | ✅ Yes (`int *p = nullptr`) | ❌ No (must be initialized) |
| **Can be reassigned** | ✅ Yes (`p = &y`) | ❌ No (binds once) |
| **Dereference syntax** | `*p` | Implicit |
| **Take address** | `&x` to get pointer | `&x` to get address (same syntax, different meaning) |
| **Use case** | Optional params, dynamic allocation, arrays | Mandatory params, operator overloads, range-for |

---

## Basic I/O: iostream

```cpp
#include <iostream>
#include <iomanip>   // for formatting

int main() {
    int age;
    std::string name;

    // Output
    std::cout << "Hello, world!" << std::endl;         // with newline
    std::cout << "Hello, world!\n";                     // same, no flush
    std::cout << "Age: " << age << ", Name: " << name;  // chaining

    // Input
    std::cin >> name;                // Read a word (stops at whitespace)
    std::getline(std::cin, name);    // Read a line (spaces included)

    // Formatted output
    std::cout << std::setw(10) << std::setfill('0') << 42;  // "0000000042"
    std::cout << std::fixed << std::setprecision(2) << 3.14159;  // "3.14"

    return 0;
}
```

---

## Function Overloading

> [!info] Function overloading
> Multiple functions can have the same name but different parameter types or counts. The compiler selects the correct overload based on the arguments. Name mangling encodes the parameter types in the symbol name — which is why C++ function names are different from C in object files.

```cpp
#include <iostream>

// Same name, different parameters — compiler picks the right one
void print(int x)        { std::cout << "int: " << x << '\n'; }
void print(double x)     { std::cout << "double: " << x << '\n'; }
void print(const char* s){ std::cout << "string: " << s << '\n'; }
void print(int x, int y) { std::cout << "two ints: " << x << ", " << y << '\n'; }

int main() {
    print(42);          // "int: 42"
    print(3.14);        // "double: 3.14"
    print("hello");     // "string: hello"
    print(1, 2);        // "two ints: 1, 2"
}
```

### Overload resolution order

```cpp
// Compiler tries (in order):
// 1. Exact match
// 2. Promotions (int → long, float → double)
// 3. Standard conversions (int → double, derived → base)
// 4. User-defined conversions
// 5. Variadic / ellipsis (...)

// If ambiguous → compile error
void foo(int x);
void foo(long x);
foo(42);    // ambiguous? int can convert to both int and long → error!
```

---

## Default Arguments

```cpp
void log(const std::string &msg,
         const std::string &level = "INFO",   // trailing defaults
         std::ostream &os = std::cout) {
    os << "[" << level << "] " << msg << '\n';
}

// Usage
log("Hello");                         // "INFO" level, cout
log("Warning!", "WARN");               // "WARN" level, cout
log("Error!", "ERROR", std::cerr);    // "ERROR" level, cerr

// ⚠️ Defaults must be trailing — can't skip "level" but provide "os"
// log("msg", std::cerr);  // ERROR: second arg must be string
```

---

## Namespaces

> [!info] Namespace
> A namespace prevents name collisions by grouping identifiers. The `std` namespace contains all standard library names. You can create your own namespaces, nest them, and use `using` declarations to bring names into scope.

```cpp
namespace MyCode {
    int value = 42;
    
    void func() {
        // code
    }
    
    namespace Detail {          // nested namespace
        int helper() { return 0; }
    }
}

// C++17: nested namespace definition
namespace MyCode::Detail {
    // same as: namespace MyCode { namespace Detail { ... } }
}

// Usage
int main() {
    int x = MyCode::value;              // qualified access
    MyCode::func();
    
    using MyCode::value;                // brings one name
    using namespace MyCode;             // brings ALL names (use sparingly)
    
    // ADL (Argument-Dependent Lookup)
    // When calling a function with an argument from a namespace,
    // that namespace is searched automatically:
    std::cout << MyCode::value;         // No need for std:: — ADL finds operator<<
}
```

### ADL (Argument-Dependent Lookup)

```cpp
namespace Geometry {
    struct Point { int x, y; };
    std::ostream& operator<<(std::ostream& os, const Point& p) {
        return os << "(" << p.x << "," << p.y << ")";
    }
}

int main() {
    Geometry::Point p{1, 2};
    std::cout << p;    // ADL finds Geometry::operator<< automatically!
    // Without ADL, we'd need: std::cout << operator<<(std::cout, p);  // ugly
}
```

---

## The `auto` Keyword

```cpp
// C++11: type deduction for variables
auto x = 42;            // int
auto y = 3.14;          // double
auto z = "hello";       // const char*
auto& ref = x;          // int& (reference deduction)
const auto& cref = x;   // const int&

// C++14: auto return type deduction
auto add(int a, int b) { return a + b; }  // deduced as int

// C++20: auto parameter (abbreviated function template)
auto multiply(auto a, auto b) {   // like template<typename T, typename U>
    return a * b;
}

// Trailing return type (C++11)
auto divide(int a, int b) -> double {  // explicitly specify return type
    return static_cast<double>(a) / b;
}
```

### When to use auto vs explicit types

```cpp
// ✅ Always use auto for:
auto it = vec.begin();                // Iterator types are verbose
auto ptr = std::make_shared<Foo>();   // Smart pointer types are verbose
auto [a, b] = get_pair();            // Structured bindings (C++17)

// ✅ Use auto with caution for:
auto result = compute();             // Fine if return type is obvious

// ❌ Avoid auto when:
auto x = some_complex_function();    // Return type is unclear from context
// Prefer explicit: ResultType x = some_complex_function();
```

---

## Pitfalls

### `#include <iostream>` vs `<iostream.h>`

The `.h` version is pre-standard. Always use `#include <iostream>` (without `.h`). The `.h` versions are not part of standard C++.

### `endl` vs `'\n'`

`std::endl` inserts a newline AND flushes the buffer. This is slow. Prefer `'\n'` for most output — `'\n'` doesn't flush, so it's much faster. Use `endl` only when you specifically need a flush (interactive output, logging to a file that must be immediately visible).

### Using `using namespace std;` in headers

Never put `using namespace std;` (or any using directive) in a header file. It forces every file that includes your header into the global namespace, causing potential name collisions. Only use it in `.cpp` files, and prefer `using` declarations over directives.

### Confusing `=` with `==` in conditions

C++ inherited this C trap: `if (x = 5)` assigns 5 to x and always evaluates to true. Some compilers warn. Use `if (5 == x)` to catch the typo (can't assign to 5). Or enable `-Werror` to make this an error.

### Name hiding in nested scopes

```cpp
int value = 10;
{
    int value = 20;    // Hides outer value
    std::cout << value;  // 20
}
std::cout << value;      // 10
```

---

> [!question]- Interview Questions
>
> **Q: What's the difference between a pointer and a reference in C++?**
> A: A reference must be initialized at declaration and cannot be reseated (changed to point somewhere else). A pointer can be null and can point to different objects over its lifetime. References are syntactic sugar for pointers with safety guarantees. Under the hood, references are implemented as pointers.
>
> **Q: What is function overloading and how does the compiler resolve it?**
> A: Multiple functions with the same name but different parameter types/counts. The compiler selects the best match: exact → promotion → standard conversion → user-defined → ellipsis. Ambiguity is a compile error. Name mangling encodes the parameter types into the symbol name.
>
> **Q: What is ADL (Argument-Dependent Lookup)?**
> A: When a function is called with an argument from a namespace, the compiler searches that namespace automatically. This is why `std::cout << x` works — ADL finds `std::operator<<` without explicit `std::` qualification. ADL is essential for operator overloads but can cause surprising overload resolution.
>
> **Q: Should you use `std::endl` or `'\n'`?**
> A: Prefer `'\n'`. `endl` inserts a newline AND flushes the output buffer, which is significantly slower. Use `endl` only when you need immediate visibility (interactive prompts, crash logs). For most output, `'\n'` is sufficient and faster.
>
> **Q: What are the C++ standards and what major features did each introduce?**
> A: C++11: auto, move semantics, lambdas, smart pointers, range-for. C++14: generic lambdas, return type deduction. C++17: structured bindings, if constexpr, filesystem, parallel algorithms. C++20: concepts, coroutines, ranges, modules, format, span. C++23: std::expected, std::generator, mdspan, import std.

---

## Cross-Links

- [[C++/01_Foundations/02_Classes_and_RAII]] for classes and constructors
- [[C++/01_Foundations/04_Operator_Overloading_and_Type_Casting]] for operator overloading
- [[C++/01_Foundations/05_Move_Semantics_and_Value_Categories]] for move semantics
- [[C++/01_Foundations/06_Templates_Basics_to_Variadic]] for templates
- [[C/01_Foundations/01_C_Basics_and_Pointers]] for C fundamentals comparison
