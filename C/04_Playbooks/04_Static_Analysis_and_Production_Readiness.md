---
tags: [c, playbook, static-analysis, cppcheck, clang-tidy, production-readiness, code-quality]
aliases: ["Static Analysis", "Production Readiness", "cppcheck", "clang-tidy", "Code Quality", "CI Pipeline"]
status: stable
updated: 2026-05-09
---

# Playbook: Static Analysis and Production Readiness

> [!summary] Goal
> Ensure C code is production-ready through static analysis, coding standards, and a comprehensive checklist. Catch bugs at compile time or in CI — before they reach production.

## Table of Contents

1. [Static Analysis Tools](#static-analysis-tools)
2. [Coding Standards](#coding-standards)
3. [Production Readiness Checklist](#production-readiness-checklist)
4. [CI Pipeline](#ci-pipeline)
5. [Pitfalls](#pitfalls)

---

## Static Analysis Tools

> [!info] Static analysis
> Static analysis examines source code without running it. It can find bugs that compilers and runtime tools miss: resource leaks, dead code, logic errors, security vulnerabilities, and violations of coding standards.

### cppcheck

```bash
# Install
sudo apt install cppcheck

# Basic usage
cppcheck --enable=all --suppress=missingIncludeSystem program.c

# Project-wide analysis
cppcheck --enable=all --suppress=missingIncludeSystem \
    --inconclusive --std=c11 \
    -I include/ src/

# Output as XML (for CI)
cppcheck --enable=all --xml program.c 2> cppcheck.xml

# Common checks enabled with --enable=all:
# style, warning, performance, portability, information, missingInclude
```

### clang-tidy

```bash
# Run clang-tidy on a file
clang-tidy program.c -- -std=c11

# With custom checks
clang-tidy program.c -checks='-*,clang-analyzer-*,bugprone-*,performance-*,readability-*' \
    -- -std=c11

# All files in a project
find src/ -name '*.c' -exec clang-tidy {} -- -I include/ \;

# Common check groups:
# clang-analyzer-*:   Deep path-sensitive analysis (null deref, memory leaks)
# bugprone-*:         Suspicious patterns (signed char, integer overflow)
# performance-*:      Performance issues (unnecessary copies)
# readability-*:      Code style issues
# modernize-*:        C11/C17 modernization suggestions
```

### GCC -fanalyzer (GCC 10+)

```bash
# GCC's built-in static analyzer
gcc -fanalyzer -O2 -g program.c -o program
# Reports: double-free, use-after-free, null dereferences, file descriptor leaks
```

### Splint (older but thorough)

```bash
sudo apt install splint
splint +bounds +bufferoverflow high program.c
```

---

## Coding Standards

### Naming conventions

```c
// Constants
#define MAX_BUFFER_SIZE 4096
#define DEFAULT_PORT 8080

// Types
typedef struct { ... } UserConfig;
typedef enum { LOG_ERROR, LOG_WARN, LOG_INFO } LogLevel;

// Functions (snake_case)
int user_config_load(UserConfig *config, const char *path);
static int parse_line(const char *line);

// Variables (snake_case)
int active_connections = 0;
static int internal_counter;

// Globals (use sparingly — prefix with g_)
int g_debug_level = 0;
```

### Function contracts

```c
/**
 * @brief Load user configuration from a file.
 *
 * @param config  [out] Initialized on success, unchanged on error
 * @param path    [in]  Path to config file
 * @return 0 on success, -1 on error (errno set)
 *
 * Memory ownership: caller must call user_config_free(config) on success
 */
int user_config_load(UserConfig *config, const char *path);
```

---

## Production Readiness Checklist

### Compilation

- [ ] Compiles cleanly with `-Wall -Wextra -Wpedantic -Werror`
- [ ] No warnings with `-Wshadow -Wstrict-prototypes -Wconversion`
- [ ] Passes `cppcheck --enable=all` with no errors
- [ ] Passes `clang-tidy` with selected checks
- [ ] Passes GCC `-fanalyzer` (at least O2)
- [ ] Runs with ASan, UBSan, Valgrind, all clean

### Testing

- [ ] Unit tests cover: normal paths, error paths, edge cases
- [ ] Static analysis passes before each commit
- [ ] Sanitizers run in CI on every PR
- [ ] Valgrind clean for memory tests
- [ ] Coverage report shows >80% branch coverage

### Memory Safety

- [ ] All `malloc`/`calloc` have matching `free`
- [ ] All `fopen` have matching `fclose`
- [ ] All `mmap` have matching `munmap`
- [ ] Resources freed on every error path (`goto cleanup` pattern)
- [ ] No unbounded string functions (`sprintf`, `strcpy`, `gets`)
- [ ] Array bounds checked before access
- [ ] Pointer validity checked before dereference

### Logic and Design

- [ ] Error paths tested (malloc failure, file open failure, etc.)
- [ ] No magic numbers (use `#define` or `enum`)
- [ ] Buffer sizes are `sizeof`-based, not hardcoded
- [ ] Thread-safe or documented as not
- [ ] Platform-specific code isolated behind `#ifdef`
- [ ] API/ABI versioned (for shared libraries)

### Documentation and Review

- [ ] All public functions have contracts (param, return, ownership)
- [ ] All `static` functions have brief comments
- [ ] Non-obvious code has inline comments explaining WHY
- [ ] Complex algorithms have references
- [ ] Doxygen or equivalent documentation generated

---

## CI Pipeline

```yaml
# .github/workflows/c-ci.yml — GitHub Actions example
name: C CI
on: [push, pull_request]
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: gcc -Wall -Wextra -Wpedantic -Werror -O2 -g program.c -o program
      - name: Static analysis
        run: cppcheck --enable=all --suppress=missingIncludeSystem .
      - name: ASan
        run: |
          gcc -g -O1 -fsanitize=address -fno-omit-frame-pointer program.c -o program-asan
          ./program-asan
      - name: UBSan
        run: |
          gcc -g -O1 -fsanitize=undefined program.c -o program-ubsan
          ./program-ubsan
      - name: Valgrind
        run: |
          gcc -g -O0 program.c -o program-debug
          valgrind --leak-check=full --error-exitcode=1 ./program-debug
```

---

## Pitfalls

### Relying solely on tools

Static analysis and sanitizers catch common bugs but miss logic errors. A program can be memory-safe and still produce wrong results. Combine with unit tests and code review.

### Fixing warnings without understanding them

Don't blindly add casts to silence warnings. `-Wconversion` warns about implicit type changes — casting doesn't fix the potential overflow, it just hides it. Understand WHY the warning exists before fixing it.

### False positives in static analysis

`cppcheck` and `clang-tidy` can report false positives. Instead of disabling the check globally, use inline suppression with a comment explaining why:

```c
// cppcheck-suppress nullPointerRedundantCheck
// We check for NULL at the caller
```

---

## Cross-Links

- [[C/04_Playbooks/01_Debug_Segfaults_and_Invalid_Memory_Access]] for runtime debugging
- [[C/04_Playbooks/02_Use_Sanitizers_ASan_UBSan_TSan]] for sanitizer usage
- [[C/04_Playbooks/03_Valgrind_Leaks_and_Heap_Corruption]] for memory profiling
- [[C/02_Core/08_Build_Systems_and_Makefiles]] for build system integration
- [[C/02_Core/06_Undefined_Behavior_and_Memory_Safety]] for UB avoidance
