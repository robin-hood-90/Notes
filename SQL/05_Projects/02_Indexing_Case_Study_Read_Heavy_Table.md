---
tags: [sql, postgresql, projects, performance, indexing]
aliases: ["Read-Heavy Indexing Case Study", "Events Table Indexing", "Composite Index Design"]
status: stable
updated: 2026-04-27
---

# Project: Indexing Case Study (Read-Heavy Table)

> [!summary] Model
> Comprehensive case study of optimizing a read-heavy events table: analyze query patterns, design composite indexes, validate performance improvements, and implement maintenance strategies. Focuses on index selectivity, scan types, and cost-benefit analysis.

## Table of Contents

1. [[#Case Study Overview]]
2. [[#Problem Statement]]
3. [[#Data Analysis]]
4. [[#Query Pattern Analysis]]
5. [[#Index Design Process]]
6. [[#Implementation Strategy]]
7. [[#Performance Testing]]
8. [[#Results Analysis]]
9. [[#Advanced Optimizations]]
10. [[#Maintenance Considerations]]
11. [[#Cost-Benefit Analysis]]
12. [[#Best Practices]]
13. [[#Pitfalls & Gotchas]]
14. [[#Interview Questions]]
15. [[#Cheat Sheet]]
16. [[#Cross-Links]]
17. [[#References]]

---

## Case Study Overview

### Business Context

**Company:** Analytics platform processing user events
**Problem:** Slow queries on events table impacting dashboard performance
**Impact:** User-facing delays, increased infrastructure costs
**Goal:** Optimize read performance by 10x while controlling write overhead

### Technical Context

**Table structure:**
```sql
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Current indexes
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_type ON events(event_type);
```

**Data characteristics:**
- 500M+ rows
- 100GB+ table size
- 10K+ inserts/second
- 1M+ reads/second
- Retention: 90 days
- Hot data: last 7 days

### Success Criteria

- [ ] Dashboard queries <100ms (currently 2-5s)
- [ ] Top 10 queries optimized
- [ ] Write performance degradation <10%
- [ ] Index maintenance time acceptable
- [ ] Query plans use indexes appropriately

---

## Problem Statement

### Current Performance Issues

**Slow queries observed:**
1. **User activity dashboard:** Recent events by user (2-3s)
2. **Event type analytics:** Events by type and time range (4-5s)
3. **Session analysis:** Events for specific session (1-2s)
4. **Geographic analysis:** Events by IP range (3-4s)

**Root causes identified:**
- Sequential scans on large table
- Inefficient index usage
- Missing composite indexes
- Poor query plan choices

### Performance Metrics

**Current baseline:**
```sql
-- Typical slow query
SELECT COUNT(*), event_type
FROM events
WHERE user_id = 12345
  AND timestamp >= '2024-01-01'
  AND timestamp < '2024-01-02'
GROUP BY event_type;

-- EXPLAIN output shows:
-- Seq Scan on events (cost=0.00..500000.00 rows=1000000 width=50)
-- Filter: (user_id = 12345) AND (timestamp >= '2024-01-01'::timestamp) AND (timestamp < '2024-01-02'::timestamp)
-- Rows: ~50,000 actual rows from 500M table
```

**Performance requirements:**
- P95 query time <100ms
- Support 1M concurrent users
- Handle 10K events/second ingestion
- Maintain sub-second dashboard loads

---

## Data Analysis

### Table Structure Deep Dive

**Complete schema:**
```sql
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (timestamp);

-- Partition by day for last 90 days
-- 90 partitions, each ~5-10GB
```

**Data distribution analysis:**
```sql
-- Row count and size
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    n_tup_ins, n_tup_upd, n_tup_del, n_live_tup
FROM pg_stat_user_tables
WHERE tablename LIKE 'events%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Column statistics
SELECT
    attname,
    n_distinct,
    most_common_vals,
    most_common_freqs,
    histogram_bounds
FROM pg_stats
WHERE tablename = 'events'
ORDER BY attname;

-- Data skew analysis
SELECT
    event_type,
    count(*) as frequency,
    round(count(*)::numeric / sum(count(*)) over (), 4) as percentage
FROM events
WHERE timestamp >= now() - interval '7 days'
GROUP BY event_type
ORDER BY count DESC
LIMIT 20;
```

### Index Usage Analysis

**Current index effectiveness:**
```sql
-- Index usage statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE tablename LIKE 'events%'
ORDER BY idx_scan DESC;

-- Unused indexes
SELECT indexname, pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE tablename LIKE 'events%' AND idx_scan = 0;

-- Index bloat check
SELECT
    nspname,
    relname,
    idxname,
    round(100 * (pg_relation_size(indexrelid) - pg_relation_size(indexrelid, 'main'))::numeric / pg_relation_size(indexrelid), 2) as bloat_pct
FROM pg_stat_user_indexes
WHERE nspname = 'public' AND relname LIKE 'events%';
```

### Query Pattern Analysis

**Top query patterns from pg_stat_statements:**
```sql
-- Enable if not already
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Top queries by total time
SELECT
    query,
    calls,
    total_time / 1000 as total_time_sec,
    mean_time / 1000 as mean_time_ms,
    rows / calls as avg_rows
FROM pg_stat_statements
WHERE query LIKE '%events%'
ORDER BY total_time DESC
LIMIT 20;

-- Query pattern clustering
SELECT
    regexp_replace(query, '[0-9]+', '?', 'g') as query_pattern,
    count(*) as pattern_count,
    sum(total_time) / 1000 as total_time_sec,
    avg(mean_time) / 1000 as avg_time_ms
FROM pg_stat_statements
WHERE query LIKE '%events%'
GROUP BY regexp_replace(query, '[0-9]+', '?', 'g')
ORDER BY sum(total_time) DESC;
```

**Common query patterns identified:**
1. **User activity:** `WHERE user_id = ? AND timestamp >= ?`
2. **Event analytics:** `WHERE event_type = ? AND timestamp BETWEEN ? AND ?`
3. **Session tracking:** `WHERE session_id = ? ORDER BY timestamp`
4. **Time-based aggregation:** `WHERE timestamp >= ? GROUP BY event_type`
5. **User + type combo:** `WHERE user_id = ? AND event_type = ? AND timestamp >= ?`

---

## Query Pattern Analysis

### Pattern 1: User Activity Queries

**Typical queries:**
```sql
-- Recent user activity
SELECT * FROM events
WHERE user_id = 12345
  AND timestamp >= NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC
LIMIT 100;

-- User events by type
SELECT event_type, COUNT(*) as count
FROM events
WHERE user_id = 12345
  AND timestamp >= '2024-01-01'
GROUP BY event_type;

-- User session events
SELECT * FROM events
WHERE user_id = 12345
  AND session_id = 'session_abc'
ORDER BY timestamp;
```

**Current execution:**
- Uses `idx_events_user_id` (good)
- Filters timestamp (good)
- But: No composite index for user_id + timestamp

**Optimization opportunity:** Composite index on (user_id, timestamp)

### Pattern 2: Event Type Analytics

**Typical queries:**
```sql
-- Events by type and time
SELECT COUNT(*) as event_count
FROM events
WHERE event_type = 'page_view'
  AND timestamp >= '2024-01-01'
  AND timestamp < '2024-01-02';

-- Type distribution over time
SELECT
    date_trunc('hour', timestamp) as hour,
    event_type,
    COUNT(*) as events
FROM events
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY date_trunc('hour', timestamp), event_type;
```

**Current execution:**
- Uses `idx_events_type` and `idx_events_timestamp`
- Often results in bitmap index scans
- High planning overhead

**Optimization opportunity:** Composite index on (event_type, timestamp)

### Pattern 3: Session Analysis

**Typical queries:**
```sql
-- Session event sequence
SELECT * FROM events
WHERE session_id = 'session_xyz'
ORDER BY timestamp;

-- Session duration
SELECT
    session_id,
    MIN(timestamp) as start_time,
    MAX(timestamp) as end_time,
    EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) as duration_sec
FROM events
WHERE session_id = 'session_xyz'
GROUP BY session_id;
```

**Current execution:**
- No index on session_id
- Results in sequential scans
- Very slow for large tables

**Optimization opportunity:** Index on session_id (possibly composite with timestamp)

### Pattern 4: Time-Based Aggregations

**Typical queries:**
```sql
-- Hourly event counts
SELECT
    date_trunc('hour', timestamp) as hour,
    COUNT(*) as total_events
FROM events
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY date_trunc('hour', timestamp);

-- Event type trends
SELECT
    event_type,
    date_trunc('day', timestamp) as day,
    COUNT(*) as daily_count
FROM events
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY event_type, date_trunc('day', timestamp);
```

**Current execution:**
- Uses timestamp index
- But GROUP BY requires sorting
- Potential for index-only scans

**Optimization opportunity:** Covering indexes with date_trunc results

### Pattern Analysis Summary

**Query pattern frequency:**
```
Pattern                    | Frequency | Current Index Usage | Optimization Potential
--------------------------|-----------|-------------------|-------------------
user_id + timestamp        | High      | Partial          | High
event_type + timestamp     | High      | Partial          | High
session_id                 | Medium    | None             | High
timestamp only             | High      | Good             | Medium
user_id + event_type       | Medium    | None             | Medium
JSONB queries              | Low       | None             | Low (GIN needed)
```

---

## Index Design Process

### Step 1: Index Selection Criteria

**Index candidates ranked by impact:**

1. **High selectivity + high frequency:** user_id + timestamp
2. **High selectivity + high frequency:** event_type + timestamp
3. **Medium selectivity + high frequency:** session_id
4. **Low selectivity but covering:** timestamp + event_type
5. **Specialized:** Partial indexes for common filters

**Index types to consider:**
- **B-Tree:** Default, good for equality and range queries
- **BRIN:** For timestamp columns (if physically ordered)
- **GIN:** For JSONB event_data
- **Partial:** For common WHERE conditions

### Step 2: Composite Index Design

**Composite index principles:**
- **Leading column:** Most selective or most frequently filtered
- **Subsequent columns:** Additional filters in query order
- **Include columns:** For index-only scans (PostgreSQL 11+)

**Index design for user queries:**
```sql
-- Option 1: (user_id, timestamp) - Good for range queries
CREATE INDEX idx_events_user_timestamp ON events(user_id, timestamp);

-- Option 2: (user_id, timestamp, event_type) - More covering
CREATE INDEX idx_events_user_timestamp_type ON events(user_id, timestamp, event_type);

-- Option 3: With INCLUDE for index-only scans
CREATE INDEX idx_events_user_timestamp_covering ON events(user_id, timestamp)
INCLUDE (event_type, session_id);
```

**Index design for analytics:**
```sql
-- For event type queries
CREATE INDEX idx_events_type_timestamp ON events(event_type, timestamp);

-- For time-based aggregations
CREATE INDEX idx_events_timestamp_type ON events(timestamp, event_type);
```

### Step 3: Index Size and Maintenance Cost

**Size estimation:**
```sql
-- Estimate index size
SELECT
    pg_size_pretty(
        (SELECT reltuples FROM pg_class WHERE relname = 'events')::bigint *
        (SELECT avg_width FROM pg_stats WHERE tablename = 'events' AND attname IN ('user_id', 'timestamp'))
    ) as estimated_index_size;

-- Current table and index sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(sum(pg_relation_size(indexrelid))) as index_size
FROM pg_stat_user_indexes
WHERE tablename = 'events'
GROUP BY schemaname, tablename;
```

**Maintenance cost analysis:**
- **Insert cost:** Each index updated on insert
- **Update cost:** Indexes updated when indexed columns change
- **Storage cost:** Index size vs. performance benefit

### Step 4: Final Index Strategy

**Recommended indexes:**

1. **Primary composite index:** (user_id, timestamp) - High impact, covers most queries
2. **Analytics index:** (event_type, timestamp) - For type-based queries
3. **Session index:** (session_id, timestamp) - For session analysis
4. **BRIN index:** timestamp - For time range queries on large datasets
5. **Partial index:** For common event types

**Index creation plan:**
```sql
-- Drop inefficient indexes first
DROP INDEX IF EXISTS idx_events_user_id;  -- Replaced by composite
DROP INDEX IF EXISTS idx_events_type;     -- Replaced by composite

-- Create new composite indexes
CREATE INDEX CONCURRENTLY idx_events_user_timestamp ON events(user_id, timestamp);
CREATE INDEX CONCURRENTLY idx_events_type_timestamp ON events(event_type, timestamp);
CREATE INDEX CONCURRENTLY idx_events_session_timestamp ON events(session_id, timestamp);

-- BRIN index for time ranges
CREATE INDEX CONCURRENTLY idx_events_timestamp_brin ON events USING brin(timestamp);

-- Partial index for common event types
CREATE INDEX CONCURRENTLY idx_events_page_views ON events(event_type, timestamp)
WHERE event_type = 'page_view';
```

---

## Implementation Strategy

### Step 1: Pre-Implementation Validation

**Test environment setup:**
```sql
-- Create test table with subset of data
CREATE TABLE events_test AS
SELECT * FROM events
WHERE timestamp >= NOW() - INTERVAL '30 days'
LIMIT 1000000;

-- Create indexes on test table
CREATE INDEX idx_test_user_timestamp ON events_test(user_id, timestamp);
CREATE INDEX idx_test_type_timestamp ON events_test(event_type, timestamp);

-- Run test queries
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM events_test
WHERE user_id = 12345 AND timestamp >= '2024-01-01';
```

### Step 2: Index Creation Best Practices

**Concurrent creation:**
```sql
-- Use CONCURRENTLY to avoid blocking writes
CREATE INDEX CONCURRENTLY idx_events_user_timestamp ON events(user_id, timestamp);

-- Monitor progress (PostgreSQL 12+)
SELECT
    phase,
    blocks_total,
    blocks_done,
    tuples_total,
    tuples_done
FROM pg_stat_progress_create_index
WHERE index_relid = 'idx_events_user_timestamp'::regclass;
```

**Index creation timing:**
- Schedule during low-traffic periods
- Monitor system resources
- Have rollback plan (drop index if issues)

**Validation after creation:**
```sql
-- Verify index exists and is valid
SELECT
    indexname,
    indisvalid,
    indisready,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_indexes
WHERE tablename = 'events' AND indexname LIKE 'idx_events%';

-- Test queries use new indexes
EXPLAIN (ANALYZE)
SELECT * FROM events
WHERE user_id = 12345 AND timestamp >= NOW() - INTERVAL '1 day'
ORDER BY timestamp DESC
LIMIT 10;
```

### Step 3: Gradual Rollout

**Phased approach:**
1. **Create indexes concurrently** on production
2. **Monitor performance** for 24-48 hours
3. **Verify query plans** use new indexes
4. **Remove old indexes** if beneficial
5. **Document changes** and update baselines

**Rollback plan:**
```sql
-- If issues arise, drop new indexes
DROP INDEX IF EXISTS idx_events_user_timestamp;
DROP INDEX IF EXISTS idx_events_type_timestamp;
DROP INDEX IF EXISTS idx_events_session_timestamp;

-- Recreate original indexes if needed
CREATE INDEX CONCURRENTLY idx_events_user_id ON events(user_id);
CREATE INDEX CONCURRENTLY idx_events_timestamp ON events(timestamp);
CREATE INDEX CONCURRENTLY idx_events_type ON events(event_type);
```

---

## Performance Testing

### Step 4: Benchmark Setup

**Test queries representing real workload:**
```sql
-- Create test queries
CREATE OR REPLACE FUNCTION benchmark_queries()
RETURNS TABLE(query_name text, execution_time interval, plan_text text) AS $$
DECLARE
    start_time timestamptz;
    end_time timestamptz;
    plan_result text;
BEGIN
    -- Query 1: User recent activity
    start_time := clock_timestamp();
    EXECUTE 'EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
             SELECT COUNT(*) FROM events
             WHERE user_id = $1 AND timestamp >= $2'
    INTO plan_result USING 12345, NOW() - INTERVAL '7 days';
    end_time := clock_timestamp();

    query_name := 'user_recent_activity';
    execution_time := end_time - start_time;
    plan_text := plan_result;
    RETURN NEXT;

    -- Query 2: Event type analytics
    start_time := clock_timestamp();
    EXECUTE 'EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
             SELECT event_type, COUNT(*) FROM events
             WHERE timestamp >= $1 AND timestamp < $2
             GROUP BY event_type'
    INTO plan_result USING '2024-01-01'::timestamptz, '2024-01-02'::timestamptz;
    end_time := clock_timestamp();

    query_name := 'event_type_analytics';
    execution_time := end_time - start_time;
    plan_text := plan_result;
    RETURN NEXT;

    -- Add more queries...
END;
$$ LANGUAGE plpgsql;
```

**Automated benchmarking:**
```sql
-- Run benchmarks before and after
CREATE TABLE benchmark_results (
    run_timestamp timestamptz DEFAULT NOW(),
    run_type text, -- 'before' or 'after'
    query_name text,
    execution_time interval,
    plan_text text
);

-- Insert results
INSERT INTO benchmark_results (run_type, query_name, execution_time, plan_text)
SELECT 'before', * FROM benchmark_queries();
```

### Step 5: Load Testing

**Simulate production load:**
```sql
-- Use pgbench with custom script
-- Create benchmark script file: benchmark.sql
SELECT COUNT(*) FROM events WHERE user_id = 12345 AND timestamp >= NOW() - INTERVAL '7 days';
SELECT event_type, COUNT(*) FROM events WHERE timestamp >= '2024-01-01' GROUP BY event_type;
SELECT * FROM events WHERE session_id = 'session_abc' ORDER BY timestamp DESC LIMIT 50;

-- Run load test
pgbench -U app_user -d analytics -c 10 -j 4 -T 300 -f benchmark.sql
```

**Monitor during load test:**
```sql
-- System performance
SELECT * FROM pg_stat_bgwriter;
SELECT * FROM pg_stat_database WHERE datname = 'analytics';

-- Query performance
SELECT
    query,
    calls,
    total_time / 1000 as total_time_sec,
    blk_read_time / 1000 as read_time_sec,
    blk_write_time / 1000 as write_time_sec
FROM pg_stat_statements
WHERE query LIKE '%events%'
ORDER BY total_time DESC
LIMIT 10;

-- Lock monitoring
SELECT locktype, mode, count(*) FROM pg_locks GROUP BY locktype, mode;
```

### Step 6: Write Performance Impact

**Measure write performance:**
```sql
-- Before indexes
CREATE TABLE insert_performance (
    test_run text,
    inserts_per_second numeric
);

-- Test insert performance
DO $$
DECLARE
    start_time timestamptz;
    end_time timestamptz;
    insert_count int := 10000;
BEGIN
    start_time := clock_timestamp();

    FOR i IN 1..insert_count LOOP
        INSERT INTO events (user_id, event_type, timestamp)
        VALUES (
            (random() * 1000000)::int,
            CASE (random() * 3)::int
                WHEN 0 THEN 'page_view'
                WHEN 1 THEN 'click'
                ELSE 'purchase'
            END,
            NOW() - (random() * INTERVAL '90 days')
        );
    END LOOP;

    end_time := clock_timestamp();

    INSERT INTO insert_performance (test_run, inserts_per_second)
    VALUES ('before_indexes', insert_count / EXTRACT(EPOCH FROM (end_time - start_time)));
END;
$$;
```

---

## Results Analysis

### Step 7: Performance Comparison

**Query performance improvements:**
```sql
-- Compare before/after results
SELECT
    query_name,
    before_time,
    after_time,
    round((before_time - after_time) / before_time * 100, 2) as improvement_pct
FROM (
    SELECT
        b.query_name,
        b.execution_time as before_time,
        a.execution_time as after_time
    FROM benchmark_results b
    JOIN benchmark_results a ON b.query_name = a.query_name
    WHERE b.run_type = 'before' AND a.run_type = 'after'
) comparisons;

-- Expected results:
-- user_recent_activity: 2.5s -> 0.05s (98% improvement)
-- event_type_analytics: 4.2s -> 0.15s (96% improvement)
-- session_analysis: 3.1s -> 0.08s (97% improvement)
```

**Plan changes observed:**
```
Before: Seq Scan on events (cost=50000.00..60000.00 rows=1000)
After:  Index Scan using idx_events_user_timestamp on events (cost=10.00..100.00 rows=50)
```

### Step 8: Index Usage Analysis

**Index effectiveness metrics:**
```sql
-- Index scan statistics
SELECT
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    CASE WHEN idx_scan > 0 THEN round(idx_tup_read::numeric / idx_scan, 2) ELSE 0 END as avg_tuples_per_scan
FROM pg_stat_user_indexes
WHERE tablename = 'events'
ORDER BY idx_scan DESC;

-- Cache efficiency
SELECT
    sum(idx_blks_read) as total_reads,
    sum(idx_blks_hit) as total_hits,
    round(sum(idx_blks_hit)::numeric / (sum(idx_blks_hit) + sum(idx_blks_read)) * 100, 2) as cache_hit_pct
FROM pg_statio_user_indexes
WHERE relname = 'events';
```

### Step 9: Write Performance Impact

**Insert/update performance:**
```sql
-- Compare insert performance
SELECT
    test_run,
    inserts_per_second,
    round(inserts_per_second / (SELECT inserts_per_second FROM insert_performance WHERE test_run = 'before_indexes') * 100, 2) as performance_pct
FROM insert_performance;

-- Expected: 85-95% of original performance (5-15% degradation)
```

**Index maintenance overhead:**
```sql
-- Index size vs. benefit
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    idx_scan as usage_count
FROM pg_stat_user_indexes
WHERE tablename = 'events'
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## Advanced Optimizations

### Covering Indexes

**Index-only scans:**
```sql
-- Include additional columns for index-only scans
CREATE INDEX idx_events_user_time_covering ON events(user_id, timestamp)
INCLUDE (event_type, session_id, event_data);

-- Verify index-only scan
EXPLAIN (ANALYZE, BUFFERS)
SELECT user_id, timestamp, event_type, session_id
FROM events
WHERE user_id = 12345 AND timestamp >= '2024-01-01';
-- Should show "Index Only Scan"
```

### Partial Indexes

**Conditional indexes:**
```sql
-- Index only recent events (hot data)
CREATE INDEX idx_events_recent_user ON events(user_id, timestamp)
WHERE timestamp >= NOW() - INTERVAL '7 days';

-- Index specific event types
CREATE INDEX idx_events_purchases ON events(user_id, timestamp, event_data)
WHERE event_type = 'purchase';
```

### BRIN Indexes for Time Series

**Block range indexes:**
```sql
-- BRIN for timestamp ranges
CREATE INDEX idx_events_timestamp_brin ON events USING brin(timestamp);

-- Performance comparison
EXPLAIN (ANALYZE)
SELECT COUNT(*) FROM events
WHERE timestamp >= '2024-01-01' AND timestamp < '2024-01-02';

-- BRIN vs B-Tree: BRIN much smaller, good for large time ranges
```

### Index Combination Strategies

**Multiple index types:**
```sql
-- B-Tree for selective queries
CREATE INDEX idx_events_user_type ON events(user_id, event_type);

-- GIN for JSONB data
CREATE INDEX idx_events_data_gin ON events USING gin(event_data);

-- Partial BRIN for archived data
CREATE INDEX idx_events_old_timestamp ON events USING brin(timestamp)
WHERE timestamp < NOW() - INTERVAL '30 days';
```

---

## Maintenance Considerations

### Index Maintenance Strategy

**Regular maintenance:**
```sql
-- Update statistics
ANALYZE events;

-- Reindex if bloated
REINDEX INDEX CONCURRENTLY idx_events_user_timestamp;

-- Monitor bloat
SELECT
    schemaname,
    tablename,
    indexname,
    round(100 * (pg_relation_size(indexrelid) - pg_relation_size(indexrelid, 'main'))::numeric / pg_relation_size(indexrelid), 2) as bloat_pct
FROM pg_stat_user_indexes
WHERE tablename = 'events' AND bloat_pct > 20;
```

### Index Usage Monitoring

**Track index effectiveness:**
```sql
-- Reset statistics
SELECT pg_stat_reset();

-- Monitor for 1 week
-- Then check usage
SELECT
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    CASE WHEN idx_scan > 0 THEN 'USED' ELSE 'UNUSED' END as status
FROM pg_stat_user_indexes
WHERE tablename = 'events';
```

**Remove unused indexes:**
```sql
-- Drop unused indexes
DROP INDEX IF EXISTS unused_index_name;
```

### Partitioning and Indexing

**Partition-aware indexing:**
```sql
-- Index on partitioned table
CREATE INDEX idx_events_partitioned_user_time ON events(user_id, timestamp);

-- Partition-specific indexes
CREATE INDEX idx_events_2024_q1_user ON events_2024_q1(user_id);
CREATE INDEX idx_events_2024_q2_user ON events_2024_q2(user_id);
-- (Only on hot partitions)
```

---

## Cost-Benefit Analysis

### Performance Benefits

**Quantitative improvements:**
- Query time reduction: 95-98% faster
- CPU usage reduction: 80% less CPU for queries
- I/O reduction: 90% fewer disk reads
- User experience: Sub-second dashboard loads

**Business impact:**
- Faster user interactions
- Reduced infrastructure costs
- Better scalability
- Improved user satisfaction

### Costs and Trade-offs

**Storage costs:**
```sql
-- Calculate total index size
SELECT
    pg_size_pretty(sum(pg_relation_size(indexrelid))) as total_index_size,
    pg_size_pretty(pg_relation_size('events')) as table_size,
    round(sum(pg_relation_size(indexrelid))::numeric / pg_relation_size('events') * 100, 2) as index_to_table_ratio
FROM pg_stat_user_indexes
WHERE tablename = 'events';

-- Expected: 50-100% of table size for comprehensive indexing
```

**Write performance costs:**
- Insert time increase: 10-20%
- Update time increase: 5-15%
- Delete time increase: Minimal
- Bulk load impact: Significant (consider dropping indexes)

**Maintenance costs:**
- Index rebuild time: Hours for large tables
- Statistics update: Regular ANALYZE required
- Monitoring overhead: Additional metrics to track

### ROI Calculation

**Cost-benefit summary:**
```
Benefit                  | Value
------------------------|--------
Query performance        | 10x faster (95% improvement)
User experience          | Sub-second responses
Infrastructure savings   | 30-50% fewer servers needed

Cost                     | Value
------------------------|--------
Storage                  | 50-100GB additional
Write performance        | 10-20% slower
Maintenance              | Weekly index monitoring

ROI                     | 5-10x performance improvement vs. 10-20% write cost
```

---

## Best Practices

### 1. Index Design Principles

**Start with query analysis:**
- Use pg_stat_statements to identify slow queries
- Focus on queries with highest total_time
- Consider query frequency and impact

**Index selectivity:**
- High selectivity (>1%) for small result sets
- Composite indexes for multi-column WHERE clauses
- INCLUDE columns for index-only scans

**Balance read vs. write:**
- Read-heavy tables: More indexes acceptable
- Write-heavy tables: Fewer, more selective indexes
- Mixed workloads: Strategic indexing based on access patterns

### 2. Implementation Best Practices

**Concurrent creation:**
- Always use CONCURRENTLY for production
- Monitor progress and system impact
- Test on staging first

**Gradual rollout:**
- Create indexes during maintenance windows
- Monitor performance for 24-48 hours
- Have rollback plan ready

**Validation:**
- Verify query plans use new indexes
- Measure actual performance improvement
- Monitor system resource usage

### 3. Monitoring and Maintenance

**Regular monitoring:**
- Index usage statistics weekly
- Index bloat monthly
- Query performance regression testing
- Storage growth trends

**Maintenance schedule:**
- ANALYZE tables weekly
- REINDEX bloated indexes monthly
- Review unused indexes quarterly
- Plan major reindexing during maintenance windows

### 4. Advanced Techniques

**Index strategies:**
- Use partial indexes for common filters
- Consider BRIN for time-series data
- Use GIN for JSONB columns when needed
- Implement index-only scans where possible

**Query optimization:**
- Rewrite queries to use indexes better
- Use query hints if necessary (pg_hint_plan)
- Consider denormalization for read-heavy workloads

### 5. Documentation and Knowledge Sharing

**Document decisions:**
- Why each index was created
- Performance improvements achieved
- Maintenance procedures
- Future considerations

**Team knowledge:**
- Share indexing best practices
- Document query optimization techniques
- Create runbooks for common issues

---

## Pitfalls and Gotchas

### Common Mistakes

1. **Over-indexing:**
   - Creating indexes for rarely used queries
   - Indexes slow down writes significantly
   - Each index consumes storage and maintenance

2. **Wrong column order in composite indexes:**
   - Leading column should be most selective
   - Order matters for index usage
   - Poor order leads to unused indexes

3. **Ignoring index maintenance:**
   - Indexes become bloated over time
   - Statistics become outdated
   - Performance degrades gradually

4. **Not testing with production data:**
   - Development data may have different distributions
   - Indexes work differently on production scale
   - Always test with realistic data volumes

5. **Focusing only on SELECT performance:**
   - INSERT/UPDATE/DELETE also affected
   - Write performance critical for high-throughput systems
   - Balance read and write optimization

### Hidden Costs

**Index maintenance during bulk loads:**
```sql
-- Drop indexes before bulk load
DROP INDEX idx_events_user_timestamp;
-- Load data
COPY events FROM 'large_file.csv' WITH CSV;
-- Recreate indexes
CREATE INDEX idx_events_user_timestamp ON events(user_id, timestamp);
```

**WAL overhead:**
- Indexes generate more WAL traffic
- Replication lag can increase
- Backup size grows

**Memory usage:**
- Index scans use more memory than seq scans
- work_mem settings may need adjustment
- Large result sets can cause memory pressure

### When NOT to Add Indexes

**Don't index when:**
- Table is small (<1000 rows)
- Query selectivity is very low (<0.1%)
- Write load is extremely high
- Storage is severely constrained
- Query is run very infrequently

**Better alternatives:**
- Table partitioning
- Summary tables/materialized views
- Query rewriting
- Application-level caching

---

## Interview Questions

### Q1: How would you optimize a read-heavy events table in PostgreSQL?

**Answer:** Systematic approach to indexing optimization:

1. **Analyze current performance:**
   ```sql
   -- Identify slow queries
   SELECT query, total_time/calls as avg_time
   FROM pg_stat_statements
   WHERE query LIKE '%events%'
   ORDER BY total_time DESC LIMIT 10;
   ```

2. **Understand query patterns:**
   - Group queries by access patterns
   - Identify common WHERE clauses, JOINs, ORDER BY
   - Determine selectivity and frequency

3. **Design appropriate indexes:**
   ```sql
   -- Composite indexes for common patterns
   CREATE INDEX idx_events_user_timestamp ON events(user_id, timestamp);
   CREATE INDEX idx_events_type_timestamp ON events(event_type, timestamp);
   ```

4. **Test and validate:**
   ```sql
   -- Before/after performance comparison
   EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
   ```

5. **Monitor and maintain:**
   - Track index usage
   - Remove unused indexes
   - Monitor bloat and rebuild when needed

**Why this approach?** Ensures optimal performance without excessive overhead.

### Q2: What factors influence composite index column order?

**Answer:** Column order in composite indexes is critical:

**Leading column considerations:**
- **Selectivity:** Most selective column first (reduces index scan size)
- **Query frequency:** Column used in most WHERE clauses
- **Data distribution:** Low cardinality columns may not help much

**Example:**
```sql
-- Good: user_id is selective, used frequently
CREATE INDEX idx_events_user_time ON events(user_id, timestamp);

-- Bad: timestamp first (less selective)
CREATE INDEX idx_events_time_user ON events(timestamp, user_id);
```

**Index usage rules:**
- Index used if leading columns are in WHERE clause
- Can use partial index scans if later columns filtered
- ORDER BY can use index if matches column order

**Testing:**
```sql
EXPLAIN SELECT * FROM events WHERE user_id = 1; -- Uses index
EXPLAIN SELECT * FROM events WHERE timestamp > '2024-01-01'; -- Doesn't use index
```

### Q3: How do you decide between B-Tree, BRIN, and GIN indexes?

**Answer:** Choose index type based on data and query patterns:

**B-Tree (default):**
- **Best for:** Equality, range queries on scalar data
- **Use when:** Standard OLTP queries, high selectivity
- **Example:** `WHERE user_id = ? AND timestamp >= ?`

**BRIN (Block Range Index):**
- **Best for:** Large ordered datasets, time-series
- **Use when:** Physically ordered data, range queries on large tables
- **Example:** `WHERE timestamp BETWEEN ? AND ?` on 100M+ rows
- **Advantages:** Much smaller than B-Tree

**GIN (Generalized Inverted Index):**
- **Best for:** Multi-value data, text search, JSONB
- **Use when:** Containment queries (`@>`, `?`), full-text search
- **Example:** `WHERE event_data @> '{"type": "click"}'`

**Decision factors:**
- Data type and distribution
- Query patterns
- Storage constraints
- Maintenance overhead

### Q4: How do you handle indexing for high-write-throughput tables?

**Answer:** Balance read performance with write overhead:

**Strategies:**

1. **Selective indexing:**
   - Only index columns used in frequent, selective queries
   - Avoid over-indexing
   - Use composite indexes to cover multiple queries

2. **Index maintenance optimization:**
   ```sql
   -- Use CONCURRENTLY for production
   CREATE INDEX CONCURRENTLY idx_events_user_time ON events(user_id, timestamp);

   -- Monitor index bloat
   REINDEX INDEX CONCURRENTLY idx_events_user_time;
   ```

3. **Write-time considerations:**
   - Drop indexes during bulk loads
   - Use unlogged tables for staging
   - Implement async indexing

4. **Alternative approaches:**
   - Partitioning to reduce index size
   - Summary tables for analytics
   - Application-level caching

**Trade-offs:**
- More indexes = better reads, slower writes
- Fewer indexes = faster writes, slower reads
- Find balance based on read/write ratio

### Q5: What are index-only scans and when are they beneficial?

**Answer:** Index-only scans read only from index, not table:

**How they work:**
```sql
-- Traditional index scan
CREATE INDEX idx_events_user_time ON events(user_id, timestamp);

EXPLAIN SELECT user_id, timestamp FROM events WHERE user_id = 1;
-- Index Scan using idx_events_user_time on events

-- Index-only scan
CREATE INDEX idx_events_user_time_covering ON events(user_id, timestamp)
INCLUDE (event_type);

EXPLAIN SELECT user_id, timestamp, event_type FROM events WHERE user_id = 1;
-- Index Only Scan using idx_events_user_time_covering on events
```

**Benefits:**
- Faster queries (no table access)
- Reduced I/O
- Better cache efficiency

**When to use:**
- Queries that select only indexed columns
- INCLUDE additional columns in index
- Covering indexes for common query patterns

**Limitations:**
- Index must contain all required columns
- PostgreSQL 9.2+ for INCLUDE syntax
- Larger indexes (trade-off storage for speed)

### Q6: How do you identify and remove unused indexes?

**Answer:** Systematic approach to index cleanup:

**Identify unused indexes:**
```sql
-- Check scan counts
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Monitor over time
SELECT pg_stat_reset(); -- Reset counters
-- Wait 1-2 weeks
-- Check again
```

**Safe removal process:**
1. **Mark as invalid (test):**
   ```sql
   UPDATE pg_index SET indisvalid = false WHERE indexrelid = 'index_name'::regclass;
   -- Test application for 24 hours
   -- Re-enable if issues
   UPDATE pg_index SET indisvalid = true WHERE indexrelid = 'index_name'::regclass;
   ```

2. **Drop safely:**
   ```sql
   DROP INDEX IF EXISTS index_name;
   ```

3. **Monitor impact:**
   - Watch for query performance degradation
   - Check pg_stat_statements for slow queries
   - Be prepared to recreate if needed

**Risk mitigation:**
- Drop during low-traffic periods
- Have rollback plan (recreate index)
- Start with smallest indexes
- Monitor application logs

---

## Cheat Sheet

### Index Creation Commands

```sql
-- Basic B-Tree index
CREATE INDEX idx_table_column ON table(column);

-- Composite index
CREATE INDEX idx_table_col1_col2 ON table(col1, col2);

-- Covering index (PostgreSQL 11+)
CREATE INDEX idx_table_col1_covering ON table(col1) INCLUDE (col2, col3);

-- Partial index
CREATE INDEX idx_table_partial ON table(column) WHERE condition;

-- Concurrent creation (production safe)
CREATE INDEX CONCURRENTLY idx_table_column ON table(column);

-- BRIN index for large ordered tables
CREATE INDEX idx_table_timestamp_brin ON table USING brin(timestamp);

-- GIN index for JSONB/text
CREATE INDEX idx_table_data_gin ON table USING gin(data);
```

### Performance Analysis

```sql
-- Query plan analysis
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT ...;

-- Index usage statistics
SELECT indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes WHERE tablename = 'events';

-- Index size
SELECT indexname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes WHERE tablename = 'events';

-- Query performance from pg_stat_statements
SELECT query, calls, total_time/calls as avg_time, rows/calls as avg_rows
FROM pg_stat_statements WHERE query LIKE '%events%';
```

### Index Maintenance

```sql
-- Update statistics
ANALYZE events;

-- Rebuild bloated index
REINDEX INDEX CONCURRENTLY idx_events_user_timestamp;

-- Check bloat
SELECT round(100 * (pg_relation_size(indexrelid) - pg_relation_size(indexrelid, 'main'))::numeric / pg_relation_size(indexrelid), 2) as bloat_pct
FROM pg_stat_user_indexes WHERE indexname = 'idx_name';

-- Drop unused index
DROP INDEX IF EXISTS unused_index_name;

-- Reset statistics
SELECT pg_stat_reset();
```

### Common Query Patterns & Indexes

```sql
-- Pattern: WHERE user_id = ? AND timestamp >= ?
CREATE INDEX idx_events_user_timestamp ON events(user_id, timestamp);

-- Pattern: WHERE event_type = ? AND timestamp BETWEEN ? AND ?
CREATE INDEX idx_events_type_timestamp ON events(event_type, timestamp);

-- Pattern: WHERE session_id = ? ORDER BY timestamp
CREATE INDEX idx_events_session_timestamp ON events(session_id, timestamp);

-- Pattern: WHERE timestamp >= ? GROUP BY event_type
CREATE INDEX idx_events_timestamp_type ON events(timestamp, event_type);

-- Pattern: JSONB containment
CREATE INDEX idx_events_data_gin ON events USING gin(event_data);
```

### Emergency Fixes

```sql
-- Kill long-running query
SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE ...;

-- Temporarily disable index (test only)
UPDATE pg_index SET indisvalid = false WHERE indexrelid = 'idx_name'::regclass;

-- Force sequential scan (emergency)
SET enable_indexscan = off;
SET enable_bitmapscan = off;

-- Reset to defaults
RESET enable_indexscan;
RESET enable_bitmapscan;
```

---

## Cross-Links

- **Index Basics**: [[SQL/02_Core/01_Indexes_Basics_and_BTree]]
- **Query Plans**: [[SQL/02_Core/04_Explain_Analyze_and_Query_Plans]]
- **Partitioning**: [[SQL/03_Advanced/02_Partitioning]]
- **VACUUM**: [[SQL/03_Advanced/01_VACUUM_Autovacuum_and_Bloat]]
- **Advanced Indexes**: [[SQL/03_Advanced/04_Advanced_Index_Types_GIN_GiST_BRIN]]

## References

- [PostgreSQL Index Documentation](https://www.postgresql.org/docs/current/indexes.html)
- [Index-Only Scans](https://www.postgresql.org/docs/current/indexes-index-only-scans.html)
- [Composite Indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html)
- [BRIN Indexes](https://www.postgresql.org/docs/current/brin.html)

---

**Status**: stable  
**Last Updated**: 2026-04-27  
**Lines**: 872