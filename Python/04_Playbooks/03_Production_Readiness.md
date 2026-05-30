---
tags: [python, playbook, production, logging, config, docker, monitoring, ci-cd]
aliases: ["Production Readiness", "Logging", "Configuration", "Docker", "Monitoring", "CI/CD"]
status: stable
updated: 2026-05-29
---

# Playbook: Production Readiness

> [!summary] Goal
> Ensure Python applications are production-ready — logging configuration, secrets management, Docker packaging, health checks, graceful shutdown, CI/CD, and monitoring.

## Table of Contents

1. [Logging Configuration](#logging-configuration)
2. [Configuration and Secrets](#configuration-and-secrets)
3. [Docker](#docker)
4. [Health Checks and Graceful Shutdown](#health-checks-and-graceful-shutdown)
5. [CI/CD](#cicd)
6. [Monitoring](#monitoring)
7. [Pitfalls](#pitfalls)

---

## Logging Configuration

```python
# logging_config.py — structured JSON logging for production
import logging
import logging.config
import json

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": json.dumps({
                "timestamp": "%(asctime)s",
                "level": "%(levelname)s",
                "name": "%(name)s",
                "message": "%(message)s",
            }),
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "json" if __debug__ else "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "json",
            "filename": "logs/app.log",
            "maxBytes": 10 * 1024 * 1024,    # 10 MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "uvicorn": {"level": "WARNING", "handlers": ["console"], "propagate": False},
        "sqlalchemy": {"level": "WARNING", "handlers": ["console"], "propagate": False},
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
```

### Correlation IDs

```python
import uuid
import logging
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="")

class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id.get()
        return True

logging.getLogger().addFilter(CorrelationFilter())

# In middleware / entry point
def handle_request(request):
    token = request_id.set(str(uuid.uuid4()))
    try:
        logger.info("Handling request")     # Includes request_id
    finally:
        request_id.reset(token)
```

---

## Configuration and Secrets

```python
# settings.py — pydantic-settings for all config
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        secrets_dir="/run/secrets",         # Docker secrets
    )

    app_name: str = "myapp"
    debug: bool = False
    log_level: str = "INFO"

    # Database
    database_url: str
    database_pool_size: int = 5

    # Redis
    redis_url: str = "redis://localhost:6379"

    # External services
    auth_service_url: str
    api_key: str                            # From env or secret file

    # Feature flags
    enable_feature_x: bool = False

settings = Settings()

# Load secrets from environment, .env, or Docker secrets
# Precedence: env vars > .env file > defaults
# Docker secrets: /run/secrets/api_key file = "api_key"
```

### Secret management checklist

- ✅ No secrets in code — use env vars or secret store
- ✅ `.env` in `.gitignore` (example file: `.env.example`)
- ✅ Docker secrets for containerised apps
- ✅ Vault / AWS Secrets Manager for production
- ✅ Don't log secrets — add `SecretStr` type in Pydantic

---

## Docker

```dockerfile
# Dockerfile — multi-stage build for production
FROM python:3.12-slim AS builder

WORKDIR /app
COPY pyproject.toml .
RUN pip install --user --no-cache-dir .

FROM python:3.12-slim
WORKDIR /app

# Copy only installed packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Non-root user
RUN groupadd -r app && useradd -r -g app app
USER app

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/db
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:16-alpine
    volumes: ["pgdata:/var/lib/postgresql/data"]
    environment:
      POSTGRES_DB: mydb
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

---

## Health Checks and Graceful Shutdown

```python
# FastAPI health check
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.db = await create_pool()
    yield
    # Shutdown
    await app.state.db.close()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        await app.state.db.fetch("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

@app.get("/ready")
async def ready():
    """Readiness check (load balancer)."""
    return {"status": "ready"}
```

### Graceful shutdown (non-FastAPI)

```python
import asyncio, signal

async def shutdown(loop, service):
    print("Shutting down...")
    await service.stop()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def main():
    service = MyService()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig, lambda: asyncio.create_task(shutdown(loop, service))
        )
    await service.run()
```

---

## CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
      redis:
        image: redis:7

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install .[dev]

      - name: Lint
        run: |
          ruff check src/
          mypy src/ --strict

      - name: Test
        run: |
          pytest tests/ -v --cov=src --cov-report=xml
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:testpass@localhost:5432/postgres
          REDIS_URL: redis://localhost:6379

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Monitoring

```python
# Prometheus metrics with prometheus_client
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from fastapi import Response
import time

REQUESTS = Counter("http_requests_total", "Total requests", ["method", "endpoint"])
LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    REQUESTS.labels(method=request.method, endpoint=request.url.path).inc()
    start = time.time()
    response = await call_next(request)
    LATENCY.labels(method=request.method, endpoint=request.url.path).observe(
        time.time() - start
    )
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(REGISTRY), media_type="text/plain")
```

---

## Pitfalls

### Logging secrets

```python
# ❌ Logging credentials
logger.info(f"Connected to {database_url}")  # Exposes password!

# ✅ Redact
from urllib.parse import urlparse
parsed = urlparse(database_url)
logger.info(f"Connected to {parsed.hostname}:{parsed.port}")
```

### Hardcoding config values

```python
# ❌
DB_URL = "postgresql://localhost/mydb"

# ✅ Environment variable
DB_URL = os.getenv("DATABASE_URL", "postgresql://localhost/mydb")
```

### Not setting Docker healthchecks

Healthchecks let the orchestrator know when your app is alive and ready. Without them, containers may serve traffic before they're ready.

### Forgetting `.dockerignore`

```dockerignore
# .dockerignore
__pycache__/
*.pyc
.env
.git/
.venv/
tests/
*.md
```

### Unhandled signals

Always handle `SIGTERM` for graceful shutdown. Without it, `docker stop` sends `SIGTERM`, and after 10s sends `SIGKILL`. Unclean shutdowns can corrupt data.

---

> [!question]- Interview Questions
>
> **Q: How do you handle configuration in production Python apps?**
> A: Use `pydantic-settings` to load from environment variables, `.env` files, or Docker secrets. Never hardcode config. Validation is automatic (URL format, port ranges, etc.). The `Settings` class is a single source of truth with IDE support.
>
> **Q: What's the difference between liveness and readiness probes?**
> A: Liveness (`/health`) tells the orchestrator if the app is alive (restart if fails). Readiness (`/ready`) tells if the app is ready to serve traffic (remove from load balancer if fails). Liveness failing → restart. Readiness failing → stop sending requests but don't restart.
>
> **Q: How do you handle graceful shutdown?**
> A: Catch `SIGTERM` and `SIGINT`. Stop accepting new requests. Complete in-flight requests (with a deadline). Close connections (DB pool, Redis). Cancel background tasks. If not clean within the grace period, exit anyway. In Docker, `STOPSIGNAL SIGTERM` with `stop_grace_period` configured.

---

## Cross-Links

- [[Python/02_Core/06_Web_Frameworks_FastAPI]] for FastAPI deployment
- [[Python/02_Core/13_Packaging_Distribution]] for Docker multi-stage builds
- [[Python/02_Core/05_Databases_Redis_Task_Queues]] for connection pooling
- [[Python/04_Playbooks/01_Debug_Memory_Leaks]] for memory debugging in production
