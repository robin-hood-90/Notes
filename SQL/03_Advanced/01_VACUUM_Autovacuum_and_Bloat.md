---
tags: [sql, postgresql, maintenance, advanced]
aliases: ["VACUUM", "Autovacuum"]
status: stable
updated: 2026-04-26
---

# VACUUM, Autovacuum, and Bloat

> [!summary] Model
> MVCC creates dead tuples that must be cleaned up. VACUUM reclaims space for reuse, updates visibility maps for index-only scans, and prevents transaction ID wraparound. Autovacuum daemon runs automatically but needs monitoring and tuning for optimal performance.

## Table of Contents

1. [[#MVCC and Dead Tuples]]
2. [[#VACUUM Process]]
3. [[#Autovacuum Daemon]]
4. [[#Table Bloat]]
5. [[#Monitoring Vacuum Activity]]
6. [[#Manual Vacuum Operations]]
7. [[#Configuration Tuning]]
8. [[#Common Issues and Solutions]]
9. [[#Best Practices]]
10. [[#Interview Questions]]

---

## MVCC and Dead Tuples

### Multi-Version Concurrency Control (MVCC)

PostgreSQL uses MVCC to allow concurrent reads without blocking writes:

```sql
-- When you UPDATE a row:
UPDATE users SET name = 'New Name' WHERE id = 1;

-- PostgreSQL doesn't overwrite the row
-- Instead, it marks the old row as "dead" and creates a new version
```

**Key Points:**
- Each row has `xmin` (transaction that created it) and `xmax` (transaction that deleted it)
- Readers see the appropriate version based on their transaction's snapshot
- Old versions become "dead tuples" when no transaction can see them anymore

### Dead Tuple Creation

Dead tuples are created by:
- **UPDATE operations**: Old row version becomes dead, new version created
- **DELETE operations**: Row marked as deleted (xmax set)
- **ROLLBACK**: Aborted transaction's inserted rows become dead

```sql
-- Example: Update creates dead tuple
BEGIN;
INSERT INTO users (name) VALUES ('Alice');  -- xmin = 100
COMMIT;

BEGIN;
UPDATE users SET name = 'Bob' WHERE name = 'Alice';  -- xmax = 100 for old, xmin = 101 for new
COMMIT;

-- Now we have 1 live tuple (xmin=101) and 1 dead tuple (xmax=100)
```

### Why Dead Tuples Matter

- **Space waste**: Dead tuples consume disk space
- **Performance impact**: Table scans read dead tuples (slow)
- **Index bloat**: Dead entries remain in indexes
- **Transaction ID wraparound**: Can cause database shutdown if not addressed

---

## VACUUM Process

### What VACUUM Does

VACUUM performs three main functions:

1. **Reclaim space**: Mark dead tuples as free for reuse
2. **Update visibility map**: Track which pages are visible to all transactions
3. **Prevent wraparound**: Keep transaction IDs from wrapping around

```sql
-- Basic VACUUM syntax
VACUUM table_name;

-- VACUUM with analysis (updates statistics)
VACUUM ANALYZE table_name;

-- VACUUM specific columns
VACUUM (ANALYZE) table_name (column1, column2);
```

### VACUUM FULL vs Regular VACUUM

| Feature | VACUUM | VACUUM FULL |
|---------|--------|-------------|
| **Blocking** | No (concurrent operations allowed) | Yes (exclusive lock) |
| **Space reclamation** | Marks space as reusable | Physically removes dead tuples |
| **Table rewrite** | No | Yes (rebuilds entire table) |
| **Performance impact** | Low | High |
| **When to use** | Regular maintenance | Emergency bloat reduction |

### Visibility Map

The visibility map tracks which table pages contain only tuples visible to all transactions:

```sql
-- Check visibility map
SELECT * FROM pg_visibility_map('table_name');

-- Pages with all-visible tuples can use index-only scans
-- Without vacuum, index-only scans are disabled
```

### VACUUM Phases

1. **Heap scan**: Identify dead tuples and update statistics
2. **Index vacuum**: Remove dead entries from indexes
3. **Heap vacuum**: Mark dead tuples as free space
4. **Visibility map update**: Mark all-visible pages

---

## Autovacuum Daemon

### How Autovacuum Works

Autovacuum runs automatically in the background:

```sql
-- Check if autovacuum is running
SELECT name, setting FROM pg_settings WHERE name LIKE 'autovacuum%';

-- Monitor autovacuum activity
SELECT schemaname, tablename, 
       last_vacuum, last_autovacuum,
       vacuum_count, autovacuum_count
FROM pg_stat_user_tables;
```

### Autovacuum Triggers

Autovacuum runs when:

1. **Threshold exceeded**: `autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor * n_tuples`
2. **Time-based**: `autovacuum_naptime` (default 20 seconds)
3. **Manual trigger**: Via configuration changes

```sql
-- Default thresholds
autovacuum_vacuum_threshold = 50        -- Base threshold
autovacuum_vacuum_scale_factor = 0.02   -- 2% of table size

-- For a table with 1000 rows:
-- Vacuum triggers at: 50 + 0.02 * 1000 = 70 dead tuples
```

### Autovacuum Variants

- **autovacuum**: Regular vacuum + analyze
- **autoanalyze**: Statistics update only
- **autovacuum (to prevent wraparound)**: Aggressive vacuum when nearing wraparound

### Autovacuum Configuration

Key settings to tune:

```sql
-- In postgresql.conf
autovacuum = on                           -- Enable autovacuum
autovacuum_max_workers = 3               -- Max concurrent workers
autovacuum_naptime = 20                  -- Seconds between checks
autovacuum_vacuum_threshold = 50         -- Dead tuple threshold
autovacuum_vacuum_scale_factor = 0.02    -- Scale factor
autovacuum_analyze_threshold = 50        -- Analyze threshold
autovacuum_analyze_scale_factor = 0.01   -- Analyze scale factor

-- Per-table overrides
ALTER TABLE table_name SET (
    autovacuum_vacuum_threshold = 100,
    autovacuum_vacuum_scale_factor = 0.05
);
```

---

## Table Bloat

### What is Table Bloat?

Table bloat occurs when dead tuples accumulate faster than VACUUM can clean them:

```sql
-- Check for bloat
SELECT schemaname, tablename,
       n_dead_tup, n_live_tup,
       ROUND(n_dead_tup::numeric / (n_live_tup + n_dead_tup) * 100, 2) as bloat_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 0
ORDER BY bloat_ratio DESC;
```

### Measuring Bloat

Several ways to measure table bloat:

1. **pg_stat_user_tables**: `n_dead_tup` / (`n_live_tup` + `n_dead_tup`)
2. **pgstattuple extension**: Detailed page-level analysis
3. **pg_bloat_check**: Automated bloat detection

```sql
-- Using pgstattuple (needs extension)
CREATE EXTENSION pgstattuple;

SELECT * FROM pgstattuple('table_name');
-- Shows: table_len, tuple_count, dead_tuple_count, free_space, etc.

-- Bloat calculation
SELECT 
    schemaname, tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    dead_tuple_percent
FROM (
    SELECT schemaname, tablename, 
           n_dead_tup::float / (n_live_tup + n_dead_tup) * 100 as dead_tuple_percent
    FROM pg_stat_user_tables
) t
WHERE dead_tuple_percent > 10;
```

### Index Bloat

Indexes can also bloat:

```sql
-- Check index bloat
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;

-- REINDEX to rebuild bloated indexes
REINDEX INDEX CONCURRENTLY index_name;
```

### Causes of Excessive Bloat

1. **High update frequency**: OLTP workloads
2. **Long-running transactions**: Prevent vacuum from cleaning
3. **Autovacuum disabled**: Manual vacuum only
4. **Poor autovacuum tuning**: Thresholds too high
5. **HOT updates blocked**: Can't update in place

---

## Monitoring Vacuum Activity

### System Catalogs

```sql
-- Current vacuum activity
SELECT pid, datname, usename, state, query
FROM pg_stat_activity
WHERE query LIKE '%VACUUM%';

-- Vacuum statistics
SELECT schemaname, tablename,
       last_vacuum, last_autovacuum,
       vacuum_count, autovacuum_count,
       n_tup_ins, n_tup_upd, n_tup_del,
       n_live_tup, n_dead_tup
FROM pg_stat_user_tables;

-- Autovacuum worker status
SELECT * FROM pg_stat_progress_vacuum;
```

### pg_stat_statements

Monitor vacuum performance:

```sql
-- Enable extension
CREATE EXTENSION pg_stat_statements;

-- Check vacuum query performance
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements
WHERE query LIKE '%VACUUM%'
ORDER BY total_time DESC;
```

### Custom Monitoring

```sql
-- Bloat monitoring query
CREATE OR REPLACE VIEW bloat_monitor AS
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    CASE WHEN n_live_tup + n_dead_tup > 0
         THEN ROUND(n_dead_tup::numeric / (n_live_tup + n_dead_tup) * 100, 2)
         ELSE 0
    END as bloat_ratio,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_stat_user_tables
WHERE n_dead_tup > 0;

-- Alert when bloat > 20%
SELECT * FROM bloat_monitor WHERE bloat_ratio > 20;
```

### Log Analysis

PostgreSQL logs vacuum activity:

```
LOG: automatic vacuum of table "public.users": index scans: 1
      pages: 0 removed, 1000 remain, 0 skipped by pointer
      tuples: 1500 removed, 1000 remain, 0 are dead but not yet removable
      buffer usage: 2000 hits, 500 misses, 1000 dirtied
      avg read rate: 4.000 MB/s, avg write rate: 2.000 MB/s
      system usage: CPU 0.01s/0.02u sec elapsed 0.03 sec
```

---

## Manual Vacuum Operations

### Standard VACUUM

```sql
-- Basic vacuum
VACUUM users;

-- Vacuum and analyze
VACUUM ANALYZE users;

-- Vacuum specific columns for analyze
VACUUM (ANALYZE) users (name, email);

-- Verbose output
VACUUM VERBOSE users;
```

### VACUUM FULL

Use only when necessary (blocking operation):

```sql
-- Full vacuum (rebuilds table)
VACUUM FULL users;

-- Alternative: CLUSTER (also blocking)
CLUSTER users;
```

### Targeted Vacuum

```sql
-- Vacuum only if needed
VACUUM (DISABLE_PAGE_SKIPPING) users;  -- Process all pages

-- Freeze tuples (prevent wraparound)
VACUUM (FREEZE) users;

-- Index cleanup
VACUUM (INDEX_CLEANUP ON) users;
VACUUM (INDEX_CLEANUP OFF) users;  -- Skip index cleanup for speed
```

### Concurrent Operations

```sql
-- Don't block concurrent operations
VACUUM (PARALLEL 2) users;  -- Use 2 workers

-- Skip pages with exclusive locks
VACUUM (SKIP_LOCKED) users;
```

---

## Configuration Tuning

### Autovacuum Tuning

```sql
-- postgresql.conf recommendations for high-traffic databases

# Increase workers
autovacuum_max_workers = 6

# More aggressive thresholds
autovacuum_vacuum_threshold = 25
autovacuum_vacuum_scale_factor = 0.01  # 1% instead of 2%

# Analyze more frequently
autovacuum_analyze_threshold = 25
autovacuum_analyze_scale_factor = 0.005  # 0.5%

# Cost-based throttling
autovacuum_vacuum_cost_delay = 10  # milliseconds
autovacuum_vacuum_cost_limit = 1000

# Prevent long-running vacuums
autovacuum_vacuum_timeout = 300000  # 5 minutes
```

### Per-Table Tuning

```sql
-- For high-update tables
ALTER TABLE high_update_table SET (
    autovacuum_vacuum_threshold = 100,
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_analyze_threshold = 50,
    autovacuum_analyze_scale_factor = 0.005
);

-- For large tables
ALTER TABLE large_table SET (
    autovacuum_vacuum_cost_delay = 5,
    autovacuum_vacuum_cost_limit = 2000
);

-- Disable autovacuum for specific tables
ALTER TABLE manual_only_table SET (
    autovacuum_enabled = false
);
```

### Cost-Based Vacuum Delays

Control vacuum I/O impact:

```sql
-- Vacuum cost parameters
vacuum_cost_page_hit = 1      -- Page found in buffer
vacuum_cost_page_miss = 10    -- Page not in buffer
vacuum_cost_page_dirty = 20   -- Page dirtied by vacuum

-- Delay when cost exceeds limit
autovacuum_vacuum_cost_delay = 20     -- ms delay
autovacuum_vacuum_cost_limit = 200    -- cost limit
```

---

## Common Issues and Solutions

### Autovacuum Not Running

**Symptoms:** High bloat, performance degradation

**Causes:**
- `autovacuum = off`
- High `autovacuum_vacuum_cost_delay`
- Long-running transactions blocking vacuum

**Solutions:**
```sql
-- Check configuration
SHOW autovacuum;

-- Enable autovacuum
ALTER SYSTEM SET autovacuum = on;

-- Reduce cost delay
ALTER SYSTEM SET autovacuum_vacuum_cost_delay = 10;

-- Kill blocking transactions
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '1 hour';
```

### Transaction ID Wraparound

**Symptoms:** Database shutdown, "transaction ID wraparound" errors

**Prevention:**
```sql
-- Check wraparound status
SELECT datname, age(datfrozenxid) as age
FROM pg_database
ORDER BY age DESC;

-- Manual freeze
VACUUM (FREEZE) table_name;

-- Force autovacuum freeze
ALTER TABLE table_name SET (
    autovacuum_freeze_min_age = 0,
    autovacuum_freeze_max_age = 100000000
);
```

### Long-Running Vacuum

**Symptoms:** Vacuum takes hours, blocks other operations

**Solutions:**
```sql
-- Run vacuum with less aggressive settings
VACUUM (INDEX_CLEANUP OFF, PARALLEL 4) large_table;

-- Use pg_repack for online rebuild (extension)
-- pg_repack rebuilds table without exclusive lock

-- Schedule during maintenance window
VACUUM FULL large_table;  -- Only during maintenance
```

### Index Bloat

**Symptoms:** Indexes much larger than expected

**Solutions:**
```sql
-- Concurrent reindex
REINDEX INDEX CONCURRENTLY index_name;

-- Rebuild all indexes on table
REINDEX TABLE CONCURRENTLY table_name;

-- Recreate index (allows customization)
CREATE INDEX CONCURRENTLY new_index_name ON table_name (column);
DROP INDEX old_index_name;
ALTER INDEX new_index_name RENAME TO old_index_name;
```

---

## Best Practices

### 1. Monitor Autovacuum Regularly

```sql
-- Daily monitoring query
SELECT schemaname, tablename,
       n_dead_tup,
       ROUND(n_dead_tup::numeric / GREATEST(n_live_tup + n_dead_tup, 1) * 100, 2) as bloat_pct,
       last_autovacuum,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000 OR ROUND(n_dead_tup::numeric / GREATEST(n_live_tup + n_dead_tup, 1) * 100, 2) > 10
ORDER BY n_dead_tup DESC;
```

### 2. Tune Autovacuum for Your Workload

**High-update OLTP:**
```sql
autovacuum_vacuum_threshold = 100
autovacuum_vacuum_scale_factor = 0.01
autovacuum_max_workers = 6
```

**Data warehouse:**
```sql
autovacuum_vacuum_threshold = 1000
autovacuum_vacuum_scale_factor = 0.05
autovacuum_max_workers = 2
```

### 3. Schedule Manual Vacuum for Large Tables

```sql
-- Cron job for weekly vacuum
0 2 * * 1 vacuumdb -d mydb -t large_table --analyze
```

### 4. Use VACUUM FREEZE Proactively

```sql
-- Prevent wraparound issues
VACUUM (FREEZE) table_name;
```

### 5. Monitor Long-Running Transactions

```sql
-- Find transactions that block vacuum
SELECT pid, datname, usename, state, 
       now() - state_change as duration,
       query
FROM pg_stat_activity
WHERE state IN ('idle in transaction', 'active')
  AND now() - state_change > interval '30 minutes'
ORDER BY duration DESC;
```

### 6. Use Extensions for Better Monitoring

```sql
-- pg_buffercache: Buffer cache analysis
CREATE EXTENSION pg_buffercache;

-- pg_stat_statements: Query performance
CREATE EXTENSION pg_stat_statements;

-- pgstattuple: Detailed tuple analysis
CREATE EXTENSION pgstattuple;
```

### 7. Plan for Maintenance Windows

```sql
-- Check current maintenance settings
SHOW maintenance_work_mem;

-- Increase for vacuum operations
SET maintenance_work_mem = '256MB';

-- Then run vacuum
VACUUM ANALYZE large_table;
```

### 8. Test Vacuum Impact

```sql
-- Before vacuum
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM table WHERE condition;

-- Run vacuum
VACUUM ANALYZE table;

-- After vacuum
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM table WHERE condition;
```

---

## Interview Questions

### Q1: What is table bloat and how does VACUUM help?

**Answer:** Table bloat occurs when PostgreSQL's MVCC creates dead tuples that accumulate faster than they can be cleaned up. VACUUM addresses this by:

1. **Reclaiming space**: Marking dead tuples as free for reuse by future INSERTs
2. **Updating visibility maps**: Tracking which pages contain only tuples visible to all transactions, enabling index-only scans
3. **Preventing wraparound**: Ensuring transaction IDs don't wrap around and cause database shutdown

Without VACUUM, tables grow indefinitely with dead data, slowing queries and wasting disk space.

### Q2: How does autovacuum decide when to run?

**Answer:** Autovacuum triggers based on configurable thresholds:

```
vacuum_threshold = autovacuum_vacuum_threshold + 
                  autovacuum_vacuum_scale_factor * live_tuples
```

For a table with 1000 live tuples:
- Default: 50 + 0.02 × 1000 = 70 dead tuples
- When dead tuples exceed this threshold, autovacuum runs

It also runs periodically based on `autovacuum_naptime` (default 20 seconds) to check all tables.

### Q3: What's the difference between VACUUM and VACUUM FULL?

**Answer:**

| VACUUM | VACUUM FULL |
|--------|-------------|
| Non-blocking (allows concurrent operations) | Blocking (exclusive table lock) |
| Marks dead space as reusable | Physically removes dead tuples |
| Fast, low overhead | Slow, high I/O |
| Doesn't shrink table size | Rewrites table, recovers space |
| Safe for production | Use only in maintenance windows |

**Use VACUUM** for regular maintenance, **VACUUM FULL** only for emergency bloat reduction.

### Q4: How do you monitor vacuum effectiveness?

**Answer:** Multiple approaches:

```sql
-- Check dead/live tuple ratios
SELECT schemaname, tablename,
       n_dead_tup, n_live_tup,
       ROUND(n_dead_tup::numeric / (n_live_tup + n_dead_tup) * 100, 2) as bloat_pct
FROM pg_stat_user_tables;

-- Monitor autovacuum activity
SELECT last_autovacuum, autovacuum_count
FROM pg_stat_user_tables;

-- Check vacuum progress
SELECT * FROM pg_stat_progress_vacuum;

-- Analyze logs for vacuum performance
-- Look for "automatic vacuum" messages
```

### Q5: What causes transaction ID wraparound and how to prevent it?

**Answer:** PostgreSQL uses 32-bit transaction IDs that eventually wrap around. Each table tracks the oldest transaction ID that could still see its tuples.

**Wraparound occurs when:** Transaction ID counter reaches ~2 billion from the oldest frozen XID.

**Prevention:**
- Autovacuum automatically freezes old tuples
- Manual `VACUUM (FREEZE)` forces freezing
- Monitor with `SELECT age(datfrozenxid) FROM pg_database;`

**Symptoms:** Database shuts down with "transaction ID wraparound" error, requiring manual recovery.

### Q6: How do you tune autovacuum for high-traffic databases?

**Answer:** Key tunings:

```sql
-- More aggressive thresholds
autovacuum_vacuum_threshold = 100  -- Lower threshold
autovacuum_vacuum_scale_factor = 0.01  -- 1% instead of 2%

-- More workers
autovacuum_max_workers = 6  -- Increase from default 3

-- Cost-based throttling
autovacuum_vacuum_cost_delay = 10  -- Allow more I/O
autovacuum_vacuum_cost_limit = 1000  -- Higher limit

-- Per-table overrides for critical tables
ALTER TABLE hot_table SET (
    autovacuum_vacuum_threshold = 50,
    autovacuum_vacuum_scale_factor = 0.005
);
```

### Q7: What are visibility maps and why are they important?

**Answer:** Visibility maps track which table pages contain only tuples visible to all current and future transactions.

**Benefits:**
- Enable **index-only scans**: Index provides all needed data, no heap access needed
- **Faster vacuum**: Vacuum can skip all-visible pages
- **Better performance**: Reduces I/O for certain query patterns

**How it works:**
- After VACUUM, all-visible pages are marked in the visibility map
- Planner can choose index-only scan when all columns are in index
- Without visibility map updates, index-only scans are disabled

### Q8: How do you handle vacuum in high-availability setups?

**Answer:** Special considerations for replication:

```sql
-- On primary: Normal vacuum
VACUUM ANALYZE table;

-- On standby: Read-only, vacuum not needed
-- But hot standby can run autovacuum

-- Replication slots prevent vacuum from removing needed WAL
-- Monitor replication lag
SELECT slot_name, pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)
FROM pg_replication_slots;

-- If lag is high, vacuum might be blocked
-- Consider temporary slot removal or catch-up
```

**Best practices:**
- Ensure standbys can keep up with primary vacuum activity
- Monitor replication slots for bloat prevention
- Use logical replication for selective table replication

---

## Summary

**Key Takeaways:**

1. **MVCC creates dead tuples** - UPDATE and DELETE operations leave old versions
2. **VACUUM reclaims space** - Marks dead tuples as reusable, updates visibility maps
3. **Autovacuum runs automatically** - But needs monitoring and tuning
4. **Table bloat hurts performance** - Dead tuples slow scans, waste space
5. **Monitor regularly** - Check pg_stat_user_tables for dead tuple counts
6. **Tune thresholds** - Lower for high-update tables, higher for large tables
7. **Use VACUUM FULL sparingly** - Blocking operation, use only when necessary
8. **Prevent wraparound** - Monitor transaction ID age, use FREEZE when needed

**Vacuum Hierarchy:**
```
Daily: Monitor bloat ratios
Weekly: Check autovacuum effectiveness  
Monthly: Manual vacuum large tables
Emergency: VACUUM FULL during maintenance
```

---

## Cross-Links

- **Indexes**: [[SQL/02_Core/01_Indexes_Basics_and_BTree]]
- **Transactions**: [[SQL/02_Core/02_Transactions_and_Locking]]
- **EXPLAIN**: [[SQL/02_Core/04_Explain_Analyze_and_Query_Plans]]
- **Partitioning**: [[SQL/03_Advanced/02_Partitioning]]
- **Replication**: [[SQL/03_Advanced/03_Replication_and_Backups]]

## References

- [PostgreSQL VACUUM Documentation](https://www.postgresql.org/docs/current/routine-vacuuming.html)
- [Autovacuum Tuning](https://www.postgresql.org/docs/current/runtime-config-autovacuum.html)
- [Visibility Maps](https://www.postgresql.org/docs/current/storage-vm.html)
- [Monitoring Stats](https://www.postgresql.org/docs/current/monitoring-stats.html)
- [Bloat Detection Scripts](https://github.com/pgexperts/pgx_scripts)

---

**Status**: stable  
**Last Updated**: 2026-04-26  
**Lines**: 856