---
tags: [go, core, database, sql, postgres, migrations, queries, transactions]
aliases: ["database/sql", "SQL Database", "Migrations", "PostgreSQL", "Go Database"]
status: stable
updated: 2026-05-03
---

# Database: SQL, Queries, and Migrations

> [!summary] Goal
> Work with relational databases in Go: open connections, execute queries, manage transactions, and handle migrations with context support.

## Table of Contents

1. [Why database/sql Matters](#why-database-sql-matters)
2. [Connecting to a Database](#connecting-to-a-database)
3. [Executing Queries](#executing-queries)
4. [Prepared Statements](#prepared-statements)
5. [Transactions](#transactions)
6. [Migrations](#migrations)
7. [Context in Database Calls](#context-in-database-calls)
8. [Pitfalls](#pitfalls)

---

## Why `database/sql` Matters

`database/sql` is Go's standard interface for SQL databases. It provides connection pooling, prepared statements, transactions, and context support — all driver-agnostic.

```mermaid
flowchart LR
    A["sql.Open(driver, dsn)"] --> B["sql.DB (connection pool)"]
    B --> C["sql.Conn (single connection)"]
    B --> D["sql.Tx (transaction)"]
    B --> E["sql.Stmt (prepared statement)"]
    C --> F["Query, QueryRow, Exec"]
    D --> F
    E --> F
```

---

## Connecting to a Database

```go
import (
    "database/sql"
    _ "github.com/lib/pq"              // PostgreSQL driver (imported for side effects)
)

// Open a connection pool — NOT a single connection
db, err := sql.Open("postgres", "postgres://user:pass@localhost:5432/mydb?sslmode=disable")
if err != nil {
    return fmt.Errorf("opening db: %w", err)
}
defer db.Close()

// Ping to verify connection
if err := db.Ping(); err != nil {
    return fmt.Errorf("pinging db: %w", err)
}

// Pool configuration
db.SetMaxOpenConns(25)                // max open connections
db.SetMaxIdleConns(10)                // max idle connections
db.SetConnMaxLifetime(5 * time.Minute) // recycle connections
db.SetConnMaxIdleTime(1 * time.Minute) // close idle too long
```

Pool size rule of thumb: `(CPU cores × 2) + effective storage`. For a typical web service, 10-25 connections.

---

## Executing Queries

```go
// QueryRow — single row
type User struct {
    ID    string
    Email string
    Name  string
}

func (r *Repository) FindByID(ctx context.Context, id string) (*User, error) {
    row := r.db.QueryRowContext(ctx,
        "SELECT id, email, name FROM users WHERE id = $1", id)

    var u User
    if err := row.Scan(&u.ID, &u.Email, &u.Name); err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, nil                    // no user found — not an error
        }
        return nil, fmt.Errorf("scanning user: %w", err)
    }
    return &u, nil
}

// Query — multiple rows
func (r *Repository) List(ctx context.Context) ([]User, error) {
    rows, err := r.db.QueryContext(ctx,
        "SELECT id, email, name FROM users ORDER BY created_at DESC")
    if err != nil {
        return nil, fmt.Errorf("querying users: %w", err)
    }
    defer rows.Close()

    var users []User
    for rows.Next() {
        var u User
        if err := rows.Scan(&u.ID, &u.Email, &u.Name); err != nil {
            return nil, fmt.Errorf("scanning user: %w", err)
        }
        users = append(users, u)
    }
    // Always check for iteration errors
    if err := rows.Err(); err != nil {
        return nil, fmt.Errorf("iterating rows: %w", err)
    }
    return users, nil
}

// Exec — write operations (INSERT, UPDATE, DELETE)
func (r *Repository) Create(ctx context.Context, u *User) error {
    _, err := r.db.ExecContext(ctx,
        "INSERT INTO users (id, email, name) VALUES ($1, $2, $3)",
        u.ID, u.Email, u.Name)
    if err != nil {
        // Check for unique constraint violation
        var pqErr *pq.Error
        if errors.As(err, &pqErr) && pqErr.Code == "23505" {
            return fmt.Errorf("user with email %s already exists", u.Email)
        }
        return fmt.Errorf("inserting user: %w", err)
    }
    return nil
}
```

---

## Prepared Statements

```go
// Prepare once, execute many times — faster and prevents SQL injection
func (r *Repository) BulkCreate(ctx context.Context, users []User) error {
    stmt, err := r.db.PrepareContext(ctx,
        "INSERT INTO users (id, email, name) VALUES ($1, $2, $3)")
    if err != nil {
        return err
    }
    defer stmt.Close()

    for _, u := range users {
        if _, err := stmt.ExecContext(ctx, u.ID, u.Email, u.Name); err != nil {
            return err
        }
    }
    return nil
}
```

---

## Transactions

```go
func (r *Repository) CreateUserWithProfile(ctx context.Context, user *User, profile *Profile) error {
    tx, err := r.db.BeginTx(ctx, &sql.TxOptions{
        Isolation: sql.LevelSerializable,
    })
    if err != nil {
        return err
    }
    // Rollback is a no-op after Commit
    defer tx.Rollback()

    if _, err := tx.ExecContext(ctx,
        "INSERT INTO users (id, email, name) VALUES ($1, $2, $3)",
        user.ID, user.Email, user.Name); err != nil {
        return err
    }

    if _, err := tx.ExecContext(ctx,
        "INSERT INTO profiles (user_id, bio) VALUES ($1, $2)",
        user.ID, profile.Bio); err != nil {
        return err
    }

    return tx.Commit()
}
```

```mermaid
sequenceDiagram
    participant App
    participant DB

    App->>DB: BeginTx
    DB-->>App: Transaction started
    App->>DB: Exec INSERT users
    App->>DB: Exec INSERT profiles
    App->>DB: Commit
    DB-->>App: Changes committed
    Note over App,DB: If any step fails → Rollback
```

---

## Migrations

### Using golang-migrate

```bash
go install -tags "postgres" github.com/golang-migrate/migrate/v4/cmd/migrate@latest

# Create migration files
migrate create -ext sql -dir migrations -seq create_users

# Result:
# migrations/
# ├── 000001_create_users.up.sql
# └── 000001_create_users.down.sql
```

```sql
-- 000001_create_users.up.sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users (email);

-- 000001_create_users.down.sql
DROP TABLE IF EXISTS users;
```

```bash
# Run migrations
migrate -path migrations -database "postgres://user:pass@localhost:5432/mydb?sslmode=disable" up

# Rollback
migrate -path migrations -database "postgres://user:pass@localhost:5432/mydb?sslmode=disable" down 1
```

### Embedding migrations with `//go:embed`

```go
import (
    "embed"
    "github.com/golang-migrate/migrate/v4/source/iofs"
)

//go:embed migrations/*.sql
var migrationsFS embed.FS

func runMigrations(db *sql.DB) error {
    source, err := iofs.New(migrationsFS, "migrations")
    if err != nil {
        return err
    }
    // Use source with migrate.New...
}
```

---

## Context in Database Calls

```go
// Always pass context to database operations
func (r *Repository) SlowQuery(ctx context.Context) error {
    // Query with timeout
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    _, err := r.db.ExecContext(ctx, "ANALYZE")
    if errors.Is(err, context.DeadlineExceeded) {
        return fmt.Errorf("query timed out: %w", err)
    }
    return err
}
```

---

## Pitfalls

### Not closing rows

```go
rows, _ := db.Query("SELECT ...")
// forgot defer rows.Close()
// connection held until rows.Next() returns false or rows.Close()
```

**Fix**: Always `defer rows.Close()` immediately after checking the query error.

### `sql.Open` doesn't connect

`sql.Open` only validates the driver name and DSN format — it doesn't actually connect.

**Fix**: Always call `db.Ping()` or `db.PingContext()` to verify the connection.

### Connection leak from incomplete transaction

```go
tx, _ := db.Begin()
// ... operations ...
// forgot tx.Commit() or tx.Rollback()
// connection stays locked until GC disposes it
```

**Fix**: Always `defer tx.Rollback()` after `Begin`. It's a no-op if committed.

---

> [!question]- Interview Questions
>
> **Q: How does `database/sql` handle connection pooling?**
> A: `sql.Open` returns a pool. `SetMaxOpenConns` limits concurrent connections. `SetMaxIdleConns` keeps idle connections ready. `SetConnMaxLifetime` recycles connections periodically.
>
> **Q: What is the role of `defer rows.Close()`?**
> A: It ensures the database connection is released back to the pool when iteration completes. Without it, connections leak. Even with `Next()` iterating through all rows, `Close()` should be deferred.
>
> **Q: How do you handle transactions in Go?**
> A: Call `db.BeginTx(ctx, opts)` to start a transaction. Always `defer tx.Rollback()` for safety. On success, call `tx.Commit()` — Rollback becomes a no-op.

---

## Cross-Links

- [[Go/02_Core/01_Context_Cancellation_and_Timeouts]] for database context patterns
- [[Go/01_Foundations/04_Modules_Packages_and_Tooling]] for //go:embed migrations
- [[Go/05_Projects/01_REST_API_net_http_Postgres]] for a complete database-backed API

---

## References

- [database/sql](https://pkg.go.dev/database/sql)
- [Go Blog: database/sql](https://go.dev/blog/sql-database)
- [golang-migrate](https://github.com/golang-migrate/migrate)
- [pgx driver](https://github.com/jackc/pgx)
