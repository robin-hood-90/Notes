---
tags: [cpp, build-systems, cmake, cpp-standard, build-configuration, toolchain, vcpkg, conan]
aliases: ["CMake C++", "C++ CMake", "CMakeLists.txt C++", "vcpkg CMake"]
status: stable
updated: 2026-05-09
---

# CMake Deep Dive for C++

> [!summary] Goal
> Master CMake for C++ projects — C++ standard management, finding C++ libraries, integrating vcpkg/Conan, exporting C++ targets, and C++-specific generator expressions.

## Table of Contents

1. [C++ Standards in CMake](#c-standards-in-cmake)
2. [C++ Compiler Detection](#c-compiler-detection)
3. [C++ Library Management](#c-library-management)
4. [C++ Export and Install](#c-export-and-install)
5. [C++ Specific Generator Expressions](#c-specific-generator-expressions)
6. [Pitfalls](#pitfalls)

---

## C++ Standards in CMake

> [!info] CMake C++ standard support
> CMake manages C++ standards through target properties and compile features. The modern approach uses `target_compile_features` rather than setting `CMAKE_CXX_STANDARD` globally. This allows different standards for different targets and propagates requirements through PUBLIC dependencies.

### Setting C++ standards

```cmake
# Method 1: Target property (recommended)
add_library(my_lib lib.cpp)
target_compile_features(my_lib PUBLIC cxx_std_17)    # Requires C++17

add_executable(myapp main.cpp)
target_compile_features(myapp PRIVATE cxx_std_20)    # Requires C++20

# Method 2: Global variable (simpler but affects everything)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)    # Error if compiler doesn't support C++20
set(CMAKE_CXX_EXTENSIONS OFF)          # Use -std=c++20, not -std=gnu++20
```

### compile_features

```cmake
# Granular feature requirements — only request what you need
target_compile_features(myapp PRIVATE
    cxx_nullptr                      # C++11: nullptr
    cxx_range_for                    # C++11: range-based for loop
    cxx_auto_type                    # C++11: auto
    cxx_lambdas                      # C++11: lambdas
    cxx_variadic_templates           # C++11: variadic templates
    cxx_move_semantics               # C++11: move semantics
    cxx_final                        # C++11: final
    cxx_override                     # C++11: override
    cxx_constexpr                    # C++11: constexpr
    cxx_decltype                     # C++11: decltype
    cxx_delegating_constructors      # C++11: delegating constructors
    cxx_rvalue_references            # C++11: &&
)
```

### Checking C++ standard features

```cmake
# Check if the compiler supports a specific feature
list(FIND CMAKE_CXX_COMPILE_FEATURES cxx_constexpr HAS_CONSTEXPR)
if(HAS_CONSTEXPR GREATER -1)
    message(STATUS "Compiler supports constexpr")
else()
    message(STATUS "Compiler does NOT support constexpr")
endif()

# Check C++ version
if(CMAKE_CXX_STANDARD EQUAL 20)
    message(STATUS "Building with C++20")
elseif(CMAKE_CXX_STANDARD EQUAL 17)
    message(STATUS "Building with C++17")
endif()
```

---

## C++ Compiler Detection

```cmake
# Detect which C++ compiler is being used
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    message(STATUS "Using GCC ${CMAKE_CXX_COMPILER_VERSION}")
    target_compile_options(myapp PRIVATE -Wno-deprecated-declarations)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    message(STATUS "Using Clang ${CMAKE_CXX_COMPILER_VERSION}")
    target_compile_options(myapp PRIVATE -Wno-deprecated)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    message(STATUS "Using MSVC ${CMAKE_CXX_COMPILER_VERSION}")
    target_compile_options(myapp PRIVATE /W4 /utf-8)
endif()
```

### MSVC-specific handling

```cmake
# MSVC uses different flags — handle with generator expressions
target_compile_options(myapp PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -Wpedantic>
    $<$<CXX_COMPILER_ID:MSVC>:/W4 /WX /utf-8 /permissive->
)

# Linking pthread on Unix, automatic on Windows
target_link_libraries(myapp PRIVATE
    $<$<PLATFORM_ID:Linux>:pthread>
    $<$<PLATFORM_ID:Windows>:>
)

# Exception handling flags
target_compile_options(myapp PRIVATE
    $<$<COMPILE_LANG_AND_ID:CXX,GNU,Clang>:-fexceptions>
    $<$<COMPILE_LANG_AND_ID:CXX,MSVC>:/EHsc>
)
```

---

## C++ Library Management

### Finding C++ libraries with find_package

```cmake
# Boost
find_package(Boost REQUIRED COMPONENTS system filesystem)
target_link_libraries(myapp PRIVATE Boost::system Boost::filesystem)
target_compile_definitions(myapp PRIVATE BOOST_ALL_DYN_LINK)

# fmtlib
find_package(fmt REQUIRED)
target_link_libraries(myapp PRIVATE fmt::fmt)

# spdlog
find_package(spdlog REQUIRED)
target_link_libraries(myapp PRIVATE spdlog::spdlog)

# nlohmann_json
find_package(nlohmann_json REQUIRED)
target_link_libraries(myapp PRIVATE nlohmann_json::nlohmann_json)

# Range-v3
find_package(range-v3 REQUIRED)
target_link_libraries(myapp PRIVATE range-v3::range-v3)
```

### vcpkg integration

```cmake
# vcpkg automatically sets CMAKE_TOOLCHAIN_FILE
# Run: cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake

# Then find_package works automatically for vcpkg-installed libraries
find_package(fmt CONFIG REQUIRED)    # Finds the vcpkg-installed version
find_package(spdlog CONFIG REQUIRED)
```

### Conan integration

```cmake
# conanfile.txt
# [requires]
# fmt/10.1.0
# spdlog/1.12.0
#
# [generators]
# CMakeDeps
# CMakeToolchain

# conan install . --output-folder=build --build=missing
# cd build && cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake

# CMakeLists.txt — same find_package commands work
find_package(fmt REQUIRED)
find_package(spdlog REQUIRED)
```

### FetchContent for C++ dependencies

```cmake
include(FetchContent)

# Header-only library
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.2
)
FetchContent_MakeAvailable(nlohmann_json)
target_link_libraries(myapp PRIVATE nlohmann_json::nlohmann_json)

# Library with compilation
FetchContent_Declare(
    fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG 10.1.0
)
set(FMT_TEST OFF CACHE BOOL "" FORCE)          # Disable tests
FetchContent_MakeAvailable(fmt)
target_link_libraries(myapp PRIVATE fmt::fmt)
```

---

## C++ Export and Install

```cmake
# Create an installable C++ library
add_library(my_lib SHARED
    src/core.cpp
    src/utils.cpp
)

target_include_directories(my_lib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

target_compile_features(my_lib PUBLIC cxx_std_17)

# Install rules
install(TARGETS my_lib
    EXPORT MyLibTargets          # Export the target for consumers
    LIBRARY DESTINATION lib      # Shared libraries
    ARCHIVE DESTINATION lib      # Static libraries
    RUNTIME DESTINATION bin      # DLLs (Windows)
    INCLUDES DESTINATION include  # Add include path to exported targets
)

install(DIRECTORY include/ DESTINATION include)

# Generate and install CMake config file for find_package
install(EXPORT MyLibTargets
    FILE MyLibTargets.cmake
    NAMESPACE MyLib::
    DESTINATION lib/cmake/MyLib
)

# Generate a Config.cmake for find_package(MyLib CONFIG)
include(CMakePackageConfigHelpers)
configure_package_config_file(
    ${CMAKE_SOURCE_DIR}/cmake/MyLibConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/MyLibConfig.cmake
    INSTALL_DESTINATION lib/cmake/MyLib
)
install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/MyLibConfig.cmake
    DESTINATION lib/cmake/MyLib
)
```

---

## C++ Specific Generator Expressions

```cmake
# C++ compile features
target_compile_features(myapp PRIVATE cxx_std_17)

# Conditional C++ standard
target_compile_features(myapp
    PRIVATE
    $<$<VERSION_GREATER_EQUAL:CMAKE_CXX_STANDARD,17>:cxx_std_17>
)

# Platform-specific C++ features
target_link_libraries(myapp PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:shlwapi.lib>
    $<$<CXX_COMPILER_ID:GNU>:dl>
)

# Debug vs Release compile flags
target_compile_options(myapp PRIVATE
    $<$<CONFIG:Debug>:-g -O0 -fno-inline>
    $<$<CONFIG:Release>:-O3 -DNDEBUG>
    $<$<CONFIG:RelWithDebInfo>:-O2 -g>
)
```

---

## Pitfalls

### Forgetting to propagate C++ standard to consumers

If your library uses C++17 features in its public headers, it must declare `cxx_std_17` as PUBLIC. Otherwise, consumers compiling with an older standard get compile errors. PRIVATE means only the library itself needs C++17, not its users.

### Mixing Debug and Release libraries

A Debug build of a library and a Release build of another library linked into the same program is undefined behavior (different iterator debugging, different allocators). Use consistent build types across all dependencies.

---

## Cross-Links

- [[C/06_Build_Systems/01_CMake_Deep_Dive]] for foundational CMake reference
- [[C/06_Build_Systems/02_Make_Deep_Dive]] for Make alternative
- [[C++/06_Build_Systems/02_Make_Deep_Dive]] for C++ Makefiles
- [[C++/01_Foundations/01_Cpp_vs_C_Syntax_Compilation]] for C++ compiler flags
- [[C++/03_Advanced/07_Performance_Cache_and_Optimization]] for PGO with CMake
