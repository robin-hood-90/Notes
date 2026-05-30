---
tags: [python, foundations, testing, pytest, fixtures, mocking, coverage]
aliases: ["Testing with Pytest", "pytest", "Fixtures", "Mocking", "Coverage"]
status: stable
updated: 2026-05-29
---

# Testing with Pytest

> [!summary] Goal
> Master pytest — the standard Python testing framework: fixtures, parameterization, mocking, `pytest-asyncio`, `factory_boy`, `Faker`, `vcrpy`, and coverage.

## Table of Contents

1. [Pytest Basics](#pytest-basics)
2. [Fixtures](#fixtures)
3. [Parameterized Tests](#parameterized-tests)
4. [Mocking](#mocking)
5. [pytest-asyncio](#pytest-asyncio)
6. [factory_boy and Faker](#factory_boy-and-faker)
7. [vcrpy and HTTP Mocking](#vcrpy-and-http-mocking)
8. [Coverage](#coverage)
9. [conftest.py](#conftestpy)
10. [Pitfalls](#pitfalls)

---

## Pytest Basics

```python
# test_math.py

def test_add():                      # Functions starting with test_ are collected
    assert 1 + 1 == 2

def test_string():
    result = "hello".upper()
    expected = "HELLO"
    assert result == expected

def test_with_approx():
    import math
    assert math.isclose(0.1 + 0.2, 0.3)

# Running:
# pytest                          # auto-discovery
# pytest test_math.py             # specific file
# pytest -v                       # verbose
# pytest -k "add or string"       # filter by test name
# pytest -x                       # stop on first failure
# pytest --pdb                    # drop into debugger on failure
```

### Test discovery

```bash
# pytest discovers tests matching:
#   test_*.py or *_test.py files
#   test_ prefixed functions (or Test* classes)
#   In current directory and subdirectories
```

---

## Fixtures

> [!info] Fixtures provide reusable test dependencies
> They run before the test; `yield` splits setup and teardown. Fixtures can request other fixtures.

```python
import pytest

# A fixture that returns data
@pytest.fixture
def sample_data():
    return {"name": "Alice", "scores": [90, 85, 92]}

def test_average(sample_data):       # pytest injects the fixture
    scores = sample_data["scores"]
    assert sum(scores) / len(scores) == 89.0

# Fixture with teardown (using yield)
@pytest.fixture
def temp_file():
    from pathlib import Path
    path = Path("temp_test.txt")
    path.write_text("test data")
    yield path
    path.unlink()                    # Teardown — always runs

def test_read(temp_file):
    assert temp_file.read_text() == "test data"

# Fixture scope
@pytest.fixture(scope="session")     # Once per test session
def db_connection(): ...

@pytest.fixture(scope="module")      # Once per module
def db_session(): ...

@pytest.fixture(scope="class")       # Once per test class
def user_data(): ...

@pytest.fixture(scope="function")    # Default — once per test
def fresh_data(): ...
```

### Built-in fixtures

| Fixture | Purpose |
|---------|---------|
| `tmp_path` | Temporary directory (`Path` object, per-test unique) |
| `tmp_path_factory` | Create temp dirs with session scope |
| `capsys` | Capture stdout/stderr |
| `monkeypatch` | Modify objects/imports temporarily |
| `caplog` | Capture log output |

```python
def test_write_file(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("content")
    assert p.read_text() == "content"

def test_stdout(capsys):
    print("hello")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"

def test_monkeypatch(monkeypatch):
    import os
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    assert os.environ["DATABASE_URL"] == "sqlite:///test.db"
```

---

## Parameterized Tests

```python
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert a + b == expected

# Multiple parameter sets — Cartesian product
@pytest.mark.parametrize("x", [0, 1])
@pytest.mark.parametrize("y", ["a", "b"])
def test_cartesian(x, y):
    pass  # runs: (0,a), (0,b), (1,a), (1,b)

# Fixture with parametrize
@pytest.fixture(params=["json", "yaml"])
def serializer(request):
    if request.param == "json":
        import json; return json.dumps
    else:
        import yaml; return yaml.dump

def test_serialize(serializer):
    result = serializer({"key": "value"})
    assert result
```

---

## Mocking

```python
from unittest.mock import Mock, patch

# Manual mock
mock_service = Mock()
mock_service.get_user.return_value = {"name": "Alice"}
mock_service.get_user.side_effect = ValueError("Not found")  # or raise

# patch — replace objects during test
def get_user_email(user_id):
    import requests
    resp = requests.get(f"https://api.example.com/users/{user_id}")
    return resp.json()["email"]

def test_get_user_email():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"email": "alice@test.com"}
        result = get_user_email(42)
        assert result == "alice@test.com"
        mock_get.assert_called_once_with("https://api.example.com/users/42")

# patch as decorator
@patch("requests.get")
def test_with_decorator(mock_get):
    mock_get.return_value.json.return_value = {"email": "bob@test.com"}
    assert get_user_email(1) == "bob@test.com"

# pytest-mock plugin
def test_with_mocker(mocker):
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"email": "carol@test.com"}
    assert get_user_email(3) == "carol@test.com"
```

---

## pytest-asyncio

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await fetch_data()
    assert result is not None

# Async fixture
@pytest.fixture
async def db_session():
    session = await create_session()
    yield session
    await session.close()

@pytest.mark.asyncio
async def test_db_query(db_session):
    result = await db_session.query("SELECT 1")
    assert result == 1
```

---

## factory_boy and Faker

```python
# pip install factory_boy faker

from factory import Factory, Faker, SubFactory, Sequence
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str
    is_active: bool

class UserFactory(Factory):
    class Meta:
        model = User

    id = Sequence(lambda n: n + 1)
    name = Faker("name")              # Random name
    email = Faker("email")            # Random email
    is_active = True

# Usage
user = UserFactory()                  # Random user
user2 = UserFactory(is_active=False)  # Override specific field
users = UserFactory.build_batch(5)    # Build 5, don't save
users = UserFactory.create_batch(5)   # Build 5, calls create
```

---

## vcrpy and HTTP Mocking

```python
# pip install vcrpy
import vcr

@vcr.use_cassette("fixtures/vcr_cassettes/github_api.yaml")
def test_github_api():
    import requests
    response = requests.get("https://api.github.com")
    assert response.status_code == 200

# First run: records real HTTP → saves to cassette file
# Subsequent runs: replays from cassette (fast, no network)

# pytest-recording (wrapper)
@pytest.mark.vcr
def test_with_recording():
    response = requests.get("https://api.github.com")
    ...

# responses library — mock HTTP without recording
import responses

@responses.activate
def test_with_responses():
    responses.get("https://api.example.com/user", json={"id": 1})
    resp = requests.get("https://api.example.com/user")
    assert resp.json()["id"] == 1
```

---

## Coverage

```bash
# pip install pytest-cov

# Run with coverage
pytest --cov=src                       # measure coverage for src/
pytest --cov=src --cov-report=term     # terminal report
pytest --cov=src --cov-report=html     # HTML report → htmlcov/
pytest --cov=src --cov-report=xml      # XML for CI

# Configuration in pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

```python
# pytest.ini / pyproject.toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
```

---

## conftest.py

> [!info] `conftest.py` shares fixtures and hooks across test files
> Place it in the test directory root. pytest automatically loads fixtures defined in `conftest.py` for all tests in that directory and subdirectories.

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / "data"

@pytest.fixture
def db_url(tmp_path_factory):
    path = tmp_path_factory.mktemp("db") / "test.db"
    return f"sqlite:///{path}"

# Command-line options
def pytest_addoption(parser):
    parser.addoption("--integration", action="store_true",
                     help="Run integration tests")

def pytest_collection_modifyitems(config, items):
    if not config.getoption("--integration"):
        skip_integration = pytest.mark.skip(reason="Need --integration flag")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
```

---

## Pitfalls

### Forgetting `return_value` vs `side_effect`

```python
mock = Mock()
mock.return_value = 42       # Always returns 42
mock.side_effect = [1, 2]    # If set, overrides return_value

# side_effect as an iterator
mock.side_effect = [1, 2, 3]
mock()  # 1
mock()  # 2
mock()  # 3
```

### Fixtures that mutate shared state

```python
@pytest.fixture
def shared_list():           # ❌ Same list for every test!
    return []

@pytest.fixture
def fresh_list():            # ✅ New list each time
    return []
```

### Mocking the wrong thing

```python
# ❌ Mock the module where it's USED, not where it's FROM
from myapp import service
import requests

# WRONG:
@patch("requests.get")         # patches requests.get globally

# RIGHT:
@patch("myapp.service.requests.get")  # patches the reference in the module under test
```

### Not setting `asyncio_mode` for pytest-asyncio

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"          # Auto-detect async tests
```

---

> [!question]- Interview Questions
>
> **Q: What's the difference between `Mock` and `MagicMock`?**
> A: `MagicMock` is a `Mock` that pre-defines all dunder methods (`__len__`, `__iter__`, `__str__`, etc.) with sensible defaults. Use `Mock` for regular objects and `MagicMock` when you need dunder method support (iterable, context manager, etc.).
>
> **Q: How does `conftest.py` scope work?**
> A: `conftest.py` is directory-scoped. A fixture defined in `tests/conftest.py` is available to all test files in `tests/` and subdirectories. Deeper `conftest.py` files override fixtures from parent directories. This lets you scope fixtures to specific test subsets.
>
> **Q: How do you test async code with pytest?**
> A: Use `pytest-asyncio`. Mark tests with `@pytest.mark.asyncio` and define async fixtures. Configure with `asyncio_mode = "auto"` in `pyproject.toml`. Use `mocker` or `@patch` with `AsyncMock` for async mocking.

---

## Cross-Links

- [[Python/01_Foundations/07_Error_Handling_Context_Managers]] for testing exceptions
- [[Python/01_Foundations/06_Modules_Packages_Virtual_Envs]] for test package structure
- [[Python/02_Core/06_Web_Frameworks_FastAPI]] for FastAPI testing with `httpx`
- [[Python/04_Playbooks/03_Production_Readiness]] for CI/CD testing
