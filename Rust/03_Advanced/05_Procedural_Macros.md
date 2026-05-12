---
tags: [rust, advanced, macros, proc-macro, syn, quote, code-generation, metaprogramming]
aliases: ["Procedural Macros", "Derive Macros", "proc_macro", "Syn Quote", "Attribute Macros"]
status: stable
updated: 2026-05-03
---

# Procedural Macros

> [!summary] Goal
> Write compile-time code generation with procedural macros: understand the `TokenStream` API, the `syn`/`quote` ecosystem, and when derive, attribute, and function-like macros are the right tool.

## Table of Contents

1. [Why Procedural Macros](#why-procedural-macros)
2. [Types of Proc Macros](#types-of-proc-macros)
3. [Project Setup](#project-setup)
4. [TokenStream API](#tokenstream-api)
5. [Parsing with `syn`](#parsing-with-syn)
6. [Generating with `quote`](#generating-with-quote)
7. [Building a Derive Macro](#building-a-derive-macro)
8. [Attribute Macros](#attribute-macros)
9. [Function-Like Macros](#function-like-macros)
10. [Testing Proc Macros](#testing-proc-macros)
11. [Debugging and Tooling](#debugging-and-tooling)
12. [Pitfalls](#pitfalls)

---

## Why Procedural Macros

Procedural macros are Rust functions that run at **compile time**, transforming one `TokenStream` into another.

```mermaid
flowchart LR
    A[Source code] --> B[Compiler tokenizes]
    B --> C[proc macro function]
    C --> D[Transformed TokenStream]
    D --> E[Compiler continues: typeck, borrowck, codegen]
```

Common use cases:
- `#[derive(Debug, Clone, Serialize, Deserialize)]` — auto-implement traits
- `#[tokio::main]` — rewrite `fn main` into an async runtime entry point
- `include_str!`, `format_args!` — compile-time computation
- Custom derive for builder patterns, newtype wrappers, validation

> [!tip] Definition
> **Procedural macro**: a function annotated with `#[proc_macro_derive]`, `#[proc_macro_attribute]`, or `#[proc_macro]` that operates on Rust token streams at compile time.

---

## Types of Proc Macros

| Type | Annotation | Input | Output | Call site |
|------|-----------|-------|--------|-----------|
| **Derive macro** | `#[proc_macro_derive(Name)]` | The struct/enum/union | Additional `impl` blocks | `#[derive(MyMacro)]` |
| **Attribute macro** | `#[proc_macro_attribute]` | The attribute args + the item | The transformed item | `#[my_attr] fn foo() {}` |
| **Function-like macro** | `#[proc_macro]` | The delimited tokens | Arbitrary tokens | `my_macro!(...)` |

---

## Project Setup

A proc macro crate must be a separate crate with `proc-macro = true`:

```toml
# Cargo.toml for the proc macro crate
[package]
name = "my-derive"
version = "0.1.0"
edition = "2021"

[lib]
proc-macro = true

[dependencies]
syn = { version = "2", features = ["derive"] }
quote = "1"
```

Then in your application crate:

```toml
# Cargo.toml for the app
[dependencies]
my-derive = { path = "../my-derive" }
```

---

## TokenStream API

The raw API operates on `proc_macro::TokenStream`:

```rust
use proc_macro::TokenStream;

#[proc_macro_derive(HelloMacro)]
pub fn hello_macro_derive(input: TokenStream) -> TokenStream {
    // input: the tokens of the struct/enum
    // output: the tokens to add (usually impl blocks)
    input  // trivial: output = input (no transformation)
}
```

### Token types

| Token | Example |
|-------|---------|
| `Ident` | `struct`, `MyStruct`, `foo` |
| `Literal` | `42`, `"hello"`, `3.14` |
| `Punct` | `+`, `->`, `::` |
| `Group` | `(...)`, `{...}`, `[...]` |

Directly manipulating `TokenStream` is tedious — use `syn` for parsing and `quote` for generation.

---

## Parsing with `syn`

```rust
use syn::{parse_macro_input, DeriveInput, Data, Fields, Type};

#[proc_macro_derive(MyTrait)]
pub fn my_trait_derive(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);

    let name = &input.ident;         // struct/enum name
    let generics = &input.generics;   // generic parameters

    match &input.data {
        Data::Struct(data) => {
            for field in &data.fields {
                let field_name = &field.ident;
                let field_type = &field.ty;
                // ...
            }
        }
        Data::Enum(data) => { /* handle enum variants */ }
        Data::Union(_) => { /* handle unions */ }
    }

    // ...
}
```

### Common `syn` types

| Type | What it represents |
|------|-------------------|
| `DeriveInput` | The parsed struct/enum/union (name, generics, data) |
| `Data::Struct` | Struct fields (named, unnamed, or unit) |
| `Data::Enum` | Enum variants and their fields |
| `Fields::Named` | `struct Foo { x: i32 }` |
| `Fields::Unnamed` | `struct Foo(i32, String)` |
| `Type` | Any Rust type |
| `Ident` | An identifier |
| `GenericParam` | Type/lifetime/const generic parameter |

---

## Generating with `quote`

The `quote!` macro creates `TokenStream` with interpolation using `#var`:

```rust
use quote::quote;

let name = "world";
let tokens = quote! {
    println!("Hello, {}!", #name);
};
// tokens is a TokenStream
```

### Interpolation rules

| Syntax | Meaning |
|--------|---------|
| `#ident` | Insert the value of `ident` (must implement `ToTokens`) |
| `#(#items),*` | Insert each element of `items` separated by `,` |
| `#(#items)*` | Insert each element without separator |

```rust
let field_names: Vec<&Ident> = /* ... */;
let field_types: Vec<&Type> = /* ... */;

let tokens = quote! {
    impl #name {
        fn new(#(#field_names: #field_types),*) -> Self {
            Self {
                #(#field_names),*
            }
        }
    }
};
```

---

## Building a Derive Macro

Full worked example: a `#[derive(IntoUppercase)]` that generates a method to convert all `String` fields to uppercase.

### Step 1: Parse the struct

```rust
#[proc_macro_derive(IntoUppercase)]
pub fn into_uppercase_derive(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.ident;

    let fields = match &input.data {
        Data::Struct(data) => &data.fields,
        _ => panic!("IntoUppercase only supports structs"),
    };

    // Collect field names and types
    let field_names: Vec<_> = fields.iter().map(|f| &f.ident).collect();
    let field_types: Vec<_> = fields.iter().map(|f| &f.ty).collect();
```

### Step 2: Generate the impl

```rust
    let expanded = quote! {
        impl #name {
            fn into_uppercase(self) -> Self {
                Self {
                    #(
                        #field_names: {
                            let mut s: String = self.#field_names.into();
                            s.make_ascii_uppercase();
                            s
                        }
                    ),*
                }
            }
        }
    };

    expanded.into()
}
```

### Step 3: Use it

```rust
#[derive(IntoUppercase)]
struct Person {
    name: String,
    city: String,
}

let p = Person {
    name: "alice".into(),
    city: "london".into(),
};
let upper = p.into_uppercase();
assert_eq!(upper.name, "ALICE");
```

---

## Attribute Macros

Attribute macros transform the item they are attached to:

```rust
#[proc_macro_attribute]
pub fn log_call(args: TokenStream, item: TokenStream) -> TokenStream {
    // args: tokens inside the attribute: #[log_call(args_here)]
    // item: the function/item the attribute is attached to
    let input_fn = parse_macro_input!(item as ItemFn);
    let fn_name = &input_fn.sig.ident;
    let fn_block = &input_fn.block;

    let expanded = quote! {
        fn #fn_name() {
            println!("Calling: {}", stringify!(#fn_name));
            #fn_block
            println!("Returned: {}", stringify!(#fn_name));
        }
    };

    expanded.into()
}
```

Usage:

```rust
#[log_call]
fn compute() -> i32 {
    42
}
```

This expands to a function that wraps the original with logging.

---

## Function-Like Macros

Function-like macros look like function calls but work on tokens:

```rust
#[proc_macro]
pub fn sql(input: TokenStream) -> TokenStream {
    let sql_str = input.to_string().trim_matches('"').to_string();

    // Parse SQL at compile time, generate validation struct
    // (simplified — real implementation would use syn to parse)
    let expanded = quote! {
        {
            println!("Executing SQL: {}", #sql_str);
            // validation and query building
        }
    };
    expanded.into()
}
```

Usage:

```rust
sql!("SELECT * FROM users WHERE id = 1");
```

---

## Testing Proc Macros

### Unit tests for parsing

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use syn;

    #[test]
    fn test_parse_struct() {
        let input = quote! {
            struct Point { x: i32, y: i32 }
        };
        let parsed = syn::parse2::<DeriveInput>(input).unwrap();
        assert_eq!(parsed.ident.to_string(), "Point");
    }
}
```

### Compile-fail tests with `trybuild`

```toml
[dev-dependencies]
trybuild = "1"
```

```rust
#[test]
fn test_compile_failures() {
    let t = trybuild::TestCases::new();
    t.compile_fail("tests/fail/*.rs");  // all files in tests/fail/ should fail
    t.pass("tests/pass/*.rs");          // all files in tests/pass/ should pass
}
```

```rust
// tests/fail/not_a_struct.rs
#[derive(IntoUppercase)]
enum NotAStruct {  // expected error: IntoUppercase only supports structs
    Variant,
}
```

### Using `cargo expand` to inspect output

```bash
cargo install cargo-expand
cargo expand  # shows the expanded macro output
```

---

## Debugging and Tooling

### Panic messages appear as compile errors

```rust
#[proc_macro_derive(MyTrait)]
pub fn derive(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);

    if input.generics.params.len() > 0 {
        panic!("MyTrait does not support generic types");
    }
    // ...
}
```

This panic becomes:

```
error: proc macro panicked
 --> src/main.rs:5:10
  |
5 | #[derive(MyTrait)]
  |          ^^^^^^^
  |
  = help: message: MyTrait does not support generic types
```

### Using `syn::Error` for structured errors

```rust
use syn::Error;

let data = match &input.data {
    Data::Struct(d) => d,
    _ => {
        return Error::new(input.span(), "MyTrait only supports structs")
            .to_compile_error()
            .into();
    }
};
```

---

## Pitfalls

### Proc macro crates can only export proc macros

```rust
// BAD — mixing regular and proc macro exports
pub fn helper() {}  // ERROR: can't export non-macro items
#[proc_macro_derive(Foo)]
pub fn foo(input: TokenStream) -> TokenStream { input }
```

**Fix**: split helper functions into a separate non-proc-macro crate.

### Compilation time impact

Proc macros run at compile time. Complex proc macros can significantly slow down builds:
- Each `syn` parse and `quote` generation takes time
- Proc macro crates are compiled before the depending crate
- **Fix**: keep proc macros minimal, cache intermediate results

### Hygiene

Identifiers generated by `quote!` are automatically hygienic (they can't collide with user code). But `Ident::new` creates unhygienic identifiers:

```rust
// The generated function name could collide
let name = Ident::new("process", Span::call_site());
```

**Fix**: use unique generated names (e.g., include the struct name).

### Debugging difficulty

Proc macro errors appear as compile errors with no debugger. Workarounds:
- Write unit tests for parsing
- Use `cargo expand` to inspect output
- Print with `eprintln!` (appears during compile)

### Wrong span for errors

Error messages may point to the wrong location:

```rust
// This points to the derive attribute, not the specific field
Error::new(input.span(), "error").to_compile_error()
```

**Fix**: use spans from specific field tokens: `field.span()`

---

> [!question]- Interview Questions
>
> **Q: What are the three types of procedural macros in Rust?**
> A: Derive macros (`#[derive(Name)]`), attribute macros (`#[attr]` on items), and function-like macros (`name!(...)`). All operate on `TokenStream` at compile time.
>
> **Q: What is the difference between declarative macros and procedural macros?**
> A: Declarative macros (`macro_rules!`) use pattern matching. Procedural macros use Rust functions on `TokenStream`. Declarative are simpler, procedural are more powerful (can parse and generate arbitrary Rust code using `syn`/`quote`).
>
> **Q: Why must proc macros be in a separate crate?**
> A: Because `proc-macro = true` changes the compilation model. The crate is compiled first and linked into the compiler, so it cannot export regular items for use in the same package.
>
> **Q: What is the `syn` crate used for?**
> A: Parsing `TokenStream` into typed AST structures (`DeriveInput`, `ItemFn`, `Type`, etc.) so you can inspect and transform the code programmatically rather than manipulating raw tokens.
>
> **Q: What is the `quote` crate used for?**
> A: Generating `TokenStream` from Rust code templates with interpolation (`#var`, `#(...)*`). It handles hygiene and correct token spacing automatically.

---

## Cross-Links

- [[Rust/03_Advanced/04_Macros_Intro_and_Derive]] for declarative macros and derive macro basics
- [[Rust/01_Foundations/05_Traits_Generics_and_Lifetimes_Intro]] for trait impl code generation
- [[Rust/02_Core/05_Serde_JSON_and_Data_Modeling]] for a real-world derive macro example (serde)
- [[Rust/01_Foundations/07_Testing_in_Rust]] for trybuild compile-fail tests

---

## References

- [Procedural Macros (Rust Reference)](https://doc.rust-lang.org/reference/procedural-macros.html)
- [The Little Book of Rust Macros](https://veykril.github.io/tlborm/)
- [syn crate](https://docs.rs/syn/)
- [quote crate](https://docs.rs/quote/)
- [trybuild crate](https://docs.rs/trybuild/)
- [proc_macro2 crate](https://docs.rs/proc-macro2/)
