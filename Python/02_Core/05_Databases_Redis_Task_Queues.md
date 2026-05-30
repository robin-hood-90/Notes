---
tags: [python, core, databases, sqlalchemy, asyncpg, redis, celery, alembic, motor]
aliases: ["Databases", "SQLAlchemy", "Alembic", "asyncpg", "Redis", "Celery", "Motor", "Task Queues"]
status: stable
updated: 2026-05-29
---

# Databases, Redis, and Task Queues

> [!summary] Goal
> Master Python database access — SQLAlchemy 2.0 ORM + Core, Alembic migrations, async drivers (asyncpg, aiosqlite, Motor), Redis caching and pub/sub, and task queues (Celery, RQ). Covers both sync and async patterns.

## Table of Contents

1. [SQLAlchemy 2.0 ORM](#sqlalchemy-20-orm)
2. [SQLAlchemy Core](#sqlalchemy-core)
3. [Alembic Migrations](#alembic-migrations)
4. [Async Drivers](#async-drivers)
5. [Redis](#redis)
6. [Celery](#celery)
7. [RQ](#rq)
8. [Connection Pooling](#connection-pooling)
9. [Pitfalls](#pitfalls)

---

## SQLAlchemy 2.0 ORM

> [!info] SQLAlchemy 2.0 (released 2023) unifies sync and async APIs
> The ORM provides a high-level, Pythonic way to interact with relational databases.

```python
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column

# Models
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)

    def __repr__(self):
        return f"User(id={self.id}, name={self.name})"

# Engine and session
engine = create_engine("postgresql://user:pass@localhost/db", echo=True)
Base.metadata.create_all(engine)          # Create tables

with Session(engine) as session:
    # Insert
    user = User(name="Alice", email="alice@example.com", age=30)
    session.add(user)
    session.commit()

    # Query
    stmt = select(User).where(User.name == "Alice")
    result = session.execute(stmt).scalar_one()
    print(result)

    # Update
    user.age = 31
    session.commit()

    # Relationship
    class Post(Base):
        __tablename__ = "posts"
        id: Mapped[int] = mapped_column(primary_key=True)
        title: Mapped[str]
        user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
        author: Mapped[User] = relationship(back_populates="posts")

    User.posts = relationship("Post", back_populates="author")
```

### Async ORM

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

async def get_user(name: str):
    async with AsyncSession(async_engine) as session:
        stmt = select(User).where(User.name == name)
        result = await session.execute(stmt)
        return result.scalar_one()
```

---

## SQLAlchemy Core

> [!info] SQLAlchemy Core provides a lower-level SQL abstraction
> Use Core when you need raw SQL control with Python composition.

```python
from sqlalchemy import Table, MetaData, text

metadata = MetaData()
users = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100)),
    Column("email", String(255)),
)

# Insert
with engine.connect() as conn:
    conn.execute(users.insert().values(name="Bob", email="bob@test.com"))
    conn.commit()

# Select
with engine.connect() as conn:
    result = conn.execute(users.select().where(users.c.name == "Bob"))
    for row in result:
        print(row.name, row.email)

# Raw SQL
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users WHERE age > :min_age"),
                          {"min_age": 18})
```

### ORM vs Core

| Aspect | ORM | Core |
|--------|:---:|:----:|
| Productivity | High (Python objects) | Medium (SQL constructs) |
| Performance | Good (with lazy loading) | Better (no identity map) |
| Complex queries | Can be awkward | Natural |
| Async support | ✅ Yes | ✅ Yes |

---

## Alembic Migrations

```python
# pip install alembic
# alembic init migrations

# alembic/env.py
from myapp.models import Base
target_metadata = Base.metadata

# Create migration
# alembic revision --autogenerate -m "add users table"

# migrations/versions/xxxx_add_users.py
def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), unique=True),
    )

def downgrade():
    op.drop_table("users")

# Run migrations
# alembic upgrade head          # Apply all pending
# alembic downgrade -1          # Rollback one
# alembic history               # Migration history
```

---

## Async Drivers

### asyncpg

```python
import asyncpg

async def main():
    conn = await asyncpg.connect(
        user="user", password="pass", database="db", host="localhost"
    )
    rows = await conn.fetch("SELECT * FROM users WHERE age > $1", 18)
    for row in rows:
        print(row["name"], row["email"])
    await conn.close()

# Connection pool
pool = await asyncpg.create_pool(min_size=5, max_size=20)
async with pool.acquire() as conn:
    result = await conn.fetchval("SELECT count(*) FROM users")
```

### aiosqlite

```python
import aiosqlite

async def main():
    async with aiosqlite.connect("data.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cursor:
            async for row in cursor:
                print(row["name"])
```

### Motor (async MongoDB)

```python
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client.mydatabase
collection = db.users

async def main():
    # Insert
    result = await collection.insert_one({"name": "Alice", "age": 30})

    # Query
    user = await collection.find_one({"name": "Alice"})

    # Aggregation
    pipeline = [{"$group": {"_id": "$age", "count": {"$sum": 1}}}]
    async for doc in collection.aggregate(pipeline):
        print(doc)
```

---

## Redis

```python
import redis.asyncio as aioredis

# Connection
r = await aioredis.from_url("redis://localhost:6379", decode_responses=True)

# String
await r.set("key", "value")
value = await r.get("key")       # "value"

# Hash
await r.hset("user:1", mapping={"name": "Alice", "age": "30"})
name = await r.hget("user:1", "name")

# List
await r.lpush("queue", "task1")
task = await r.brpop("queue")    # Blocking pop

# Set
await r.sadd("tags", "python", "async")
members = await r.smembers("tags")

# Expiry
await r.setex("cache:key", 3600, "cached_value")   # Expire in 1 hour

# Pub/Sub
pubsub = r.pubsub()
await pubsub.subscribe("channel")
async for message in pubsub.listen():
    if message["type"] == "message":
        print(message["data"])

# Redis as cache with serialization
import json

async def get_user(user_id: int):
    cached = await r.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    user = await fetch_from_db(user_id)
    await r.setex(f"user:{user_id}", 300, json.dumps(user, default=str))
    return user
```

---

## Celery

> [!info] Celery is a distributed task queue
> It runs tasks asynchronously (in worker processes) and can schedule periodic tasks. It needs a message broker (Redis or RabbitMQ).

```python
# tasks.py
from celery import Celery

app = Celery("myapp",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

@app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_email(self, to: str, subject: str, body: str):
    try:
        # Actually send email
        mailer.send(to, subject, body)
    except ConnectionError as exc:
        raise self.retry(exc=exc)

@app.task
def process_image(image_path: str):
    # CPU-intensive work
    return transform_image(image_path)

# Periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    "send-daily-digest": {
        "task": "tasks.send_daily_digest",
        "schedule": crontab(hour=8, minute=0),
    },
}

# Running:
# celery -A tasks worker --loglevel=info         # Start worker
# celery -A tasks beat --loglevel=info            # Start scheduler
```

```python
# Calling tasks
from tasks import send_email, process_image

# Async
result = send_email.delay("user@example.com", "Hello", "Body")

# With arguments
result = process_image.apply_async(args=["/path/to/image.jpg"],
                                   queue="high_priority")

# Check result
result.id                    # Task ID
result.ready()               # Bool
result.get(timeout=10)       # Block until done
result.traceback             # Error traceback if failed

# Task chaining
from celery import chain
chain = chain(
    process_image.s("/path/to/image.jpg"),
    send_email.s("admin@example.com", "Done", "Image processed"),
)
chain()
```

---

## RQ

> [!info] RQ (Redis Queue) is a simpler alternative to Celery
> It uses Redis as the broker and has minimal configuration.

```python
# tasks.py
import time
from rq import Queue
from redis import Redis

redis_conn = Redis()
queue = Queue(connection=redis_conn)

def send_email(to, subject):
    time.sleep(2)
    print(f"Sent email to {to}")

# Enqueue
job = queue.enqueue(send_email, "user@example.com", "Hello")
job.id                   # Job ID
job.result               # None (not done yet)

# Delay
job = queue.enqueue_in(timedelta(hours=1), send_email, "user@test.com", "Later")

# Running: rq worker

# RQ vs Celery
# Celery: distributed, scheduled tasks, multiple brokers, complex
# RQ: simple, Redis-only, fewer features, easier to debug
```

---

## Connection Pooling

```python
# SQLAlchemy
engine = create_engine(
    "postgresql://user:pass@localhost/db",
    pool_size=5,               # Connections kept in pool
    max_overflow=10,           # Extra connections allowed
    pool_timeout=30,           # Wait for connection (seconds)
    pool_pre_ping=True,        # Health check before use
)

# asyncpg
pool = await asyncpg.create_pool(
    min_size=5,
    max_size=20,
    command_timeout=60,
)

# Redis
r = await aioredis.from_url(
    "redis://localhost:6379",
    max_connections=20,
    socket_connect_timeout=5,
    socket_timeout=10,
)

# Always close pools on shutdown
async def shutdown():
    await pool.close()
    await r.close()
```

---

## Pitfalls

### N+1 queries in ORM

```python
# ❌ N+1: 1 query for posts + N queries for authors
posts = session.execute(select(Post)).scalars()
for post in posts:
    print(post.author.name)      # Triggers a query per post!

# ✅ Eager loading
stmt = select(Post).options(joinedload(Post.author))
posts = session.execute(stmt).scalars()
```

### Not using connection pools

Creating a new database connection for every request is slow and exhausts resources. Always use a pool.

### Async in sync code / sync in async code

```python
# ❌ Blocking the event loop
async def get_user():
    user = sync_query()        # Blocks event loop!
    return user

# ✅ Use async driver
async def get_user():
    async with AsyncSession(engine) as session:
        return await session.get(User, 1)
```

### Celery task serialization

Celery tasks must be serializable (pickle or JSON). Avoid passing complex objects or database connections as arguments.

### Redis key naming conventions

Use `:` as separator (like `user:123:email`). Keep keys short but meaningful. Set TTL for cache keys.

---

> [!question]- Interview Questions
>
> **Q: What's the difference between SQLAlchemy ORM and Core?**
> A: ORM maps database rows to Python objects (productivity, identity map, lazy loading). Core uses SQL expression language (more control, better for complex queries, less overhead). Use ORM for CRUD, Core for analytics and bulk operations.
>
> **Q: When would you use Celery vs RQ?**
> A: Celery for distributed systems with multiple workers, scheduled tasks (beat), multiple brokers (Redis, RabbitMQ, SQS), and complex routing. RQ for simpler needs where Redis is already in the stack and you want minimal configuration.
>
> **Q: How do you handle connection pooling?**
> A: Use the pool built into the library (SQLAlchemy `pool_size`, asyncpg `create_pool`, Redis `max_connections`). Configure min/max sizes based on expected concurrency. Always close the pool on shutdown. Use `pool_pre_ping=True` (SQLAlchemy) to detect stale connections.

---

## Cross-Links

- [[Python/02_Core/06_Web_Frameworks_FastAPI]] for FastAPI database integration
- [[Python/01_Foundations/11_Async_Python_Basics]] for async patterns
- [[Python/05_Projects/01_REST_API_FastAPI_Postgres]] for database project
- [[Python/04_Playbooks/03_Production_Readiness]] for production database config
