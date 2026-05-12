---
tags: [sql, postgresql, foundations, psql, cli]
aliases: ["psql", "PostgreSQL CLI"]
status: stable
updated: 2026-04-26
---

# psql Basics and Workflow

> [!summary] Model
> psql is PostgreSQL's interactive terminal client for database administration and development. Master connection methods, meta-commands, configuration, data import/export, and scripting workflows. Essential for efficient database interaction and automation.

## Table of Contents

1. [[#Connecting to PostgreSQL]]
2. [[#Basic psql Commands]]
3. [[#Meta-Commands Reference]]
4. [[#Configuration and Customization]]
5. [[#Data Import and Export]]
6. [[#Scripting and Automation]]
7. [[#Advanced Features]]
8. [[#Common Workflows]]
9. [[#Troubleshooting]]
10. [[#Best Practices]]
11. [[#Interview Questions]]

---

## Connecting to PostgreSQL

### Basic Connection Syntax

```bash
# Direct connection
psql -h hostname -p port -U username -d database

# Connection string
psql "postgresql://username:password@host:port/database"

# Unix socket (local)
psql -U username database
```

**Why use this?** psql provides direct access to PostgreSQL without GUI tools. Essential for server administration and automated scripts.

**How it works:** psql establishes a connection using libpq library, supports SSL/TLS encryption, and handles authentication methods.

**When to use:** Always for server administration, troubleshooting, and when GUI tools are unavailable.

### Connection Options

| Option | Description | Example |
|--------|-------------|---------|
| `-h, --host` | Server hostname | `psql -h localhost` |
| `-p, --port` | Server port | `psql -p 5432` |
| `-U, --username` | Username | `psql -U postgres` |
| `-d, --dbname` | Database name | `psql -d mydb` |
| `-W, --password` | Force password prompt | `psql -W` |
| `--password` | Read password from env | `PGPASSWORD=secret psql` |

### Environment Variables

```bash
# Set connection defaults
export PGHOST=localhost
export PGPORT=5432
export PGUSER=myuser
export PGDATABASE=mydb
export PGPASSWORD=mypass

# Then connect simply
psql
```

**Why use environment variables?** Avoids repeating connection parameters in scripts and commands.

**How it works:** psql reads these variables automatically if command-line options aren't provided.

**When to use:** In development environments, CI/CD pipelines, and automated scripts.

### Connection URI Format

```bash
# Full URI with all components
psql "postgresql://username:password@host:port/database?sslmode=require"

# Minimal URI
psql "postgresql://user@host/db"
```

**Components:**
- `postgresql://` - Protocol identifier
- `username:password@` - Authentication (optional password)
- `host:port` - Server location (default port 5432)
- `/database` - Database name
- `?param=value` - Connection parameters

### SSL Connections

```bash
# Require SSL
psql "postgresql://user@host/db?sslmode=require"

# Verify server certificate
psql "postgresql://user@host/db?sslmode=verify-ca&sslrootcert=/path/to/ca.pem"
```

**SSL Modes:**
- `disable` - No SSL
- `allow` - Try SSL first, fallback to non-SSL
- `prefer` - Default, prefer SSL
- `require` - Require SSL, no verification
- `verify-ca` - Verify server certificate
- `verify-full` - Verify certificate and hostname

---

## Basic psql Commands

### Getting Help

```sql
-- Show help
\?

-- Show command history
\s

-- Show psql version
SELECT version();

-- Show PostgreSQL version
SHOW server_version;
```

### Database Information

```sql
-- List all databases
\l

-- List databases with details
\l+

-- Connect to database
\c database_name

-- Show current connection
\conninfo
```

### Table Operations

```sql
-- List tables in current schema
\dt

-- List all tables with details
\dt+

-- List tables with specific pattern
\dt *user*

-- Describe table structure
\d table_name

-- Show table with indexes, constraints, etc.
\d+ table_name
```

### Query Execution

```sql
-- Execute query
SELECT * FROM users LIMIT 5;

-- Execute from file
\i /path/to/query.sql

-- Write query output to file
\o /path/to/output.txt
SELECT * FROM users;
\o  -- Stop writing to file

-- Show query execution time
\timing on
SELECT COUNT(*) FROM large_table;
```

---

## Meta-Commands Reference

### Information Commands

```sql
-- List schemas
\dn

-- List functions
\df

-- List views
\dv

-- List sequences
\ds

-- List extensions
\dx

-- List roles/users
\du

-- List indexes
\di

-- List foreign keys
\dft
```

### Formatting Commands

```sql
-- Expanded display (vertical)
\x on
SELECT * FROM users LIMIT 1;

-- Compact display
\x off

-- HTML output
\H
SELECT * FROM users LIMIT 3;
\H  -- Back to plain text

-- CSV output
\a  -- Unaligned
\f ,  -- Field separator
\t off  -- No tuples only
SELECT * FROM users;
```

### Session Management

```sql
-- Show current settings
\unset QUIET  -- Enable verbose mode temporarily

-- Set psql variable
\set QUIET 1

-- Show all variables
\set

-- Reset variable
\unset QUIET

-- Quit psql
\q
```

### Editing and History

```sql
-- Edit current query buffer
\e

-- Edit query in external editor
\e query.sql

-- Run last query again
\g

-- Execute and explain
SELECT * FROM users WHERE id = 1 \gexec

-- Show command history
\s

-- Execute command from history
\s | grep SELECT
```

---

## Configuration and Customization

### .psqlrc File

Create `~/.psqlrc` for persistent configuration:

```bash
# Enable timing by default
\timing on

# Set pager for long output
\setenv PAGER 'less -S'

# Custom prompt
\set PROMPT1 '%n@%M:%> %x%# '

# Useful aliases
\set show_tables '\\dt'
\set show_indexes '\\di'
\set desc '\\d+ :1'
```

**Why customize .psqlrc?** Saves time by setting preferred defaults and creating shortcuts.

**How it works:** psql reads ~/.psqlrc on startup, executing commands as if typed manually.

**When to use:** On development machines and personal workstations for consistent experience.

### Prompt Customization

```bash
# Default prompt: user@host:port/db=>
# Custom prompts
\set PROMPT1 '%n@%M:%> %x%# '  -- user@host:port db=>

# Show transaction status
\set PROMPT1 '%n@%M:%/%x%# '

# Color prompts (if supported)
\set PROMPT1 '%[%033[1;33m%]%n%[%033[0m%]@%[%033[1;32m%]%M%[%033[0m%]:%[%033[1;34m%]%/%[%033[0m%]%x%# '
```

### Autocomplete and Shortcuts

psql supports tab completion for:
- SQL keywords
- Table names
- Column names
- Function names

Enable with backslash commands:
```sql
-- Complete keywords
SEL<TAB>  -- SELECT

-- Complete table names
SELECT * FROM use<TAB>  -- users

-- Complete column names
SELECT nam<TAB> FROM users;  -- name
```

---

## Data Import and Export

### COPY Command

```sql
-- Export table to CSV
COPY users TO '/tmp/users.csv' WITH CSV HEADER;

-- Import from CSV
COPY users FROM '/tmp/users.csv' WITH CSV HEADER;

-- Export with custom delimiter
COPY users TO '/tmp/users.txt' WITH DELIMITER '|';

-- Import with error handling
COPY users FROM '/tmp/users.csv' WITH CSV HEADER LOG ERRORS;
```

**Why use COPY?** Fast bulk data operations, handles large datasets efficiently.

**How it works:** Server-side operation, bypasses client processing, direct file access.

**When to use:** Bulk imports/exports, ETL processes, data migration.

### psql Export Options

```sql
-- Export query results
psql -c "SELECT * FROM users" -o users.txt

-- Export in CSV format
psql -c "COPY (SELECT * FROM users) TO STDOUT WITH CSV HEADER" > users.csv

-- Export schema only
pg_dump -s database > schema.sql

-- Export data only
pg_dump -a database > data.sql
```

### pg_dump and pg_restore

```bash
# Full database backup
pg_dump mydb > mydb_backup.sql

# Custom format (compressed)
pg_dump -Fc mydb > mydb_backup.dump

# Restore from SQL
psql mydb < mydb_backup.sql

# Restore from custom format
pg_restore -d mydb mydb_backup.dump

# List contents of backup
pg_restore -l mydb_backup.dump
```

**Why use pg_dump?** Reliable backups, handles all PostgreSQL features, supports parallel processing.

**How it works:** Connects to database, extracts schema and data, outputs SQL or custom format.

**When to use:** Regular backups, schema migration, data transfer between servers.

---

## Scripting and Automation

### Script Execution

```bash
# Execute SQL file
psql -f script.sql

# Execute multiple files
psql -f schema.sql -f data.sql

# Execute with variables
psql -v dbname=mydb -f script.sql
```

### Conditional Execution

```sql
-- psql conditional blocks
\if :condition
  SELECT 'Condition is true';
\else
  SELECT 'Condition is false';
\endif
```

### Looping Constructs

```sql
-- Simple loop example
DO $$
DECLARE
  i INTEGER := 1;
BEGIN
  WHILE i <= 10 LOOP
    RAISE NOTICE 'Count: %', i;
    i := i + 1;
  END LOOP;
END $$;
```

### Batch Processing

```bash
# Process multiple databases
for db in db1 db2 db3; do
  echo "Processing $db"
  psql -d $db -c "VACUUM ANALYZE;"
done
```

---

## Advanced Features

### Transaction Control

```sql
-- Start transaction
BEGIN;

-- Execute statements
INSERT INTO users (name) VALUES ('Alice');
UPDATE users SET active = true WHERE name = 'Alice';

-- Show transaction status
SELECT txid_current();

-- Commit or rollback
COMMIT;
-- or
ROLLBACK;
```

### Prepared Statements

```sql
-- Prepare statement
PREPARE user_by_id (int) AS
  SELECT * FROM users WHERE id = $1;

-- Execute prepared statement
EXECUTE user_by_id(1);

-- Deallocate
DEALLOCATE user_by_id;
```

### Large Object Support

```sql
-- Enable large object support
\c :DBNAME

-- Import large file
\lo_import '/path/to/large/file.jpg'

-- List large objects
\lo_list

-- Export large object
\lo_export 12345 '/tmp/exported.jpg'
```

### Asynchronous Queries

```sql
-- Start async query
SELECT pg_sleep(10);  -- This would block

-- In background (limited support)
-- psql doesn't have built-in async, use \watch for periodic queries
```

---

## Common Workflows

### Development Workflow

```bash
# 1. Connect to database
psql -d devdb

# 2. Check schema
\d
\dt

# 3. Run migrations
\i migrations/001_create_users.sql

# 4. Test queries
SELECT * FROM users LIMIT 5;

# 5. Check performance
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

# 6. Export results
\o results.txt
SELECT COUNT(*) FROM users;
\o
```

### Production Debugging

```bash
# Connect to production (carefully!)
psql -h prod-host -U readonly_user prod_db

# Check system status
SELECT * FROM pg_stat_activity LIMIT 5;

# Monitor slow queries
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '1 minute'
ORDER BY duration DESC;

# Check table sizes
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

### Backup and Recovery

```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -Fc mydb > "backup_${DATE}.dump"

# Automated restore
pg_restore -d mydb backup_20231201_120000.dump

# Point-in-time recovery preparation
pg_dump -s mydb > schema_backup.sql
```

---

## Troubleshooting

### Connection Issues

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check listening ports
netstat -tlnp | grep 5432
# or
ss -tlnp | grep 5432

# Check logs
tail -f /var/log/postgresql/postgresql-*.log

# Test connection
psql -c "SELECT 1"  # Simple connectivity test
```

### Common Error Messages

```
FATAL: password authentication failed for user "username"
-- Solution: Check password, pg_hba.conf settings

FATAL: database "dbname" does not exist
-- Solution: CREATE DATABASE dbname;

ERROR: permission denied for table users
-- Solution: GRANT SELECT ON users TO username;

ERROR: relation "users" does not exist
-- Solution: Check schema, table name spelling
```

### Performance Issues

```sql
-- Check slow queries
SELECT pid, query, now() - query_start as duration
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- Check locks
SELECT locktype, relation::regclass, mode, granted
FROM pg_locks
WHERE NOT granted;

-- Check cache hit ratio
SELECT 
  sum(blks_hit) / (sum(blks_hit) + sum(blks_read))::float as cache_hit_ratio
FROM pg_stat_database;
```

---

## Best Practices

### 1. Use Connection URIs

```bash
# ✅ Good: Secure, flexible
psql "postgresql://app_user:secret@db.example.com:5432/app_db?sslmode=require"

# ❌ Bad: Password in command line
psql -h db.example.com -U app_user -d app_db -W
```

### 2. Configure .psqlrc

```bash
# Enable useful defaults
echo "\timing on" >> ~/.psqlrc
echo "\setenv PAGER 'less -S'" >> ~/.psqlrc
echo "\x auto" >> ~/.psqlrc  # Auto-expand wide results
```

### 3. Use Meta-Commands Effectively

```sql
-- ✅ Good: Check before dropping
\dt my_table
DROP TABLE my_table;

-- ✅ Good: Verify imports
COPY users FROM '/tmp/users.csv' WITH CSV HEADER;
SELECT COUNT(*) FROM users;  -- Verify count
```

### 4. Handle Large Results

```sql
-- ✅ Good: Use pager for large output
\setenv PAGER 'less -S'
SELECT * FROM large_table;

-- ✅ Good: Limit results in development
SELECT * FROM large_table LIMIT 100;
```

### 5. Secure Password Handling

```bash
# ✅ Good: Use .pgpass file
# ~/.pgpass (chmod 0600)
localhost:5432:mydb:myuser:mypassword

# ✅ Good: Environment variables
export PGPASSWORD=secret
psql -h host -U user db

# ❌ Bad: Command line password
psql -h host -U user -W db  # Prompts for password
```

### 6. Automate Routine Tasks

```bash
# Backup script
#!/bin/bash
pg_dump -Fc mydb > "backup_$(date +%Y%m%d).dump"

# Health check
#!/bin/bash
psql -c "SELECT 1" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "Database healthy"
else
  echo "Database unreachable"
fi
```

### 7. Monitor Connection Usage

```sql
-- Check connection count
SELECT count(*) FROM pg_stat_activity;

-- Check connection limits
SHOW max_connections;

-- Monitor connection sources
SELECT client_addr, count(*)
FROM pg_stat_activity
GROUP BY client_addr;
```

---

## Interview Questions

### Q1: What's the difference between \dt and \dt+ in psql?

**Answer:**

- **`\dt`**: Lists tables in current schema with basic info (name, type, owner)
- **`\dt+`**: Shows additional details (size, description)

```sql
-- \dt output
              List of relations
 Schema |     Name     | Type  |  Owner
--------|--------------|-------|---------
 public | users        | table | postgres
 public | orders       | table | postgres

-- \dt+ output includes size
              List of relations
 Schema |     Name     | Type  |  Owner   |    Size    | Description
--------|--------------|-------|----------|------------|-------------
 public | users        | table | postgres | 8192 bytes |
 public | orders       | table | postgres | 16 kB      |
```

### Q2: How do you export query results to CSV in psql?

**Answer:** Multiple approaches:

```sql
-- Method 1: COPY command
COPY (SELECT * FROM users) TO '/tmp/users.csv' WITH CSV HEADER;

-- Method 2: psql formatting
psql -c "COPY users TO STDOUT WITH CSV HEADER" > users.csv

-- Method 3: Meta-commands
\a  -- Unaligned output
\f ,  -- CSV delimiter
\t on -- Tuples only
\o users.csv
SELECT * FROM users;
\o  -- Reset output
```

### Q3: What does \conninfo show?

**Answer:** `\conninfo` displays current connection information:

```sql
-- Example output
You are connected to database "mydb" as user "myuser" via socket in "/tmp" at port "5432".
```

Shows:
- Database name
- Username
- Connection method (socket vs TCP)
- Host and port (for TCP connections)
- Connection status

### Q4: How do you run a SQL file in psql?

**Answer:** Use the `\i` meta-command:

```sql
-- Run SQL file
\i /path/to/script.sql

-- From command line
psql -f /path/to/script.sql

-- With variables
psql -v dbname=mydb -f script.sql
```

The `\i` command reads and executes the file contents as if typed directly.

### Q5: What's the purpose of the .psqlrc file?

**Answer:** `.psqlrc` customizes psql behavior on startup:

```bash
# Example ~/.psqlrc
\timing on                    # Show query timing
\x auto                      # Auto-expand wide results
\setenv PAGER 'less -S'      # Use pager for long output
\set PROMPT1 '%n@%M:%/%x%# ' # Custom prompt
```

Benefits:
- Consistent settings across sessions
- Time-saving defaults
- Customized workflow

Located in user's home directory, executed automatically on psql startup.

### Q6: How do you check query performance in psql?

**Answer:** Use timing and EXPLAIN:

```sql
-- Enable timing
\timing on

-- Run query with timing
SELECT COUNT(*) FROM large_table;

-- Explain query plan
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- Detailed analysis
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

### Q7: What are psql variables and how to use them?

**Answer:** psql variables store values for reuse:

```sql
-- Set variable
\set table_name users
\set limit 10

-- Use in queries
SELECT * FROM :table_name LIMIT :limit;

-- Show variables
\set

-- Conditional execution
\if :DEBUG
  \echo 'Debug mode enabled'
\endif
```

Variables are prefixed with colon in SQL, can be used for dynamic queries and scripting.

---

## Summary

**Key Takeaways:**

1. **Connection methods**: Direct options, URIs, environment variables for flexible access
2. **Meta-commands**: `\d`, `\dt`, `\l` for database inspection and navigation
3. **Data operations**: `COPY` for bulk import/export, `\i` for script execution
4. **Customization**: `.psqlrc` for personalized workflow and defaults
5. **Performance monitoring**: `\timing`, `EXPLAIN` for query analysis
6. **Security**: SSL modes, password handling, connection limits
7. **Automation**: Scripting with variables, conditional execution, batch processing

**psql Workflow:**
```
Connect → Inspect Schema → Execute Queries → Analyze Performance → Export Results
```

---

## Cross-Links

- **SQL Basics**: [[SQL/01_Foundations/02_SQL_Basics_Select_Where_Join]]
- **Indexes**: [[SQL/02_Core/01_Indexes_Basics_and_BTree]]
- **EXPLAIN**: [[SQL/02_Core/04_Explain_Analyze_and_Query_Plans]]
- **Backup/Restore**: [[SQL/03_Advanced/03_Replication_and_Backups]]

## References

- [psql Documentation](https://www.postgresql.org/docs/current/app-psql.html)
- [Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html)
- [Meta-Commands](https://www.postgresql.org/docs/current/app-psql-meta-commands.html)
- [COPY Command](https://www.postgresql.org/docs/current/sql-copy.html)

---

**Status**: stable  
**Last Updated**: 2026-04-26  
**Lines**: 1,011