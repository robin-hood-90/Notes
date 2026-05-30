---
tags: [python, core, libraries, typer, rich, pydantic, loguru, attrs, tqdm, pydantic-settings, dotenv]
aliases: ["Common Libraries", "Typer", "Rich", "Pydantic", "Loguru", "attrs", "tqdm", "python-dotenv"]
status: stable
updated: 2026-05-29
---

# Common Libraries Reference

> [!summary] Goal
> Quick reference for the most useful Python third-party libraries — Typer (CLI), Rich (terminal output), Pydantic (validation), Loguru (logging), attrs (classes), and more.

## Table of Contents

1. [Typer](#typer)
2. [Rich](#rich)
3. [Pydantic v2](#pydantic-v2)
4. [Pydantic-Settings](#pydantic-settings)
5. [Loguru](#loguru)
6. [attrs](#attrs)
7. [tqdm](#tqdm)
8. [python-dotenv](#python-dotenv)
9. [Pitfalls](#pitfalls)

---

## Typer

> [!info] Typer builds CLIs with type hints — like FastAPI for the command line

```python
import typer
from typing import Optional
from rich import print as rprint

app = typer.Typer()

@app.command()
def greet(
    name: str,
    age: int = typer.Option(30, help="Age of the person"),
    formal: bool = typer.Option(False, "--formal", "-f"),
):
    """Greet someone with optional formality."""
    if formal:
        rprint(f"[bold]Good day[/bold], {name}. Age: {age}")
    else:
        rprint(f"Hi [green]{name}[/green], you're {age}!")

@app.command()
def validate(file: str = typer.Argument(..., help="File to validate")):
    """Validate a file."""
    rprint(f"Validating [yellow]{file}[/yellow]...")

if __name__ == "__main__":
    app()

# Usage:
# python cli.py greet Alice --age 30 --formal
# python cli.py validate data.txt
```

### Autocomplete

```python
@app.command()
def search(
    term: str = typer.Argument(..., help="Search term", autocompletion=complete_search),
):
    pass

def complete_search(ctx, param, incomplete):
    # Return list of matching suggestions
    return [item for item in ["alpha", "beta", "gamma"] if item.startswith(incomplete)]
```

### Subcommands

```python
app = typer.Typer()
users_app = typer.Typer()
app.add_typer(users_app, name="users")

@users_app.command("list")
def list_users():
    """List all users."""

@users_app.command("create")
def create_user(name: str):
    """Create a new user."""

# python cli.py users list
# python cli.py users create Alice
```

---

## Rich

> [!info] Rich provides beautiful terminal output — tables, panels, progress bars, syntax highlighting, and tracebacks

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track, Progress
from rich.syntax import Syntax
from rich.traceback import install

console = Console()

# Basic
console.print("Hello [bold green]World[/bold green]!")
console.print("[red]Error:[/red] Something went wrong")

# Table
table = Table(title="Users")
table.add_column("Name", style="cyan")
table.add_column("Age", style="magenta")
table.add_column("Role", style="green")
table.add_row("Alice", "30", "Engineer")
table.add_row("Bob", "25", "Designer")
table.add_row("Carol", "35", "Manager")
console.print(table)

# Panel
panel = Panel(
    "This is the panel content\nWith multiple lines",
    title="Info",
    border_style="blue",
)
console.print(panel)

# Progress bar
for _ in track(range(100), description="Processing..."):
    do_work()

# With Progress as context manager
with Progress() as progress:
    task = progress.add_task("[green]Downloading...", total=100)
    for i in range(100):
        progress.update(task, advance=1)

# Syntax highlighting
code = '''
def hello():
    print("Hello, World!")
'''
syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
console.print(syntax)

# Rich tracebacks
install(show_locals=True)    # Beautiful tracebacks on unhandled exceptions
```

---

## Pydantic v2

> [!info] Pydantic v2 (Rust-based) provides runtime data validation with type hints
> Already covered in depth in C06 (FastAPI), but here's the standalone reference.

```python
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150, default=None)
    tags: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def name_must_be_meaningful(cls, v):
        if v.strip() == "":
            raise ValueError("Name cannot be blank")
        return v.strip()

    @model_validator(mode="after")
    def check_adult(self):
        if self.age is not None and self.age < 18:
            print(f"Warning: {self.name} is under 18")
        return self

# TypeAdapter — validate single values (not models)
from pydantic import TypeAdapter
int_list = TypeAdapter(list[int])
int_list.validate_python([1, 2, 3])        # [1, 2, 3]
int_list.validate_python(["a", "b"])        # ValidationError

# Serialisation
user = UserCreate(name="Alice", email="alice@test.com", age=30)
json_str = user.model_dump_json(indent=2)
dict_data = user.model_dump()

# Deserialisation
from_json = UserCreate.model_validate_json(json_str)
from_dict = UserCreate.model_validate(dict_data)
```

---

## Pydantic-Settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    redis_url: str = "redis://localhost:6379"
    secret_key: str
    allowed_hosts: list[str] = ["localhost"]

    @property
    def db_url_async(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")

settings = Settings()
# Loads from .env file OR environment variables
# .env file is optional — if set, env vars take precedence
```

```env
# .env
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=changeme-in-production
DEBUG=True
```

---

## Loguru

> [!info] Loguru is a zero-config logging library that replaces the stdlib `logging` module

```python
from loguru import logger

# Zero config — just import and use
logger.debug("This is a debug message")
logger.info("Server started on port {}", 8080)
logger.warning("Disk space low: {} GB", free_space)
logger.error("Failed to connect: {}", err)
logger.critical("System shutting down")

# Configure output
logger.remove()                           # Remove default handler
logger.add("app.log", rotation="10 MB", retention="30 days", level="DEBUG")
logger.add(sys.stderr, level="WARNING")
logger.add("errors.log", level="ERROR", backtrace=True, diagnose=True)

# Structured logging
logger.info("User {} logged in from {}", user_id, ip_address)

# Exception catch
@logger.catch
def risky_function():
    1 / 0                                # Automatically logged

# Context
with logger.contextualize(request_id=request_id):
    logger.info("Processing request")     # Includes request_id

# Bind to logger for persistent context
logger = logger.bind(service="myapp")
logger.info("Service started")            # Includes service=myapp
```

---

## attrs

> [!info] `attrs` is the library that inspired `dataclasses` — with more features

```python
import attr

@attr.define
class Point:
    x: float
    y: float

    @x.validator
    def check_x(self, attribute, value):
        if value < 0:
            raise ValueError("x must be non-negative")

@attr.define
class Rectangle:
    width: float = attr.field(validator=attr.validators.gt(0))
    height: float = attr.field(validator=attr.validators.gt(0))

    @property
    def area(self) -> float:
        return self.width * self.height

p = Point(1.0, 2.0)
print(p)                    # Point(x=1.0, y=2.0)
p == Point(1.0, 2.0)       # True

# Frozen (immutable)
@attr.frozen
class Config:
    name: str
    version: int

# Slots (like __slots__)
@attr.define(slots=True)
class FastPoint:
    x: float
    y: float
```

### attrs vs dataclasses

| Feature | `dataclasses` | `attrs` |
|---------|:-------------:|:-------:|
| Built-in (no dependency) | ✅ | ❌ |
| Validators | Manual (`__post_init__`) | Built-in |
| Frozen | `frozen=True` | `@attr.frozen` |
| Slots | Manual `__slots__` | `slots=True` |
| Converters | No | `converter=int` |
| Equals/hash customization | Limited | `eq=False`, `order=False` |

---

## tqdm

```python
from tqdm import tqdm, trange
import time

# Basic
for i in tqdm(range(100)):
    time.sleep(0.01)

# trange = tqdm(range(...))
for i in trange(100):
    time.sleep(0.01)

# With description
for i in tqdm(range(100), desc="Processing"):
    time.sleep(0.01)

# Manual
pbar = tqdm(total=100)
for i in range(100):
    pbar.update(1)
    pbar.set_description(f"Item {i}")
pbar.close()

# Nested
for i in tqdm(range(10), desc="Outer"):
    for j in tqdm(range(100), desc="Inner", leave=False):
        time.sleep(0.001)

# File download example
import requests
response = requests.get(url, stream=True)
total = int(response.headers.get("content-length", 0))
with tqdm(total=total, unit="B", unit_scale=True) as pbar:
    for chunk in response.iter_content(chunk_size=8192):
        pbar.update(len(chunk))
```

---

## python-dotenv

```python
# Load .env files for local development
from dotenv import load_dotenv
import os

load_dotenv()                                      # Load .env
load_dotenv(".env.local", override=True)            # Override with local
load_dotenv(dotenv_path=".env.production")          # Specific file

# With pydantic-settings (recommended), this is built-in
# For standalone use:
database_url = os.getenv("DATABASE_URL")
```

---

## Pitfalls

### Typer: forgetting `if __name__ == "__main__"`

```python
app = typer.Typer()
# ...
if __name__ == "__main__":
    app()                    # ✅ Required
```

### Rich: not using context managers for Progress

```python
# ❌ Manual — easy to forget close()
pbar = Progress()
pbar.add_task(...)
# pbar.stop() not called

# ✅ Context manager
with Progress() as pbar:
    ...
```

### Loguru: thread safety

Loguru is thread-safe by default. But if you use `logger.add()` with custom sinks, ensure they're thread-safe too.

### Pydantic: `field_validator` order

Validators run in the order they're defined. Use `mode="before"` for pre-validation transforms.

### tqdm: nested progress bars in Jupyter

Use `from tqdm.notebook import tqdm` for Jupyter notebook support.

---

> [!question]- Interview Questions
>
> **Q: How does Typer compare to argparse?**
> A: Typer uses type hints to auto-generate CLI arguments and options, has built-in help and autocomplete, supports subcommands, and integrates with Rich for beautiful output. argparse requires manual definition of every argument and subcommand. Typer is the modern choice for Python CLIs.
>
> **Q: What's the difference between pydantic-settings and python-dotenv?**
> A: python-dotenv only loads `.env` files into `os.environ`. pydantic-settings loads from `.env` files AND environment variables, validates types, and provides IDE autocomplete via a `BaseSettings` class. pydantic-settings is the recommended approach.
>
> **Q: When would you use attrs over dataclasses?**
> A: Use attrs when you need validators, converters, frozen-by-default, `__slots__` generation, or more flexible equality/hash configuration. Use dataclasses when you want zero dependencies and simpler configuration. For most cases, dataclasses are sufficient.

---

## Cross-Links

- [[Python/02_Core/06_Web_Frameworks_FastAPI]] for Pydantic in FastAPI
- [[Python/05_Projects/03_CLI_Tool_Typer_Rich]] for a complete CLI project
- [[Python/04_Playbooks/03_Production_Readiness]] for Loguru and settings in production
- [[Python/02_Core/13_Packaging_Distribution]] for publishing CLI tools
