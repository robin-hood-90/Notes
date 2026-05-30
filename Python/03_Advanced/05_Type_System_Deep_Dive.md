---
tags: [python, advanced, typing, mypy, protocol, typeddict, generics, typeguard, stubs]
aliases: ["Type System", "mypy", "Protocol", "TypedDict", "Type Guards", "Generic", "Stub Files"]
status: stable
updated: 2026-05-29
---

# Type System Deep Dive

> [!summary] Goal
> Master Python's type system — `Protocol` for structural typing, `TypedDict`, `Literal`, `Final`, `@overload`, `TypeGuard`, `Self`, `Never`, mypy strict mode, and stub files.

## Table of Contents

1. [Protocol (Structural Subtyping)](#protocol-structural-subtyping)
2. [TypedDict](#typeddict)
3. [Literal, Final, and TypeAlias](#literal-final-and-typealias)
4. [@overload](#overload)
5. [TypeGuard and TypeIs](#typeguard-and-typeis)
6. [Self and Never](#self-and-never)
7. [Generics and TypeVar](#generics-and-typevar)
8. [mypy Strict Mode](#mypy-strict-mode)
9. [Stub Files](#stub-files)
10. [Pitfalls](#pitfalls)

---

## Protocol (Structural Subtyping)

> [!info] `Protocol` enables structural subtyping (duck typing at the type-checker level) — any class with the required methods satisfies the protocol implicitly.

```python
from typing import Protocol, runtime_checkable

class Drawable(Protocol):
    def draw(self) -> str: ...

class Circle:
    def draw(self) -> str:           # Implicitly satisfies Drawable
        return "Drawing circle"

class Square:
    def draw(self) -> str:
        return "Drawing square"
    def area(self) -> float:         # Extra method is fine
        return 4.0

def render(obj: Drawable) -> None:   # Accepts any Drawable
    print(obj.draw())

render(Circle())                     # ✅ OK
render(Square())                     # ✅ OK (structural match)

# Runtime checkable
@runtime_checkable
class Named(Protocol):
    name: str

@runtime_checkable
class HasName:
    def __init__(self):
        self.name = "Alice"

isinstance(HasName(), Named)         # True (runtime check works!)
```

### Protocol vs ABC

| Feature | Protocol | ABC |
|---------|:--------:|:---:|
| Inheritance | Implicit (structural) | Required (`extends`) |
| Runtime check | With `@runtime_checkable` | `isinstance` works |
| Use case | Duck typing in types | Shared implementation |
| Multiple | ✅ Or-combine protocols | ✅ Multiple inheritance |

---

## TypedDict

> [!info] `TypedDict` defines the expected shape of a dict (used for JSON-like data)

```python
from typing import TypedDict, NotRequired

class UserDict(TypedDict):
    id: int
    name: str
    email: str
    age: NotRequired[int]           # Python 3.11+

# Usage
user: UserDict = {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com",
}                                   # ✅ Valid

user = {"id": "abc"}                # ❌ mypy: wrong type for id

# Total=True by default (all keys required)
class Config(TypedDict, total=False):
    debug: bool                     # All optional
    port: int
```

---

## Literal, Final, and TypeAlias

```python
from typing import Literal, Final, TypeAlias

# Literal — exact value constraint
def set_mode(mode: Literal["rgb", "grayscale", "cmyk"]) -> None: ...

set_mode("rgb")                     # ✅ OK
set_mode("hsl")                     # ❌ mypy: invalid literal

# Final — cannot be reassigned
MAX_RETRIES: Final = 3
MAX_RETRIES = 5                     # ❌ mypy: cannot assign to final

# TypeAlias — named type
Vector: TypeAlias = list[float]

def dot_product(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))
```

---

## @overload

> [!info] `@overload` lets you define multiple type signatures for a single implementation

```python
from typing import overload

@overload
def process(data: str) -> str: ...

@overload
def process(data: bytes) -> bytes: ...

@overload
def process(data: None) -> None: ...

# Actual implementation (no type hints needed — covers all overloads)
def process(data):
    if data is None:
        return None
    if isinstance(data, str):
        return data.upper()
    return data.hex()

# mypy infers correct types:
result1: str = process("hello")      # ✅
result2: bytes = process(b"hello")   # ✅
result3: None = process(None)        # ✅
```

### Common overload patterns

```python
# Factory return types
@overload
def create_parser(format: Literal["json"]) -> JSONParser: ...

@overload
def create_parser(format: Literal["yaml"]) -> YAMLParser: ...

def create_parser(format: str):
    if format == "json":
        return JSONParser()
    return YAMLParser()
```

---

## TypeGuard and TypeIs

```python
from typing import TypeGuard, TypeIs

# TypeGuard — custom type narrowing
def is_string_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(items: list[object]) -> None:
    if is_string_list(items):
        # items is narrowed to list[str]
        print(" ".join(items))

# TypeIs (Python 3.11+) — more precise than TypeGuard
def is_int(val: object) -> TypeIs[int]:
    return isinstance(val, int)

def process_val(val: object) -> None:
    if is_int(val):
        # val is int (TypeIs narrows the original variable)
        print(val + 1)
```

### TypeGuard vs TypeIs

| Feature | TypeGuard | TypeIs (3.11+) |
|---------|:---------:|:--------------:|
| Narrowing scope | Return value only | Original variable |
| Negation support | ❌ | ✅ `not TypeIs` works |
| When to use | Checked container types | Single object types |

---

## Self and Never

```python
from typing import Self, Never

# Self — return type of chained methods / classmethods
class Builder:
    def __init__(self):
        self._value = 0

    def add(self, n: int) -> Self:          # Returns Builder subclass
        self._value += n
        return self

    def build(self) -> int:
        return self._value

class AdvancedBuilder(Builder):
    def multiply(self, n: int) -> Self:
        self._value *= n
        return self

result = AdvancedBuilder().add(5).multiply(2).build()  # mypy tracks the type

# Never — unreachable (exhaustiveness checking)
def assert_never(value: Never) -> None:
    raise AssertionError(f"Unhandled: {value}")

from enum import Enum
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

def describe(color: Color) -> str:
    if color is Color.RED:
        return "Red"
    elif color is Color.GREEN:
        return "Green"
    elif color is Color.BLUE:
        return "Blue"
    else:
        assert_never(color)                 # ❌ If a new color is added, mypy errors!
```

---

## Generics and TypeVar

```python
from typing import TypeVar, Generic, Sequence

T = TypeVar("T")                            # Generic type
U = TypeVar("U", bound=Comparable)           # Constrained
V = TypeVar("V", int, str)                  # Restricted to int or str

# Generic function
def first(seq: Sequence[T]) -> T:
    return seq[0]

# Generic class
class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

stack = Stack[int]()
stack.push(42)
value = stack.pop()                         # int (inferred)

# TypeVar with constraints (covariant, contravariant)
T_co = TypeVar("T_co", covariant=True)       # For ReadOnly containers
T_contra = TypeVar("T_contra", contravariant=True)  # For WriteOnly containers
```

---

## mypy Strict Mode

```toml
[tool.mypy]
strict = true                         # Enables all strict flags
# Equivalent to:
# --no-implicit-any
# --no-implicit-reexport
# --disallow-untyped-defs
# --disallow-untyped-calls
# --disallow-incomplete-defs
# --check-untyped-defs
# --disallow-subclassing-any
# --disallow-any-generics
# --warn-redundant-casts
# --warn-unused-ignores
# --warn-return-any
# --warn-unreachable
```

```bash
# Run mypy
mypy src/                          # Check all files
mypy src/ --strict                 # Strict mode
mypy src/ --ignore-missing-imports # Skip missing stubs
mypy src/ --show-error-codes       # Show error codes
mypy src/ --python-version 3.12    # Target Python version
```

```python
# Stub-only packages for third-party libs
# pip install types-requests types-pytz types-PyYAML
```

---

## Stub Files

> [!info] `.pyi` files define type signatures separate from implementation
> Used for: C extensions, closed-source libraries, or separating types from code.

```python
# mymodule.pyi — type stubs
def greet(name: str, age: int = 30) -> str: ...
class User:
    def __init__(self, name: str) -> None: ...
    def get_name(self) -> str: ...

# mymodule.py — implementation (no type hints needed)
def greet(name, age=30):
    return f"{name} is {age}"

class User:
    def __init__(self, name):
        self._name = name
    def get_name(self):
        return self._name
```

```bash
# Distribute stubs
# Option 1: Alongside .py files (my_module.py + my_module.pyi)
# Option 2: In typeshed (for external libraries)
# Option 3: In stub-only package: pip install types-mylib
```

---

## Pitfalls

### Protocol is not runtime-checkable by default

Add `@runtime_checkable` for `isinstance` with Protocols. Without it, `isinstance` raises `TypeError`.

### TypeVar bounding

```python
T = TypeVar("T", bound=float)     # Accepts float and subclasses (int)
T = TypeVar("T", int, str)         # Accepts ONLY int or str (union)
```

### `Any` defeats type checking

```python
x: Any = some_function()
x.some_method()                    # No error — Any disables checking!
```

### Mutable defaults in generic classes

Mutable default values in generic classes can cause subtle type errors. Use `None` + `if` check instead.

---

> [!question]- Interview Questions
>
> **Q: What's the difference between `Protocol` and `ABC`?**
> A: Protocol uses structural subtyping (duck typing) — any class with matching methods satisfies it implicitly. ABC requires explicit inheritance. Protocol is better for interfaces that many unrelated types implement. ABC is better for shared implementation via template method pattern.
>
> **Q: What does `mypy --strict` enable?**
> A: It enables ~12 stricter flags including `--disallow-untyped-defs` (must annotate all functions), `--no-implicit-any` (no hidden Any), `--warn-unreachable` (dead code detection), and `--disallow-any-generics` (must specify generic parameters). It's the gold standard for type-safe Python.
>
> **Q: When would you use `TypeGuard` vs `isinstance`?**
> A: `isinstance` is runtime-native but can only check single types. `TypeGuard` lets you define custom narrowing logic (e.g., "this list of objects contains only strings"). `TypeIs` (3.11+) is preferred over `TypeGuard` for single-object checks because it narrows the original variable.

---

## Cross-Links

- [[Python/01_Foundations/03_Functions_Deep_Dive]] for function annotations
- [[Python/02_Core/12_Metaprogramming_Descriptors]] for runtime type inspection
- [[Python/02_Core/13_Packaging_Distribution]] for distributing stub files
- [[Python/01_Foundations/10_Testing_with_Pytest]] for testing with type hints
