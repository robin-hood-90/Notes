---
tags: [sql, postgresql, advanced, partitioning, performance, scalability]
aliases: ["Table Partitioning", "Partitioning Strategies"]
status: stable
updated: 2026-04-26
---

# Partitioning

> [!summary] Model
> Partitioning divides large tables into smaller, manageable pieces called partitions. PostgreSQL supports range, list, and hash partitioning. Partition pruning eliminates irrelevant partitions during queries, improving performance for large datasets. Choose partitioning strategy based on query patterns and data distribution.

## Table of Contents

1. [[#Partitioning Concepts]]
2. [[#Range Partitioning]]
3. [[#List Partitioning]]
4. [[#Hash Partitioning]]
5. [[#Partition Pruning]]
6. [[#Partition Maintenance]]
7. [[#Indexing Partitioned Tables]]
8. [[#Performance Considerations]]
9. [[#Common Patterns]]
10. [[#Best Practices]]
11. [[#Interview Questions]]

---

## Partitioning Concepts

### What is Partitioning?

Partitioning splits a large table into smaller, more manageable pieces called partitions:

```sql
-- Logical table (partitioned)
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE,
    customer_id INTEGER,
    amount DECIMAL
) PARTITION BY RANGE (sale_date);

-- Physical partitions (created automatically or manually)
CREATE TABLE sales_2023 PARTITION OF sales
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE sales_2024 PARTITION OF sales
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

**Why partition?** Improves query performance, simplifies maintenance, enables data lifecycle management.

**How it works:** PostgreSQL treats partitioned table as a virtual table; queries access only relevant partitions.

**When to use:** Tables > 100GB, time-series data, frequent range queries, data archiving needs.

### Partition Types

PostgreSQL supports three partitioning strategies:

| Type | Use Case | Key Column Type | Example |
|------|----------|-----------------|---------|
| **Range** | Time-series, ordered data | DATE, TIMESTAMP, INTEGER | Sales by month/year |
| **List** | Categorical data | TEXT, ENUM, INTEGER | Data by region/country |
| **Hash** | Even distribution | Any hashable type | Load balancing |

**Why different types?** Each optimizes for specific query patterns and data distributions.

**How to choose:** Analyze query patterns - range for time queries, list for categories, hash for uniform access.

**When to partition:** Table size > 10-100GB, query performance issues, maintenance challenges.

### Partition Structure

```sql
-- Partitioned table hierarchy
sales (partitioned table)
├── sales_2023_q1 (partition)
├── sales_2023_q2 (partition)
├── sales_2023_q3 (partition)
└── sales_2023_q4 (partition)
```

**Why hierarchical?** Logical organization, automatic routing of INSERT/UPDATE/DELETE operations.

**How it works:** PostgreSQL automatically routes data to correct partition based on partition key.

**Where partitions live:** Same tablespace as parent unless specified otherwise.

---

## Range Partitioning

### Basic Range Partitioning

Range partitioning divides data by contiguous ranges of values:

```sql
-- Create partitioned table
CREATE TABLE sensor_data (
    sensor_id INTEGER,
    reading_time TIMESTAMPTZ NOT NULL,
    temperature DECIMAL,
    humidity DECIMAL
) PARTITION BY RANGE (reading_time);

-- Create partitions for each month
CREATE TABLE sensor_data_2024_01 PARTITION OF sensor_data
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE sensor_data_2024_02 PARTITION OF sensor_data
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Continue for all months...
```

**Why range partitioning?** Natural for time-series data, enables efficient range queries.

**How it works:** Each partition has a range defined by FROM and TO values (TO is exclusive).

**When to use:** Time-series data, ordered numeric data, log data, historical records.

### Range Partitioning by Time

```sql
-- Daily partitions for high-volume data
CREATE TABLE logs (
    id BIGSERIAL,
    level TEXT,
    message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create daily partitions
DO $$
DECLARE
    start_date DATE := '2024-01-01';
    end_date DATE := '2024-12-31';
    current_date DATE := start_date;
BEGIN
    WHILE current_date <= end_date LOOP
        EXECUTE format(
            'CREATE TABLE logs_%s PARTITION OF logs FOR VALUES FROM (%L) TO (%L)',
            to_char(current_date, 'YYYY_MM_DD'),
            current_date,
            current_date + INTERVAL '1 day'
        );
        current_date := current_date + INTERVAL '1 day';
    END LOOP;
END $$;
```

**Why daily partitions?** Easy maintenance, fine-grained control for high-volume tables.

**How to automate:** Use scripts or stored procedures to create partitions in advance.

**When to use:** Log tables, event streams, IoT data, audit trails.

### Range Partitioning by Numbers

```sql
-- Partition by customer ID ranges
CREATE TABLE customer_orders (
    customer_id INTEGER,
    order_id INTEGER,
    order_date DATE,
    amount DECIMAL
) PARTITION BY RANGE (customer_id);

-- Create partitions for customer ID ranges
CREATE TABLE customer_orders_1_1000 PARTITION OF customer_orders
    FOR VALUES FROM (1) TO (1001);

CREATE TABLE customer_orders_1001_2000 PARTITION OF customer_orders
    FOR VALUES FROM (1001) TO (2001);

-- Hash-based assignment could also work here
```

**Why numeric ranges?** Balanced partitions when data is uniformly distributed by numeric key.

**How it works:** Define contiguous ranges that don't overlap.

**When to use:** Sequential IDs, evenly distributed numeric keys.

---

## List Partitioning

### Basic List Partitioning

List partitioning assigns rows to partitions based on discrete values:

```sql
-- Partition by region
CREATE TABLE sales_by_region (
    id SERIAL,
    region TEXT,
    customer_id INTEGER,
    amount DECIMAL,
    sale_date DATE
) PARTITION BY LIST (region);

-- Create region-specific partitions
CREATE TABLE sales_us_east PARTITION OF sales_by_region
    FOR VALUES IN ('NY', 'MA', 'CT', 'RI', 'VT', 'NH', 'ME');

CREATE TABLE sales_us_west PARTITION OF sales_by_region
    FOR VALUES IN ('CA', 'WA', 'OR', 'NV', 'AZ');

CREATE TABLE sales_europe PARTITION OF sales_by_region
    FOR VALUES IN ('UK', 'DE', 'FR', 'IT', 'ES');

-- Default partition for unmatched values
CREATE TABLE sales_other PARTITION OF sales_by_region DEFAULT;
```

**Why list partitioning?** Natural for categorical data, enables region-specific optimizations.

**How it works:** Each partition explicitly lists allowed values for the partition key.

**When to use:** Geographic data, status codes, categories with known values.

### List Partitioning with Enums

```sql
-- Use enum for type safety
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    id SERIAL,
    customer_id INTEGER,
    status order_status,
    order_date DATE,
    total DECIMAL
) PARTITION BY LIST (status);

-- Create status-based partitions
CREATE TABLE orders_pending PARTITION OF orders
    FOR VALUES IN ('pending');

CREATE TABLE orders_active PARTITION OF orders
    FOR VALUES IN ('processing', 'shipped');

CREATE TABLE orders_completed PARTITION OF orders
    FOR VALUES IN ('delivered');

CREATE TABLE orders_cancelled PARTITION OF orders
    FOR VALUES IN ('cancelled');
```

**Why enum with list?** Type safety, prevents invalid status values, clear partition boundaries.

**How it works:** Enum ensures only valid values, list partitioning organizes by status.

**When to use:** Workflow data, status-based systems, categorical business logic.

### Default Partitions

```sql
-- Handle unexpected values
CREATE TABLE user_events (
    user_id INTEGER,
    event_type TEXT,
    event_data JSONB,
    created_at TIMESTAMPTZ
) PARTITION BY LIST (event_type);

-- Known event types
CREATE TABLE events_login PARTITION OF user_events
    FOR VALUES IN ('login', 'logout');

CREATE TABLE events_purchase PARTITION OF user_events
    FOR VALUES IN ('purchase', 'refund');

-- Catch-all for new event types
CREATE TABLE events_other PARTITION OF user_events DEFAULT;
```

**Why default partitions?** Handle new categories without schema changes, prevent insert failures.

**How it works:** DEFAULT partition accepts any values not covered by other partitions.

**When to use:** Evolving schemas, unknown future categories, flexible data models.

---

## Hash Partitioning

### Basic Hash Partitioning

Hash partitioning distributes rows evenly across partitions:

```sql
-- Hash partition by user ID
CREATE TABLE user_activity (
    user_id INTEGER,
    activity_type TEXT,
    activity_data JSONB,
    created_at TIMESTAMPTZ
) PARTITION BY HASH (user_id);

-- Create 4 hash partitions (PostgreSQL calculates ranges)
CREATE TABLE user_activity_0 PARTITION OF user_activity
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE user_activity_1 PARTITION OF user_activity
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE user_activity_2 PARTITION OF user_activity
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE user_activity_3 PARTITION OF user_activity
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

**Why hash partitioning?** Even data distribution when no natural partitioning key exists.

**How it works:** Hash function on partition key determines partition assignment.

**When to use:** Primary key partitioning, load balancing, no obvious range/list key.

### Hash Partitioning for Performance

```sql
-- High-traffic table with hash partitioning
CREATE TABLE api_requests (
    id BIGSERIAL,
    user_id INTEGER,
    endpoint TEXT,
    response_time INTEGER,
    created_at TIMESTAMPTZ
) PARTITION BY HASH (user_id);

-- Create many partitions for parallelism
DO $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 0..15 LOOP
        EXECUTE format(
            'CREATE TABLE api_requests_%s PARTITION OF api_requests FOR VALUES WITH (MODULUS 16, REMAINDER %s)',
            i, i
        );
    END LOOP;
END $$;
```

**Why many partitions?** Enables parallel query execution, reduces lock contention.

**How it works:** PostgreSQL can scan partitions in parallel, improving query performance.

**When to use:** High-throughput tables, concurrent workloads, large user bases.

### Choosing Modulus and Remainder

```sql
-- General formula
MODULUS = number of partitions
REMAINDER = partition number (0 to MODULUS-1)

-- Examples:
-- 4 partitions: MODULUS 4, REMAINDER 0,1,2,3
-- 8 partitions: MODULUS 8, REMAINDER 0,1,2,3,4,5,6,7
-- 16 partitions: MODULUS 16, REMAINDER 0-15

-- PostgreSQL hash function determines assignment
SELECT mod(hashtext('some_value'), 4);  -- Returns 0-3
```

**Why power of 2?** Easy to understand, balanced distribution.

**How PostgreSQL hashes:** Uses internal hash function, ensures even distribution.

**When to change:** Performance needs, data growth, query patterns change.

---

## Partition Pruning

### How Partition Pruning Works

Partition pruning eliminates irrelevant partitions during query execution:

```sql
-- Query prunes to relevant partitions
EXPLAIN SELECT * FROM sensor_data
WHERE reading_time >= '2024-03-01' AND reading_time < '2024-04-01';

-- Output shows partition pruning:
-- "Partitions selected: sensor_data_2024_03"
```

**Why partition pruning?** Avoids scanning all partitions, improves query performance.

**How it works:** Query planner analyzes WHERE conditions, excludes partitions that can't contain matching rows.

**When it works:** WHERE clauses constrain the partition key with constants or simple expressions.

### Pruning Examples

```sql
-- ✅ Effective pruning
SELECT * FROM sales WHERE sale_date = '2024-03-15';           -- Single partition
SELECT * FROM sales WHERE sale_date BETWEEN '2024-01-01' AND '2024-03-31'; -- Multiple partitions
SELECT * FROM orders WHERE region IN ('US', 'EU');            -- List pruning

-- ❌ No pruning (scans all partitions)
SELECT * FROM sales WHERE customer_id = 123;                  -- Wrong column
SELECT * FROM sales WHERE EXTRACT(year FROM sale_date) = 2024; -- Function on partition key
SELECT * FROM sales WHERE sale_date > NOW() - INTERVAL '1 day'; -- Dynamic value
```

**Why pruning fails?** Complex expressions prevent the planner from determining partition boundaries.

**How to fix:** Use constraints directly on partition key, avoid functions.

**When pruning is critical:** Large partitioned tables, performance-sensitive queries.

### Runtime Pruning

```sql
-- Runtime pruning with prepared statements
PREPARE get_user_orders (INTEGER, DATE) AS
SELECT * FROM orders
WHERE customer_id = $1 AND order_date >= $2;

-- Partition pruning happens at execution time
EXECUTE get_user_orders(123, '2024-01-01');
```

**Why runtime pruning?** Parameters evaluated at execution, not planning time.

**How it works:** PostgreSQL defers pruning until parameter values are known.

**When it helps:** Dynamic queries, prepared statements, application-generated queries.

### Partition Pruning Monitoring

```sql
-- Check if partitions are pruned
EXPLAIN (ANALYZE, VERBOSE)
SELECT * FROM large_partitioned_table
WHERE partition_key = 'some_value';

-- Look for in query plan:
-- "Partitions selected: table_part_1, table_part_2"
-- "Partitions pruned: table_part_3, table_part_4"

-- Statistics
SELECT schemaname, tablename,
       seq_scan, idx_scan,
       seq_tup_read, idx_tup_fetch
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

**Why monitor pruning?** Ensure partitioning provides expected performance benefits.

**How to verify:** EXPLAIN shows selected partitions, statistics show scan patterns.

**When to investigate:** Slow queries on partitioned tables, unexpected full table scans.

---

## Partition Maintenance

### Adding New Partitions

```sql
-- Add future partition (range)
CREATE TABLE sales_2025 PARTITION OF sales
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Add new category (list)
CREATE TABLE sales_asia PARTITION OF sales_by_region
    FOR VALUES IN ('JP', 'KR', 'CN', 'IN');

-- Attach existing table as partition
ALTER TABLE sales ATTACH PARTITION sales_2024_default
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

**Why add partitions?** Handle new data ranges or categories.

**How it works:** ATTACH makes existing table a partition; CREATE creates new partition.

**When to add:** Before data arrives, during maintenance windows.

### Detaching Partitions

```sql
-- Detach partition (becomes regular table)
ALTER TABLE sales DETACH PARTITION sales_2023;

-- Detach with constraints
ALTER TABLE sales DETACH PARTITION sales_2023
    CONCURRENTLY;  -- Non-blocking (PostgreSQL 13+)

-- Now can drop or archive
DROP TABLE sales_2023;
-- or
ALTER TABLE sales_2023 RENAME TO sales_2023_archived;
```

**Why detach partitions?** Archive old data, remove unwanted partitions.

**How it works:** DETACH removes from partitioned table, partition becomes standalone table.

**When to detach:** Data lifecycle management, archiving old data.

### Splitting and Merging Partitions

```sql
-- Split partition (advanced, requires careful planning)
-- 1. Detach partition
ALTER TABLE sales DETACH PARTITION sales_2024;

-- 2. Split data into new tables
CREATE TABLE sales_2024_q1 AS
SELECT * FROM sales_2024 WHERE sale_date < '2024-04-01';

CREATE TABLE sales_2024_q2 AS
SELECT * FROM sales_2024 WHERE sale_date >= '2024-04-01';

-- 3. Attach new partitions
ALTER TABLE sales ATTACH PARTITION sales_2024_q1
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

ALTER TABLE sales ATTACH PARTITION sales_2024_q2
    FOR VALUES FROM ('2024-04-01') TO ('2025-01-01');
```

**Why split partitions?** Finer granularity for large partitions, performance optimization.

**How it works:** Manual process requiring data movement and constraint management.

**When to split:** Performance issues with large partitions, changing access patterns.

### Automatic Partition Creation

```sql
-- Function to create partitions automatically
CREATE OR REPLACE FUNCTION create_partition_if_not_exists(
    table_name TEXT,
    partition_name TEXT,
    partition_range TEXT
) RETURNS VOID AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_inherits i ON c.oid = i.inhrelid
        WHERE c.relname = partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF %I %s',
            partition_name, table_name, partition_range
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT create_partition_if_not_exists(
    'events',
    'events_2024_05',
    'FOR VALUES FROM (''2024-05-01'') TO (''2024-06-01'')'
);
```

**Why automate?** Handle future partitions without manual intervention.

**How it works:** Check catalog, create if missing.

**When to use:** Applications that need to create partitions on demand.

---

## Indexing Partitioned Tables

### Local vs Global Indexes

```sql
-- Local index (on each partition)
CREATE INDEX ON sales (sale_date);  -- Automatically local

-- Explicit local index
CREATE INDEX ON sales_2024 (customer_id);

-- Global index (on partitioned table)
CREATE INDEX CONCURRENTLY ON sales (customer_id);  -- PostgreSQL 11+

-- Unique indexes must be local
CREATE UNIQUE INDEX ON sales (id);  -- Local by default
```

**Why local indexes?** Smaller indexes, partition pruning applies to indexes too.

**How they work:** Each partition has its own index, queries only search relevant partition indexes.

**When to use:** Most cases, especially for partition key columns.

### Index Partitioning Strategies

```sql
-- Index on partition key (usually automatic)
CREATE INDEX ON sales (sale_date);

-- Index on commonly queried columns
CREATE INDEX ON sales (customer_id, sale_date);

-- Partial indexes on partitions
CREATE INDEX ON sales_2024 (amount) WHERE amount > 1000;

-- Covering indexes
CREATE INDEX ON sales (customer_id, sale_date, amount);
```

**Why index strategies?** Optimize query performance for different access patterns.

**How to choose:** Analyze query patterns, consider index size vs benefit.

**When to add:** After partitioning, when queries are slow.

### Index Maintenance

```sql
-- Reindex partition
REINDEX INDEX sales_2024_customer_id_idx;

-- Reindex all partitions
DO $$
DECLARE
    part_name TEXT;
BEGIN
    FOR part_name IN
        SELECT inhrelid::regclass::text
        FROM pg_inherits
        WHERE inhparent = 'sales'::regclass
    LOOP
        EXECUTE format('REINDEX TABLE %I', part_name);
    END LOOP;
END $$;
```

**Why maintenance?** Indexes can become bloated, especially on high-update partitions.

**How to automate:** Regular reindexing jobs, monitor index bloat.

**When to reindex:** Performance degradation, after bulk operations.

---

## Performance Considerations

### Partition Size Guidelines

```sql
-- Check partition sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Ideal partition sizes:
-- Small partitions: < 1GB (fast operations)
-- Medium partitions: 1-10GB (balanced)
-- Large partitions: > 10GB (may need splitting)
```

**Why size matters?** Query performance, maintenance time, backup/restore speed.

**How to measure:** pg_total_relation_size(), monitor growth over time.

**When to adjust:** Performance issues, maintenance windows too long.

### Query Performance Analysis

```sql
-- Analyze partitioned query
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM sales
WHERE sale_date BETWEEN '2024-01-01' AND '2024-03-31'
  AND customer_id = 123;

-- Check for:
-- Partition pruning working
-- Parallel workers used
-- Buffer usage
-- Execution time
```

**Why analyze?** Ensure partitioning provides expected benefits.

**How to optimize:** Adjust partition boundaries, add indexes, change partitioning strategy.

**When to analyze:** After partitioning, when performance doesn't improve.

### Parallel Query Execution

```sql
-- Enable parallel queries
SET max_parallel_workers_per_gather = 4;

-- Check if parallel execution works
EXPLAIN (ANALYZE)
SELECT COUNT(*), AVG(amount)
FROM sales
WHERE sale_date >= '2024-01-01';

-- Look for:
-- "Workers Planned: 4"
-- "Workers Launched: 4"
```

**Why parallel queries?** Faster execution on partitioned tables.

**How it works:** PostgreSQL can scan partitions in parallel.

**When it helps:** Large partitions, CPU-bound queries, multiple partitions accessed.

### Partitioning Overhead

```sql
-- Check catalog overhead
SELECT count(*) as partition_count
FROM pg_inherits
WHERE inhparent = 'sales'::regclass;

-- Monitor catalog bloat
SELECT
    schemaname,
    tablename,
    n_tup_ins, n_tup_upd, n_tup_del,
    n_live_tup, n_dead_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

**Why monitor overhead?** Too many partitions can hurt performance.

**How to optimize:** Consolidate small partitions, use appropriate partition counts.

**When overhead matters:** Thousands of partitions, catalog-intensive operations.

---

## Common Patterns

### Time-Series Partitioning

```sql
-- Daily partitions for logs
CREATE TABLE application_logs (
    id BIGSERIAL,
    level TEXT,
    message TEXT,
    user_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Automated daily partition creation
CREATE OR REPLACE FUNCTION create_daily_partition(
    base_table TEXT,
    partition_date DATE
) RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_name := base_table || '_' || to_char(partition_date, 'YYYY_MM_DD');
    start_date := partition_date;
    end_date := partition_date + INTERVAL '1 day';

    IF NOT EXISTS (
        SELECT 1 FROM pg_class
        WHERE relname = partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
            partition_name, base_table, start_date, end_date
        );
    END IF;
END;
$$ LANGUAGE plpgsql;
```

**Why daily partitions?** Fine-grained control, easy archiving, optimal for log data.

**How to automate:** Cron jobs or application triggers to create partitions in advance.

**When to use:** High-volume time-series data, audit logs, event streams.

### Geographical Partitioning

```sql
-- Partition by country/region
CREATE TABLE user_registrations (
    id SERIAL,
    country_code TEXT,
    user_name TEXT,
    email TEXT,
    registered_at TIMESTAMPTZ
) PARTITION BY LIST (country_code);

-- Regional partitions
CREATE TABLE registrations_na PARTITION OF user_registrations
    FOR VALUES IN ('US', 'CA', 'MX');

CREATE TABLE registrations_eu PARTITION OF user_registrations
    FOR VALUES IN ('UK', 'DE', 'FR', 'IT', 'ES');

-- Data sovereignty compliance
-- Keep EU data in EU partitions for GDPR
```

**Why geographical?** Data locality, compliance with regional regulations.

**How to implement:** List partitioning by country/region codes.

**When to use:** Global applications, data residency requirements, regional reporting.

### Hash Partitioning for Scalability

```sql
-- User activity with hash partitioning
CREATE TABLE user_sessions (
    user_id INTEGER,
    session_id TEXT,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    data JSONB
) PARTITION BY HASH (user_id);

-- Create power-of-2 partitions
DO $$
DECLARE
    modulus INTEGER := 16;
    i INTEGER;
BEGIN
    FOR i IN 0..modulus-1 LOOP
        EXECUTE format(
            'CREATE TABLE user_sessions_%s PARTITION OF user_sessions FOR VALUES WITH (MODULUS %s, REMAINDER %s)',
            i, modulus, i
        );
    END LOOP;
END $$;

-- Benefits: Even distribution, parallel queries
```

**Why hash for scalability?** Even load distribution, no hotspots.

**How it scales:** Add more partitions as data grows.

**When to use:** Primary key partitioning, uniform access patterns.

---

## Best Practices

### 1. Choose Partition Key Wisely

```sql
-- ✅ Good: Frequently queried in WHERE clauses
CREATE TABLE orders PARTITION BY RANGE (order_date);

-- ❌ Bad: Rarely used in queries
CREATE TABLE orders PARTITION BY RANGE (created_by_user_id);
```

### 2. Plan Partition Boundaries

```sql
-- ✅ Future-proof: Create partitions in advance
-- Create next 12 months of partitions

-- ❌ Reactive: Create partitions as needed
-- Risk of insert failures during partition creation
```

### 3. Monitor Partition Usage

```sql
-- Check partition access patterns
SELECT
    schemaname,
    tablename,
    seq_scan, seq_tup_read,
    idx_scan, idx_tup_fetch,
    n_tup_ins, n_tup_upd, n_tup_del
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY seq_scan DESC;
```

### 4. Automate Partition Management

```sql
-- Create partitions script
-- Run weekly/monthly to create future partitions

-- Archive old partitions
-- Move to separate tablespace or export
```

### 5. Test Partition Queries

```sql
-- Verify pruning
EXPLAIN SELECT * FROM partitioned_table
WHERE partition_key = 'test_value';

-- Test performance
SELECT * FROM partitioned_table
WHERE partition_key BETWEEN 'start' AND 'end';
```

### 6. Consider Partition Count

```sql
-- Too few: Large partitions, poor pruning
-- Too many: Catalog overhead, maintenance complexity
-- Ideal: 10-100 partitions per table
```

### 7. Index Strategically

```sql
-- Local indexes for partition-specific queries
-- Global indexes for cross-partition queries
-- Partial indexes for common filters
```

### 8. Plan for Data Lifecycle

```sql
-- Hot data: Recent partitions, fast storage
-- Warm data: Older partitions, slower storage
-- Cold data: Archived partitions, separate system
```

---

## Interview Questions

### Q1: What is table partitioning and why use it?

**Answer:** Table partitioning divides a large table into smaller, more manageable pieces called partitions. PostgreSQL supports range, list, and hash partitioning.

**Benefits:**
- **Performance**: Queries can prune irrelevant partitions, scanning less data
- **Maintenance**: Easier to manage smaller partitions (backup, restore, vacuum)
- **Scalability**: Handle tables larger than available RAM
- **Data lifecycle**: Archive old partitions, keep recent data optimized

**Example:**
```sql
CREATE TABLE sales PARTITION BY RANGE (sale_date);
CREATE TABLE sales_2024 PARTITION OF sales
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

**When to use:** Tables > 100GB, time-series data, frequent range queries.

### Q2: Explain the difference between range, list, and hash partitioning.

**Answer:**

**Range Partitioning:**
- Divides data by contiguous value ranges
- Best for: Time-series data, ordered numeric data
- Example: Sales by month/year
```sql
PARTITION BY RANGE (sale_date)
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01')
```

**List Partitioning:**
- Assigns rows based on discrete values
- Best for: Categorical data, geographic regions
- Example: Data by country/state
```sql
PARTITION BY LIST (country)
FOR VALUES IN ('US', 'CA', 'MX')
```

**Hash Partitioning:**
- Distributes rows evenly using hash function
- Best for: Even data distribution, load balancing
- Example: User data across servers
```sql
PARTITION BY HASH (user_id)
FOR VALUES WITH (MODULUS 4, REMAINDER 0)
```

### Q3: How does partition pruning work?

**Answer:** Partition pruning eliminates irrelevant partitions during query execution, improving performance by scanning less data.

**How it works:**
1. Query planner analyzes WHERE conditions
2. Determines which partitions can contain matching rows
3. Excludes partitions that cannot match

**Examples:**
```sql
-- ✅ Prunes to relevant partitions
SELECT * FROM sales WHERE sale_date = '2024-03-15';

-- ❌ No pruning (scans all)
SELECT * FROM sales WHERE customer_id = 123;  -- Wrong column
SELECT * FROM sales WHERE EXTRACT(year FROM sale_date) = 2024;  -- Function
```

**Monitoring:**
```sql
EXPLAIN SELECT * FROM partitioned_table WHERE partition_key = 'value';
-- Look for "Partitions selected: table_part_1"
```

### Q4: When should you NOT use partitioning?

**Answer:** Avoid partitioning when it doesn't provide benefits or adds unnecessary complexity.

**Don't partition when:**
- Table is small (< 10GB)
- Queries don't filter on partition key
- Simple CRUD operations dominate
- Maintenance overhead outweighs benefits

**Anti-patterns:**
```sql
-- ❌ Partitioning small lookup table
CREATE TABLE status_codes PARTITION BY LIST (category);  -- Only 100 rows

-- ❌ No partition key queries
SELECT * FROM partitioned_table WHERE other_column = 'value';  -- Scans all partitions
```

**Consider alternatives:**
- Regular indexes for performance
- Table inheritance for complex schemas
- Separate tables for different data types

### Q5: How do you add a new partition to an existing partitioned table?

**Answer:** Use CREATE TABLE ... PARTITION OF syntax to add new partitions.

```sql
-- Add range partition
CREATE TABLE sales_2025 PARTITION OF sales
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Add list partition
CREATE TABLE sales_asia PARTITION OF sales_by_region
    FOR VALUES IN ('JP', 'KR', 'CN');

-- Attach existing table
ALTER TABLE sales ATTACH PARTITION sales_2024
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

**Best practices:**
- Create partitions before data arrives
- Test with sample data first
- Update application code if needed
- Reindex if necessary

### Q6: What are the performance implications of partitioning?

**Answer:** Partitioning can significantly improve or hurt performance depending on usage.

**Benefits:**
- **Query performance**: Pruning reduces data scanned
- **Maintenance**: Smaller partitions faster to vacuum/index
- **Parallelism**: Multiple partitions can be processed in parallel
- **Archiving**: Easy to detach/archive old partitions

**Costs:**
- **Planning overhead**: More complex query planning
- **Catalog bloat**: Many partitions increase catalog size
- **Index overhead**: Local indexes on each partition
- **Memory usage**: More metadata to cache

**Monitoring:**
```sql
EXPLAIN (ANALYZE) SELECT * FROM partitioned_table WHERE partition_key = 'value';
-- Check for pruning and parallel workers
```

### Q7: How do you migrate an existing table to partitioning?

**Answer:** Careful process to avoid downtime:

**Step 1: Create partitioned table**
```sql
CREATE TABLE sales_new (
    id SERIAL,
    sale_date DATE,
    amount DECIMAL
) PARTITION BY RANGE (sale_date);
```

**Step 2: Create partitions**
```sql
CREATE TABLE sales_2024 PARTITION OF sales_new
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

**Step 3: Copy data**
```sql
INSERT INTO sales_new SELECT * FROM sales;
```

**Step 4: Switch tables (with care)**
```sql
BEGIN;
ALTER TABLE sales RENAME TO sales_old;
ALTER TABLE sales_new RENAME TO sales;
COMMIT;
```

**Step 5: Update permissions and constraints**

**Zero-downtime approach:** Use logical replication or application-level switching.

### Q8: Explain hash partitioning and when to use it.

**Answer:** Hash partitioning distributes rows evenly across partitions using a hash function on the partition key.

**How it works:**
- PostgreSQL applies hash function to partition key
- Result modulo number of partitions determines assignment
- Ensures even data distribution

**Syntax:**
```sql
CREATE TABLE data PARTITION BY HASH (user_id);

CREATE TABLE data_0 PARTITION OF data
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE data_1 PARTITION OF data
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
-- etc.
```

**When to use:**
- No natural partitioning key (range/list)
- Want even data distribution
- Primary key partitioning for scalability
- Load balancing across partitions

**Advantages:**
- Even partition sizes
- Predictable distribution
- Good for parallel queries

**Disadvantages:**
- No logical grouping (all partitions may be needed)
- Harder to reason about data location

---

## Summary

**Key Takeaways:**

1. **Partitioning types**: Range (time/ordered), List (categories), Hash (even distribution)
2. **Partition pruning**: Eliminates irrelevant partitions for better performance
3. **Maintenance**: Add/detach partitions for data lifecycle management
4. **Indexing**: Local indexes for partition-specific queries
5. **Performance**: Benefits large tables with appropriate query patterns
6. **Planning**: Choose partition key based on query patterns, plan boundaries carefully
7. **Monitoring**: Check pruning effectiveness, partition sizes, query performance

**Partitioning Decision Flow:**
```
Table size > 10GB?
├── No → Don't partition
└── Yes → Query patterns?
    ├── Time-based ranges → Range partitioning
    ├── Categorical data → List partitioning  
    └── Even distribution → Hash partitioning
```

---

## Cross-Links

- **Indexes**: [[SQL/02_Core/01_Indexes_Basics_and_BTree]]
- **VACUUM**: [[SQL/03_Advanced/01_VACUUM_Autovacuum_and_Bloat]]
- **Query Planning**: [[SQL/02_Core/04_Explain_Analyze_and_Query_Plans]]
- **Replication**: [[SQL/03_Advanced/03_Replication_and_Backups]]

## References

- [PostgreSQL Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)
- [Partition Pruning](https://www.postgresql.org/docs/current/ddl-partitioning.html#DDL-PARTITIONING-DECLARATIVE-PRUNING)
- [Partitioning Best Practices](https://www.postgresql.org/docs/current/ddl-partitioning.html#DDL-PARTITIONING-IMPLEMENTATION-PARTITIONING-USING-INHERITANCE)

---

**Status**: stable  
**Last Updated**: 2026-04-26  
**Lines**: 856