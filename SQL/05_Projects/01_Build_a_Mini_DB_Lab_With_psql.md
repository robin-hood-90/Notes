---
tags: [sql, postgresql, projects, hands-on, lab]
aliases: ["PostgreSQL Mini Lab", "Database Playground Project", "psql Learning Lab"]
status: stable
updated: 2026-04-27
---

# Project: Build a Mini Database Lab (psql-first)

> [!summary] Model
> Comprehensive hands-on PostgreSQL playground: create schema, generate realistic data, experiment with indexing, locking, isolation levels, and query optimization. Learn by doing with reproducible experiments and measurable outcomes.

## Table of Contents

1. [[#Project Overview]]
2. [[#Prerequisites]]
3. [[#PostgreSQL Setup]]
4. [[#Database Creation]]
5. [[#Schema Design]]
6. [[#Data Generation]]
7. [[#Core Experiments]]
8. [[#Advanced Experiments]]
9. [[#Troubleshooting]]
10. [[#Extensions & Variations]]
11. [[#Best Practices]]
12. [[#Interview Questions]]
13. [[#Cheat Sheet]]
14. [[#Cross-Links]]
15. [[#References]]

---

## Project Overview

### What You'll Build

A complete PostgreSQL learning environment featuring:
- **E-commerce schema** with users, orders, products
- **Realistic data** (10K-100K rows) for meaningful experiments
- **Reproducible experiments** for indexing, locking, isolation
- **Measurement tools** to quantify performance differences
- **psql-first approach** emphasizing command-line mastery

### Learning Objectives

By the end of this project, you'll understand:
- PostgreSQL architecture and internals
- Query planning and optimization
- Concurrency control and locking
- Isolation levels and their trade-offs
- Index selection and maintenance
- Performance monitoring and troubleshooting

### Time Investment

- **Setup:** 30-60 minutes
- **Basic experiments:** 2-3 hours
- **Advanced experiments:** 4-6 hours
- **Total:** One full day of hands-on learning

### Prerequisites Check

- [ ] PostgreSQL installed and running
- [ ] psql command-line access
- [ ] Basic SQL knowledge
- [ ] Text editor for scripts
- [ ] Optional: git for version control

---

## Prerequisites

### System Requirements

**Hardware:**
- 2GB RAM minimum (4GB recommended)
- 2GB disk space for data
- Multi-core CPU for concurrent experiments

**Software:**
- PostgreSQL 12+ (latest stable recommended)
- psql client
- Bash/shell environment
- Optional: pgAdmin for visualization

### PostgreSQL Installation

**Ubuntu/Debian:**
```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

**macOS (Homebrew):**
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql

# Start service
brew services start postgresql

# Create database cluster
initdb /usr/local/var/postgres
```

**Windows:**
```powershell
# Using Chocolatey
choco install postgresql

# Or download from postgresql.org
# Run installer as administrator
```

**Docker (cross-platform):**
```bash
# Run PostgreSQL in Docker
docker run --name postgres-lab \
  -e POSTGRES_PASSWORD=mylabpass \
  -e POSTGRES_DB=lab \
  -p 5432:5432 \
  -d postgres:15

# Connect to container
docker exec -it postgres-lab psql -U postgres -d lab
```

### Verification

```bash
# Check PostgreSQL version
psql --version

# Check if service is running
pg_isready

# Connect to default database
psql -U postgres

# Check PostgreSQL status
psql -U postgres -c "SELECT version();"
```

---

## PostgreSQL Setup

### Configuration for Learning

**Basic configuration for experiments:**
```bash
# Edit postgresql.conf (location varies by installation)
# On Ubuntu: /etc/postgresql/15/main/postgresql.conf
# On macOS: /usr/local/var/postgres/postgresql.conf

# Key settings for learning environment
shared_buffers = 256MB          # Buffer cache
work_mem = 4MB                  # Sort/hash memory
maintenance_work_mem = 64MB     # Maintenance operations
random_page_cost = 4.0          # Disk vs memory cost
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'ddl'           # Log schema changes
log_min_duration_statement = 1000  # Log slow queries
```

**Apply configuration:**
```bash
# Reload configuration (no restart needed for many settings)
psql -U postgres -c "SELECT pg_reload_conf();"

# Or restart service
sudo systemctl restart postgresql
```

### User and Database Setup

**Create lab user:**
```sql
-- Connect as superuser
psql -U postgres

-- Create lab user
CREATE USER lab_user WITH PASSWORD 'labpass';
ALTER USER lab_user CREATEDB;
ALTER USER lab_user SUPERUSER;  -- For experiments
```

**Create lab database:**
```sql
-- Create database
CREATE DATABASE lab OWNER lab_user;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE lab TO lab_user;

-- Connect to lab database
\c lab
```

**Verify setup:**
```sql
-- Check current user and database
SELECT current_user, current_database();

-- Check permissions
\du lab_user
\l lab
```

---

## Database Creation

### Project Structure

**Directory structure:**
```
postgres-lab/
├── setup.sql          # Schema creation
├── data.sql           # Sample data generation
├── experiments.sql    # Experiment scripts
├── results/           # Experiment outputs
└── README.md          # Project documentation
```

**Create project directory:**
```bash
# Create project directory
mkdir postgres-lab
cd postgres-lab

# Create SQL files
touch setup.sql data.sql experiments.sql
mkdir results
```

### Initial Database Setup

**Create setup script:**
```sql
-- setup.sql
-- PostgreSQL Mini Lab Setup

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_buffercache;

-- Create schema
CREATE SCHEMA IF NOT EXISTS lab;

-- Set search path
SET search_path TO lab, public;

-- Create roles for experiments
CREATE ROLE experimenter;
GRANT USAGE ON SCHEMA lab TO experimenter;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA lab TO experimenter;
ALTER DEFAULT PRIVILEGES IN SCHEMA lab GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO experimenter;
```

**Run setup:**
```bash
psql -U lab_user -d lab -f setup.sql
```

---

## Schema Design

### E-commerce Schema

**Business requirements:**
- Users can place orders
- Orders contain multiple items
- Products have categories and pricing
- Track order status and timestamps

**Entity-Relationship Design:**
```
users (id, email, name, created_at)
    ↓
orders (id, user_id, status, total, created_at, updated_at)
    ↓
order_items (id, order_id, product_id, quantity, price)
    ↓
products (id, name, category, price, stock_quantity, created_at)
```

### Table Creation Script

**Complete schema:**
```sql
-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
    total DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (total >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create order_items table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to orders table
CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Run schema creation:**
```bash
psql -U lab_user -d lab -f setup.sql -c "\i schema.sql"
```

---

## Data Generation

### Realistic Data Strategy

**Data volumes for experiments:**
- **Users:** 10,000 (mix of active/inactive)
- **Products:** 1,000 (various categories and price ranges)
- **Orders:** 50,000 (realistic order frequency)
- **Order Items:** 150,000 (average 3 items per order)

**Data characteristics:**
- Realistic distributions (not uniform)
- Temporal patterns (recent orders more common)
- Referential integrity maintained

### Data Generation Script

**Generate users:**
```sql
-- Generate 10,000 users
INSERT INTO users (email, name, created_at)
SELECT
    'user' || i || '@example.com',
    'User ' || i,
    NOW() - (random() * INTERVAL '2 years')
FROM generate_series(1, 10000) AS i;

-- Make some users more recent
UPDATE users SET created_at = NOW() - (random() * INTERVAL '30 days')
WHERE random() < 0.3;
```

**Generate products:**
```sql
-- Generate 1,000 products
INSERT INTO products (name, category, price, stock_quantity, created_at)
SELECT
    'Product ' || i,
    CASE
        WHEN i % 4 = 0 THEN 'Electronics'
        WHEN i % 4 = 1 THEN 'Books'
        WHEN i % 4 = 2 THEN 'Clothing'
        ELSE 'Home & Garden'
    END,
    (random() * 500 + 10)::numeric(10,2),  -- $10-$510
    (random() * 1000 + 10)::int,           -- 10-1010 stock
    NOW() - (random() * INTERVAL '1 year')
FROM generate_series(1, 1000) AS i;
```

**Generate orders and items:**
```sql
-- Generate orders (one per user on average, some users have multiple)
INSERT INTO orders (user_id, status, total, created_at, updated_at)
SELECT
    u.id,
    CASE
        WHEN random() < 0.7 THEN 'delivered'
        WHEN random() < 0.8 THEN 'shipped'
        WHEN random() < 0.9 THEN 'confirmed'
        ELSE 'pending'
    END,
    0,  -- Will calculate later
    NOW() - (random() * INTERVAL '1 year'),
    NOW() - (random() * INTERVAL '1 year')
FROM users u
CROSS JOIN generate_series(1, (random() * 5 + 1)::int) AS gs
ORDER BY random();

-- Generate order items
INSERT INTO order_items (order_id, product_id, quantity, price, created_at)
SELECT
    o.id,
    p.id,
    (random() * 5 + 1)::int,  -- 1-5 items
    p.price,
    o.created_at + (random() * INTERVAL '1 day')
FROM orders o
CROSS JOIN LATERAL (
    SELECT id, price
    FROM products
    ORDER BY random()
    LIMIT (random() * 3 + 1)::int  -- 1-3 products per order
) p;

-- Calculate order totals
UPDATE orders
SET total = (
    SELECT sum(oi.quantity * oi.price)
    FROM order_items oi
    WHERE oi.order_id = orders.id
);
```

### Data Validation

**Verify data integrity:**
```sql
-- Check row counts
SELECT 'users' as table_name, count(*) as rows FROM users
UNION ALL
SELECT 'products', count(*) FROM products
UNION ALL
SELECT 'orders', count(*) FROM orders
UNION ALL
SELECT 'order_items', count(*) FROM order_items;

-- Check referential integrity
SELECT count(*) as orphaned_orders
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
WHERE u.id IS NULL;

-- Check data distributions
SELECT category, count(*) as products, avg(price)::numeric(10,2) as avg_price
FROM products
GROUP BY category
ORDER BY count DESC;

-- Sample data
SELECT u.name, o.total, count(oi.*) as items
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
GROUP BY u.id, u.name, o.id, o.total
ORDER BY o.total DESC
LIMIT 10;
```

---

## Core Experiments

### Experiment 1: Indexing Impact

**Objective:** Demonstrate how indexes affect query performance

**Setup:**
```sql
-- Create test table without indexes
CREATE TABLE test_users AS SELECT * FROM users LIMIT 1000;
ALTER TABLE test_users DROP CONSTRAINT IF EXISTS test_users_pkey;
DROP INDEX IF EXISTS idx_test_users_email;

-- Measure query without index
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_users WHERE email = 'user500@example.com';
```

**Experiment:**
```sql
-- Add index
CREATE INDEX idx_test_users_email ON test_users(email);

-- Measure query with index
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM test_users WHERE email = 'user500@example.com';

-- Compare results
-- Note: execution time, buffers hit/read, node type
```

**Variations:**
- Partial index: `CREATE INDEX ON test_users(email) WHERE active = true;`
- Covering index: `CREATE INDEX ON test_users(email, name);`
- Multi-column index: `CREATE INDEX ON test_users(last_name, first_name);`

### Experiment 2: Lock Contention

**Objective:** Experience locking behavior and resolution

**Setup:**
```sql
-- Create test table
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    balance DECIMAL(10,2) NOT NULL DEFAULT 1000.00
);

INSERT INTO accounts (balance) SELECT 1000.00 FROM generate_series(1, 10);
```

**Experiment (Two psql sessions):**

**Session 1:**
```sql
-- Start transaction
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- Don't commit yet
```

**Session 2:**
```sql
-- Try to update same row
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
-- This will wait for session 1
```

**Session 1:**
```sql
-- Check locks
SELECT * FROM pg_locks WHERE pid <> pg_backend_pid();
COMMIT;
```

**Observations:**
- Session 2 waits for lock
- Lock appears in pg_locks
- Commit releases lock

**Variations:**
- Try `SELECT ... FOR UPDATE`
- Test `NOWAIT` option
- Create deadlock scenario

### Experiment 3: Isolation Levels

**Objective:** Compare behavior of different isolation levels

**Setup:**
```sql
-- Create test table
CREATE TABLE test_balance (
    id SERIAL PRIMARY KEY,
    amount DECIMAL(10,2) NOT NULL DEFAULT 100.00
);
INSERT INTO test_balance (amount) VALUES (100.00);
```

**Experiment (Two sessions):**

**Session 1 (READ COMMITTED - default):**
```sql
BEGIN;
SELECT amount FROM test_balance WHERE id = 1;  -- Shows 100
-- Don't commit
```

**Session 2:**
```sql
BEGIN;
UPDATE test_balance SET amount = 200 WHERE id = 1;
COMMIT;
```

**Session 1:**
```sql
SELECT amount FROM test_balance WHERE id = 1;  -- Shows 200
COMMIT;
```

**Repeat with SERIALIZABLE:**

**Session 1:**
```sql
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT amount FROM test_balance WHERE id = 1;  -- Shows 100
-- Don't commit
```

**Session 2:**
```sql
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
UPDATE test_balance SET amount = 300 WHERE id = 1;
COMMIT;
```

**Session 1:**
```sql
SELECT amount FROM test_balance WHERE id = 1;  -- Still shows 100
COMMIT;  -- Will show serialization failure
```

**Observations:**
- READ COMMITTED sees committed changes
- SERIALIZABLE prevents serialization anomalies

### Experiment 4: VACUUM and Bloat

**Objective:** Observe table bloat and VACUUM impact

**Setup:**
```sql
-- Create test table
CREATE TABLE bloated_table (
    id SERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert initial data
INSERT INTO bloated_table (data)
SELECT repeat('x', 1000) FROM generate_series(1, 10000);
```

**Create bloat:**
```sql
-- Update most rows (creates dead tuples)
UPDATE bloated_table SET data = repeat('y', 1000)
WHERE id % 2 = 0;

-- Delete some rows
DELETE FROM bloated_table WHERE id % 10 = 0;

-- Check table size
SELECT pg_size_pretty(pg_relation_size('bloated_table'));
```

**Run VACUUM:**
```sql
-- Analyze bloat before
SELECT * FROM pg_stat_user_tables WHERE relname = 'bloated_table';

-- Run VACUUM
VACUUM bloated_table;

-- Check size after
SELECT pg_size_pretty(pg_relation_size('bloated_table'));

-- Run VACUUM FULL
VACUUM FULL bloated_table;
SELECT pg_size_pretty(pg_relation_size('bloated_table'));
```

**Observations:**
- Table size increases with updates/deletes
- VACUUM reclaims space
- VACUUM FULL compacts table

---

## Advanced Experiments

### Experiment 5: Query Plan Analysis

**Objective:** Understand query planner decisions

**Setup:**
```sql
-- Create table with different data distributions
CREATE TABLE skewed_data (
    id SERIAL PRIMARY KEY,
    category VARCHAR(10),
    value INTEGER
);

-- Insert skewed data
INSERT INTO skewed_data (category, value)
SELECT
    CASE WHEN i % 100 = 0 THEN 'rare' ELSE 'common' END,
    i
FROM generate_series(1, 100000) i;
```

**Experiment:**
```sql
-- Query common category
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM skewed_data WHERE category = 'common';

-- Query rare category
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM skewed_data WHERE category = 'rare';

-- Add index
CREATE INDEX idx_skewed_category ON skewed_data(category);

-- Re-run queries
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM skewed_data WHERE category = 'common';

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM skewed_data WHERE category = 'rare';
```

**Observations:**
- Planner chooses seq scan for common values
- Index scan preferred for rare values
- ANALYZE affects planner decisions

### Experiment 6: Partitioning

**Objective:** Experience partitioned table performance

**Setup:**
```sql
-- Create partitioned table
CREATE TABLE orders_partitioned (
    id SERIAL,
    user_id INTEGER,
    amount DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE orders_2024_q1 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Add indexes to partitions
CREATE INDEX idx_orders_2024_q1_created_at ON orders_2024_q1(created_at);
CREATE INDEX idx_orders_2024_q2_created_at ON orders_2024_q2(created_at);

-- Insert data
INSERT INTO orders_partitioned (user_id, amount, created_at)
SELECT
    (random() * 1000)::int + 1,
    (random() * 1000)::numeric(10,2),
    '2024-01-01'::timestamp + (random() * 180 * INTERVAL '1 day')
FROM generate_series(1, 100000);
```

**Experiment:**
```sql
-- Query specific partition
EXPLAIN (ANALYZE)
SELECT * FROM orders_partitioned
WHERE created_at BETWEEN '2024-01-01' AND '2024-03-31';

-- Query across partitions
EXPLAIN (ANALYZE)
SELECT * FROM orders_partitioned
WHERE created_at BETWEEN '2024-02-01' AND '2024-05-31';

-- Compare with non-partitioned table
CREATE TABLE orders_regular AS SELECT * FROM orders_partitioned;
CREATE INDEX idx_orders_regular_created_at ON orders_regular(created_at);

EXPLAIN (ANALYZE)
SELECT * FROM orders_regular
WHERE created_at BETWEEN '2024-01-01' AND '2024-03-31';
```

**Observations:**
- Partition pruning eliminates irrelevant partitions
- Partitioned queries can be faster
- Index maintenance differs

### Experiment 7: Connection Pooling

**Objective:** Understand connection pool behavior

**Setup:**
```sql
-- Enable statement statistics
CREATE EXTENSION pg_stat_statements;

-- Create test workload
CREATE OR REPLACE FUNCTION simulate_workload()
RETURNS void AS $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 1..100 LOOP
        PERFORM count(*) FROM users WHERE id = (random() * 10000)::int;
        PERFORM pg_sleep(0.01);  -- Simulate work
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

**Experiment:**
```sql
-- Clear stats
SELECT pg_stat_statements_reset();

-- Run workload in single connection
SELECT simulate_workload();

-- Check stats
SELECT query, calls, total_time/calls as avg_time
FROM pg_stat_statements
WHERE query LIKE '%users%'
ORDER BY total_time DESC
LIMIT 5;

-- Simulate multiple connections (run in parallel terminals)
-- psql -U lab_user -d lab -c "SELECT simulate_workload();" &
-- Repeat 5 times

-- Monitor connections
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;

-- Check performance impact
SELECT * FROM pg_stat_bgwriter;
```

**Observations:**
- Connection overhead
- Shared buffer usage
- Lock contention effects

---

## Troubleshooting

### Common Issues

**1. Permission denied:**
```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA lab TO lab_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA lab TO lab_user;
```

**2. Connection refused:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check port
netstat -tlnp | grep 5432

# Check logs
tail -f /var/log/postgresql/postgresql-15-main.log
```

**3. Slow data generation:**
```sql
-- Use COPY for faster loading
COPY users(email, name) FROM STDIN WITH CSV;
user1@example.com,User 1
user2@example.com,User 2
\.
```

**4. Out of disk space:**
```bash
# Check disk usage
df -h

# Find large files
find /var/lib/postgresql -type f -size +100M

# Clean up
./cleanup.sh
```

### Performance Issues

**Slow queries:**
```sql
-- Find slow queries
SELECT pid, query, extract(epoch from (now() - query_start)) as duration
FROM pg_stat_activity
WHERE state = 'active' AND query_start < now() - interval '10 seconds';

-- Kill if necessary
SELECT pg_cancel_backend(pid);
```

**High CPU usage:**
```sql
-- Check active queries
SELECT pid, query, state
FROM pg_stat_activity
WHERE state = 'active';

-- Check system stats
SELECT * FROM pg_stat_bgwriter;
```

### Data Issues

**Inconsistent data:**
```sql
-- Recreate data
DROP SCHEMA lab CASCADE;
CREATE SCHEMA lab;
\i setup.sql
\i data.sql
```

**Missing data:**
```sql
-- Check for missing references
SELECT count(*) as orphaned_orders
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
WHERE u.id IS NULL;
```

---

## Extensions and Variations

### Additional Experiments

**1. Replication setup:**
```sql
-- Set up streaming replication
-- Configure primary and standby
-- Test failover scenarios
```

**2. Backup and recovery:**
```sql
-- Create backup
pg_dump -U lab_user -d lab > backup.sql

-- Test recovery
createdb lab_restore
psql -U lab_user -d lab_restore < backup.sql
```

**3. Extension usage:**
```sql
-- Install additional extensions
CREATE EXTENSION pg_repack;     -- Online table reorganization
CREATE EXTENSION pg_prewarm;    -- Table prewarming
CREATE EXTENSION pg_cron;       -- Job scheduling
```

### Advanced Variations

**High concurrency testing:**
```bash
# Use pgbench for load testing
pgbench -U lab_user -d lab -c 10 -j 2 -T 60
```

**Custom data generators:**
```sql
-- Create more realistic data distributions
CREATE OR REPLACE FUNCTION random_normal(mean float, stddev float)
RETURNS float AS $$
BEGIN
    RETURN mean + stddev * sqrt(-2 * ln(random())) * cos(2 * pi() * random());
END;
$$ LANGUAGE plpgsql;
```

**Monitoring dashboard:**
```sql
-- Create monitoring views
CREATE VIEW system_health AS
SELECT
    now() as timestamp,
    (SELECT count(*) FROM pg_stat_activity) as connections,
    (SELECT sum(blks_hit) FROM pg_stat_database WHERE datname = current_database()) as buffer_hits,
    (SELECT sum(blks_read) FROM pg_stat_database WHERE datname = current_database()) as buffer_reads
;
```

---

## Best Practices

### Lab Maintenance

**Regular cleanup:**
```bash
# Create cleanup script
#!/bin/bash
psql -U lab_user -d lab << 'EOF'
-- Reset lab database
DROP SCHEMA IF EXISTS lab CASCADE;
CREATE SCHEMA lab;
\i setup.sql
\i data.sql
EOF
```

**Backup important experiments:**
```bash
# Backup results
mkdir -p experiments/$(date +%Y%m%d)
cp results/* experiments/$(date +%Y%m%d)/
```

### Learning Optimization

**Experiment structure:**
1. **Hypothesis:** What do you expect to happen?
2. **Setup:** Prepare data and conditions
3. **Measurement:** Capture before/after metrics
4. **Analysis:** Explain results
5. **Documentation:** Record findings

**Progressive difficulty:**
- Start with basic queries
- Add complexity gradually
- Compare different approaches
- Measure performance impact

### Safety Measures

**Isolation:**
- Use dedicated database for experiments
- Don't run on production systems
- Backup before destructive operations

**Resource management:**
- Monitor disk space usage
- Limit concurrent experiments
- Clean up after each session

---

## Interview Questions

### Q1: How would you set up a PostgreSQL testing environment?

**Answer:** Create an isolated environment for safe experimentation:

1. **Install PostgreSQL:**
   ```bash
   # Local installation or Docker
   docker run -d --name postgres-test -p 5432:5432 postgres:15
   ```

2. **Create test database:**
   ```sql
   CREATE DATABASE test_db;
   CREATE USER test_user WITH PASSWORD 'testpass';
   GRANT ALL PRIVILEGES ON DATABASE test_db TO test_user;
   ```

3. **Load schema and data:**
   ```sql
   \i schema.sql
   \i test_data.sql
   ```

4. **Configure for testing:**
   ```sql
   ALTER SYSTEM SET log_statement = 'ddl';
   ALTER SYSTEM SET log_min_duration_statement = 1000;
   SELECT pg_reload_conf();
   ```

5. **Run experiments:**
   - Test query performance
   - Try different configurations
   - Practice troubleshooting

**Why this approach?** Provides safe, reproducible environment for learning PostgreSQL internals.

### Q2: How do you generate realistic test data in PostgreSQL?

**Answer:** Use built-in functions and careful planning:

**Basic data generation:**
```sql
-- Generate series
INSERT INTO users (email, name)
SELECT
    'user' || i || '@example.com',
    'User ' || i
FROM generate_series(1, 10000) i;

-- Random data
INSERT INTO products (name, price, category)
SELECT
    'Product ' || i,
    (random() * 1000)::numeric(10,2),
    (ARRAY['Electronics', 'Books', 'Clothing'])[(random()*3)::int + 1]
FROM generate_series(1, 1000) i;
```

**Realistic distributions:**
```sql
-- Normal distribution
CREATE OR REPLACE FUNCTION random_normal(mean float, stddev float)
RETURNS float AS $$
BEGIN
    RETURN mean + stddev * sqrt(-2 * ln(random())) * cos(2 * pi() * random());
END;
$$ LANGUAGE plpgsql;

-- Use for prices
UPDATE products SET price = random_normal(100, 50);
```

**Referential integrity:**
```sql
-- Generate orders for existing users
INSERT INTO orders (user_id, total)
SELECT
    u.id,
    (random() * 500)::numeric(10,2)
FROM users u
ORDER BY random()
LIMIT 50000;
```

**Why realistic data?** Affects query planner decisions and performance characteristics.

### Q3: How would you investigate a slow query in your lab?

**Answer:** Systematic investigation using EXPLAIN and monitoring:

1. **Capture the query:**
   ```sql
   -- Enable logging
   SET log_min_duration_statement = 0;
   -- Run the slow query
   ```

2. **Analyze execution plan:**
   ```sql
   EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
   SELECT * FROM large_table WHERE condition;
   ```

3. **Check for missing indexes:**
   ```sql
   -- Look for seq scans on large tables
   SELECT * FROM pg_stat_user_tables
   WHERE seq_scan > idx_scan * 10;
   ```

4. **Examine table statistics:**
   ```sql
   ANALYZE table_name;  -- Update statistics
   SELECT * FROM pg_stats WHERE tablename = 'table_name';
   ```

5. **Test optimizations:**
   ```sql
   CREATE INDEX ON table_name(column);
   -- Re-run EXPLAIN ANALYZE
   ```

6. **Check system resources:**
   ```sql
   SELECT * FROM pg_stat_activity WHERE state = 'active';
   SELECT * FROM pg_stat_bgwriter;
   ```

**Why this methodology?** Isolates whether issue is query, index, statistics, or system-related.

### Q4: How do you simulate production-like load in your lab?

**Answer:** Use pgbench and custom scripts:

**pgbench for OLTP load:**
```bash
# Initialize test database
pgbench -U lab_user -d lab -i -s 10  # Scale factor 10

# Run benchmark
pgbench -U lab_user -d lab -c 10 -j 2 -T 60  # 10 clients, 60 seconds
```

**Custom load scripts:**
```sql
-- Create load testing function
CREATE OR REPLACE FUNCTION stress_test()
RETURNS void AS $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 1..1000 LOOP
        -- Simulate application queries
        PERFORM count(*) FROM users WHERE created_at > now() - interval '1 day';
        PERFORM * FROM orders WHERE status = 'pending' LIMIT 10;
        PERFORM sum(total) FROM orders WHERE user_id = (random()*10000)::int;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Run concurrent load
-- Launch multiple psql sessions running stress_test()
```

**Monitoring during load:**
```sql
-- Watch system during test
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;

-- Check performance
SELECT * FROM pg_stat_database;

-- Monitor locks
SELECT locktype, mode, count(*) FROM pg_locks GROUP BY locktype, mode;
```

**Why simulate load?** Reveals concurrency issues, locking problems, and performance bottlenecks not visible with single queries.

---

## Cheat Sheet

### Quick Setup

```bash
# One-line setup (Ubuntu)
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createuser -s lab_user
sudo -u postgres createdb lab -O lab_user
psql -U lab_user -d lab -f setup.sql

# Docker setup
docker run -d --name postgres-lab -e POSTGRES_PASSWORD=labpass -p 5432:5432 postgres:15
psql -h localhost -U postgres -d postgres -c "CREATE DATABASE lab;"
```

### Essential Commands

```sql
-- Check status
SELECT version();
SELECT current_database(), current_user;
\l  -- List databases
\dt -- List tables
\d table_name -- Describe table

-- Performance monitoring
SELECT * FROM pg_stat_activity;
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
SELECT * FROM pg_stat_user_tables;
SELECT * FROM pg_stat_user_indexes;

-- Cleanup
DROP SCHEMA lab CASCADE;
VACUUM FULL;
REINDEX DATABASE lab;
```

### Common Experiments

```sql
-- Index impact
CREATE TABLE test AS SELECT * FROM large_table LIMIT 10000;
EXPLAIN ANALYZE SELECT * FROM test WHERE col = 'value';
CREATE INDEX ON test(col);
EXPLAIN ANALYZE SELECT * FROM test WHERE col = 'value';

-- Lock testing (Session 1)
BEGIN; UPDATE table SET col = val WHERE id = 1;
-- Session 2: UPDATE table SET col = val WHERE id = 1;  -- Waits

-- Isolation testing
-- Session 1: BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- Session 2: UPDATE ... (will cause serialization failure)
```

### Troubleshooting

```sql
-- Connection issues
pg_isready
SELECT * FROM pg_stat_activity WHERE state != 'idle';

-- Performance issues
SELECT pid, query, extract(epoch from (now() - query_start)) as duration
FROM pg_stat_activity WHERE state = 'active' ORDER BY query_start;

-- Space issues
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Kill problematic queries
SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE ...;
```

### Data Generation

```sql
-- Basic series
INSERT INTO table(col) SELECT generate_series(1,1000);

-- Random data
INSERT INTO table(num_col, text_col)
SELECT (random()*1000)::int, md5(random()::text)
FROM generate_series(1,10000);

-- Realistic dates
INSERT INTO table(created_at)
SELECT now() - (random() * interval '1 year')
FROM generate_series(1,1000);

-- Foreign keys
INSERT INTO child(parent_id, data)
SELECT (random()*1000)::int + 1, 'data'
FROM generate_series(1,1000);
```

---

## Cross-Links

- **psql Basics**: [[SQL/01_Foundations/01_psql_Basics_and_Workflow]]
- **Query Plans**: [[SQL/02_Core/04_Explain_Analyze_and_Query_Plans]]
- **Indexes**: [[SQL/02_Core/01_Indexes_Basics_and_BTree]]
- **Transactions**: [[SQL/02_Core/02_Transactions_and_Locking]]
- **Isolation**: [[SQL/02_Core/03_Isolation_Levels_and_Anomalies]]
- **VACUUM**: [[SQL/03_Advanced/01_VACUUM_Autovacuum_and_Bloat]]
- **Partitioning**: [[SQL/03_Advanced/02_Partitioning]]

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/current/)
- [pgbench Manual](https://www.postgresql.org/docs/current/pgbench.html)
- [EXPLAIN Details](https://www.postgresql.org/docs/current/using-explain.html)
- [Index Types](https://www.postgresql.org/docs/current/indexes-types.html)

---

**Status**: stable  
**Last Updated**: 2026-04-27  
**Lines**: 856