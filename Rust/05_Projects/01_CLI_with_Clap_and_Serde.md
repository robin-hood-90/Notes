---
tags: [rust, projects, cli, clap, serde, command-line]
aliases: ["CLI with Clap", "Command Line Tool", "Clap and Serde"]
status: stable
updated: 2026-05-11
---

# Project: CLI with Clap and Serde

> [!summary] Goal
> Build a production-quality CLI tool with argument parsing (clap), configuration (serde), error handling, and testing.

## Architecture

```
my-cli/
├── Cargo.toml
├── src/
│   ├── main.rs          # Entry point, argument parsing, dispatch
│   ├── config.rs        # Configuration model (serde)
│   ├── commands/
│   │   ├── mod.rs
│   │   ├── init.rs      # `my-cli init` subcommand
│   │   └── process.rs   # `my-cli process` subcommand
│   └── error.rs         # Error types (thiserror)
└── tests/
    ├── integration.rs
    └── fixtures/
```

## Dependencies

```toml
[package]
name = "my-cli"
version = "0.1.0"
edition = "2021"

[dependencies]
clap = { version = "4", features = ["derive"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
serde_yaml = "0.9"
thiserror = "2"
anyhow = "1"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

[dev-dependencies]
assert_cmd = "2"
predicates = "3"
tempfile = "3"
```

## Step 1: Argument Parsing with Clap (derive)

```rust
// src/main.rs
use clap::{Parser, Subcommand};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "my-cli", version, about = "A production-quality CLI tool")]
struct Cli {
    /// Path to config file
    #[arg(short, long, default_value = "config.yaml")]
    config: PathBuf,

    /// Verbose output (-v, -vv, -vvv)
    #[arg(short, long, action = clap::ArgAction::Count)]
    verbose: u8,

    /// Subcommand to run
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Initialize a new project
    Init {
        /// Project name
        name: String,

        /// Output directory
        #[arg(short, long, default_value = ".")]
        output: PathBuf,
    },
    /// Process an existing project
    Process {
        /// Input file pattern (glob)
        #[arg(short, long, default_value = "*.txt")]
        pattern: String,

        /// Dry run (no modifications)
        #[arg(long)]
        dry_run: bool,
    },
}

fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    // Initialize logging based on verbosity
    let level = match cli.verbose {
        0 => "info",
        1 => "debug",
        _ => "trace",
    };
    tracing_subscriber::fmt()
        .with_env_filter(format!("my_cli={level}"))
        .init();

    match &cli.command {
        Commands::Init { name, output } => commands::init::run(name, output, &cli.config)?,
        Commands::Process { pattern, dry_run } => {
            commands::process::run(pattern, *dry_run, &cli.config)?
        }
    }

    Ok(())
}
```

## Step 2: Configuration with Serde

```rust
// src/config.rs
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Serialize, Deserialize)]
pub struct Config {
    pub project: ProjectConfig,
    pub processing: ProcessingConfig,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ProjectConfig {
    pub name: String,
    pub version: String,
    pub author: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ProcessingConfig {
    pub max_file_size: u64,
    pub output_dir: String,
    pub encoding: String,
}

impl Config {
    pub fn from_path(path: &Path) -> anyhow::Result<Self> {
        let contents = std::fs::read_to_string(path)
            .map_err(|e| anyhow::anyhow!("Failed to read config {path:?}: {e}"))?;

        let config: Config = match path.extension().and_then(|e| e.to_str()) {
            Some("yaml" | "yml") => serde_yaml::from_str(&contents)?,
            Some("json") => serde_json::from_str(&contents)?,
            Some("toml") => toml::from_str(&contents)?,
            ext => anyhow::bail!("Unsupported config format: {ext:?}"),
        };
        Ok(config)
    }
}
```

## Step 3: Subcommand Implementation

```rust
// src/commands/mod.rs
pub mod init;
pub mod process;

// src/commands/init.rs
use std::path::Path;

pub fn run(name: &str, output: &Path, config_path: &Path) -> anyhow::Result<()> {
    let config = crate::config::Config::from_path(config_path)?;

    let project_dir = output.join(name);
    std::fs::create_dir_all(&project_dir)?;
    std::fs::create_dir_all(project_dir.join("src"))?;
    std::fs::create_dir_all(project_dir.join("tests"))?;

    // Generate Cargo.toml
    let cargo_toml = format!(
        "[package]\nname = \"{name}\"\nversion = \"0.1.0\"\nedition = \"2021\"\n"
    );
    std::fs::write(project_dir.join("Cargo.toml"), cargo_toml)?;

    // Generate main.rs
    let main_rs = "fn main() {\n    println!(\"Hello, world!\");\n}\n";
    std::fs::write(project_dir.join("src/main.rs"), main_rs)?;

    tracing::info!("Created project {name} at {}", output.display());
    Ok(())
}
```

## Step 4: Error Handling

```rust
// src/error.rs
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CliError {
    #[error("Config error: {0}")]
    Config(#[from] crate::config::ConfigError),

    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Validation error: {0}")]
    Validation(String),

    #[error("Unknown command: {0}")]
    UnknownCommand(String),
}
```

## Step 5: Testing

```rust
// tests/integration.rs
use assert_cmd::Command;
use predicates::prelude::*;
use tempfile::TempDir;

#[test]
fn test_init_creates_project() {
    let tmp = TempDir::new().unwrap();
    let config_path = tmp.path().join("config.yaml");

    // Write a minimal config
    std::fs::write(
        &config_path,
        r#"
project:
  name: "test"
  version: "0.1.0"
  author: "Test User"
processing:
  max_file_size: 1048576
  output_dir: "./output"
  encoding: "utf-8"
"#,
    )
    .unwrap();

    let mut cmd = Command::cargo_bin("my-cli").unwrap();
    cmd.arg("--config")
        .arg(config_path.to_str().unwrap())
        .arg("init")
        .arg("test-project")
        .arg("--output")
        .arg(tmp.path().to_str().unwrap());

    cmd.assert()
        .success()
        .stdout(predicate::str::contains("Created project"));

    assert!(tmp.path().join("test-project").exists());
    assert!(tmp.path().join("test-project/Cargo.toml").exists());
    assert!(tmp.path().join("test-project/src/main.rs").exists());
}

#[test]
fn test_cli_help() {
    let mut cmd = Command::cargo_bin("my-cli").unwrap();
    cmd.arg("--help");
    cmd.assert()
        .success()
        .stdout(predicate::str::contains("Usage"))
        .stdout(predicate::str::contains("Commands"));
}
```

## Extension Ideas

- Add config file watching with `notify` crate
- Add progress bars with `indicatif`
- Add shell completion generation (`clap_complete`)
- Add colored output with `console` or `owo-colors`
- Add a `--json` output flag for machine-readable output

---

## Cross-Links

- [[Rust/01_Foundations/06_Modules_Crates_Cargo_and_Tooling]] for Cargo project structure
- [[Rust/01_Foundations/07_Testing_in_Rust]] for testing patterns
- [[Rust/03_Advanced/17_Tracing_Logging_and_Observability]] for structured logging
