---
tags: [python, advanced, design-patterns, singleton, factory, observer, strategy, adapter, dependency-injection]
aliases: ["Design Patterns", "Pythonic Design Patterns", "Singleton", "Factory", "Observer", "Strategy", "DI"]
status: stable
updated: 2026-05-29
---

# Design Patterns Pythonically

> [!summary] Goal
> Implement classic design patterns (GoF) the Pythonic way — using closures, descriptors, `__init_subclass__`, metaclasses, and language features instead of verbose class hierarchies.

## Table of Contents

1. [Singleton](#singleton)
2. [Factory](#factory)
3. [Observer](#observer)
4. [Strategy](#strategy)
5. [Adapter](#adapter)
6. [Dependency Injection](#dependency-injection)
7. [Null Object](#null-object)
8. [Pitfalls](#pitfalls)

---

## Singleton

> [!info] Pythonic singletons use modules (module-level is inherently singleton) or metaclasses

```python
# Method 1: Module-level (simplest — module is only imported once)
# singleton.py
class _Database:
    def __init__(self):
        self.connection = None

db = _Database()         # Import this: from singleton import db

# Method 2: Metaclass
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = None

db1 = Database()
db2 = Database()
db1 is db2               # True

# Method 3: Class decorator
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Config:
    def __init__(self):
        self.settings = {}
```

---

## Factory

> [!info] Pythonic factories use classmethods or simple functions — no `FactoryFactory` needed

```python
from enum import Enum, auto

class ConnectorType(Enum):
    POSTGRES = auto()
    SQLITE = auto()
    MONGODB = auto()

class Connector:
    """Factory via classmethod."""
    @classmethod
    def create(cls, type_: ConnectorType, **kwargs):
        if type_ == ConnectorType.POSTGRES:
            return PostgresConnector(**kwargs)
        elif type_ == ConnectorType.SQLITE:
            return SQLiteConnector(**kwargs)
        elif type_ == ConnectorType.MONGODB:
            return MongoConnector(**kwargs)
        raise ValueError(f"Unknown type: {type_}")

# Or as a standalone function
def create_connector(type_: str, **kwargs):
    connectors = {
        "postgres": PostgresConnector,
        "sqlite": SQLiteConnector,
        "mongo": MongoConnector,
    }
    cls = connectors.get(type_)
    if cls is None:
        raise ValueError(f"Unknown connector: {type_}")
    return cls(**kwargs)

# Registration-based factory (open/closed)
class ConnectorRegistry:
    _connectors: dict[str, type] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(connector_cls):
            cls._connectors[name] = connector_cls
            return connector_cls
        return decorator

    @classmethod
    def create(cls, name: str, **kwargs):
        connector_cls = cls._connectors.get(name)
        if connector_cls is None:
            raise ValueError(f"Unknown connector: {name}")
        return connector_cls(**kwargs)

@ConnectorRegistry.register("postgres")
class PostgresConnector: ...
```

---

## Observer

> [!info] Pythonic observers use events, callbacks, or `blinker` — not the GoF pattern verbatim

```python
# Method 1: Callbacks (simplest)
class EventEmitter:
    def __init__(self):
        self._handlers: dict[str, list[callable]] = {}

    def on(self, event: str, handler: callable):
        self._handlers.setdefault(event, []).append(handler)

    def off(self, event: str, handler: callable):
        self._handlers.get(event, []).remove(handler)

    def emit(self, event: str, *args, **kwargs):
        for handler in self._handlers.get(event, []):
            handler(*args, **kwargs)

emitter = EventEmitter()
emitter.on("user.created", lambda u: print(f"Email: {u.email}"))
emitter.on("user.created", lambda u: print(f"Log: {u.id}"))
emitter.emit("user.created", user)

# Method 2: Descriptors for observable properties
class ObservableProperty:
    def __set_name__(self, owner, name):
        self.private = f"_{name}"
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private, None)

    def __set__(self, obj, value):
        old = getattr(obj, self.private, None)
        setattr(obj, self.private, value)
        obj._notify(self.name, old, value)

class ObservableModel:
    def __init__(self):
        self._observers = []

    def bind_to(self, observer):
        self._observers.append(observer)

    def _notify(self, name, old, new):
        for obs in self._observers:
            obs(self, name, old, new)

# Method 3: blinker library (recommended for real apps)
# pip install blinker
from blinker import signal

user_created = signal("user-created")

@user_created.connect
def send_email(sender, **kwargs):
    print(f"Email to {kwargs['user'].email}")

@user_created.connect
def log_event(sender, **kwargs):
    print(f"Log: user {kwargs['user'].id} created")

user_created.send(user=user)
```

---

## Strategy

> [!info] In Python, strategies are just functions/lambdas — no Strategy class hierarchy needed

```python
from typing import Callable

# Strategies as callables
TaxCalculator = Callable[[float], float]

def vat_tax(price: float) -> float:
    return price * 0.20

def sales_tax(price: float) -> float:
    return price * 0.08

def no_tax(price: float) -> float:
    return 0.0

class Order:
    def __init__(self, items: list[float], tax_strategy: TaxCalculator):
        self.items = items
        self.tax_strategy = tax_strategy

    def total(self) -> float:
        subtotal = sum(self.items)
        return subtotal + self.tax_strategy(subtotal)

order = Order([100, 200], vat_tax)
print(order.total())              # 360 = 300 + 60

# Strategy as enum + dict
from enum import Enum

class TaxType(Enum):
    VAT = "vat"
    SALES = "sales"
    NONE = "none"

TAX_RATES = {
    TaxType.VAT: 0.20,
    TaxType.SALES: 0.08,
    TaxType.NONE: 0.0,
}

def calculate_tax(price: float, tax_type: TaxType) -> float:
    return price * TAX_RATES[tax_type]
```

---

## Adapter

> [!info] Python's duck typing makes structural adapters mostly unnecessary — use `__getattr__` delegation

```python
# Adapter via __getattr__ delegation
class ThirdPartyLogger:
    def write_log(self, message):
        print(f"LOG: {message}")

class StdlibLoggerAdapter:
    """Adapts ThirdPartyLogger to stdlib logging interface."""
    def __init__(self, logger: ThirdPartyLogger):
        self._logger = logger

    def __getattr__(self, name):
        # Delegate unknown methods to the wrapped logger
        return getattr(self._logger, name)

    def info(self, message):
        self._logger.write_log(f"INFO: {message}")

    def error(self, message):
        self._logger.write_log(f"ERROR: {message}")

# Usage — adapts to any interface
def process(logger):
    logger.info("Processing started")
    logger.warning("Low memory")   # Delegated via __getattr__

process(StdlibLoggerAdapter(ThirdPartyLogger()))
```

---

## Dependency Injection

> [!info] Pythonic DI uses explicit constructor injection and type hints — no DI container needed for most cases

```python
from dataclasses import dataclass
from typing import Protocol

class Database(Protocol):
    async def query(self, sql: str) -> list[dict]: ...

class UserRepository:
    def __init__(self, db: Database):           # Constructor injection
        self._db = db

    async def get_user(self, user_id: int):
        return await self._db.query(
            f"SELECT * FROM users WHERE id = {user_id}"
        )

class UserService:
    def __init__(self, repo: UserRepository):   # Constructor injection
        self._repo = repo

    async def get_profile(self, user_id: int):
        user = await self._repo.get_user(user_id)
        return {"name": user["name"], "email": user["email"]}

# Wiring (at application entry point)
async def main():
    db = AsyncPostgresPool("postgresql://...")
    repo = UserRepository(db)
    service = UserService(repo)
    profile = await service.get_profile(42)
```

---

## Null Object

> [!info] Use `None` checks or a sentinel object instead of None-checking everywhere

```python
# Instead of:
def get_logger():
    if debug_mode:
        return Logger()
    return None

def process():
    logger = get_logger()
    if logger:                           # Check everywhere
        logger.info("Processing")

# Use a null object:
class NullLogger:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None   # No-op for any method

    def __bool__(self):
        return False

NULL_LOGGER = NullLogger()

def get_logger():
    return Logger() if debug_mode else NULL_LOGGER

def process():
    logger = get_logger()
    logger.info("Processing")           # Safe — no-op if null logger
```

---

## Pitfalls

### Singleton overuse

Singletons are global state in disguise. They make testing harder (can't isolate). Prefer dependency injection.

### Observer memory leaks

Unsubscribed observers prevent garbage collection. Use weak references (`weakref.WeakSet`) or `blinker`'s auto-cleanup.

### Strategy as class hierarchy

```python
# ❌ GoF-style Strategy class hierarchy (verbose)
class TaxStrategy:
    def calculate(self, price): ...
class VatTax(TaxStrategy): ...
class SalesTax(TaxStrategy): ...

# ✅ Pythonic: just use a function
def vat_tax(price): ...
```

### DI container overuse

Python doesn't need a DI container (like Spring). Simple constructor injection + manual wiring at the entry point is sufficient for most applications.

---

> [!question]- Interview Questions
>
> **Q: How do you implement the Singleton pattern in Python?**
> A: The simplest approach is a module (Python modules are singletons). For classes, use a metaclass that caches instances in `__call__`, or a class decorator that wraps `__init__` with caching. Module-level singletons are the most Pythonic.
>
> **Q: How does the Strategy pattern differ in Python vs Java?**
> A: In Java, Strategy requires an interface + concrete classes. In Python, strategies are just callables (functions, lambdas, or objects with `__call__`). The interface is implicit (duck typing). This makes the pattern nearly invisible in idiomatic Python.
>
> **Q: What's the Pythonic way to do dependency injection?**
> A: Explicit constructor injection with type hints (`def __init__(self, db: Database)`). Wire dependencies at the application entry point. No DI container needed — Python's flexibility makes containers unnecessary for most projects. Use `fastapi.Depends` for web endpoints.

---

## Cross-Links

- [[Python/01_Foundations/04_OOP_Classes_Dunder_Methods]] for class basics
- [[Python/02_Core/12_Metaprogramming_Descriptors]] for metaclasses and descriptors
- [[Python/02_Core/06_Web_Frameworks_FastAPI]] for FastAPI's DI system
- [[Python/01_Foundations/05_Iterators_Generators_Decorators]] for decorators as factories
