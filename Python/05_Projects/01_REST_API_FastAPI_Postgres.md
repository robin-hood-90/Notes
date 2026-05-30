---
tags: [python, project, fastapi, sqlalchemy, postgres, docker, pytest]
aliases: ["Project: REST API", "FastAPI + PostgreSQL Project", "FastAPI Project"]
status: draft
updated: 2026-05-29
---

# Project: REST API — FastAPI + PostgreSQL

> [!summary] Goal
> Build a production-grade REST API with FastAPI, SQLAlchemy 2.0 async, Alembic migrations, Pydantic v2, pytest, and Docker Compose.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Models](#models)
3. [API Endpoints](#api-endpoints)
4. [Dependencies](#dependencies)
5. [Testing](#testing)
6. [Deployment](#deployment)

---

## Project Structure

```
myapi/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, lifespan, middleware
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── database.py          # Engine, session factory
│   ├── repositories.py      # Database access layer
│   ├── services.py          # Business logic
│   ├── dependencies.py      # FastAPI dependencies
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── items.py
│   └── settings.py          # pydantic-settings
├── tests/
│   ├── conftest.py
│   ├── test_users.py
│   └── test_items.py
├── migrations/
│   └── versions/
├── alembic.ini
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

---

## Models

```python
# src/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime, func

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    items: Mapped[list["Item"]] = relationship(back_populates="owner")

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(1000))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    owner: Mapped[User] = relationship(back_populates="items")
```

---

## API Endpoints

```python
# src/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.schemas import UserCreate, UserResponse
from src.services import UserService
from src.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.create(data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

```python
# src/schemas.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    email: str
    created_at: datetime
```

---

## Testing

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
async def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post("/users/", json={
        "name": "Alice",
        "email": "alice@test.com",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert "id" in data
```

---

## Deployment

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+asyncpg://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_PASSWORD: pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
```

```bash
# Run
docker compose up --build

# Migrate
docker compose exec api alembic upgrade head

# Test
pytest tests/ -v --cov=src
```

---

## Cross-Links

- [[Python/02_Core/06_Web_Frameworks_FastAPI]] for FastAPI reference
- [[Python/02_Core/05_Databases_Redis_Task_Queues]] for SQLAlchemy reference
- [[Python/01_Foundations/10_Testing_with_Pytest]] for testing patterns
- [[Python/04_Playbooks/03_Production_Readiness]] for deployment
