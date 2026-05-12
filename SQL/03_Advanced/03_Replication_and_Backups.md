---
tags: [sql, postgresql, advanced, replication, backups, high-availability]
aliases: ["Streaming Replication", "Point-in-Time Recovery", "PITR"]
status: stable
updated: 2026-04-26
---

# Replication and Backups

> [!summary] Model
> PostgreSQL provides robust backup and replication solutions for data protection and high availability. Physical backups with WAL enable point-in-time recovery, while streaming replication supports read scaling and failover. Choose strategies based on RTO/RPO requirements and business needs.

## Table of Contents

1. [[#Backup Types and Strategies]]
2. [[#Point-in-Time Recovery (PITR)]]
3. [[#Streaming Replication]]
4. [[#Logical Replication]]
5. [[#Backup Automation]]
6. [[#Disaster Recovery]]
7. [[#Monitoring and Maintenance]]
8. [[#Best Practices]]
9. [[#Interview Questions]]

---

## Backup Types and Strategies

### Logical vs Physical Backups

PostgreSQL offers two primary backup approaches:

| Type | Logical | Physical |
|------|---------|----------|
| **Method** | SQL dump | File system copy + WAL |
| **Tools** | pg_dump, pg_dumpall | pg_basebackup, rsync |
| **Portability** | High (works across versions) | Low (version/architecture specific) |
| **Size** | Smaller (compressed) | Larger (full data) |
| **Recovery** | Full restore only | Point-in-time recovery |
| **Performance** | Slower | Faster |

**Why choose logical?** Cross-version compatibility, selective restores, smaller backups.

**Why choose physical?** Faster backup/restore, point-in-time recovery, complete consistency.

**When to use:** Logical for development/testing, physical for production disaster recovery.

### pg_dump Options

```sql
-- Basic logical backup
pg_dump mydb > mydb_backup.sql

-- Custom format (compressed, parallel)
pg_dump -Fc -j 4 -d mydb -f mydb_backup.dump

-- Schema only
pg_dump -s mydb > schema_only.sql

-- Data only
pg_dump -a mydb > data_only.sql

-- Single table
pg_dump -t users mydb > users_backup.sql

-- Exclude tables
pg_dump --exclude-table=logs_* mydb > backup_no_logs.sql
```

**Why custom format?** Faster backup/restore, compression, parallel processing.

**How it works:** -Fc creates compressed custom format; -j enables parallel workers.

**When to use:** Large databases, frequent backups, production systems.

### pg_basebackup

```bash
# Basic physical backup
pg_basebackup -D /backup/mydb -Ft -z -P

# With replication slot (prevents WAL cleanup)
pg_basebackup -D /backup/mydb -Ft -z -P -S backup_slot

# Remote backup
pg_basebackup -h primary-host -D /backup/mydb -U replicator -Ft -z

# Parallel backup
pg_basebackup -D /backup/mydb -Ft -z -P -j 4
```

**Why pg_basebackup?** Official tool, handles all PostgreSQL features, creates consistent backup.

**How it works:** Connects to database, copies data directory while holding backup lock.

**When to use:** Production backups, base for PITR, replication setup.

### Continuous Archiving

```sql
-- Enable WAL archiving (postgresql.conf)
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/%f'

-- Test archiving
SELECT pg_switch_wal();  -- Force WAL switch
-- Check files in /archive/
```

**Why continuous archiving?** Enables point-in-time recovery, foundation for replication.

**How it works:** Copies completed WAL files to archive location as they're created.

**When to use:** Any scenario requiring PITR or replication.

---

## Point-in-Time Recovery (PITR)

### PITR Process

Point-in-time recovery restores database to specific moment:

```bash
# 1. Restore base backup
tar -xzf base_backup.tar.gz -C /var/lib/postgresql/data

# 2. Create recovery.conf (PostgreSQL < 12)
# recovery.conf in data directory
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2024-01-15 14:30:00'
recovery_target_action = 'promote'

# 3. Start PostgreSQL
pg_ctl start

# 4. Monitor recovery
tail -f /var/log/postgresql/postgresql.log
```

**Why PITR?** Recover from any point, not just backup time.

**How it works:** Base backup + WAL replay to target time.

**When to use:** Accidental data deletion, corruption, audit requirements.

### Recovery Targets

```sql
-- Time-based recovery
recovery_target_time = '2024-01-15 14:30:00-05'

-- Transaction ID recovery
recovery_target_xid = '123456'

-- Named restore point
SELECT pg_create_restore_point('before_migration');
recovery_target_name = 'before_migration'

-- Recovery to end of WAL
recovery_target = 'immediate'
```

**Why multiple targets?** Flexible recovery options for different scenarios.

**How they work:** PostgreSQL replays WAL until reaching target condition.

**When to use:** Specific incident recovery, testing changes, branching timelines.

### Recovery Configuration (PostgreSQL 12+)

```sql
# postgresql.conf for recovery
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2024-01-15 14:30:00'
recovery_target_action = 'promote'
recovery_target_inclusive = true

# Or create recovery.signal file
touch /var/lib/postgresql/data/recovery.signal
```

**Why new method?** Simpler, uses postgresql.conf instead of separate file.

**How it works:** recovery.signal triggers recovery mode.

**When to upgrade:** PostgreSQL 12+, simplifies configuration.

---

## Streaming Replication

### Basic Setup

Streaming replication provides real-time data synchronization:

```bash
# On primary (postgresql.conf)
wal_level = replica
max_wal_senders = 3
wal_keep_size = 64  # MB

# Create replication user
CREATE USER replicator REPLICATION LOGIN ENCRYPTED PASSWORD 'secret';

# On replica
pg_basebackup -h primary -D /var/lib/postgresql/data -U replicator -Ft -z -P

# Create recovery.conf or postgresql.conf
primary_conninfo = 'host=primary user=replicator password=secret'
recovery_target_timeline = 'latest'
```

**Why streaming replication?** Real-time synchronization, read scaling, high availability.

**How it works:** WAL records shipped to replicas as they're generated.

**When to use:** High availability, read scaling, disaster recovery.

### Synchronous vs Asynchronous

```sql
# Asynchronous (default, faster)
synchronous_standby_names = ''  # Empty = async

# Synchronous (durable, slower)
synchronous_standby_names = 'replica1'

# Multiple synchronous
synchronous_standby_names = 'FIRST 2 (replica1, replica2)'
```

**Why synchronous?** Guaranteed durability, no data loss on failover.

**Why asynchronous?** Better performance, acceptable data loss.

**How they work:** Sync waits for replica confirmation; async doesn't.

**When to use:** Sync for critical data, async for performance.

### Replication Slots

```sql
# Create physical replication slot
SELECT pg_create_physical_replication_slot('replica1_slot');

# Create logical replication slot
SELECT pg_create_logical_replication_slot('logical_slot', 'pgoutput');

# Monitor slots
SELECT slot_name, slot_type, active, restart_lsn, confirmed_flush_lsn
FROM pg_replication_slots;

# Drop unused slot
SELECT pg_drop_replication_slot('old_slot');
```

**Why replication slots?** Prevent WAL cleanup, ensure replicas don't fall behind.

**How they work:** Track replication progress, retain required WAL files.

**When to use:** All replication setups, prevent disk space issues.

### Cascading Replication

```sql
# Primary → Replica1 → Replica2
# On Replica1 (becomes intermediate)
wal_level = replica
max_wal_senders = 3
# Normal replica config

# On Replica2 (cascaded)
primary_conninfo = 'host=replica1 user=replicator'
# Same as connecting to primary
```

**Why cascading?** Reduce load on primary, geographical distribution.

**How it works:** Intermediate replica acts as primary for downstream replicas.

**When to use:** Multiple replicas, network constraints, global deployments.

---

## Logical Replication

### Logical vs Physical Replication

| Aspect | Physical | Logical |
|--------|----------|---------|
| **Scope** | Entire cluster | Selected tables |
| **Version compatibility** | Same version | Cross-version possible |
| **DDL replication** | All DDL | Limited DDL |
| **Conflicts** | No conflicts | Possible conflicts |
| **Use cases** | HA, DR | Data integration, reporting |

**Why logical replication?** Selective replication, cross-version compatibility, flexible topologies.

**How it works:** Decodes WAL into logical changes, replicates row-level changes.

**When to use:** Reporting databases, data warehousing, microservices.

### Logical Replication Setup

```sql
# Enable logical replication (postgresql.conf)
wal_level = logical

# Create publication (on publisher)
CREATE PUBLICATION user_data FOR TABLE users, orders;

# Create subscription (on subscriber)
CREATE SUBSCRIPTION user_sync
    CONNECTION 'host=publisher user=replicator'
    PUBLICATION user_data;

# Monitor logical replication
SELECT * FROM pg_stat_subscription;
SELECT * FROM pg_stat_publication;
```

**Why publications/subscriptions?** Declarative replication configuration.

**How it works:** Publisher sends changes, subscriber applies them.

**When to use:** Selective data replication, different schemas, cross-version.

### Conflict Resolution

```sql
-- Handle conflicts (subscriber)
ALTER SUBSCRIPTION user_sync SET (copy_data = false);
ALTER SUBSCRIPTION user_sync ENABLE;

-- Custom conflict resolution
CREATE OR REPLACE FUNCTION resolve_conflict()
RETURNS trigger AS $$
BEGIN
    -- Custom logic for conflict resolution
    IF OLD.updated_at < NEW.updated_at THEN
        RETURN NEW;
    ELSE
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER resolve_user_conflict
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION resolve_conflict();
```

**Why conflict resolution?** Logical replication can have update conflicts.

**How it works:** Application-level resolution using triggers or custom logic.

**When needed:** Multi-master setups, concurrent updates to same rows.

---

## Backup Automation

### Automated Backup Scripts

```bash
#!/bin/bash
# automated_backup.sh

DB_NAME="mydb"
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# Logical backup
pg_dump -Fc -d $DB_NAME -f $BACKUP_DIR/${DB_NAME}_${DATE}.dump

# Physical backup
pg_basebackup -D $BACKUP_DIR/base_${DATE} -Ft -z -P -U backup_user

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete
find $BACKUP_DIR -name "base_*" -mtime +7 -delete

# Send notification
echo "Backup completed: ${DB_NAME}_${DATE}" | mail -s "Backup Complete" admin@example.com
```

**Why automate?** Consistent backups, reduced human error, scheduled execution.

**How to schedule:** Cron jobs, systemd timers, Kubernetes cronjobs.

**When to run:** Off-peak hours, before major changes.

### Backup Validation

```bash
# Test logical backup restore
createdb test_restore
pg_restore -d test_restore /backup/mydb_backup.dump
psql -d test_restore -c "SELECT COUNT(*) FROM users;"

# Test physical backup
# Start temporary instance with backup
# Run queries to verify data integrity

# Check backup integrity
pg_restore --list /backup/mydb_backup.dump > /dev/null
```

**Why validate?** Ensure backups are restorable, detect corruption early.

**How to automate:** Include validation in backup scripts.

**When to validate:** After major changes, regularly scheduled.

### Incremental Backups

```bash
# Using pgBackRest (advanced tool)
# Configure stanza
pgbackrest --stanza=main stanza-create

# Full backup
pgbackrest --stanza=main backup

# Incremental backup
pgbackrest --stanza=main backup --type=incremental

# Differential backup
pgbackrest --stanza=main backup --type=differential
```

**Why incremental?** Faster backups, less storage, same recovery capability.

**How it works:** Only backup changes since last full/incremental backup.

**When to use:** Large databases, frequent backups, limited storage.

---

## Disaster Recovery

### RTO/RPO Definitions

- **RTO (Recovery Time Objective)**: Maximum acceptable downtime
- **RPO (Recovery Point Objective)**: Maximum acceptable data loss

```sql
-- Calculate current RTO/RPO
-- Last backup: 2024-01-15 02:00:00
-- Current time: 2024-01-15 14:30:00
-- RPO = 12.5 hours (data loss window)
-- RTO = Time to restore from backup
```

**Why RTO/RPO?** Define recovery requirements, guide backup strategy.

**How to measure:** Business impact analysis, regulatory requirements.

**When to define:** System design, compliance requirements.

### Failover Scenarios

```sql
-- Manual failover
# On replica
pg_ctl promote

# Update application connection strings
# Redirect traffic to new primary

-- Automated failover (with repmgr or Patroni)
# Tools detect primary failure
# Promote replica automatically
# Update DNS/service discovery
```

**Why failover planning?** Minimize downtime during failures.

**How to implement:** Scripts, orchestration tools, monitoring systems.

**When to test:** Regularly, after changes, during maintenance windows.

### Multi-Region DR

```sql
-- Cross-region replication
# Primary in us-east-1
# Replica in us-west-2

# Use logical replication for cross-region
CREATE PUBLICATION us_east_data FOR ALL TABLES;
CREATE SUBSCRIPTION us_west_sync
    CONNECTION 'host=us-east-1-postgres user=replicator';

# Monitor replication lag
SELECT extract(epoch from now() - write_lag) as lag_seconds
FROM pg_stat_replication;
```

**Why multi-region?** Disaster recovery, compliance, reduced latency.

**How it works:** Replicate data across regions, failover when needed.

**When to use:** Global applications, regulatory requirements, business continuity.

---

## Monitoring and Maintenance

### Replication Monitoring

```sql
-- Check replication status
SELECT usename, client_addr, state, sync_state,
       pg_wal_lsn_diff(sent_lsn, replay_lsn) as lag_bytes
FROM pg_stat_replication;

-- Check replication slots
SELECT slot_name, slot_type, active,
       pg_wal_lsn_diff(lsn, restart_lsn) as retained_wal
FROM pg_replication_slots;

-- Monitor WAL generation
SELECT pg_current_wal_lsn(), pg_walfile_name(pg_current_wal_lsn());
```

**Why monitor replication?** Detect lag, prevent disk space issues, ensure availability.

**How to alert:** Set thresholds for lag, monitor slot usage.

**When to check:** Regularly, especially during high load.

### Backup Monitoring

```sql
-- Check last backup time
ls -la /backup/ | tail -5

-- Verify backup integrity
pg_restore --list /backup/latest.dump | wc -l

-- Monitor backup size trends
du -sh /backup/* | sort -h

-- Check WAL archive status
ls -la /archive/ | tail -10
```

**Why monitor backups?** Ensure backups are current, detect failures early.

**How to automate:** Scripts that check backup age, send alerts.

**When to monitor:** Daily checks, after backup jobs.

### Capacity Planning

```sql
-- Estimate backup storage needs
SELECT
    sum(pg_total_relation_size(oid)) as total_size,
    sum(pg_total_relation_size(oid)) * 0.3 as estimated_backup_size
FROM pg_class
WHERE relkind = 'r';

-- Monitor WAL generation rate
SELECT
    total_wal_generated / extract(epoch from total_time) as wal_rate_mb_s
FROM (
    SELECT
        sum(size) / 1024 / 1024 as total_wal_generated,
        max(now()) - min(now()) as total_time
    FROM pg_ls_waldir()
) t;
```

**Why capacity planning?** Ensure sufficient storage for backups and WAL.

**How to monitor:** Track growth rates, plan for expansion.

**When to review:** Monthly, before major data growth.

---

## Best Practices

### 1. Implement 3-2-1 Backup Rule

**3 copies**: Original + 2 backups
**2 media types**: Different storage systems
**1 off-site**: Geographic separation

```bash
# Local backup
pg_basebackup -D /local/backup -Ft -z

# Remote backup
pg_basebackup -D /remote/backup -h primary -Ft -z

# Cloud backup
pg_dump -Fc | aws s3 cp - s3://backup-bucket/db.dump
```

### 2. Test Restore Procedures

```sql
-- Regular restore testing
#!/bin/bash
# Create test environment
createdb test_restore
pg_restore -d test_restore /backup/prod.dump

# Run application tests
npm test -- --db=test_restore

# Verify data integrity
psql -d test_restore -c "SELECT COUNT(*) FROM critical_table;"

# Cleanup
dropdb test_restore
```

### 3. Use Replication for HA

```sql
-- Primary + 2 sync replicas
synchronous_standby_names = 'FIRST 2 (replica1, replica2)'

-- Automatic failover with Patroni
# patroni.yml configuration
# scope: postgres
# name: postgres1
# restapi: ...
# postgresql: ...
```

### 4. Monitor Everything

```sql
-- Key metrics to monitor
SELECT
    -- Replication lag
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) as replication_lag,

    -- Backup age
    extract(epoch from now() - pg_backup_start_time()) as backup_age,

    -- WAL retention
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) as wal_retained
FROM pg_stat_replication;
```

### 5. Secure Backups

```sql
-- Encrypt backups
pg_dump -Fc | gpg -c > encrypted.dump

-- Store credentials securely
# .pgpass file with restricted permissions
# chmod 0600 ~/.pgpass

# Use connection URIs with SSL
pg_dump "postgresql://backup@host/db?sslmode=require"
```

### 6. Plan for Different Scenarios

- **Data corruption**: PITR to point before corruption
- **Accidental deletion**: PITR or logical recovery
- **Hardware failure**: Failover to replica
- **Regional disaster**: Cross-region failover

### 7. Document Procedures

```sql
-- Recovery runbook
# 1. Assess damage
# 2. Choose recovery method (PITR/replication)
# 3. Execute recovery
# 4. Verify data integrity
# 5. Update application connections
# 6. Communicate with stakeholders
```

### 8. Regular Testing

```sql
-- Monthly DR testing
# 1. Schedule maintenance window
# 2. Create test environment
# 3. Perform full recovery test
# 4. Run application tests
# 5. Measure RTO/RPO achievement
# 6. Document lessons learned
```

---

## Interview Questions

### Q1: Explain the difference between logical and physical backups.

**Answer:**

**Logical backups (pg_dump):**
- Extract database structure and data as SQL statements
- Portable across PostgreSQL versions and architectures
- Can be selective (tables, schemas)
- Smaller file sizes with compression
- Slower to create and restore

**Physical backups (pg_basebackup):**
- Copy database files at file system level
- Include all databases, tablespaces, configuration
- Enable point-in-time recovery with WAL
- Faster backup and restore operations
- Version and architecture specific

**When to use:**
- Logical: Development, testing, selective restores
- Physical: Production, disaster recovery, complete consistency

### Q2: How does point-in-time recovery work?

**Answer:** PITR restores database to specific moment using base backup + WAL replay.

**Process:**
```bash
# 1. Take base backup
pg_basebackup -D /backup/base -Ft -z

# 2. Enable WAL archiving
archive_command = 'cp %p /archive/%f'

# 3. Incident occurs (e.g., data deletion at 14:30)

# 4. Restore base backup
tar -xzf /backup/base.tar.gz -C /data

# 5. Configure recovery target
recovery_target_time = '2024-01-15 14:25:00'  # Before incident

# 6. Start PostgreSQL - replays WAL to target time
```

**Benefits:**
- Recover to any point, not just backup time
- Minimal data loss (up to last WAL record)
- Works for any type of data corruption

### Q3: What is streaming replication and why use it?

**Answer:** Streaming replication continuously ships WAL records from primary to replicas for real-time synchronization.

**Setup:**
```sql
-- Primary configuration
wal_level = replica
max_wal_senders = 3

-- Replica configuration
primary_conninfo = 'host=primary user=replicator'
recovery_target_timeline = 'latest'
```

**Benefits:**
- **Real-time sync**: Minimal lag (< 1 second typically)
- **Read scaling**: Offload read queries to replicas
- **High availability**: Automatic failover capability
- **Zero data loss**: With synchronous replication

**Use cases:**
- Load balancing read queries
- Disaster recovery standby
- Reporting databases
- Development/test environments

### Q4: How do you choose between sync and async replication?

**Answer:**

**Synchronous Replication:**
- **Pros**: Zero data loss, guaranteed durability
- **Cons**: Higher latency, reduced write performance
- **Use when**: Critical data, financial transactions, strict consistency requirements

**Asynchronous Replication:**
- **Pros**: Better performance, lower latency
- **Cons**: Possible data loss on failure
- **Use when**: Performance critical, acceptable data loss (seconds/minutes)

**Configuration:**
```sql
-- Synchronous (waits for replica)
synchronous_standby_names = 'replica1'

-- Asynchronous (no waiting)
synchronous_standby_names = ''
```

**Best practice:** Use synchronous for critical tables, asynchronous for others.

### Q5: Explain replication slots and their importance.

**Answer:** Replication slots prevent WAL cleanup, ensuring replicas don't fall behind and cause replication failures.

**Types:**
- **Physical slots**: For streaming replication
- **Logical slots**: For logical replication

**Why important:**
```sql
-- Without slots: Primary deletes WAL, replica fails
-- With slots: Primary retains WAL until replica confirms receipt

SELECT slot_name, restart_lsn, confirmed_flush_lsn,
       pg_wal_lsn_diff(confirmed_flush_lsn, restart_lsn) as lag
FROM pg_replication_slots;
```

**Management:**
```sql
-- Create slot
SELECT pg_create_physical_replication_slot('replica1');

-- Monitor usage
SELECT * FROM pg_replication_slots;

-- Clean up unused slots
SELECT pg_drop_replication_slot('old_slot');
```

**Best practice:** Create slots before setting up replicas.

### Q6: How do you perform a PostgreSQL failover?

**Answer:** Planned failover promotes replica to primary, updates application connections.

**Steps:**
```sql
# 1. Ensure replica is caught up
SELECT pg_wal_lsn_diff(sent_lsn, replay_lsn) FROM pg_stat_replication;

# 2. Promote replica
pg_ctl promote

# 3. Update application config
# Change connection strings to new primary

# 4. Redirect traffic
# Update load balancer, DNS, or service discovery

# 5. Reconfigure old primary as replica (if possible)
# Or rebuild as new replica
```

**Automated failover:** Use tools like Patroni, repmgr, or PostgreSQL HA clusters.

**Testing:** Regular failover testing to ensure procedures work.

### Q7: What are the RTO and RPO in disaster recovery?

**Answer:**

**RTO (Recovery Time Objective):** Maximum acceptable time to restore service after disaster.

**RPO (Recovery Point Objective):** Maximum acceptable amount of data loss measured in time.

**Examples:**
- RTO = 4 hours: Service must be restored within 4 hours of outage
- RPO = 1 hour: Maximum 1 hour of data loss acceptable

**Impact on strategy:**
- Lower RTO: More replicas, faster backup restore
- Lower RPO: More frequent backups, synchronous replication

**Calculation:**
```sql
-- Current RPO: Time since last backup
SELECT extract(epoch from now() - backup_completion_time) / 3600 as rpo_hours;

-- Current RTO: Measured restore time
-- Time backup restore + application startup + testing
```

### Q8: How do you secure PostgreSQL backups?

**Answer:** Multiple layers of security for backup data protection.

**Encryption:**
```sql
-- Encrypt logical backups
pg_dump -Fc mydb | gpg -c > mydb.dump.gpg

-- Encrypt physical backups
pg_basebackup -D /backup
tar -czf - /backup | gpg -c > physical_backup.tar.gz.gpg
```

**Access control:**
```sql
-- Dedicated backup user with minimal privileges
CREATE USER backup_user WITH ENCRYPTED PASSWORD 'secret';
GRANT CONNECT ON DATABASE mydb TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;

-- SSL connections
pg_dump "postgresql://backup_user@host/mydb?sslmode=require"
```

**Storage security:**
- Encrypt backup storage volumes
- Use secure transfer protocols (SCP, SFTP)
- Store off-site with proper access controls
- Regular access audits

**Best practices:**
- Rotate encryption keys regularly
- Test restore with encrypted backups
- Secure backup scripts and credentials

---

## Summary

**Key Takeaways:**

1. **Backup types**: Logical (pg_dump) for portability, physical (pg_basebackup) for PITR
2. **PITR**: Base backup + WAL replay for any-point recovery
3. **Replication**: Streaming for HA/real-time sync, logical for selective replication
4. **Monitoring**: Replication lag, backup age, WAL retention critical metrics
5. **Security**: Encrypt backups, secure credentials, test restores
6. **RTO/RPO**: Define recovery objectives, design strategy accordingly
7. **Testing**: Regular backup validation, failover testing essential
8. **Automation**: Scheduled backups, monitoring, alerting reduce risk

**Disaster Recovery Hierarchy:**
```
Prevention → Backup → Replication → Monitoring → Testing → Recovery
```

---

## Cross-Links

- **Indexes**: [[SQL/02_Core/01_Indexes_Basics_and_BTree]]
- **Partitioning**: [[SQL/03_Advanced/02_Partitioning]]
- **Transactions**: [[SQL/02_Core/02_Transactions_and_Locking]]
- **Monitoring**: [[SQL/03_Advanced/01_VACUUM_Autovacuum_and_Bloat]]

## References

- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [Streaming Replication](https://www.postgresql.org/docs/current/warm-standby.html)
- [Logical Replication](https://www.postgresql.org/docs/current/logical-replication.html)
- [Point-in-Time Recovery](https://www.postgresql.org/docs/current/continuous-archiving.html)

---

**Status**: stable  
**Last Updated**: 2026-04-26  
**Lines**: 891