---
tags: [python, foundations, stdlib, datetime, regex, logging, argparse, collections, itertools, functools, typing]
aliases: ["Standard Library Essentials", "datetime", "re", "logging", "argparse", "typing"]
status: stable
updated: 2026-05-29
---

# Standard Library Essentials

> [!summary] Goal
> Master Python's most-used standard library modules — `datetime`, `re`, `logging`, `argparse`, `math`, and the `typing` module basics.

## Table of Contents

1. [datetime](#datetime)
2. [re — Regular Expressions](#re--regular-expressions)
3. [math and statistics](#math-and-statistics)
4. [argparse](#argparse)
5. [logging](#logging)
6. [typing Basics](#typing-basics)
7. [Pitfalls](#pitfalls)

---

## datetime

```python
from datetime import datetime, date, time, timedelta, timezone

# Current time
now = datetime.now()                       # local time (naive)
utc_now = datetime.now(timezone.utc)       # UTC (aware)
today = date.today()                       # date only

# Construction
dt = datetime(2026, 5, 29, 10, 30, 0)
dt = datetime.fromisoformat("2026-05-29T10:30:00+00:00")  # Python 3.7+
dt = datetime.strptime("2026-05-29", "%Y-%m-%d")

# Formatting
dt.strftime("%Y-%m-%d %H:%M")          # "2026-05-29 10:30"
dt.isoformat()                         # "2026-05-29T10:30:00"

# Arithmetic
tomorrow = today + timedelta(days=1)
diff = timedelta(hours=5, minutes=30)
past = now - diff

# Timezone handling
# Naive vs aware
naive = datetime(2026, 5, 29, 10, 0)            # no tz info
aware = datetime(2026, 5, 29, 10, 0, tzinfo=timezone.utc)  # with tz

# Convert between timezones
from zoneinfo import ZoneInfo  # Python 3.9+
est = aware.astimezone(ZoneInfo("America/New_York"))

# Always store UTC, convert on display
def store_time():
    return datetime.now(timezone.utc)           # UTC in database

def display_time(dt: datetime, tz_str: str = "local"):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)   # Assume UTC if naive
    local = dt.astimezone(ZoneInfo(tz_str) if tz_str != "local" else None)
    return local.isoformat()
```

### Common patterns

| Pattern | Code |
|---------|------|
| Parse ISO 8601 | `datetime.fromisoformat(s)` |
| Format for logs | `dt.isoformat()` |
| N days ago | `datetime.now() - timedelta(days=n)` |
| Unix timestamp | `dt.timestamp()` |
| From timestamp | `datetime.fromtimestamp(ts, tz=timezone.utc)` |

---

## re — Regular Expressions

```python
import re

# Compile once, use many times (faster)
pattern = re.compile(r"\d+")          # raw string!
text = "abc 123 def 456"

# Match — at the beginning
m = pattern.match("123abc")           # Match object (or None)
m.group()    # "123"

# Search — anywhere
m = pattern.search(text)              # "123"
m.start()    # 4
m.end()      # 7

# Find all
pattern.findall(text)                 # ["123", "456"]

# Find iter (memory efficient)
for m in pattern.finditer(text):
    print(m.group())                  # "123", "456"

# Split
re.split(r"\s+", "a b   c")          # ["a", "b", "c"]

# Substitution
re.sub(r"\d+", "X", text)            # "abc X def X"
re.sub(r"\d+", lambda m: str(int(m.group()) * 2), text)  # "abc 246 def 912"

# Groups
pattern = re.compile(r"(\w+)@(\w+\.\w+)")
m = pattern.match("alice@example.com")
m.group(0)   # "alice@example.com"
m.group(1)   # "alice"
m.group(2)   # "example.com"
m.groups()   # ("alice", "example.com")
```

### Common regex patterns

| Pattern | Matches |
|---------|---------|
| `\d+` | One or more digits |
| `\w+` | One or more word chars (`[a-zA-Z0-9_]`) |
| `\s` | Whitespace |
| `.` | Any char except newline |
| `^` / `$` | Start / end of string |
| `(?:...)` | Non-capturing group |
| `(?P<name>...)` | Named group |

> [!warning] Regex performance
> Never use `re.search(r"(a+)+b", "a" * 30)` — catastrophic backtracking! Always compile, use raw strings, and avoid nested quantifiers on overlapping patterns.

---

## math and statistics

```python
import math, statistics, random

# math
math.ceil(3.1)     # 4
math.floor(3.9)    # 3
math.trunc(3.9)    # 3 (toward zero)
math.isclose(0.1 + 0.2, 0.3, rel_tol=1e-9)  # True — safe float compare
math.sqrt(16)      # 4.0
math.log(100, 10)  # 2.0
math.inf           # Infinity
math.nan           # NaN

# statistics
statistics.mean([1, 2, 3, 4])    # 2.5
statistics.median([1, 2, 3, 100])  # 2.5 (robust to outliers)
statistics.stdev([1, 2, 3, 4])    # ~1.29 (sample std dev)

# random
random.random()                    # [0.0, 1.0)
random.randint(1, 6)              # int in [1, 6]
random.choice(["a", "b", "c"])    # random element
random.sample(range(100), 5)      # 5 unique samples
random.shuffle(lst)               # in-place shuffle
random.seed(42)                   # reproducible sequence
```

---

## argparse

```python
import argparse

parser = argparse.ArgumentParser(
    prog="myapp",
    description="My CLI application",
)
parser.add_argument("input", help="Input file path")          # positional
parser.add_argument("-o", "--output", help="Output file")     # optional
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")
parser.add_argument("--limit", type=int, default=10, help="Max results")
parser.add_argument("--format", choices=["json", "yaml"], default="json")
parser.add_argument("--log-level", default="INFO")

args = parser.parse_args()

# Usage
# python myapp.py data.txt -o out.json -v --limit 20 --format json

print(args.input)       # "data.txt"
print(args.output)      # "out.json"
print(args.verbose)     # True
print(args.limit)       # 20

# Subcommands
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")

parse_cmd = subparsers.add_parser("parse")
parse_cmd.add_argument("file")

validate_cmd = subparsers.add_parser("validate")
validate_cmd.add_argument("file")

args = parser.parse_args()
if args.command == "parse":
    ...
```

---

## logging

> [!info] Use `logging` over `print` for any non-trivial application
> Logging provides levels, formatting, multiple outputs (file + console), and configurable verbosity without changing code.

```python
import logging

# Basic configuration (set once at app startup)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

# Module-level logger
logger = logging.getLogger(__name__)

logger.debug("Detailed debug info")      # Only shown if level <= DEBUG
logger.info("Server started on port %d", 8080)
logger.warning("Disk space low: %.1f GB", free_space)
logger.error("Failed to connect: %s", err)
logger.critical("System shutting down")

# Structured logging (Python 3.12+)
logging.basicConfig(
    level=logging.INFO,
    format=json.dumps({
        "timestamp": "%(asctime)s",
        "level": "%(levelname)s",
        "logger": "%(name)s",
        "message": "%(message)s",
    }),
)
```

### Logging to file + console

```python
import logging

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

# File handler
fh = logging.FileHandler("app.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

logger.addHandler(ch)
logger.addHandler(fh)
```

---

## typing Basics

> [!info] Type hints (PEP 484, Python 3.5+) enable static type checking with mypy/pyright

```python
from typing import List, Dict, Optional, Union, Any, Callable, Tuple, Set

# Basic annotations
def greet(name: str, age: int = 30) -> str:
    return f"{name} is {age} years old"

# Containers
def process(items: list[int]) -> int:           # Python 3.9+ — built-in generics
    return sum(items)

def lookup(key: str, mapping: dict[str, int]) -> Optional[int]:
    return mapping.get(key)                     # Could be None

# Union
def parse(value: Union[int, str]) -> int:       # Python 3.10+: int | str
    return int(value)

# Callable
def run_callback(fn: Callable[[int, str], bool]) -> None:
    result = fn(42, "test")

# Any
def identity(x: Any) -> Any:
    return x
```

> [!tip] Python 3.10+ syntax
> - `X | Y` instead of `Union[X, Y]`
> - `list[X]` instead of `List[X]` (also works in 3.9+)
> - `X | None` instead of `Optional[X]`

---

## Pitfalls

### Naive datetime vs aware datetime

```python
# ❌ Mixing naive and aware
naive = datetime(2026, 5, 29, 10, 0)
aware = datetime(2026, 5, 29, 10, 0, tzinfo=timezone.utc)
# aware - naive  # TypeError: can't subtract offset-naive and offset-aware datetimes

# ✅ Always compare same type
naive = naive.replace(tzinfo=timezone.utc)  # or use zoneinfo
```

### Regex raw strings

```python
# Without raw string: \d means backspace + d? or just escape?
re.search("\d+", "123")   # May or may not work depending on how \d is interpreted
re.search(r"\d+", "123")  # ✅ Always correct
```

### Logging with lazy formatting

```python
# ❌ Always evaluates, even if level is too low
logger.debug("Processing: %s", expensive_repr())

# ✅ %-formatting is lazy — only formatted if level allows
# But this is still wrong for f-strings:
logger.debug(f"Processing: {expensive_repr()}")   # Always evaluated!

# Correct:
logger.debug("Processing: %s", expensive_repr())   # Lazy!
```

### argparse with `--` separator

`argparse` supports `--` to separate positional args from flags. Use `parse_known_args()` if you need to pass through unknown args.

---

> [!question]- Interview Questions
>
> **Q: What's the difference between `datetime.utcnow()` and `datetime.now(timezone.utc)`?**
> A: `utcnow()` returns a naive datetime (no tzinfo). `now(timezone.utc)` returns an aware datetime with UTC timezone. Naive datetimes are ambiguous — always use aware datetimes for storage and conversion.
>
> **Q: Why should you compile regular expressions?**
> A: `re.compile()` pre-compiles the pattern into an internal bytecode, avoiding re-parsing the pattern on every call. For patterns used in a loop, this is significantly faster. It also makes the code cleaner by giving the pattern a name.
>
> **Q: What logging levels exist and when should you use each?**
> A: DEBUG (detailed diagnostics for developers), INFO (normal operation events), WARNING (something unexpected but not an error), ERROR (the application failed to do something), CRITICAL (the application cannot continue). Configure the minimum level per environment — DEBUG in dev, WARNING+ in production.

---

## Cross-Links

- [[Python/01_Foundations/08_File_IO_Serialization]] for `pathlib`, file I/O
- [[Python/01_Foundations/10_Testing_with_Pytest]] for testing with pytest
- [[Python/01_Foundations/05_Iterators_Generators_Decorators]] for `itertools`, `functools`
- [[Python/02_Core/13_Packaging_Distribution]] for `pyproject.toml` and entry points
