---
tags: [java, advanced, pattern-matching, sealed-classes, switch-pattern, record-pattern, instanceof]
aliases: ["Pattern Matching", "Sealed Classes", "Pattern Matching for instanceof", "Pattern Matching for switch", "Record Patterns"]
status: stable
updated: 2026-05-09
---

# Pattern Matching and Sealed Classes

> [!summary] Goal
> Master Java's pattern matching features: `instanceof` patterns (Java 16), `switch` expression patterns (Java 21), sealed classes (Java 17), and record patterns (Java 21). Understand how these features work together to enable exhaustive, type-safe data processing.

## Table of Contents

1. [Pattern Matching for instanceof](#pattern-matching-for-instanceof)
2. [Sealed Classes](#sealed-classes)
3. [Pattern Matching for switch](#pattern-matching-for-switch)
4. [Record Patterns](#record-patterns)
5. [Pitfalls](#pitfalls)

---

## Pattern Matching for instanceof

> [!info] Pattern matching
> Pattern matching allows you to test a value against a pattern and extract components in a single step. Instead of "check type, cast, use," you do it in one concise expression. The pattern variable is scoped to the branch where the pattern matches.

```java
// ❌ Old way: check, cast, use — verbose and error-prone
if (obj instanceof String) {
    String s = (String) obj;          // Cast is redundant but required
    if (s.length() > 0) {
        System.out.println(s.trim());
    }
}

// ✅ Pattern matching for instanceof (Java 16+)
if (obj instanceof String s && s.length() > 0) {  // s is in scope here
    System.out.println(s.trim());
}
// s is NOT in scope here (outside the if block)

// Guard conditions with && — the pattern variable is available in subsequent conditions
if (obj instanceof String s && s.startsWith("http")) {
    System.out.println("URL: " + s);
}
```

### Nested pattern matching

```java
// Checking nested types becomes readable
record Box(Object content) {}

void process(Object obj) {
    if (obj instanceof Box(String s) && s.length() > 5) {
        // Extracted String s from Box — in one step!
        System.out.println("Long string in box: " + s);
    }
}
```

---

## Sealed Classes

> [!info] Sealed class
> A sealed class restricts which classes can extend it. This enables exhaustive pattern matching — the compiler knows all possible subtypes at compile time. Sealed classes bring algebraic data types to Java, similar to `sealed` classes in Scala or `enum` variants in Rust.

```java
// Define a sealed hierarchy — all permitted subclasses must be declared
public sealed interface Shape
    permits Circle, Rectangle, Triangle {  // Only these three can implement Shape
    double area();
}

// Permitted subclasses must be: final, sealed, or non-sealed
public final class Circle implements Shape {
    private final double radius;
    public Circle(double radius) { this.radius = radius; }
    @Override public double area() { return Math.PI * radius * radius; }
}

public final class Rectangle implements Shape {
    private final double width, height;
    public Rectangle(double width, double height) { this.width = width; this.height = height; }
    @Override public double area() { return width * height; }
}

public final class Triangle implements Shape {
    private final double base, height;
    public Triangle(double base, double height) { this.base = base; this.height = height; }
    @Override public double area() { return 0.5 * base * height; }
}
```

### Sealed class rules

| Rule | Explanation |
|------|-------------|
| **Permits clause** | Lists all allowed subclasses (must be in the same module or compiled together) |
| **Subclass must be final** | No further extension — terminates the hierarchy |
| **Subclass can be sealed** | Extends the hierarchy further |
| **Subclass can be non-sealed** | Allows unknown extensions (breaks exhaustiveness) |

### Exhaustive switch with sealed types

```java
// The compiler knows all possible subtypes — no default needed!
double area = switch (shape) {
    case Circle c     -> Math.PI * c.radius() * c.radius();
    case Rectangle r  -> r.width() * r.height();
    case Triangle t   -> 0.5 * t.base() * t.height();
    // No default needed — all cases covered
    // If a new shape is added, this switch won't compile!
};
```

---

## Pattern Matching for switch

> [!info] Switch pattern matching
> Java 21 extends `switch` to work with types, not just primitive constants. You can match on type, extract components (destructuring), add `when` clauses (guards), and the compiler enforces exhaustiveness. Combined with sealed classes, this replaces the Visitor pattern for many use cases.

```java
// Switch on type — no more if-else instanceof chains
String formatted = switch (obj) {
    case Integer i -> "Integer: " + i;
    case String s  -> "String: " + s;
    case null      -> "null";            // Null handling — no more NPE!
    default        -> "Unknown: " + obj.getClass();
};

// Guards with `when` clause
String classify = switch (obj) {
    case String s when s.length() > 10 -> "Long string: " + s;
    case String s                      -> "Short string: " + s;
    case Integer i when i < 0          -> "Negative: " + i;
    case Integer i                     -> "Positive or zero: " + i;
    case null                          -> "null";
    default                            -> "Other";
};

// Exhaustive switch on sealed types (no default needed)
String description = switch (shape) {
    case Circle c     -> "Circle(radius=" + c.radius() + ")";
    case Rectangle r  -> "Rectangle(" + r.width() + "x" + r.height() + ")";
    case Triangle t   -> "Triangle(base=" + t.base() + ", height=" + t.height() + ")";
};
```

### Dominance — ordering matters

```java
// Patterns are evaluated top-to-bottom. More specific patterns FIRST.
String result = switch (obj) {
    case String s               -> "String: " + s;  // Generic
    case String s when s.isEmpty() -> "Empty!";     // ❌ Unreachable! More specific MUST come first
    default                     -> "Other";
};

// Correct order:
String result = switch (obj) {
    case String s when s.isEmpty() -> "Empty!";     // Specific first
    case String s                   -> "String: " + s;
    default                         -> "Other";
};
```

---

## Record Patterns (Java 21)

> [!info] Record pattern
> Record patterns destructure records in pattern matching. Instead of extracting components manually, you match on the record structure directly. Combined with nested patterns, this is incredibly powerful for processing tree-like data.

```java
// Without record patterns — manual extraction
if (obj instanceof Point p) {
    int x = p.x();
    int y = p.y();
    // ... use x, y
}

// With record patterns — destructure in the match
if (obj instanceof Point(int x, int y)) {
    // x and y are extracted directly!
    System.out.println("Point(" + x + ", " + y + ")");
}

// Nested record patterns — destructure nested records
record Location(String city, Point coordinates) {}
record Point(int x, int y) {}

void process(Object obj) {
    if (obj instanceof Location(var city, Point(int x, int y))) {
        // Extracts city from Location, x and y from Point — all in one pattern!
        System.out.println(city + " at (" + x + ", " + y + ")");
    }
}
```

### Generic record patterns

```java
record Pair<T, U>(T first, U second) {}

void process(Object obj) {
    if (obj instanceof Pair(String name, Integer count)) {
        // Type inference: name is String, count is Integer
        System.out.println(name + ": " + count);
    }
}
```

---

## Pitfalls

### Pattern variable scope confusion

```java
if (obj instanceof String s) {
    System.out.println(s);   // ✅ s is in scope
}
// System.out.println(s);    // ❌ s is NOT in scope here

if (obj instanceof String s && s.length() > 0) { }  // ✅ s in scope in guard
// if (obj instanceof String s || s.length() > 0) { } // ❌ ERROR: s not in scope (|| short-circuits)
```

### Forgetting null handling

`switch` pattern matching throws `NullPointerException` for null input unless you add a `case null`. Always include `case null` for robust code.

### Non-exhaustive switch on non-sealed types

For `switch` on `Object` or non-sealed types, you MUST include `default`. Only sealed types guarantee exhaustiveness. Forgetting `default` causes a compile error only if the compiler can prove non-exhaustiveness.

### Reordering patterns incorrectly

Dominance matters: put more specific patterns (with `when` guards) before general ones. The compiler warns about unreachable code for wrongly ordered patterns.

---

> [!question]- Interview Questions
>
> **Q: How does pattern matching for instanceof improve over casting?**
> A: It eliminates the three-step pattern (check type, cast, use) with a single expression. The pattern variable is scoped to the branch where the pattern matches, preventing accidental use outside the checked scope. It's also safer with nested record patterns — extracting components becomes a one-liner.
>
> **Q: What is a sealed class and why would you use one?**
> A: A sealed class restricts which other classes can extend it. Use sealed classes when you have a fixed set of subtypes (like Shape → Circle, Rectangle, Triangle). Benefits: (1) exhaustive pattern matching — the compiler knows all subtypes and can verify switch completeness, (2) documents the design intent explicitly, (3) prevents API misuse.
>
> **Q: What is a guarded pattern in switch?**
> A: A guarded pattern adds a boolean condition with `when`: `case String s when s.length() > 10`. The pattern matches only if both the type matches AND the guard evaluates to true. More specific guards must come before less specific patterns to avoid unreachable code.
>
> **Q: How do record patterns work?**
> A: Record patterns destructure the record in the pattern itself. `case Point(int x, int y)` matches a `Point` record and binds its components to `x` and `y`. Nesting is supported: `case Location(String city, Point(int x, int y))` destructures a `Location` containing a `Point` — all in one pattern.
>
> **Q: What is the relationship between sealed classes and exhaustive switch?**
> A: Sealed classes define a closed set of subtypes. The compiler knows every possible subtype at compile time. When you switch on a sealed type, the compiler can verify all cases are covered — no `default` needed. If you add a new permitted subclass and the switch isn't updated, it won't compile.

---

## Cross-Links

- [[Java/01_Foundations/05_Modern_Java_Language_Features]] for records, enums, and enhanced switch
- [[Java/03_Advanced/06_Virtual_Threads_and_Structured_Concurrency]] for concurrent pattern matching
- [[Java/03_Advanced/08_Module_System_JPMS]] for sealed classes across module boundaries
- [[Java/03_Advanced/09_Reflection_and_Annotations]] for reflection on sealed classes
- [[Java/01_Foundations/02_Collections_and_Generics]] for generic record patterns
