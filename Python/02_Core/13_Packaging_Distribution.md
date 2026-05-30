---
tags: [python, core, packaging, pyproject, setuptools, wheel, twine, cibuildwheel, mypyc, pyinstaller]
aliases: ["Packaging", "Distribution", "pyproject.toml", "setuptools", "PyPI", "Wheel", "C Extensions"]
status: stable
updated: 2026-05-29
---

# Packaging and Distribution

> [!summary] Goal
> Master Python packaging — `pyproject.toml`, setuptools, entry points, building wheels, publishing to PyPI, C extensions, mypyc compilation, and standalone executables.

## Table of Contents

1. [pyproject.toml](#pyprojecttoml)
2. [setuptools](#setuptools)
3. [Entry Points](#entry-points)
4. [Building and Publishing](#building-and-publishing)
5. [C Extensions](#c-extensions)
6. [mypyc](#mypyc)
7. [Standalone Executables](#standalone-executables)
8. [Pitfalls](#pitfalls)

---

## pyproject.toml

> [!info] `pyproject.toml` (PEP 517/518/621) is the modern Python packaging standard
> It replaces `setup.py`, `setup.cfg`, and `requirements.txt` for project metadata.

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "myproject"
version = "0.1.0"
description = "A useful Python project"
readme = "README.md"
requires-python = ">=3.12"
license = {text = "MIT"}
keywords = ["example", "python"]

authors = [
    {name = "Alice", email = "alice@example.com"},
]

dependencies = [
    "requests>=2.31",
    "click>=8.0",
    "rich>=13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
    "mypy>=1.0",
]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]

[project.urls]
homepage = "https://github.com/user/myproject"
documentation = "https://myproject.readthedocs.io"
repository = "https://github.com/user/myproject"

[tool.setuptools.packages.find]
where = ["src"]
include = ["myproject*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py312"
```

---

## setuptools

```python
# setup.py (legacy, but still needed for C extensions)
from setuptools import setup, find_packages

setup(
    name="myproject",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31",
    ],
    extras_require={
        "dev": ["pytest", "ruff"],
    },
    python_requires=">=3.12",
)
```

```bash
# Install in development mode
pip install -e .

# Build
python -m build                    # Build wheel + sdist

# Or use the modern way:
pip install build
python -m build                     # Produces dist/*.whl and dist/*.tar.gz
```

---

## Entry Points

> [!info] Entry points make your package installable as a CLI command
> Defined in `pyproject.toml` under `[project.scripts]`.

```toml
[project.scripts]
myapp = "myproject.cli:main"
```

```python
# myproject/cli.py
def main():
    """CLI entry point."""
    import sys
    print(f"Hello from {sys.argv[1:]}")

# After pip install -e ., `myapp` is available on PATH
```

### Other entry points

```toml
[project.scripts]
myapp = "myproject.cli:main"

[project.gui-scripts]
mygui = "myproject.gui:launch"

[project.entry-points."myproject.plugins"]
plugin_a = "myproject_plugin_a:register"
```

---

## Building and Publishing

```bash
# Install build tools
pip install build twine

# Build
python -m build

# Check for issues
twine check dist/*

# Publish to Test PyPI (for testing)
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Publish to PyPI
twine upload dist/*

# Versioning — bump before build
# Manual: change version in pyproject.toml
# Or use: bumpver, hatch, or poetry
```

### Versioning best practices

- Follow [SemVer](https://semver.org/) (`MAJOR.MINOR.PATCH`)
- Pre-release labels: `1.0.0a1` (alpha), `1.0.0b1` (beta), `1.0.0rc1` (release candidate)
- Use `calver` (YYYY.MINOR.PATCH) for continuous releases

---

## C Extensions

```python
from setuptools import Extension, setup

# C extension — calls C code from Python
module = Extension(
    "myproject._fastmath",         # Module name
    sources=["src/_fastmath.c"],   # C source files
    include_dirs=["/usr/include"], # Header directories
    libraries=["m"],               # Link libraries
)

setup(
    name="myproject",
    version="0.1.0",
    ext_modules=[module],
)
```

```c
// src/_fastmath.c
#include <Python.h>

static PyObject* fast_add(PyObject* self, PyObject* args) {
    double a, b;
    if (!PyArg_ParseTuple(args, "dd", &a, &b))
        return NULL;
    return PyFloat_FromDouble(a + b);
}

static PyMethodDef FastMathMethods[] = {
    {"fast_add", fast_add, METH_VARARGS, "Add two numbers quickly"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef fastmath_module = {
    PyModuleDef_HEAD_INIT,
    "_fastmath",
    NULL,
    -1,
    FastMathMethods
};

PyMODINIT_FUNC PyInit__fastmath(void) {
    return PyModule_Create(&fastmath_module);
}
```

```python
# Using the extension
import myproject._fastmath
result = myproject._fastmath.fast_add(3.14, 2.71)   # 5.85
```

### cibuildwheel — build for all platforms in CI

```yaml
# .github/workflows/build.yml
- name: Build wheels
  uses: pypa/cibuildwheel@v2.16
```

---

## mypyc

> [!info] `mypyc` compiles Python type-annotated code to C extensions
> It's the easiest way to speed up Python — just add type hints and compile.

```python
# mymath.py — add type hints
def add(a: int, b: int) -> int:
    return a + b

def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

```bash
# Compile
mypyc mymath.py

# Result: mymath.cpython-312-x86_64-linux-gnu.so
# Drop-in replacement for mymath.py — 2-10× faster

# In pyproject.toml
[tool.mypyc]
packages = ["myproject", "myproject._fastmath"]
```

---

## Standalone Executables

### PyInstaller

```bash
# Single-file executable
pip install pyinstaller
pyinstaller --onefile myapp.py
# Result: dist/myapp (single binary, all dependencies bundled)

# With custom name, icon, no console window (for GUI apps)
pyinstaller --onefile --name MyApp --windowed --icon=app.ico myapp.py

# For complex apps, use .spec file
pyinstaller myapp.spec
```

### Nuitka (alternative)

```bash
pip install nuitka
nuitka --standalone --onefile myapp.py
# Compiles Python to C++, then to a binary
# Faster startup than PyInstaller, larger binary
```

---

## Pitfalls

### Forgetting `.gitignore` for build artifacts

```gitignore
# Add to .gitignore
dist/
*.egg-info/
__pycache__/
*.so
*.pyd
```

### Not pinning build dependencies

```toml
[build-system]
requires = ["setuptools>=68.0,<69.0"]    # Pin major version
```

### Publishing with stale files

Always run `python -m build` with a clean `dist/` directory. Old files in `dist/` will cause version conflicts.

### Forgetting `__init__.py` in subpackages

Without `__init__.py`, packages may not be found by setuptools' `find_packages()`.

### Not testing the built wheel

```bash
# Always test before publishing
pip install dist/myproject-0.1.0-py3-none-any.whl
python -c "import myproject; myproject.main()"
```

---

> [!question]- Interview Questions
>
> **Q: What's the difference between `setup.py` and `pyproject.toml`?**
> A: `pyproject.toml` (PEP 621) is the modern standard. `setup.py` is legacy but still needed for C extensions and dynamic metadata. `pyproject.toml` declares static metadata declaratively; `setup.py` runs arbitrary Python code.
>
> **Q: How do entry points work?**
> A: Entry points are defined in `pyproject.toml` under `[project.scripts]`. During `pip install`, setuptools generates a small wrapper script in the `bin/` directory that imports and calls the specified function. This makes your package installable as a CLI command.
>
> **Q: What is `mypyc` and when would you use it?**
> A: `mypyc` compiles type-annotated Python to C extensions using mypy's type information. It can speed up CPU-bound Python code by 2-10× with minimal effort — just add type hints. Use it for performance-critical modules without writing C manually.

---

## Cross-Links

- [[Python/01_Foundations/06_Modules_Packages_Virtual_Envs]] for module basics
- [[Python/03_Advanced/04_C_Extensions_FFI]] for C extensions and pybind11
- [[Python/04_Playbooks/03_Production_Readiness]] for production deployment
- [[Python/05_Projects/03_CLI_Tool_Typer_Rich]] for a complete CLI project with entry points
