---
tags: [sql, postgresql, advanced, security, roles, rls, ssl, authentication]
aliases: ["PostgreSQL Security", "Database Security", "RLS", "Roles and Permissions", "pg_hba.conf"]
status: stable
updated: 2026-05-03
---

# Database Security

> [!summary] Goal
> Secure a PostgreSQL database: manage roles and permissions, encrypt connections, implement row-level security, and configure authentication to prevent unauthorized access.

## Table of Contents

1. [Why Database Security Matters](#why-database-security-matters)
2. [Roles and Users](#roles-and-users)
3. [Privileges: GRANT and REVOKE](#privileges-grant-and-revoke)
4. [Row-Level Security (RLS)](#row-level-security)
5. [Authentication Methods](#authentication-methods)
6. [SSL/TLS Connection Security](#ssl-tls-connection-security)
7. [Encryption at Rest](#encryption-at-rest)
8. [Audit Logging](#audit-logging)
9. [Security Hardening Checklist](#security-hardening-checklist)
10. [Pitfalls](#pitfalls)

---

## Why Database Security Matters

PostgreSQL's security model operates at multiple layers:

```mermaid
flowchart TD
    A[Client connection] --> B[pg_hba.conf authentication]
    B --> C[SSL/TLS encryption]
    C --> D[Role-based access control]
    D --> E[Database-level privileges]
    E --> F[Schema-level privileges]
    F --> G[Table-level privileges]
    G --> H[Row-Level Security]
    H --> I[Column-level privileges]
    I --> J[Data access]
```

Each layer must be configured correctly for the system to be secure.

---

## Roles and Users

In PostgreSQL, a **role** is a login name, a group, or both. A **user** is simply a role with `LOGIN` privilege.

### Creating roles

```sql
-- Login role (user)
CREATE ROLE app_user WITH LOGIN PASSWORD 'secure_password';

-- Group role (no login)
CREATE ROLE read_only;
CREATE ROLE read_write;

-- Role with expiration and connection limit
CREATE ROLE temporary_user WITH
    LOGIN PASSWORD 'temp_pass'
    VALID UNTIL '2026-12-31'
    CONNECTION LIMIT 5;
```

### Role hierarchy

```sql
-- Assign group membership
GRANT read_only TO app_user;
GRANT read_write TO admin_user;

-- Inheritance — member roles inherit privileges of parent
CREATE ROLE developers;
CREATE ROLE alice LOGIN INHERIT;
GRANT developers TO alice;
-- alice automatically has all privileges granted to developers
```

### Modifying roles

```sql
ALTER ROLE app_user WITH PASSWORD 'new_password';
ALTER ROLE app_user WITH NOLOGIN;        -- temporarily disable login
ALTER ROLE app_user WITH CONNECTION LIMIT 10;
ALTER ROLE app_user VALID UNTIL '2027-01-01';
DROP ROLE IF EXISTS temporary_user;
```

### Predefined roles

| Role | Privilege |
|------|-----------|
| `pg_read_all_data` | Read all data (PG 14+) |
| `pg_write_all_data` | Write all data (PG 14+) |
| `pg_read_all_stats` | Read system statistics |
| `pg_signal_backend` | Cancel/terminate other backends |

---

## Privileges: GRANT and REVOKE

### Database-level

```sql
GRANT CONNECT, CREATE ON DATABASE mydb TO app_user;
REVOKE CREATE ON DATABASE mydb FROM public;  -- prevent schema creation by default
```

### Schema-level

```sql
GRANT USAGE ON SCHEMA public TO read_only;
GRANT USAGE, CREATE ON SCHEMA public TO read_write;
```

### Table-level

```sql
GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO read_write;
GRANT SELECT (name, email) ON users TO support_team;  -- column-level
```

### Future tables (default privileges)

```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO read_only;

ALTER DEFAULT PRIVILEGES FOR ROLE table_owner
    GRANT INSERT ON TABLES TO read_write;
```

### Revoking public access

```sql
-- Remove default PUBLIC privileges
REVOKE ALL ON DATABASE mydb FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;

-- Then grant only what's needed to specific roles
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
```

---

## Row-Level Security (RLS)

RLS restricts which rows a user can see or modify, based on the current user or session context.

### Enabling RLS

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    total DECIMAL(10,2),
    status TEXT
);

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
```

### Policy types

```sql
-- Users can only see their own orders
CREATE POLICY user_orders ON orders
    FOR SELECT
    USING (customer_id = current_setting('app.current_user_id')::INTEGER);

-- Managers can see all orders with status 'shipped'
CREATE POLICY manager_orders ON orders
    FOR SELECT
    USING (current_role = 'manager');

-- Users can only modify their own pending orders
CREATE POLICY update_own_orders ON orders
    FOR UPDATE
    USING (customer_id = current_setting('app.current_user_id')::INTEGER)
    WITH CHECK (status = 'pending');
```

### RLS with application users

```sql
-- Set user context at session start
SELECT set_config('app.current_user_id', '42', false);

-- Or in a function
CREATE FUNCTION set_session_user_id(uid INTEGER)
RETURNS VOID
LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    PERFORM set_config('app.current_user_id', uid::TEXT, true);
END $$;
```

### Bypassing RLS

```sql
-- Table owner and superuser bypass RLS by default
-- Grant explicit bypass to specific roles:
ALTER TABLE orders FORCE ROW LEVEL SECURITY;
```

### Checking RLS policies

```sql
-- List policies on a table
SELECT * FROM pg_policies WHERE tablename = 'orders';

-- Show which rows are visible to current user
SELECT * FROM orders;  -- only rows allowed by active policies
```

---

## Authentication Methods

pg_hba.conf (PostgreSQL Host-Based Authentication) controls which authentication method is used for each connection type.

```
# TYPE  DATABASE  USER       ADDRESS        METHOD      OPTIONS
local   all       all                       peer
host    all       all        127.0.0.1/32   scram-sha-256
host    all       all        ::1/128        scram-sha-256
hostssl all       all        0.0.0.0/0      scram-sha-256  clientcert=1
```

### Common authentication methods

| Method | Security | Use case |
|--------|----------|----------|
| `trust` | None | Local dev only — never in production |
| `peer` | High | Local Unix socket, OS user matches DB user |
| `password` | Low | Plain text password (avoid) |
| `md5` | Medium | Legacy — avoid if possible |
| `scram-sha-256` | High | **Recommended** for password auth |
| `cert` | Very high | Client SSL certificate |
| `ldap` | High | Integration with corporate LDAP/AD |
| `gss` | Very high | Kerberos authentication |
| `pam` | High | Pluggable Authentication Modules |

### Best practice configuration

```
# Local connections (admin only)
local   all   all                    peer

# Local TCP (application)
host    all   app_user   127.0.0.1/32  scram-sha-256

# Remote connections — require SSL + SCRAM
hostssl all   app_user   10.0.0.0/8    scram-sha-256
hostssl all   readonly   10.0.0.0/8    scram-sha-256

# Replication (dedicated user, restricted network)
hostssl replication  replicator  10.0.0.0/8  scram-sha-256
```

---

## SSL/TLS Connection Security

### Server-side configuration

```conf
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'
ssl_min_protocol_version = 'TLSv1.3'
ssl_ciphers = 'HIGH:!aNULL:!eNULL:!MD5'
```

### Client connection with SSL

```bash
# Require SSL
psql "host=db.example.com dbname=mydb user=app_user sslmode=require"

# Verify server certificate
psql "host=db.example.com dbname=mydb user=app_user sslmode=verify-full sslrootcert=ca.pem"

# Client certificate
psql "host=db.example.com dbname=mydb user=app_user sslmode=verify-full sslcert=client.crt sslkey=client.key"
```

### SSL modes

| Mode | Encryption | Server cert verification | Protection |
|------|-----------|-------------------------|------------|
| `disable` | No | N/A | Eavesdropping |
| `allow` | Prefer non-SSL | No | Minimal |
| `prefer` (default) | Yes if available | No | Most connections |
| `require` | Yes | No | Eavesdropping |
| `verify-ca` | Yes | Yes (CA check) | Man-in-the-middle |
| `verify-full` | Yes | Yes (CA + hostname) | Man-in-the-middle + spoofing |

---

## Encryption at Rest

PostgreSQL does not natively support transparent data encryption (TDE). Options include:

```sql
-- pgcrypto extension for column-level encryption
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive data
INSERT INTO users (email, ssn)
VALUES (
    'alice@example.com',
    pgp_sym_encrypt('123-45-6789', 'encryption_key')
);

-- Decrypt
SELECT pgp_sym_decrypt(ssn, 'encryption_key') FROM users WHERE id = 1;
```

**Other options:**
- **Filesystem encryption**: LUKS, eCryptfs (transparent at OS level)
- **TDE solutions**: pg_tde extension (third party)
- **Full disk encryption**: dm-crypt, BitLocker (prevents physical theft)

---

## Audit Logging

### PostgreSQL audit log

```conf
# postgresql.conf
log_destination = 'csvlog'
logging_collector = on
log_statement = 'ddl'           # log all DDL
log_line_prefix = '%t %u %d '   # timestamp, user, database
log_connections = on
log_disconnections = on
log_checkpoints = on
log_lock_waits = on
log_min_duration_statement = 1000  # log queries > 1 second
```

### pgaudit extension

```sql
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- Log all DDL
ALTER SYSTEM SET pgaudit.log = 'write,ddl';
-- Log all reads on sensitive tables
SELECT pgaudit.audit_table('users');
SELECT pgaudit.audit_table('orders');
```

---

## Security Hardening Checklist

- [ ] Remove default `public` schema privileges: `REVOKE CREATE ON SCHEMA public FROM PUBLIC`
- [ ] Use `scram-sha-256` for all password-based authentication
- [ ] Enable `ssl = on` in production; set `ssl_min_protocol_version = 'TLSv1.3'`
- [ ] Use `sslmode=verify-full` in client applications
- [ ] Create separate roles for read-only, read-write, and admin access
- [ ] Apply `ALTER DEFAULT PRIVILEGES` so new tables inherit correct permissions
- [ ] Enable RLS on tables with multi-tenant or user-scoped data
- [ ] Set `password_encryption = 'scram-sha-256'`
- [ ] Rotate passwords regularly; use `VALID UNTIL` for temporary access
- [ ] Configure `log_statement = 'ddl'` and `log_min_duration_statement` for monitoring
- [ ] Restrict network access: bind to specific IPs, not `0.0.0.0`
- [ ] Encrypt sensitive columns with `pgcrypto` if needed
- [ ] Run `SELECT * FROM pg_hba_file_rules()` to verify auth configuration

---

## Pitfalls

### Overly permissive PUBLIC privileges

```sql
-- By default, PUBLIC can CREATE in the public schema
-- This allows any user to create objects
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
```

**Fix**: Revoke CREATE from PUBLIC in production databases.

### RLS not applied to table owner

Table owners bypass RLS by default. Use `ALTER TABLE ... FORCE ROW LEVEL SECURITY` to enforce RLS on owners too.

### SSL without verification

```bash
# sslmode=require encrypts traffic but does not verify server identity
# Man-in-the-middle is still possible
psql "sslmode=require host=db.example.com"
```

**Fix**: Use `sslmode=verify-full` with proper CA certificates.

### Password in connection string

```bash
# BAD — password visible in process list, logs
psql postgresql://user:password@host/db

# GOOD — use .pgpass or environment variable
psql postgresql://user@host/db  # prompts for password
```

**Fix**: Use `.pgpass` file (mode 0600) or `PGPASSWORD` environment variable (still not ideal — prefer .pgpass).

### Granting more than needed

```sql
-- BAD: gives UPDATE and DELETE to a read-only role
GRANT ALL ON orders TO read_only;

-- GOOD: explicit minimal privileges
GRANT SELECT ON orders TO read_only;
```

---

> [!question]- Interview Questions
>
> **Q: What is the difference between a role and a user in PostgreSQL?**
> A: A role can be a user (with LOGIN), a group (without LOGIN), or both. Every user is a role with LOGIN privilege.
>
> **Q: How does Row-Level Security work?**
> A: RLS adds a policy to a table that filters rows based on the current user or session context. The policy's USING clause determines which rows are visible, and WITH CHECK determines which rows can be inserted/updated.
>
> **Q: What authentication methods should you use in production?**
> A: `scram-sha-256` for password-based, `cert` for certificate-based, or `ldap`/`gss` for enterprise single sign-on. Never use `trust` in production. Prefer `hostssl` lines over `host` to require encryption.
>
> **Q: What is the purpose of `pg_hba.conf`?**
> A: It controls which hosts, databases, users, and authentication methods are allowed to connect to the PostgreSQL server. Rules are evaluated in order — the first matching rule applies.
>
> **Q: What are default privileges and why are they important?**
> A: Default privileges (`ALTER DEFAULT PRIVILEGES`) define the permissions that new objects (tables, functions) will have when created. Without them, every newly created table requires a manual GRANT.

---

## Cross-Links

- [[SQL/01_Foundations/04_Schema_Design_Basics]] for schema-level privilege planning
- [[SQL/01_Foundations/01_psql_Basics_and_Workflow]] for SSL connection examples
- [[SQL/03_Advanced/03_Replication_and_Backups]] for replication user security
- [[SQL/05_Projects/01_Build_a_Mini_DB_Lab_With_psql]] for hands-on role and privilege setup
- [[SQL/04_Playbooks/03_Incident_Playbook_Connection_Exhaustion]] for connection management

---

## References

- [PostgreSQL Security Documentation](https://www.postgresql.org/docs/current/security.html)
- [PostgreSQL Roles](https://www.postgresql.org/docs/current/user-manag.html)
- [PostgreSQL Row-Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [PostgreSQL SSL/TLS](https://www.postgresql.org/docs/current/ssl-tcp.html)
- [pg_hba.conf Documentation](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)
- [pgaudit Extension](https://www.postgresql.org/docs/current/pgaudit.html)
