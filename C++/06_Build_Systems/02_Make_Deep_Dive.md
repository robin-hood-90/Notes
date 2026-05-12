---
tags: [cpp, build-systems, make, makefile, gnu-make, cpp-compilation, build-automation]
aliases: ["Make C++", "C++ Makefile", "GNU Make C++", "C++ Build Automation"]
status: stable
updated: 2026-05-09
---

# Make Deep Dive for C++

> [!summary] Goal
> Master GNU Make for C++ projects — C++ compiler flags, C++ standard management, header dependency auto-generation, and C++-specific Makefile patterns.

## Table of Contents

1. [C++ Compiler Flags](#c-compiler-flags)
2. [C++ Standard Selection](#c-standard-selection)
3. [Header Dependency Auto-Generation](#header-dependency-auto-generation)
4. [C++ Makefile Templates](#c-makefile-templates)
5. [Pitfalls](#pitfalls)

---

## C++ Compiler Flags

> [!info] C++ compilation flags
> C++ compilation differs from C in several key flag areas: C++ standard version, exception handling, RTTI, name mangling, and C++ specific warnings. Always use `g++` (not `gcc`) for C++ files.

```makefile
# C++ compiler
CXX       = g++
CXXFLAGS  = -std=c++20 -Wall -Wextra -Wpedantic -Werror
CXXFLAGS  += -O2 -g
LDFLAGS   = -lpthread

# C++ specific warnings (GCC/Clang)
CXXFLAGS += -Wnon-virtual-dtor -Wold-style-cast -Woverloaded-virtual
CXXFLAGS += -Wsign-promo -Wnoexcept -Wzero-as-null-pointer-constant
CXXFLAGS += -Wctor-dtor-privacy -Wreorder -Wno-undefined-var-template
```

### Common C++ flags

| Flag | Purpose |
|------|---------|
| `-std=c++20` | Use C++20 standard |
| `-fexceptions` | Enable exceptions (default on) |
| `-fno-rtti` | Disable RTTI (smaller binary, no dynamic_cast) |
| `-fno-exceptions` | Disable exceptions (game/embedded) |
| `-Wnon-virtual-dtor` | Warn about classes with virtual functions but non-virtual dtor |
| `-Woverloaded-virtual` | Warn if a virtual function is hidden by an overload |
| `-Wold-style-cast` | Warn about C-style casts (`(int)x`) |
| `-Wzero-as-null-pointer-constant` | Warn about `NULL` instead of `nullptr` |
| `-Wnoexcept` | Warn about functions that can be noexcept but aren't |

---

## C++ Standard Selection

```makefile
# Method 1: Set the standard globally
CXXFLAGS += -std=c++20

# Method 2: Detect and set based on compiler version
GCC_MAJOR := $(shell $(CXX) -dumpversion | cut -f1 -d.)
GCC_MINOR := $(shell $(CXX) -dumpversion | cut -f2 -d.)

ifneq ($(findstring clang,$(shell $(CXX) --version 2>/dev/null)),)
    # Clang
    CXXFLAGS += -std=c++20
else ifeq ($(shell test $(GCC_MAJOR) -ge 11; echo $$?),0)
    # GCC 11+ supports C++20
    CXXFLAGS += -std=c++20
else ifeq ($(shell test $(GCC_MAJOR) -ge 8; echo $$?),0)
    # GCC 8+ supports C++17
    CXXFLAGS += -std=c++17
else
    CXXFLAGS += -std=c++14
endif
```

---

## Header Dependency Auto-Generation

> [!info] C++ header dependencies
> C++ headers are more complex than C — templates, inline functions, and the STL are all in headers. The `-M` family of flags generates `.d` files that Make reads as dependency rules.

```makefile
# Generate dependency files alongside .o files
CXXFLAGS += -MD -MP

# -MD: generate .d file with dependency info
# -MP: create phony targets for each header (avoids errors when headers are removed)

# Include generated dependency files
-include $(OBJS:.o=.d)
```

### Full C++ Makefile with auto-deps

```makefile
CXX       = g++
CXXFLAGS  = -std=c++20 -Wall -Wextra -Wpedantic -Wnon-virtual-dtor
CXXFLAGS  += -O2 -g -MD -MP
LDFLAGS   = -lpthread

SRC_DIR   = src
OBJ_DIR   = obj
SRCS      = $(wildcard $(SRC_DIR)/*.cpp)
OBJS      = $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(SRCS))
TARGET    = myapp

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp | $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(OBJ_DIR):
	mkdir -p $@

clean:
	rm -rf $(OBJ_DIR) $(TARGET)

-include $(wildcard $(OBJ_DIR)/*.d)
```

---

## C++ Makefile Templates

### Minimal C++ project Makefile

```makefile
CXX      = g++
CXXFLAGS = -std=c++20 -Wall -Wextra -O2 -g
LDFLAGS  = -lpthread
TARGET   = myapp

SRCS := $(wildcard *.cpp)
OBJS := $(SRCS:.cpp=.o)

$(TARGET): $(OBJS)
	$(CXX) -o $@ $^ $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

.PHONY: clean
clean:
	rm -f $(OBJS) $(TARGET)
```

### Library + executable (non-recursive)

```makefile
CXX       = g++
CXXFLAGS  = -std=c++20 -Wall -Wextra -O2 -g -fPIC -MD -MP
ARFLAGS   = rcs

LIB_DIR   = lib
SRC_DIR   = src
TEST_DIR  = tests

LIB_SRCS  = $(wildcard $(LIB_DIR)/*.cpp)
LIB_OBJS  = $(LIB_SRCS:.cpp=.o)
LIB_TARGET = libapp.a

APP_SRCS  = $(wildcard $(SRC_DIR)/*.cpp)
APP_OBJS  = $(APP_SRCS:.cpp=.o)
APP_TARGET = myapp

TEST_SRCS = $(wildcard $(TEST_DIR)/*.cpp)
TEST_OBJS = $(TEST_SRCS:.cpp=.o)
TEST_TARGET = test_app

.PHONY: all clean test

all: $(LIB_TARGET) $(APP_TARGET)

$(LIB_TARGET): $(LIB_OBJS)
	$(AR) $(ARFLAGS) $@ $^

$(APP_TARGET): $(APP_OBJS) $(LIB_TARGET)
	$(CXX) -o $@ $^ -lpthread

$(TEST_TARGET): $(TEST_OBJS) $(LIB_TARGET)
	$(CXX) -o $@ $^ -lpthread

test: $(TEST_TARGET)
	./$(TEST_TARGET)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(LIB_OBJS) $(APP_OBJS) $(TEST_OBJS)
	rm -f $(LIB_TARGET) $(APP_TARGET) $(TEST_TARGET)
	rm -f $(wildcard *.d) $(wildcard $(LIB_DIR)/*.d)
	rm -f $(wildcard $(SRC_DIR)/*.d) $(wildcard $(TEST_DIR)/*.d)

-include $(wildcard *.d)
-include $(wildcard $(LIB_DIR)/*.d)
-include $(wildcard $(SRC_DIR)/*.d)
```

### C++20 modules (experimental Make support)

```makefile
# C++20 modules in Make — compiler-dependent flags
CXXFLAGS += -std=c++20 -fmodules-ts       # GCC: modules TS
# Or: CXXFLAGS += -std=c++20 -stdlib=libc++ -fmodules  # Clang

# Each .cppm module file must be compiled before files that import it
# Order matters — not all build systems handle this well yet
# Prefer CMake for modules (better support)
```

---

## Pitfalls

### Using `gcc` instead of `g++` for C++

`gcc` handles C++ source files differently than `g++`. `g++` automatically links the C++ standard library. `gcc` does not. Always use `g++` for C++ files, or use `gcc -lstdc++` if you must use gcc.

### Forgetting `-pthread` for multithreaded programs

On Linux, multithreaded C++ programs need the pthread library. Without `-lpthread` or `-pthread`, `std::thread` and `std::async` may not work correctly. Always add `-pthread` to both compile AND link flags.

### Template instantiation across compilation units

Templates are instantiated in each translation unit. Without explicit instantiation, the linker may produce duplicate symbols or fail to find symbols. The `-fimplicit-templates` flag (GCC) or explicit template instantiation in `.cpp` files fix this.

---

## Cross-Links

- [[C/06_Build_Systems/02_Make_Deep_Dive]] for foundational Make reference
- [[C++/06_Build_Systems/01_CMake_Deep_Dive]] for CMake alternative
- [[C/06_Build_Systems/01_CMake_Deep_Dive]] for CMake fundamentals
- [[C++/01_Foundations/01_Cpp_vs_C_Syntax_Compilation]] for C++ compiler flags
- [[C++/02_Core/08_Undefined_Behavior_and_Low_Level_Cpp]] for ODR violations in templates
