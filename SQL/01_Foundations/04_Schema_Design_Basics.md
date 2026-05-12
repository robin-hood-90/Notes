---
tags: [sql, postgresql, foundations, schema, normalization, data-types]
aliases: ["Database Schema", "Table Design", "Normalization"]
status: stable
updated: 2026-04-26
---

# Schema Design Basics

> [!summary] Model
> Database schema design balances normalization (data integrity) with denormalization (performance). Master PostgreSQL data types, constraints, relationships, and indexing strategies. Choose appropriate structures for your access patterns and data integrity requirements.

## Table of Contents

1. [[#Data Types]]
2. [[#Normalization]]
3. [[#Constraints]]
4. [[#Primary and Foreign Keys]]
5. [[#Indexes and Performance]]
6. [[#Views and Abstractions]]
7. [[#Design Patterns]]
8. [[#Best Practices]]
9. [[#Interview Questions]]

---

## Data Types

### Numeric Types

```sql
-- Integer types
CREATE TABLE products (
    id SERIAL PRIMARY KEY,              -- Auto-incrementing integer
    quantity SMALLINT,                  -- -32,768 to +32,767
    stock INTEGER,                      -- -2B to +2B
    big_number BIGINT                   -- -9Q to +9Q
);

-- Decimal types
CREATE TABLE financial (
    id SERIAL PRIMARY KEY,
    price DECIMAL(10,2),                -- Exact decimal, 8 digits before, 2 after
    interest_rate NUMERIC(5,4),         -- 5 total digits, 4 after decimal
    balance MONEY                       -- Currency with $ symbol
);
```

**Why choose specific numeric types?** Storage efficiency and precision requirements.

**How they work:** SMALLINT (2 bytes), INTEGER (4 bytes), BIGINT (8 bytes), DECIMAL exact precision.

**When to use:**
- SMALLINT: Limited range values (status codes, ratings)
- INTEGER: Standard counters, IDs
- BIGINT: Large counts, timestamps
- DECIMAL: Financial calculations requiring exact precision

### Character Types

```sql
-- Character types
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,      -- Variable length, max 50 chars
    email VARCHAR(255) UNIQUE,          -- Variable length, max 255 chars
    bio TEXT,                           -- Unlimited length text
    status CHAR(1) DEFAULT 'A'          -- Fixed length, exactly 1 char
);

-- PostgreSQL-specific
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    tags TEXT[],                        -- Array of strings
    metadata JSONB                      -- JSON binary data
);
```

**Why VARCHAR vs TEXT?** VARCHAR has length limit enforcement, TEXT is more flexible.

**How they work:** VARCHAR(n) stores up to n characters; TEXT stores unlimited; CHAR(n) pads with spaces.

**When to use:**
- VARCHAR(n): Known maximum length, want constraint enforcement
- TEXT: Large content, no length limits
- CHAR(n): Fixed-width codes (status, flags)

### Date/Time Types

```sql
-- Date and time types
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_date DATE,                    -- Date only (YYYY-MM-DD)
    start_time TIME,                    -- Time only (HH:MM:SS)
    created_at TIMESTAMP,               -- Date + time without timezone
    updated_at TIMESTAMPTZ,             -- Date + time with timezone
    duration INTERVAL                   -- Time intervals
);

-- Usage
INSERT INTO events VALUES
(1, '2023-12-25', '14:30:00', '2023-12-25 14:30:00', '2023-12-25 14:30:00+05:30', '2 hours');

-- Timezone handling
SELECT created_at AT TIME ZONE 'UTC' FROM events;
SELECT updated_at AT TIME ZONE 'America/New_York' FROM events;
```

**Why TIMESTAMPTZ over TIMESTAMP?** Timezone-aware storage prevents ambiguity.

**How they work:** TIMESTAMP stores date+time as-is; TIMESTAMPTZ converts to UTC internally.

**When to use:**
- DATE: Birth dates, event dates (no time needed)
- TIME: Daily schedules, recurring times
- TIMESTAMP: Local timestamps, no timezone concerns
- TIMESTAMPTZ: Global applications, user-facing times, audit trails

### PostgreSQL-Specific Types

```sql
-- UUID for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Arrays
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    tags TEXT[],                        -- Array of tags
    images TEXT[],                      -- Array of image URLs
    prices DECIMAL[]                    -- Array of price history
);

-- JSONB for flexible data
CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY,
    profile_data JSONB,                 -- Flexible profile information
    settings JSONB
);

-- ENUM for controlled vocabularies
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    status user_status DEFAULT 'active'
);
```

**Why use these types?** Better data integrity, PostgreSQL optimizations, native operations.

**How they work:** UUID generates unique IDs; arrays store multiple values; JSONB indexes and queries JSON; ENUM constrains to specific values.

**When to use:**
- UUID: Distributed systems, security (hard to guess)
- Arrays: Multiple values per row, tags, categories
- JSONB: Flexible schemas, user preferences, metadata
- ENUM: Status fields, categories with fixed options

---

## Normalization

### First Normal Form (1NF)

**Definition:** Eliminate repeating groups, ensure atomic values.

```sql
-- ❌ Not 1NF: Repeating groups
CREATE TABLE orders_bad (
    order_id INTEGER,
    customer_name TEXT,
    product1_name TEXT, product1_qty INTEGER,
    product2_name TEXT, product2_qty INTEGER,
    product3_name TEXT, product3_qty INTEGER
);

-- ✅ 1NF: Atomic values, no repeating groups
CREATE TABLE orders (
    order_id INTEGER,
    customer_name TEXT
);

CREATE TABLE order_items (
    order_id INTEGER,
    product_name TEXT,
    quantity INTEGER
);
```

**Why 1NF?** Eliminates data redundancy and update anomalies.

**How to achieve:** Split tables so each field contains single values.

**When to apply:** Always - foundation of good schema design.

### Second Normal Form (2NF)

**Definition:** 1NF + no partial dependencies (non-key fields depend on entire primary key).

```sql
-- ❌ Not 2NF: Partial dependency
CREATE TABLE order_items_bad (
    order_id INTEGER,
    product_id INTEGER,
    product_name TEXT,          -- Depends only on product_id
    quantity INTEGER,
    PRIMARY KEY (order_id, product_id)
);

-- ✅ 2NF: Separate partial dependencies
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT
);
```

**Why 2NF?** Eliminates redundant data storage and update inconsistencies.

**How to achieve:** Move fields that depend on part of key to separate tables.

**When to apply:** Composite primary keys with partial dependencies.

### Third Normal Form (3NF)

**Definition:** 2NF + no transitive dependencies (non-key fields don't depend on other non-key fields).

```sql
-- ❌ Not 3NF: Transitive dependency
CREATE TABLE employees_bad (
    employee_id INTEGER PRIMARY KEY,
    employee_name TEXT,
    department_id INTEGER,
    department_name TEXT,       -- Depends on department_id, not employee_id
    department_location TEXT    -- Also depends on department_id
);

-- ✅ 3NF: Separate transitive dependencies
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    employee_name TEXT,
    department_id INTEGER REFERENCES departments(department_id)
);

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT,
    department_location TEXT
);
```

**Why 3NF?** Eliminates update, insert, and delete anomalies.

**How to achieve:** Move fields that depend on other non-key fields to separate tables.

**When to apply:** When non-key fields reference other non-key fields.

### Denormalization

**When to denormalize:** Read-heavy workloads, performance-critical queries.

```sql
-- Normalized (3NF)
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date DATE
);

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
);

-- Denormalized (for performance)
CREATE TABLE orders_denorm (
    order_id INTEGER PRIMARY KEY,
    customer_name TEXT,         -- Denormalized
    customer_email TEXT,        -- Denormalized
    order_date DATE
);
```

**Why denormalize?** Faster reads, fewer joins, simpler queries.

**How to implement:** Duplicate data, use triggers to maintain consistency.

**When to use:** Reporting databases, data warehouses, read-heavy OLTP.

---

## Constraints

### Primary Key Constraints

```sql
-- Single column primary key
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL
);

-- Composite primary key
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    PRIMARY KEY (order_id, product_id)
);

-- Natural vs surrogate keys
CREATE TABLE countries (
    code CHAR(3) PRIMARY KEY,           -- Natural key
    name TEXT NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,              -- Surrogate key
    username TEXT UNIQUE NOT NULL
);
```

**Why primary keys?** Uniquely identify rows, enable relationships, provide indexing.

**How they work:** Automatically create unique indexes, enforce NOT NULL.

**When to use:** Every table needs a primary key.

### Foreign Key Constraints

```sql
-- Basic foreign key
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date DATE
);

-- With actions
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id)
        ON DELETE CASCADE              -- Delete orders when customer deleted
        ON UPDATE RESTRICT,            -- Prevent customer ID changes
    order_date DATE
);

-- Self-referencing
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name TEXT,
    manager_id INTEGER REFERENCES employees(id)
);
```

**Why foreign keys?** Maintain referential integrity, prevent orphaned records.

**How they work:** Validate references exist, can cascade operations.

**When to use:** All relationships between tables.

### Check Constraints

```sql
-- Basic check
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price DECIMAL CHECK (price > 0),
    quantity INTEGER CHECK (quantity >= 0)
);

-- Complex checks
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT CHECK (email LIKE '%@%'),
    age INTEGER CHECK (age >= 18 AND age <= 120),
    status TEXT CHECK (status IN ('active', 'inactive', 'suspended'))
);

-- Table-level checks
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    start_date DATE,
    end_date DATE,
    CHECK (end_date >= start_date)
);
```

**Why check constraints?** Enforce business rules at database level.

**How they work:** Validate conditions before insert/update.

**When to use:** Data validation, business rules, range limits.

### Unique Constraints

```sql
-- Single column unique
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE,
    username TEXT
);

-- Multiple unique constraints
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT,
    username TEXT,
    UNIQUE (email),
    UNIQUE (username)
);

-- Composite unique
CREATE TABLE user_permissions (
    user_id INTEGER REFERENCES users(id),
    permission TEXT,
    UNIQUE (user_id, permission)        -- User can't have duplicate permissions
);
```

**Why unique constraints?** Prevent duplicate values, enforce business rules.

**How they work:** Create unique indexes, reject duplicates.

**When to use:** Natural keys, business uniqueness requirements.

### Exclusion Constraints

```sql
-- Prevent overlapping date ranges
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    room_id INTEGER,
    check_in DATE,
    check_out DATE,
    EXCLUDE (room_id WITH =, daterange(check_in, check_out) WITH &&)
);

-- Prevent double-booking
INSERT INTO reservations (room_id, check_in, check_out) VALUES
(1, '2023-12-01', '2023-12-05');  -- OK

INSERT INTO reservations (room_id, check_in, check_out) VALUES
(1, '2023-12-03', '2023-12-07');  -- ERROR: overlaps
```

**Why exclusion constraints?** Complex business rules like no overlaps, resource conflicts.

**How they work:** Use GiST indexes to check complex conditions.

**When to use:** Scheduling, resource allocation, complex uniqueness rules.

---

## Primary and Foreign Keys

### Primary Key Design

```sql
-- Surrogate keys (recommended)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL
);

-- Natural keys (sometimes)
CREATE TABLE countries (
    iso_code CHAR(3) PRIMARY KEY,
    name TEXT NOT NULL
);

-- Composite keys
CREATE TABLE user_permissions (
    user_id INTEGER,
    permission_id INTEGER,
    PRIMARY KEY (user_id, permission_id)
);
```

**Why surrogate keys?** Simple, never change, auto-generated.

**How to choose:** Surrogate for most cases, natural only when stable and meaningful.

**When to use composite:** Many-to-many relationships, natural composite identifiers.

### Foreign Key Relationships

```sql
-- One-to-many
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id)
);

-- Many-to-many
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- One-to-one
CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    bio TEXT,
    avatar_url TEXT
);
```

**Why relationships?** Maintain data integrity, enable joins.

**How they work:** Foreign keys reference primary keys, enforce existence.

**When to model:** Entity relationships in your domain.

### Foreign Key Actions

```sql
-- CASCADE: Propagate deletes/updates
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE RESTRICT
);

-- SET NULL: Clear references
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- RESTRICT: Prevent if references exist
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    manager_id INTEGER REFERENCES employees(id) ON DELETE RESTRICT
);
```

**Why actions?** Handle related data when parent records change.

**How they work:** Automatically maintain consistency on changes.

**When to use:**
- CASCADE: Parent-child hierarchies
- SET NULL: Optional relationships
- RESTRICT: Prevent accidental deletions

---

## Indexes and Performance

### Index Basics

```sql
-- Single column index
CREATE INDEX ON users (email);

-- Composite index
CREATE INDEX ON orders (customer_id, order_date);

-- Unique index
CREATE UNIQUE INDEX ON users (lower(email));

-- Partial index
CREATE INDEX ON orders (customer_id) WHERE status = 'active';

-- Expression index
CREATE INDEX ON users (lower(email));
```

**Why indexes?** Speed up queries, enforce uniqueness.

**How they work:** B-Tree structure for fast lookups.

**When to index:** Foreign keys, WHERE clauses, JOIN conditions, ORDER BY.

### Index Types

```sql
-- Hash index (equality only)
CREATE INDEX CONCURRENTLY ON users USING HASH (status);

-- GIN index (arrays, full-text)
CREATE INDEX ON products USING GIN (tags);

-- GiST index (geometric, ranges)
CREATE INDEX ON events USING GIST (period);

-- BRIN index (large ordered tables)
CREATE INDEX ON logs USING BRIN (created_at);
```

**Why different types?** Optimized for specific data types and query patterns.

**How to choose:** B-Tree for general use, specialized for specific needs.

**When to use each:** B-Tree (default), GIN (arrays/JSON), BRIN (time-series).

### Index Maintenance

```sql
-- Reindex (blocking)
REINDEX INDEX users_email_idx;

-- Concurrent reindex (non-blocking)
REINDEX INDEX CONCURRENTLY users_email_idx;

-- Reindex table
REINDEX TABLE users;

-- Monitor index usage
SELECT schemaname, tablename, indexname,
       idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

**Why maintenance?** Indexes can become bloated or corrupted.

**How to monitor:** pg_stat_user_indexes shows usage statistics.

**When to reindex:** After bulk operations, if bloat detected.

---

## Views and Abstractions

### Basic Views

```sql
-- Simple view
CREATE VIEW active_users AS
SELECT id, name, email FROM users WHERE status = 'active';

-- Query like table
SELECT * FROM active_users WHERE name LIKE 'John%';

-- Complex view
CREATE VIEW order_summary AS
SELECT
    o.id,
    u.name as customer_name,
    o.order_date,
    o.total_amount,
    COUNT(oi.id) as item_count
FROM orders o
JOIN users u ON o.customer_id = u.id
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, u.name, o.order_date, o.total_amount;
```

**Why views?** Simplify complex queries, provide abstractions.

**How they work:** Stored queries executed when accessed.

**When to use:** Report queries, API endpoints, security.

### Materialized Views

```sql
-- Materialized view (pre-computed)
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT
    DATE_TRUNC('month', order_date) as month,
    SUM(total_amount) as total_sales,
    COUNT(*) as order_count
FROM orders
WHERE order_date >= '2023-01-01'
GROUP BY DATE_TRUNC('month', order_date);

-- Refresh periodically
REFRESH MATERIALIZED VIEW monthly_sales;

-- Refresh concurrently (non-blocking)
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales;
```

**Why materialized views?** Pre-compute expensive queries for fast access.

**How they work:** Store results on disk, refresh manually or automatically.

**When to use:** Expensive aggregations, slowly changing data.

---

## Design Patterns

### Audit Trail Pattern

```sql
-- Main table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    total_amount DECIMAL,
    status TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit table
CREATE TABLE order_audit (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    old_status TEXT,
    new_status TEXT,
    changed_by INTEGER REFERENCES users(id),
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger to populate audit
CREATE OR REPLACE FUNCTION audit_order_status() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO order_audit (order_id, old_status, new_status, changed_by)
        VALUES (NEW.id, OLD.status, NEW.status, NEW.updated_by);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER order_status_audit
    AFTER UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION audit_order_status();
```

**Why audit trails?** Track changes, compliance, debugging.

**How to implement:** Separate audit tables with triggers.

**When to use:** Financial data, user actions, regulatory requirements.

### Soft Delete Pattern

```sql
-- Soft delete instead of hard delete
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    deleted_at TIMESTAMPTZ,  -- NULL = active, NOT NULL = deleted
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for performance
CREATE INDEX ON users (deleted_at) WHERE deleted_at IS NULL;

-- "Delete" query
UPDATE users SET deleted_at = NOW() WHERE id = 123;

-- Active users view
CREATE VIEW active_users AS
SELECT * FROM users WHERE deleted_at IS NULL;

-- Include soft-deleted in reports
SELECT name, deleted_at FROM users WHERE deleted_at IS NOT NULL;
```

**Why soft deletes?** Preserve data for audit, allow undelete, maintain referential integrity.

**How to implement:** deleted_at column instead of actual DELETE.

**When to use:** User data, important business records.

### Polymorphic Associations

```sql
-- Single table for multiple entity types
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT,
    entity_type TEXT,  -- 'post', 'video', 'image'
    entity_id INTEGER, -- ID in respective table
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments for different entities
INSERT INTO comments (content, entity_type, entity_id, user_id) VALUES
('Great post!', 'post', 123, 456),
('Nice video!', 'video', 789, 456);

-- Query with joins
SELECT c.content, c.entity_type,
       COALESCE(p.title, v.title, i.filename) as entity_title
FROM comments c
LEFT JOIN posts p ON c.entity_type = 'post' AND c.entity_id = p.id
LEFT JOIN videos v ON c.entity_type = 'video' AND c.entity_id = v.id
LEFT JOIN images i ON c.entity_type = 'image' AND c.entity_id = i.id;
```

**Why polymorphic?** Single comments table for multiple entity types.

**How to implement:** entity_type + entity_id columns.

**When to use:** Comments, tags, ratings across different entities.

---

## Best Practices

### 1. Use Appropriate Data Types

```sql
-- ✅ Good: Semantic types
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    name TEXT,
    event_date DATE,
    start_time TIME,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ❌ Bad: Using text for everything
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    name TEXT,
    event_date TEXT,  -- Should be DATE
    start_time TEXT,  -- Should be TIME
    created_at TEXT   -- Should be TIMESTAMPTZ
);
```

### 2. Normalize, Then Denormalize Selectively

```sql
-- Start normalized
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    total DECIMAL
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT
);

-- Denormalize for performance if needed
ALTER TABLE orders ADD COLUMN customer_name TEXT;
-- Update with trigger to maintain
```

### 3. Use Constraints Liberally

```sql
-- ✅ Comprehensive constraints
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE CHECK (email LIKE '%@%'),
    age INTEGER CHECK (age >= 0 AND age <= 150),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. Index Foreign Keys and WHERE Clauses

```sql
-- ✅ Essential indexes
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date DATE,
    status TEXT
);

CREATE INDEX ON orders (customer_id);           -- Foreign key
CREATE INDEX ON orders (order_date);            -- Common filter
CREATE INDEX ON orders (status, order_date);    -- Composite for queries
```

### 5. Use Surrogate Keys for Relationships

```sql
-- ✅ Surrogate primary keys
CREATE TABLE users (
    id SERIAL PRIMARY KEY,      -- Surrogate
    email TEXT UNIQUE           -- Natural, but not PK
);

-- ❌ Natural primary keys that change
CREATE TABLE users (
    email TEXT PRIMARY KEY      -- Email can change!
);
```

### 6. Plan for Growth and Changes

```sql
-- ✅ Extensible design
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    metadata JSONB,             -- Flexible for future fields
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add new fields without schema changes
UPDATE products SET metadata = metadata || '{"weight": 1.5}' WHERE id = 1;
```

### 7. Document Your Schema

```sql
-- ✅ Self-documenting with comments
COMMENT ON TABLE users IS 'Registered system users';
COMMENT ON COLUMN users.email IS 'Unique email address for login';
COMMENT ON INDEX users_email_idx IS 'Speeds up email lookups for authentication';

-- View comments
SELECT obj_description('users'::regclass);
SELECT col_description('users'::regclass, 'email'::name);
```

### 8. Test Schema Changes

```sql
-- Test before applying to production
-- 1. Create test database
createdb schema_test

-- 2. Apply changes
psql -d schema_test -f schema_changes.sql

-- 3. Test queries
psql -d schema_test -f test_queries.sql

-- 4. Performance test
pgbench -d schema_test -f custom_test.sql
```

---

## Interview Questions

### Q1: Explain database normalization and its forms.

**Answer:** Normalization eliminates data redundancy and ensures data integrity through progressive forms:

**1NF (First Normal Form):** Eliminate repeating groups, ensure atomic values
- No arrays or multiple values in single field
- Each column contains single values

**2NF (Second Normal Form):** 1NF + no partial dependencies
- Non-key fields depend on entire primary key
- Remove fields that depend on part of composite key

**3NF (Third Normal Form):** 2NF + no transitive dependencies
- Non-key fields don't depend on other non-key fields
- Each field depends only on the primary key

**Example:**
```sql
-- Unnormalized
student: "John Doe", courses: ["Math101", "CS201"]

-- 1NF
students: id, name
student_courses: student_id, course_code

-- 2NF (if course_name depends only on course_code)
students: id, name
courses: code, name
student_courses: student_id, course_code

-- 3NF (if dept depends only on course)
students: id, name
courses: code, name, dept_id
departments: id, name
student_courses: student_id, course_code
```

### Q2: When should you denormalize a database?

**Answer:** Denormalize when read performance is critical and you're willing to accept update complexity:

**When to denormalize:**
- Read-heavy workloads (OLAP, reporting)
- Complex joins hurting performance
- Real-time query requirements
- Data warehouses

**Costs:**
- Update anomalies (data inconsistency)
- Increased storage
- Complex update logic (triggers, application code)
- Potential data integrity issues

**Example:**
```sql
-- Normalized (3NF)
orders: id, customer_id, total
customers: id, name, email

-- Denormalized for fast reports
orders: id, customer_name, customer_email, total

-- But now updates require:
UPDATE orders SET customer_name = 'New Name'
WHERE customer_id = 123;
-- Must update all historical orders!
```

### Q3: What's the difference between surrogate and natural keys?

**Answer:**

**Natural Keys:** Meaningful business identifiers
- Examples: email, SSN, ISBN, employee_id
- Pros: No additional columns, meaningful
- Cons: Can change, might not be unique, large size

**Surrogate Keys:** Database-generated artificial identifiers
- Examples: SERIAL, UUID, IDENTITY
- Pros: Never change, always unique, small size
- Cons: No business meaning, additional column

**Best practice:** Use surrogate keys for primary keys, natural keys for unique constraints when stable.

```sql
-- Good design
CREATE TABLE users (
    id SERIAL PRIMARY KEY,        -- Surrogate
    email TEXT UNIQUE NOT NULL,   -- Natural, unique
    employee_id TEXT UNIQUE       -- Natural, unique if stable
);
```

### Q4: How do you design for scalability?

**Answer:** Design for growth considering data volume, query patterns, and maintenance:

**1. Partitioning:**
```sql
-- Partition large tables
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE,
    amount DECIMAL
) PARTITION BY RANGE (sale_date);

CREATE TABLE sales_2023 PARTITION OF sales
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
```

**2. Indexing strategy:**
- Index foreign keys automatically
- Index WHERE and JOIN conditions
- Consider partial indexes for common filters
- Use appropriate index types (B-tree, GIN, BRIN)

**3. Schema evolution:**
- Use JSONB for flexible fields
- Plan for nullable columns
- Consider table inheritance for similar entities

**4. Archiving strategy:**
- Move old data to separate tables
- Use partitioning for easy archiving
- Consider separate databases for historical data

### Q5: Explain different constraint types and when to use them.

**Answer:**

**PRIMARY KEY:** Uniquely identifies rows, automatically indexed
```sql
id SERIAL PRIMARY KEY
```
**Use:** Every table needs one

**FOREIGN KEY:** Maintains referential integrity
```sql
customer_id INTEGER REFERENCES customers(id)
```
**Use:** Relationships between tables

**UNIQUE:** Prevents duplicate values
```sql
email TEXT UNIQUE
```
**Use:** Business uniqueness rules

**CHECK:** Validates column values
```sql
age INTEGER CHECK (age >= 0 AND age <= 120)
```
**Use:** Data validation rules

**NOT NULL:** Prevents NULL values
```sql
name TEXT NOT NULL
```
**Use:** Required fields

**EXCLUSION:** Complex business rules
```sql
EXCLUDE (room_id WITH =, daterange(check_in, check_out) WITH &&)
```
**Use:** Overlapping ranges, resource conflicts

### Q6: How do you handle schema changes in production?

**Answer:** Careful process to avoid downtime and data loss:

**1. Plan changes:**
- Assess impact on applications
- Plan rollback strategy
- Test on staging environment

**2. Safe changes:**
```sql
-- Add nullable column
ALTER TABLE users ADD COLUMN phone TEXT;

-- Add with default (locks table)
ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active' NOT NULL;

-- Rename column
ALTER TABLE users RENAME COLUMN name TO full_name;
```

**3. Risky changes:**
```sql
-- Add NOT NULL to existing column (check first)
ALTER TABLE users ADD CONSTRAINT check_phone_not_null
    CHECK (phone IS NOT NULL) NOT VALID;

-- Later make valid
ALTER TABLE users VALIDATE CONSTRAINT check_phone_not_null;
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
```

**4. Use tools:**
- pg_dump for backups
- pglogical for zero-downtime changes
- Consider migration tools (Flyway, Liquibase)

### Q7: What's the difference between VARCHAR and TEXT?

**Answer:**

**VARCHAR(n):** Variable length with maximum limit
- Storage: Actual length + 1 byte
- Constraint: Enforces maximum length
- Index: Can use =, LIKE operations

**TEXT:** Unlimited variable length
- Storage: Actual length + 1 byte (same as VARCHAR)
- No length limit
- Same performance characteristics

**When to use:**
- VARCHAR(n): Known maximum length, want enforcement
- TEXT: Unknown length, flexible content

**PostgreSQL optimization:** Both perform identically, TEXT is preferred for simplicity.

### Q8: How do you design for time-series data?

**Answer:** Special considerations for timestamped data:

**1. Partitioning by time:**
```sql
CREATE TABLE sensor_data (
    sensor_id INTEGER,
    timestamp TIMESTAMPTZ,
    value DECIMAL
) PARTITION BY RANGE (timestamp);

-- Monthly partitions
CREATE TABLE sensor_data_2023_12 PARTITION OF sensor_data
    FOR VALUES FROM ('2023-12-01') TO ('2024-01-01');
```

**2. BRIN indexes for time:**
```sql
CREATE INDEX ON sensor_data USING BRIN (timestamp);
-- Efficient for large time-series tables
```

**3. Retention policies:**
```sql
-- Automatic cleanup
CREATE OR REPLACE FUNCTION cleanup_old_data() RETURNS void AS $$
BEGIN
    DELETE FROM sensor_data WHERE timestamp < NOW() - INTERVAL '1 year';
END;
$$ LANGUAGE plpgsql;
```

**4. Compression:**
```sql
-- Use table compression for old partitions
ALTER TABLE sensor_data_2022 SET (autovacuum_enabled = false);
-- Implement custom compression strategy
```

**5. Schema design:**
- Use TIMESTAMPTZ for timezone handling
- Consider JSONB for flexible sensor metadata
- Pre-aggregate for common time ranges

---

## Summary

**Key Takeaways:**

1. **Data Types**: Choose semantic types (TIMESTAMPTZ, DECIMAL) over generic (TEXT)
2. **Normalization**: Start normalized, denormalize selectively for performance
3. **Constraints**: Use liberally for data integrity (PRIMARY KEY, FOREIGN KEY, CHECK)
4. **Indexes**: Index foreign keys, WHERE clauses, JOIN conditions
5. **Keys**: Surrogate primary keys, natural unique constraints
6. **Relationships**: Foreign keys with appropriate actions (CASCADE, RESTRICT)
7. **Design**: Plan for growth, document schema, test changes
8. **Performance**: Balance normalization with query efficiency

**Schema Design Process:**
```
1. Understand requirements and access patterns
2. Identify entities and relationships  
3. Choose data types and constraints
4. Normalize to appropriate level
5. Add indexes for performance
6. Create views/abstractions
7. Test and iterate
```

---

## Cross-Links

- **Indexes**: [[SQL/02_Core/01_Indexes_Basics_and_BTree]]
- **Constraints**: [[SQL/02_Core/02_Transactions_and_Locking]]
- **Partitioning**: [[SQL/03_Advanced/02_Partitioning]]
- **JSONB**: [[SQL/03_Advanced/04_Advanced_Index_Types_GIN_GiST_BRIN]]

## References

- [PostgreSQL Data Types](https://www.postgresql.org/docs/current/datatype.html)
- [Database Normalization](https://en.wikipedia.org/wiki/Database_normalization)
- [Schema Design Best Practices](https://www.postgresql.org/docs/current/ddl.html)

---

**Status**: stable  
**Last Updated**: 2026-04-26  
**Lines**: 1,423