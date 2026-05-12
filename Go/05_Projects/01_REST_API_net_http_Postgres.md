---
tags: [go, projects, rest, api, postgres, chi, crud]
aliases: ["REST API Project", "Go REST API", "CRUD Service"]
status: stable
updated: 2026-05-03
---

# Project: REST API with chi and PostgreSQL

> [!summary] Goal
> Build a production-ready REST API with `chi` router, PostgreSQL storage, SQL migrations, structured logging, and graceful shutdown.

## Project Structure

```
myapi/
├── cmd/server/main.go
├── internal/
│   ├── handler/user.go
│   ├── repository/user.go
│   ├── model/user.go
│   └── middleware/logging.go
├── migrations/
│   └── 000001_create_users.up.sql
├── go.mod
├── Dockerfile
└── docker-compose.yml
```

## main.go

```go
package main

import (
    "context"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
    "database/sql"
    _ "github.com/lib/pq"
    "github.com/go-chi/chi/v5"
    chiMiddleware "github.com/go-chi/chi/v5/middleware"
)

type Config struct {
    Port       string
    DatabaseURL string
}

func loadConfig() Config {
    return Config{
        Port:       getEnv("PORT", "8080"),
        DatabaseURL: getEnv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/myapi?sslmode=disable"),
    }
}

func getEnv(key, defaultVal string) string {
    if val := os.Getenv(key); val != "" {
        return val
    }
    return defaultVal
}

func main() {
    cfg := loadConfig()

    db, err := sql.Open("postgres", cfg.DatabaseURL)
    if err != nil {
        slog.Error("opening database", "error", err)
        os.Exit(1)
    }
    defer db.Close()

    db.SetMaxOpenConns(25)
    db.SetMaxIdleConns(10)
    db.SetConnMaxLifetime(5 * time.Minute)

    if err := db.Ping(); err != nil {
        slog.Error("connecting to database", "error", err)
        os.Exit(1)
    }

    repo := repository.NewUserRepository(db)
    handler := handler.NewUserHandler(repo)

    r := chi.NewRouter()
    r.Use(chiMiddleware.Logger)
    r.Use(chiMiddleware.Recoverer)
    r.Use(chiMiddleware.Timeout(30 * time.Second))

    r.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte("ok"))
    })

    r.Route("/api/users", func(r chi.Router) {
        r.Get("/", handler.List)
        r.Post("/", handler.Create)
        r.Get("/{id}", handler.GetByID)
        r.Put("/{id}", handler.Update)
        r.Delete("/{id}", handler.Delete)
    })

    srv := &http.Server{
        Addr:    ":" + cfg.Port,
        Handler: r,
    }

    go func() {
        slog.Info("server starting", "port", cfg.Port)
        if err := srv.ListenAndServe(); err != http.ErrServerClosed {
            slog.Error("server error", "error", err)
            os.Exit(1)
        }
    }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    slog.Info("shutting down...")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    srv.Shutdown(ctx)
}
```

## model/user.go

```go
package model

type User struct {
    ID        string `json:"id"`
    Email     string `json:"email"`
    Name      string `json:"name"`
    Age       int    `json:"age,omitempty"`
}

type CreateUserRequest struct {
    Email string `json:"email"`
    Name  string `json:"name"`
    Age   int    `json:"age"`
}
```

## repository/user.go

```go
package repository

import (
    "context"
    "database/sql"
    "errors"
    "myapi/internal/model"
)

type UserRepository struct {
    db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) Create(ctx context.Context, u *model.User) error {
    _, err := r.db.ExecContext(ctx,
        "INSERT INTO users (id, email, name, age) VALUES ($1, $2, $3, $4)",
        u.ID, u.Email, u.Name, u.Age)
    return err
}

func (r *UserRepository) FindByID(ctx context.Context, id string) (*model.User, error) {
    row := r.db.QueryRowContext(ctx,
        "SELECT id, email, name, age FROM users WHERE id = $1", id)
    var u model.User
    if err := row.Scan(&u.ID, &u.Email, &u.Name, &u.Age); err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, nil
        }
        return nil, err
    }
    return &u, nil
}

func (r *UserRepository) List(ctx context.Context) ([]model.User, error) {
    rows, err := r.db.QueryContext(ctx,
        "SELECT id, email, name, age FROM users ORDER BY name")
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var users []model.User
    for rows.Next() {
        var u model.User
        if err := rows.Scan(&u.ID, &u.Email, &u.Name, &u.Age); err != nil {
            return nil, err
        }
        users = append(users, u)
    }
    return users, rows.Err()
}

func (r *UserRepository) Update(ctx context.Context, u *model.User) error {
    _, err := r.db.ExecContext(ctx,
        "UPDATE users SET email=$1, name=$2, age=$3 WHERE id=$4",
        u.Email, u.Name, u.Age, u.ID)
    return err
}

func (r *UserRepository) Delete(ctx context.Context, id string) error {
    _, err := r.db.ExecContext(ctx, "DELETE FROM users WHERE id=$1", id)
    return err
}
```

## handler/user.go

```go
package handler

import (
    "encoding/json"
    "fmt"
    "net/http"
    "time"
    "myapi/internal/repository"
    "myapi/internal/model"
    "github.com/go-chi/chi/v5"
)

type UserHandler struct {
    repo *repository.UserRepository
}

func NewUserHandler(repo *repository.UserRepository) *UserHandler {
    return &UserHandler{repo: repo}
}

func (h *UserHandler) List(w http.ResponseWriter, r *http.Request) {
    users, err := h.repo.List(r.Context())
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    if users == nil {
        users = []model.User{}
    }
    json.NewEncoder(w).Encode(users)
}

func (h *UserHandler) GetByID(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    user, err := h.repo.FindByID(r.Context(), id)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    if user == nil {
        http.Error(w, "not found", http.StatusNotFound)
        return
    }
    json.NewEncoder(w).Encode(user)
}

func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    var req model.CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "invalid request", http.StatusBadRequest)
        return
    }

    user := &model.User{
        ID:    generateID(),
        Email: req.Email,
        Name:  req.Name,
        Age:   req.Age,
    }
    if err := h.repo.Create(r.Context(), user); err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(user)
}

func generateID() string { return "usr_" + fmt.Sprintf("%x", time.Now().UnixNano()) }
```

## Docker and Docker Compose

```dockerfile
# Dockerfile (multi-stage)
FROM golang:1.22 AS build
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o server ./cmd/server

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /app/server /server
EXPOSE 8080
CMD ["/server"]
```

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapi
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d

  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      DATABASE_URL: postgres://postgres:postgres@db:5432/myapi?sslmode=disable
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

---

## Cross-Links

- [[Go/02_Core/04_NetHTTP_Server_Middleware_and_Clients]] for HTTP and middleware
- [[Go/02_Core/06_Database_SQL_and_Migrations]] for database patterns
- [[Go/04_Playbooks/04_Production_Readiness_Checklist]] for production settings
