---
tags: [cpp, core, undefined-behavior, object-lifetime, static-init-order, odr, strict-aliasing, launder]
aliases: ["Undefined Behavior", "Object Lifetime", "Static Init Order Fiasco", "ODR Violation", "Most Vexing Parse"]
status: stable
updated: 2026-05-09
---

# Undefined Behavior, Object Lifetimes, and Low-Level C++

> [!summary] Goal
> Understand C++ undefined behavior — all the subtle ways C++ can silently break. Master object lifetime rules, the static initialization order fiasco, ODR violations, strict aliasing, and low-level topics that every expert needs to know.

## Table of Contents

1. [Undefined Behavior Sources](#undefined-behavior-sources)
2. [Object Lifetime](#object-lifetime)
3. [Static Initialization Order Fiasco](#static-initialization-order-fiasco)
4. [Most Vexing Parse](#most-vexing-parse)
5. [ODR Violations](#odr-violations)
6. [Pitfalls](#pitfalls)

---

## Undefined Behavior Sources

> [!info] Undefined behavior (UB)
> The C++ standard says certain operations have undefined behavior — the compiler can emit any code. It can optimize assuming UB never happens. The program may crash, produce wrong results, appear to work correctly, or delete your files. Common UB sources in C++ (beyond C UB):

| UB source | Example | Consequence |
|-----------|---------|-------------|
| **Signed integer overflow** | `INT_MAX + 1` | Compiler may optimize away the check |
| **Null pointer dereference** | `*p` where `p == nullptr` | Usually crash, but compiler may delete the null check |
| **Array bounds violation** | `arr[5]` where `arr` has 5 elements | Memory corruption |
| **Use-after-free** | `*p` after `delete p` | Heap corruption |
| **Double delete** | `delete p; delete p;` | Heap corruption |
| **Calling virtual on destroyed object** | Calling virtual fn in destructor after derived is destroyed | Dispatches to base version (not derived) |
| **Strict aliasing violation** | `float* f = reinterpret_cast<float*>(&int_val)` | Compiler may optimize incorrectly |
| **Dereferencing past-the-end iterator** | `*v.end()` | UB |
| **Reordering volatile access** | Multiple volatile writes without seq point | Compiler may reorder |
| **Modifying const object** | `const_cast` on a truly const object | May work or crash (in ROM) |

```cpp
// The compiler may optimize this assuming signed overflow never happens
int square(int x) {
    return x * x;
}
// If x = 1000000, x*x = 10^12 > INT_MAX = ~2.1×10^9 → UB
// Compiler: "sq should never overflow, remove overflow checks"
```

---

## Object Lifetime

> [!info] Object lifetime
> An object's lifetime begins when its constructor completes and ends when its destructor starts. Between these events, the object is "alive" — virtual functions dispatch correctly, `this` is valid. Before construction or after destruction, accessing the object is UB (with some exceptions for transparently replaceable objects in C++17+).

```cpp
struct Widget {
    Widget() { std::cout << "Alive\n"; }
    ~Widget() { std::cout << "Dead\n"; }
    void speak() { std::cout << "Hello\n"; }
};

// Lifetime starts after constructor completes
// Lifetime ends when destructor starts
// Between ~Widget() start and completion: object is in destruction — don't call virtual fns
```

### Placement new and explicit destruction

```cpp
alignas(Widget) char buffer[sizeof(Widget)];
Widget* w = new (buffer) Widget();     // Lifetime starts
w->speak();
w->~Widget();                           // Lifetime ends
// Buffer can now be reused for something else
```

### Transparently replaceable objects (C++17)

```cpp
// C++17: a new object can transparently replace an old one
// if they have the same type, are in the same memory, etc.
// This makes std::launder useful:
struct X {
    const int n;
};

X* p = new X{42};
// p->n = 10;  // ❌ ERROR: n is const
new (p) X{10};  // OK: replaces the object
// int val = p->n;  // UB? The compiler may have cached p->n = 42
int val = std::launder(p)->n;  // ✅ Correct: tells compiler to re-read
```

---

## Static Initialization Order Fiasco

> [!info] Static init order fiasco
> The order of initialization of non-local static objects (globals, namespace-scope statics, class statics) across different translation units is **undefined**. If one global's constructor depends on another global from a different .cpp file, your program may crash — and only sometimes (it depends on the linker order).

```cpp
// file: a.cpp
struct A {
    A() { std::cout << B::getValue(); }   // ❌ B may not be initialized yet!
};
A global_a;

// file: b.cpp
struct B {
    static int getValue() { return 42; }
    static int value;          // May not be initialized when A tries to use it
};
int B::value = 42;

// If A is initialized before B, A reads uninitialized memory!
```

### Fix: Construct On First Use Idiom

```cpp
// file: a.cpp
A& global_a() {
    static A instance;          // ✅ Initialized on first call — guaranteed order
    return instance;
}

// file: b.cpp
B& global_b() {
    static B instance;          // ✅ Same pattern
    return instance;
}

// Now a's constructor calls global_b().getValue()
// global_b() is called → B is initialized → safe!

// NOTE: static locals are also thread-safe (C++11+)
```

---

## Most Vexing Parse

> [!info] Most vexing parse
> In C++, anything that CAN be parsed as a function declaration WILL be parsed as a function declaration. This leads to the "most vexing parse" — you think you're constructing an object, but the compiler sees a function declaration.

```cpp
class Widget {
public:
    Widget(int x) {}
};

// Intended: create a Widget
Widget w();        // ❌ Oops! This is a function declaration!
// "w is a function taking no parameters, returning a Widget"

// ✅ Correct:
Widget w{42};      // C++11 uniform initialization — no ambiguity
Widget w(42);      // Also works (int parameter prevents the function interpretation)

// Another example:
std::ifstream file("data.txt");
Widget w(file);    // ❌ Is this a function declaration? "w is a function taking an ifstream"
// ✅ Correct:
Widget w{file};    // Braces = no ambiguity
Widget w((file));  // Extra parentheses force expression, not declaration
```

### I hate this — rule of thumb

```cpp
// When in doubt, use braces {} instead of parentheses ()
// Braces are never parsed as function declarations

std::vector<int> v(10);      // vector of 10 ints
std::vector<int> v{10};      // vector with one element: 10

// Types with initializer_list constructors behave differently with {}!
// Use braces for initialization, parentheses for construction with value arguments
```

---

## ODR Violations

> [!info] ODR (One Definition Rule)
> Every function, variable, type, class, enum, and template must have exactly one definition across the entire program. Violations are difficult to debug — the linker may silently pick one definition, leading to hard-to-find bugs.

### Common ODR violations

```cpp
// header.h
struct S { int x; };           // OK: classes can be defined in headers

// inline functions are OK
inline int max(int a, int b) { return a > b ? a : b; }

// But this is WRONG:
// a.cpp
int global_value = 42;

// b.cpp
int global_value = 100;      // ❌ ODR violation — two definitions!
// Linker may pick one silently!
```

### ODR with templates (the reason templates are in headers)

```cpp
// template.h
template<typename T>
T max(T a, T b) { return a > b ? a : b; }  // OK: defined in header

// Instantiated in multiple .cpp files — linker deduplicates
// This works because templates have a special ODR exemption
```

---

## Pitfalls

### Calling virtual functions in constructor/destructor

During construction, the vtable changes as each constructor runs. Before the Derived constructor runs, the vtable points to Base — calling a virtual function calls the Base version, NOT the Derived override. Similarly during destruction.

### Const data member + move

A `const` member prevents move assignment (can't assign to a const member). Classes with const members are neither copyable nor movable — the compiler-generated move operations are deleted. Use `const` members sparingly.

### Object slicing with collections

```cpp
std::vector<Base> vec;
vec.push_back(Derived{});    // ❌ Sliced! Only Base portion stored
// Use std::vector<std::unique_ptr<Base>> or std::vector<std::shared_ptr<Base>>
```

### Dangling references from temporary binding

```cpp
int&& rref = 42;                  // OK: extends lifetime
const int& cref = compute_int();  // OK: extends lifetime
// BUT:
std::vector<int>&& rv = std::vector<int>{1, 2, 3};  // OK: extends
// auto& x = function_returning_vector().front();    // ❌ Dangling!
```

---

> [!question]- Interview Questions
>
> **Q: What is the static initialization order fiasco?**
> A: The order of initialization of non-local static objects (across translation units) is undefined. If global A's constructor uses global B, and B is defined in a different .cpp file, B may not be initialized yet. Fix: use a function-local static (Construct On First Use Idiom) — `static B& getB() { static B instance; return instance; }`. The static local is initialized on first call, guaranteeing order.
>
> **Q: What is the most vexing parse?**
> A: C++ parses anything that looks like a function declaration as a function declaration. `Widget w();` is a function declaration, not a Widget construction. Fix: use uniform initialization `Widget w{};` or extra parentheses `Widget w((Widget()));`. When in doubt, use braces instead of parentheses.
>
> **Q: What is an ODR violation?**
> A: The One Definition Rule requires every function, variable, type, and template to have exactly one definition. Common violations: defining the same global variable in two .cpp files, defining a non-inline function in a header included in multiple .cpp files, or defining a member function in a header without `inline`.
>
> **Q: What does std::launder do?**
> A: `std::launder(p)` tells the compiler to treat the pointer as though it points to a new object at the same address, bypassing the assumption that the old object's state (const values, references) is still valid. Used after placement new in the same memory location, especially when the old object has const or reference members.
>
> **Q: Can you call a virtual function from a constructor?**
> A: You can call it, but the Base version will be called, not the Derived override. During Base construction, the object's vtable points to Base's vtable — the Derived part hasn't been constructed yet. The same applies during destruction (after Derived's destructor runs, the vtable reverts to Base's).

---

## Cross-Links

- [[C++/01_Foundations/02_Classes_and_RAII]] for constructor/destructor lifetime
- [[C++/01_Foundations/03_Inheritance_Polymorphism_and_Virtual_Functions]] for virtual calls and slicing
- [[C++/01_Foundations/04_Operator_Overloading_and_Type_Casting]] for reinterpret_cast and aliasing
- [[C++/01_Foundations/05_Move_Semantics_and_Value_Categories]] for const members and move
- [[C++/03_Advanced/08_Game_Engine_and_Driver_Dev]] for placement new in game engines
