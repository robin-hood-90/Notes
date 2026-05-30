---
tags: [python, project, cli, typer, rich, httpx, pytest, pypi]
aliases: ["Project: CLI Tool", "Typer CLI", "Rich CLI", "CLI Tool"]
status: draft
updated: 2026-05-29
---

# Project: CLI Tool — Typer + Rich + httpx

> [!summary] Goal
> Build and publish a CLI tool using Typer, Rich, and httpx with entry points, testing, and PyPI distribution.

## Table of Contents

1. [Project Structure](#project-structure)
2. [CLI Definition](#cli-definition)
3. [Rich Output](#rich-output)
4. [API Client](#api-client)
5. [Testing](#testing)
6. [Packaging and Publishing](#packaging-and-publishing)

---

## Project Structure

```
mycli/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── client.py            # API client (httpx)
│   ├── display.py           # Rich output formatting
│   └── settings.py          # Config
├── tests/
│   ├── conftest.py
│   └── test_cli.py
├── pyproject.toml
└── README.md
```

---

## CLI Definition

```python
# src/main.py
import typer
from typing import Optional
from src.client import APIClient
from src.display import display_user, display_table

app = typer.Typer()

@app.command()
def get_user(
    user_id: int = typer.Argument(..., help="User ID to fetch"),
    format: str = typer.Option("table", "--format", "-f",
                               help="Output format: table, json"),
):
    """Fetch a user by ID and display details."""
    client = APIClient()
    user = client.fetch_user(user_id)
    if format == "json":
        typer.echo(user.model_dump_json(indent=2))
    else:
        display_user(user)

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Max results"),
):
    """Search for users."""
    client = APIClient()
    results = client.search_users(query, limit=limit)
    display_table(results)

@app.callback()
def main():
    """MyCLI — a demonstration CLI tool."""

if __name__ == "__main__":
    app()
```

---

## Rich Output

```python
# src/display.py
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()

def display_user(user):
    panel = Panel(
        f"[bold]{user.name}[/bold]\n"
        f"[cyan]Email:[/cyan] {user.email}\n"
        f"[green]Role:[/green] {user.role}\n"
        f"[yellow]ID:[/yellow] {user.id}",
        title=f"User {user.id}",
        border_style="blue",
    )
    console.print(panel)

def display_table(users):
    table = Table(title="Search Results")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Email", style="yellow")
    table.add_column("Role")

    for user in users:
        table.add_row(str(user.id), user.name, user.email, user.role)

    console.print(table)
```

---

## API Client

```python
# src/client.py
import httpx
from pydantic import BaseModel
from src.settings import settings

class User(BaseModel):
    id: int
    name: str
    email: str
    role: str

class APIClient:
    def __init__(self):
        self.client = httpx.Client(
            base_url=settings.api_base_url,
            timeout=30,
            headers={"User-Agent": "mycli/1.0"},
        )

    def fetch_user(self, user_id: int) -> User:
        resp = self.client.get(f"/users/{user_id}")
        resp.raise_for_status()
        return User.model_validate(resp.json())

    def search_users(self, query: str, limit: int = 10) -> list[User]:
        resp = self.client.get("/users", params={"q": query, "limit": limit})
        resp.raise_for_status()
        return [User.model_validate(u) for u in resp.json()]
```

---

## Testing

```python
# tests/test_cli.py
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()

def test_get_user_json():
    result = runner.invoke(app, ["get-user", "1", "--format", "json"])
    assert result.exit_code == 0
    assert '"id": 1' in result.stdout

def test_search():
    result = runner.invoke(app, ["search", "Alice"])
    assert result.exit_code == 0
    assert "Alice" in result.stdout

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
```

---

## Packaging and Publishing

```toml
[project]
name = "mycli"
version = "0.1.0"
description = "A demonstration CLI tool"
requires-python = ">=3.12"
dependencies = [
    "typer>=0.9",
    "rich>=13.0",
    "httpx>=0.25",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
]

[project.scripts]
mycli = "src.main:app"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1",
]
```

```bash
# Install
pip install -e .

# Run
mycli get-user 42
mycli search "Alice" --limit 20 --format json

# Build and publish
python -m build
twine check dist/*
twine upload dist/*

# Test
pytest tests/ -v --cov=src
```

---

## Cross-Links

- [[Python/02_Core/14_Common_Libraries_Reference]] for Typer/Rich reference
- [[Python/02_Core/13_Packaging_Distribution]] for publishing to PyPI
- [[Python/01_Foundations/10_Testing_with_Pytest]] for testing
- [[Python/02_Core/03_Network_Programming_HTTP]] for httpx reference
