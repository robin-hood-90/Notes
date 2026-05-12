---
tags: [rust, projects, http, axum, postgres, sqlx, web-api]
aliases: ["HTTP API with Axum", "Axum Postgres", "Rust Web Server"]
status: stable
updated: 2026-05-11
---

# Project: HTTP API with Axum and Postgres

> [!summary] Goal
> Build a production-ready HTTP API with Axum, async PostgreSQL (sqlx), structured error handling, middleware, and testing.

## Architecture

```
my-api/
├── Cargo.toml
├── src/
│   ├── main.rs              # Server setup, router, startup
│   ├── routes/
│   │   ├── mod.rs
│   │   ├── health.rs        # GET /health
│   │   ├── users.rs         # CRUD /users
│   │   └── items.rs         # CRUD /items
│   ├── models/
│   │   ├── mod.rs
│   │   ├── user.rs
│   │   └── item.rs
│   ├── db/
│   │   ├── mod.rs
│   │   ├── users.rs
│   │   └── items.rs
│   ├── error.rs             # AppError type
│   └── config.rs            # App config from env
└── tests/
    ├── common/
    │   └── mod.rs            # Test helpers
    ├── health_test.rs
    └── users_test.rs
```

## Dependencies

```toml
[package]
name = "my-api"
version = "0.1.0"
edition = "2021"

[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
sqlx = { version = "0.8", features = ["runtime-tokio", "postgres", "uuid"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
thiserror = "2"
uuid = { version = "1", features = ["v4", "serde"] }
tower-http = { version = "0.5", features = ["trace", "cors"] }

[dev-dependencies]
reqwest = { version = "0.12", features = ["json"] }
testcontainers = "0.23"
testcontainers-modules = "0.10"
tracing-test = "0.2"
```

## Step 1: Application State and Router

```rust
// src/main.rs
use axum::{routing::get, Router};
use sqlx::postgres::PgPoolOptions;
use std::sync::Arc;
use tracing_subscriber::EnvFilter;

mod config;
mod db;
mod error;
mod models;
mod routes;

#[derive(Clone)]
pub struct AppState {
    pub db: sqlx::PgPool,
    pub config: Arc<config::Config>,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env())
        .init();

    let config = config::Config::from_env()?;

    let pool = PgPoolOptions::new()
        .max_connections(config.db_max_connections)
        .connect(&config.database_url)
        .await?;

    // Run migrations
    sqlx::migrate!("./migrations").run(&pool).await?;

    let state = AppState {
        db: pool,
        config: Arc::new(config),
    };

    let app = Router::new()
        .route("/health", get(routes::health::health_check))
        .nest("/api/users", routes::users::router())
        .nest("/api/items", routes::items::router())
        .layer(tower_http::trace::TraceLayer::new_for_http())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    tracing::info!("Server listening on {}", listener.local_addr()?);
    axum::serve(listener, app).await?;

    Ok(())
}
```

## Step 2: Configuration

```rust
// src/config.rs
pub struct Config {
    pub database_url: String,
    pub db_max_connections: u32,
    pub host: String,
    pub port: u16,
    pub log_level: String,
}

impl Config {
    pub fn from_env() -> anyhow::Result<Self> {
        Ok(Self {
            database_url: std::env::var("DATABASE_URL")
                .unwrap_or_else(|_| "postgres://postgres:postgres@localhost:5432/myapp".into()),
            db_max_connections: std::env::var("DB_MAX_CONNECTIONS")
                .ok()
                .and_then(|s| s.parse().ok())
                .unwrap_or(10),
            host: std::env::var("HOST").unwrap_or_else(|_| "0.0.0.0".into()),
            port: std::env::var("PORT")
                .ok()
                .and_then(|s| s.parse().ok())
                .unwrap_or(3000),
            log_level: std::env::var("LOG_LEVEL")
                .unwrap_or_else(|_| "info".into()),
        })
    }
}
```

## Step 3: Error Handling

```rust
// src/error.rs
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;

#[derive(thiserror::Error, Debug)]
pub enum AppError {
    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Validation error: {0}")]
    Validation(String),

    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),

    #[error("Internal error: {0}")]
    Internal(String),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, message) = match &self {
            AppError::NotFound(msg) => (StatusCode::NOT_FOUND, msg.clone()),
            AppError::Validation(msg) => (StatusCode::BAD_REQUEST, msg.clone()),
            AppError::Database(e) => {
                tracing::error!(error = %e, "Database error");
                (StatusCode::INTERNAL_SERVER_ERROR, "Internal server error".into())
            }
            AppError::Internal(msg) => {
                tracing::error!(error = %msg, "Internal error");
                (StatusCode::INTERNAL_SERVER_ERROR, msg.clone())
            }
        };

        (status, Json(json!({"error": message}))).into_response()
    }
}
```

## Step 4: Models and DB Layer

```rust
// src/models/user.rs
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize, FromRow)]
pub struct User {
    pub id: Uuid,
    pub name: String,
    pub email: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Deserialize)]
pub struct CreateUserRequest {
    pub name: String,
    pub email: String,
}

// src/db/users.rs
use crate::models::user::{CreateUserRequest, User};
use crate::error::AppError;
use sqlx::PgPool;

pub async fn create_user(pool: &PgPool, req: CreateUserRequest) -> Result<User, AppError> {
    let user = sqlx::query_as::<_, User>(
        "INSERT INTO users (id, name, email) VALUES ($1, $2, $3) RETURNING *"
    )
    .bind(Uuid::new_v4())
    .bind(&req.name)
    .bind(&req.email)
    .fetch_one(pool)
    .await?;

    Ok(user)
}

pub async fn get_user(pool: &PgPool, user_id: Uuid) -> Result<User, AppError> {
    let user = sqlx::query_as::<_, User>(
        "SELECT * FROM users WHERE id = $1"
    )
    .bind(user_id)
    .fetch_optional(pool)
    .await?
    .ok_or_else(|| AppError::NotFound(format!("User {user_id}")))?;

    Ok(user)
}

pub async fn list_users(pool: &PgPool) -> Result<Vec<User>, AppError> {
    let users = sqlx::query_as::<_, User>(
        "SELECT * FROM users ORDER BY created_at DESC LIMIT 100"
    )
    .fetch_all(pool)
    .await?;

    Ok(users)
}
```

## Step 5: Route Handlers

```rust
// src/routes/users.rs
use axum::{
    extract::{Path, State},
    routing::{get, post},
    Json, Router,
};
use uuid::Uuid;

use crate::models::user::CreateUserRequest;
use crate::{AppState, error::AppError};

pub fn router() -> Router<AppState> {
    Router::new()
        .route("/", get(list_users).post(create_user))
        .route("/{id}", get(get_user))
}

async fn list_users(
    State(state): State<AppState>,
) -> Result<Json<Vec<crate::models::user::User>>, AppError> {
    let users = crate::db::users::list_users(&state.db).await?;
    Ok(Json(users))
}

async fn create_user(
    State(state): State<AppState>,
    Json(req): Json<CreateUserRequest>,
) -> Result<Json<crate::models::user::User>, AppError> {
    if req.name.trim().is_empty() {
        return Err(AppError::Validation("Name cannot be empty".into()));
    }
    if !req.email.contains('@') {
        return Err(AppError::Validation("Invalid email".into()));
    }

    let user = crate::db::users::create_user(&state.db, req).await?;
    Ok(Json(user))
}

async fn get_user(
    State(state): State<AppState>,
    Path(user_id): Path<Uuid>,
) -> Result<Json<crate::models::user::User>, AppError> {
    let user = crate::db::users::get_user(&state.db, user_id).await?;
    Ok(Json(user))
}
```

## Step 6: Database Migrations

```sql
-- migrations/20240101000000_create_users.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

## Step 7: Integration Tests

```rust
// tests/users_test.rs
use my_api::{config::Config, AppState};
use sqlx::PgPool;
use testcontainers::runners::AsyncRunner;
use testcontainers_modules::postgres::Postgres;

async fn setup_test_state() -> (AppState, AsyncRunner) {
    let container = Postgres::default()
        .start()
        .await
        .expect("Failed to start postgres container");

    let host = container.get_host().await.unwrap();
    let port = container.get_host_port_ipv4(5432).await.unwrap();
    let database_url = format!("postgres://postgres:postgres@{host}:{port}/postgres");

    let pool = PgPool::connect(&database_url).await.unwrap();
    sqlx::migrate!("./migrations").run(&pool).await.unwrap();

    let state = AppState {
        db: pool,
        config: std::sync::Arc::new(Config::from_env().unwrap()),
    };

    (state, container)
}

#[tokio::test]
async fn test_create_and_get_user() {
    let (state, _container) = setup_test_state().await;

    let app = my_api::app(state);

    // Use reqwest to test the full stack
    let client = reqwest::Client::new();
    // ... full integration test
}
```

## Extension Ideas

- Add authentication with JWT (`jsonwebtoken`)
- Add pagination with cursor-based pagination
- Add request validation with `validator` crate
- Add rate limiting with `tower-governor`
- Add OpenAPI docs with `utoipa`
- Add structured error codes for API consumers

---

## Cross-Links

- [[Rust/02_Core/04_Async_Await_Tokio_Basics]] for async runtime patterns
- [[Rust/03_Advanced/17_Tracing_Logging_and_Observability]] for HTTP tracing
- [[Rust/01_Foundations/07_Testing_in_Rust]] for integration test patterns
