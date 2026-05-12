---
tags: [sql, postgresql, foundations, select, joins, subqueries]
aliases: ["SQL Basics", "SELECT Query", "JOIN Operations"]
status: stable
updated: 2026-05-03
---

# SQL Basics: SELECT, WHERE, and JOIN

> [!summary] Model
> SQL query execution follows logical order: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT. Master SELECT for data retrieval, WHERE for filtering, and JOINs for combining tables. Understand NULL handling, pattern matching, and join strategies for efficient queries.

## Table of Contents

1. [[#SELECT Statement]]
2. [[#WHERE Clause]]
3. [[#JOIN Operations]]
   - [[#Inner JOIN]]
   - [[#LEFT JOIN (LEFT OUTER JOIN)]]
   - [[#RIGHT JOIN (RIGHT OUTER JOIN)]]
   - [[#FULL JOIN (FULL OUTER JOIN)]]
   - [[#CROSS JOIN]]
    - [[#Self JOINs]]
    - [[#LATERAL JOINs]]
    - [[#Complex JOINs and Multi-Table Relationships]]
4. [[#Subqueries (Nested Queries)]]
   - [[#Scalar Subqueries]]
   - [[#Correlated Subqueries]]
   - [[#EXISTS and NOT EXISTS]]
   - [[#IN and NOT IN Subqueries]]
   - [[#Subqueries in FROM Clause]]
5. [[#NULL Handling]]
6. [[#Query Execution Order]]
7. [[#Common Patterns]]
8. [[#Performance Considerations]]
9. [[#Best Practices]]
10. [[#Interview Questions]]

---

## SELECT Statement

### Basic SELECT Syntax

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT id, name, email FROM users;

-- Select with column aliases
SELECT name AS full_name, email AS contact FROM users;

-- Select with expressions
SELECT id, name, created_at::date AS signup_date FROM users;
```

**Why use SELECT?** Retrieves data from database tables. Foundation of all data access operations.

**How it works:** PostgreSQL processes SELECT by scanning tables, applying filters, and returning result set.

**When to use:** Whenever you need to retrieve data - reports, API responses, data analysis.

### Column Selection Strategies

```sql
-- ✅ Good: Explicit columns (preferred)
SELECT id, name, email FROM users;

-- ❌ Bad: SELECT * (avoid in production)
SELECT * FROM users;

-- ✅ Good: * for quick exploration
SELECT * FROM users LIMIT 5;
```

**Why avoid SELECT *?** Unnecessary data transfer, brittle to schema changes, potential security issues.

**How it impacts performance:** Transfers more data over network, may prevent index-only scans.

**When SELECT * is acceptable:** Development/debugging, when you need all columns.

### DISTINCT for Unique Values

```sql
-- Get unique values
SELECT DISTINCT department FROM employees;

-- Multiple columns
SELECT DISTINCT department, location FROM employees;

-- Count distinct combinations
SELECT COUNT(DISTINCT department) FROM employees;
```

**Why use DISTINCT?** Removes duplicate rows from result set.

**How it works:** PostgreSQL sorts data and removes duplicates, can be expensive on large datasets.

**When to use:** Finding unique categories, data profiling, eliminating duplicates in reports.

---

## WHERE Clause

### Comparison Operators

```sql
-- Equality
SELECT * FROM users WHERE status = 'active';

-- Inequality
SELECT * FROM users WHERE age > 18;

-- Range
SELECT * FROM products WHERE price BETWEEN 10 AND 100;

-- List membership
SELECT * FROM users WHERE role IN ('admin', 'moderator');

-- Pattern matching
SELECT * FROM users WHERE email LIKE '%@company.com';
```

**Why use WHERE?** Filters rows before they reach SELECT, reducing data processing.

**How it works:** Applied during table scan or index lookup, before aggregation.

**When to use:** Always when you don't need all rows - improves performance and clarity.

### Pattern Matching

```sql
-- LIKE patterns
SELECT * FROM users WHERE name LIKE 'John%';      -- Starts with John
SELECT * FROM users WHERE name LIKE '%Smith';     -- Ends with Smith
SELECT * FROM users WHERE name LIKE '%John%';     -- Contains John

-- Wildcards
SELECT * FROM files WHERE path LIKE '%.pdf';      -- PDF files

-- ILIKE (case insensitive)
SELECT * FROM users WHERE name ILIKE 'john%';     -- Case insensitive

-- SIMILAR TO (regex-like)
SELECT * FROM users WHERE email SIMILAR TO '%@(gmail|yahoo).com';
```

**Why choose LIKE vs ILIKE?** LIKE is faster but case-sensitive; ILIKE handles case variations.

**How they work:** LIKE uses simple pattern matching; ILIKE converts to lowercase first.

**When to use each:**
- LIKE: Exact case matching, performance-critical queries
- ILIKE: User input search, case-insensitive lookups
- SIMILAR TO: Complex patterns with regex-like syntax

### Logical Operators

```sql
-- AND: All conditions must be true
SELECT * FROM users
WHERE age >= 18 AND status = 'active';

-- OR: At least one condition must be true
SELECT * FROM users
WHERE department = 'IT' OR department = 'HR';

-- NOT: Negate condition
SELECT * FROM users
WHERE NOT status = 'inactive';

-- Complex combinations
SELECT * FROM users
WHERE (age >= 18 AND status = 'active')
   OR role = 'admin';
```

**Why use logical operators?** Combine multiple conditions for precise filtering.

**How they work:** AND has higher precedence than OR; use parentheses for clarity.

**When to use:** Complex business rules, multi-criteria filtering.

---

## JOIN Operations

### INNER JOIN

```sql
-- Basic inner join
SELECT u.name, o.order_date, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- Multiple joins
SELECT u.name, p.title, r.rating
FROM users u
INNER JOIN reviews r ON u.id = r.user_id
INNER JOIN products p ON r.product_id = p.id;
```

**Why use INNER JOIN?** Returns only matching rows from both tables. Most common join type.

**How it works:** For each row in left table, finds matching rows in right table based on condition.

**When to use:** When you need data that exists in both tables (e.g., users with orders).

### LEFT JOIN

```sql
-- Left join (left outer join)
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- Find users without orders
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```

**Why use LEFT JOIN?** Returns all rows from left table, matching rows from right table (NULL if no match).

**How it works:** Preserves all rows from left table, adds matching data from right.

**When to use:** When you want all records from primary table even if no related data exists.

### RIGHT JOIN

```sql
-- Right join (less common)
SELECT u.name, o.amount
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;
```

**Why use RIGHT JOIN?** Opposite of LEFT JOIN - preserves all rows from right table.

**How it works:** Same as LEFT JOIN but preserves right table rows.

**When to use:** Rarely used; usually LEFT JOIN is preferred for readability.

### FULL OUTER JOIN

```sql
-- Full outer join
SELECT u.name, o.order_date
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id;
```

**Why use FULL OUTER JOIN?** Returns all rows from both tables, with NULLs where no match.

**How it works:** Combines LEFT and RIGHT JOIN results.

**When to use:** Data analysis, finding unmatched records in both tables.

### CROSS JOIN

```sql
-- Cross join (Cartesian product)
SELECT u.name, p.title
FROM users u
CROSS JOIN products p;
```

**Why use CROSS JOIN?** Returns every combination of rows from both tables.

**How it works:** No join condition - every row paired with every other row.

**When to use:** Rarely; can be useful for generating test data or matrix operations.

### Self-JOINs

Self-joins allow a table to be joined with itself, which is useful for hierarchical data, sequential relationships, or comparing rows within the same table.

**Why use self-joins?** Query relationships within a single table without creating separate tables.

**How self-joins work:** Use table aliases to treat the same table as two different tables.

**When to use:** Hierarchical data (org charts, categories), sequential data (previous/next records), comparative analysis.

#### Example: Employee Hierarchy

**Sample table:**
```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    manager_id INTEGER REFERENCES employees(id),
    department VARCHAR(50),
    salary DECIMAL(10,2),
    hire_date DATE
);

INSERT INTO employees VALUES
(1, 'Alice Johnson', NULL, 'Executive', 150000, '2020-01-01'),
(2, 'Bob Smith', 1, 'Engineering', 120000, '2020-03-15'),
(3, 'Carol Williams', 1, 'Sales', 110000, '2020-05-20'),
(4, 'David Brown', 2, 'Engineering', 95000, '2021-01-10'),
(5, 'Eva Davis', 2, 'Engineering', 90000, '2021-06-01'),
(6, 'Frank Miller', 3, 'Sales', 85000, '2021-09-15');
```

**Find employee-manager relationships:**
```sql
SELECT
    e.name AS employee_name,
    e.department AS employee_dept,
    m.name AS manager_name,
    m.department AS manager_dept
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id
ORDER BY e.id;

-- Result:
-- employee_name | employee_dept | manager_name | manager_dept
-- --------------|---------------|--------------|-------------
-- Alice Johnson | Executive     | NULL         | NULL
-- Bob Smith     | Engineering   | Alice Johnson| Executive
-- Carol Williams| Sales         | Alice Johnson| Executive
-- David Brown   | Engineering   | Bob Smith    | Engineering
-- Eva Davis     | Engineering   | Bob Smith    | Engineering
-- Frank Miller  | Sales         | Carol Williams| Sales
```

**Why LEFT JOIN?** Shows top-level employees (CEO) who have no manager.

**Alternative with INNER JOIN:** Only shows employees with managers.

#### Example: Hierarchical Categories

**Sample table:**
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    level INTEGER DEFAULT 1
);

INSERT INTO categories VALUES
(1, 'Electronics', NULL, 1),
(2, 'Computers', 1, 2),
(3, 'Laptops', 2, 3),
(4, 'Desktops', 2, 3),
(5, 'Phones', 1, 2),
(6, 'Smartphones', 5, 3),
(7, 'Books', NULL, 1),
(8, 'Fiction', 7, 2),
(9, 'Non-Fiction', 7, 2);
```

**Show category hierarchy:**
```sql
SELECT
    c.name AS category,
    c.level,
    p.name AS parent_category,
    p.level AS parent_level
FROM categories c
LEFT JOIN categories p ON c.parent_id = p.id
ORDER BY c.id;

-- Result shows full hierarchy with parent-child relationships
```

#### Example: Sequential Data (Previous/Next)

**Sample table:**
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO orders VALUES
(1, 1, '2024-01-01', 100.00),
(2, 1, '2024-01-15', 250.00),
(3, 1, '2024-02-01', 75.00),
(4, 2, '2024-01-10', 300.00);
```

**Find customer's previous and next order:**
```sql
SELECT
    o1.id,
    o1.order_date,
    o1.amount,
    prev.order_date AS prev_order_date,
    prev.amount AS prev_amount,
    next.order_date AS next_order_date,
    next.amount AS next_amount
FROM orders o1
LEFT JOIN orders prev ON o1.customer_id = prev.customer_id
    AND prev.order_date < o1.order_date
    AND prev.order_date = (
        SELECT MAX(order_date) FROM orders
        WHERE customer_id = o1.customer_id AND order_date < o1.order_date
    )
LEFT JOIN orders next ON o1.customer_id = next.customer_id
    AND next.order_date > o1.order_date
    AND next.order_date = (
        SELECT MIN(order_date) FROM orders
        WHERE customer_id = o1.customer_id AND order_date > o1.order_date
    )
ORDER BY o1.customer_id, o1.order_date;
```

**Why complex self-joins?** Find adjacent records in sequence.

**Alternative:** Use window functions for simpler sequential queries.

#### Self-Join Performance Considerations

**Why self-joins can be slow:** Table scanned multiple times.

**How to optimize:**
- Add indexes on join columns
- Use appropriate join types
- Consider alternative approaches (CTEs, window functions)

**When to avoid self-joins:** Very large tables, simple queries solvable otherwise.

---

### LATERAL JOINs

A `LATERAL` join allows a subquery in the `FROM` clause to reference columns from preceding `FROM` items. This enables row-by-row processing where the right side depends on the current row of the left side.

**Why LATERAL?** Without `LATERAL`, a subquery in `FROM` or `JOIN` is evaluated independently and cannot reference columns from other tables in the same `FROM` clause. `LATERAL` lifts that restriction.

```mermaid
flowchart LR
    A[Left table row] --> B[LATERAL subquery executes for this row]
    B --> C[Returns computed row(s)]
    C --> D[Joined result for this left row]
    D --> E[Next left row → repeat]
```

#### Basic LATERAL

```sql
SELECT u.name, recent.order_id, recent.order_date
FROM users u
LEFT JOIN LATERAL (
    SELECT id AS order_id, order_date
    FROM orders
    WHERE user_id = u.id
    ORDER BY order_date DESC
    LIMIT 1
) recent ON true;
```

**What this does:** For each user, find their most recent order. `u.id` is referenced inside the subquery.

**Why use LATERAL vs alternatives:**

| Approach | Behavior | Best for |
|----------|----------|----------|
| `LATERAL` subquery | Executes per left row, can `LIMIT` per group | Top-N per group, complex per-row computation |
| `GROUP BY` + aggregate | Single scan, requires all rows | Simple aggregations (COUNT, MAX) |
| `ROW_NUMBER()` window | Scans all rows, then filters | Top-N with window functions |
| Correlated subquery in `SELECT` | Executes per row | Simple scalar lookups |

#### LATERAL with INNER JOIN

```sql
SELECT p.name, recent.price
FROM products p
JOIN LATERAL (
    SELECT price FROM price_history
    WHERE product_id = p.id
    ORDER BY recorded_at DESC
    LIMIT 1
) recent ON true;
```

If the lateral subquery returns no rows, the product is excluded (like `INNER JOIN`).

#### LATERAL with multiple columns

```sql
SELECT u.name, top_order.*
FROM users u
CROSS JOIN LATERAL (
    SELECT o.id, o.total, o.order_date
    FROM orders o
    WHERE o.user_id = u.id
    ORDER BY o.total DESC
    LIMIT 3
) top_order;
```

**How it works:** `CROSS JOIN LATERAL` forces the subquery to return at least one row per left row — if it produces no rows, the left row is dropped.

#### LATERAL with functions

`LATERAL` is also useful with set-returning functions:

```sql
SELECT u.id, tag
FROM users u
CROSS JOIN LATERAL unnest(string_to_array(u.tags, ',')) AS tag;
```

#### LATERAL for aggregation per group

```sql
SELECT d.name, emp.*
FROM departments d
CROSS JOIN LATERAL (
    SELECT e.name, e.salary
    FROM employees e
    WHERE e.dept_id = d.id
    ORDER BY e.salary DESC
    LIMIT 1
) emp;
```

**When to use LATERAL:**
- Top-N per group (best alternative to `ROW_NUMBER()` + filter)
- Complex per-row transformations
- Calling set-returning functions per row
- When a correlated subquery in `WHERE`/`SELECT` is too limiting

**Performance note:** LATERAL executes the subquery once per left row. Ensure the subquery has proper indexes (e.g., index on `orders(user_id, order_date DESC)` for the top-N example).

---

### Complex JOINs and Multi-Table Relationships

Complex joins involve multiple tables with various relationship types, requiring careful planning of join order and conditions.

**Why complex joins matter?** Real-world data is rarely in two tables.

**How to approach:** Start with core entities, add related tables, ensure proper join conditions.

**When to use:** Reporting, data analysis, API responses with related data.

#### Example: E-commerce Order Details

**Tables:**
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date DATE,
    status VARCHAR(20)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2),
    category VARCHAR(50)
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER,
    unit_price DECIMAL(10,2)
);

-- Sample data
INSERT INTO customers VALUES (1, 'John Doe', 'john@example.com');
INSERT INTO orders VALUES (1, 1, '2024-01-15', 'completed');
INSERT INTO products VALUES (1, 'Laptop', 1200.00, 'Electronics'), (2, 'Book', 25.00, 'Education');
INSERT INTO order_items VALUES (1, 1, 1, 1, 1200.00), (2, 1, 2, 2, 25.00);
```

**Complex join query:**
```sql
SELECT
    c.name AS customer_name,
    c.email,
    o.id AS order_id,
    o.order_date,
    o.status,
    p.name AS product_name,
    p.category,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN products p ON oi.product_id = p.id
WHERE o.status = 'completed'
  AND o.order_date >= '2024-01-01'
ORDER BY c.name, o.order_date, p.name;
```

**Why multiple INNER JOINs?** Each order can have multiple items, each item references a product.

**Result:** Complete order details with customer and product information.

#### Example: Social Network Friends

**Tables:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(50)
);

CREATE TABLE friendships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    friend_id INTEGER REFERENCES users(id),
    status VARCHAR(20), -- 'pending', 'accepted', 'blocked'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, friend_id)
);

-- Ensure bidirectional friendships
INSERT INTO friendships (user_id, friend_id, status) VALUES (2, 1, 'accepted');
```

**Find mutual friends:**
```sql
SELECT
    u1.name AS person1,
    u2.name AS person2,
    u3.name AS mutual_friend
FROM users u1
INNER JOIN friendships f1 ON u1.id = f1.user_id AND f1.status = 'accepted'
INNER JOIN users u3 ON f1.friend_id = u3.id  -- mutual friend
INNER JOIN friendships f2 ON u3.id = f2.user_id AND f2.status = 'accepted'
INNER JOIN users u2 ON f2.friend_id = u2.id  -- person2 is also friend of mutual
WHERE u1.id < u2.id  -- Avoid duplicate pairs
  AND u1.id <> u2.id
  AND NOT EXISTS (
      SELECT 1 FROM friendships
      WHERE (user_id = u1.id AND friend_id = u2.id) OR (user_id = u2.id AND friend_id = u1.id)
  )
ORDER BY u1.name, u2.name, u3.name;
```

**Why complex?** Find people who are not directly friends but have mutual friends.

#### Join Order Optimization

**Why join order matters:** Affects query performance significantly.

**How PostgreSQL optimizes:** Cost-based optimizer tries different join orders.

**Manual control (rarely needed):**
```sql
-- Force specific join order
SELECT /*+ JOIN_ORDER(u, o, oi, p) */ *
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;
```

**Best practice:** Let PostgreSQL optimize, but understand when to intervene.

#### Common Complex Join Patterns

**1. Master-Detail with Aggregates:**
```sql
SELECT
    c.name,
    COUNT(o.id) as order_count,
    SUM(o.total) as total_spent,
    AVG(o.total) as avg_order_value
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;
```

**2. Multiple Lookup Tables:**
```sql
SELECT
    e.name,
    d.name as department,
    l.city as location,
    m.name as manager
FROM employees e
JOIN departments d ON e.dept_id = d.id
JOIN locations l ON d.location_id = l.id
LEFT JOIN employees m ON e.manager_id = m.id;
```

**3. Conditional Joins:**
```sql
SELECT
    p.name,
    CASE
        WHEN p.category = 'Electronics' THEN e.warranty_years
        WHEN p.category = 'Books' THEN NULL
        ELSE NULL
    END as warranty_info
FROM products p
LEFT JOIN electronics e ON p.id = e.product_id AND p.category = 'Electronics';
```

## Subqueries (Nested Queries)

Subqueries are queries nested within other queries, allowing complex data filtering and computation.

**Why use subqueries?** Solve problems requiring multiple query steps, filter based on aggregates, or compute values for comparisons.

**How subqueries work:** Inner query executes first, results used by outer query.

**When to use:** Complex filtering, existence checks, derived tables, correlated computations.

**Performance note:** Can be inefficient if not optimized; sometimes JOINs are better.

### Scalar Subqueries

Return single value, used in SELECT, WHERE, or other clauses.

**Why scalar subqueries?** Compute single values for each row.

**How they work:** Must return exactly one row and one column.

**When to use:** Row-level calculations, comparisons with aggregates.

**Example: Customer's latest order date:**
```sql
SELECT
    c.name,
    c.email,
    (SELECT MAX(o.order_date) FROM orders o WHERE o.customer_id = c.id) AS latest_order_date
FROM customers c;

-- Result: Each customer with their most recent order date
```

**Example: Compare to average:**
```sql
SELECT
    p.name,
    p.price,
    (SELECT AVG(price) FROM products WHERE category = p.category) AS category_avg_price,
    CASE WHEN p.price > (SELECT AVG(price) FROM products WHERE category = p.category)
         THEN 'Above Average' ELSE 'Below Average' END AS price_category
FROM products p;
```

**Why useful?** Compare individual values to group aggregates.

### Correlated Subqueries

Reference columns from outer query, execute once per outer row.

**Why correlated subqueries?** Row-specific filtering or calculations.

**How they work:** Inner query runs for each outer row, using outer values.

**When to use:** Existence checks, row-specific aggregations.

**Performance:** Can be slow on large datasets; consider JOIN alternatives.

**Example: Customers with orders above average:**
```sql
SELECT c.name, c.email
FROM customers c
WHERE (SELECT AVG(o.amount) FROM orders o WHERE o.customer_id = c.id) > 100;

-- Only customers whose average order amount > $100
```

**Example: Most expensive product per category:**
```sql
SELECT p.name, p.category, p.price
FROM products p
WHERE p.price = (
    SELECT MAX(price) FROM products WHERE category = p.category
);

-- One product per category with highest price
```

**Optimization note:** Above query can be rewritten with window functions for better performance.

### EXISTS and NOT EXISTS

Test for existence of related rows, often more efficient than counting.

**Why EXISTS/NOT EXISTS?** Short-circuit evaluation - stops at first match.

**How they work:** Return true/false based on whether inner query returns any rows.

**When to use:** Existence checks, especially with correlated subqueries.

**Performance advantage:** Don't count all matching rows, just check existence.

**Example: Customers with orders:**
```sql
SELECT c.name, c.email
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.id
    AND o.order_date >= '2024-01-01'
);

-- More efficient than COUNT(*) > 0
```

**Example: Products never ordered:**
```sql
SELECT p.name, p.category
FROM products p
WHERE NOT EXISTS (
    SELECT 1 FROM order_items oi
    WHERE oi.product_id = p.id
);

-- Products with no order history
```

**Example: Departments with high earners:**
```sql
SELECT d.name
FROM departments d
WHERE EXISTS (
    SELECT 1 FROM employees e
    WHERE e.dept_id = d.id
    AND e.salary > (SELECT AVG(salary) FROM employees)
);

-- Departments with at least one employee above company average salary
```

### IN and NOT IN Subqueries

Test membership in a set of values.

**Why IN/NOT IN?** Clean syntax for set membership tests.

**How they work:** Inner query returns list of values, outer checks membership.

**When to use:** Fixed lists, small result sets from subquery.

**Performance:** Good for small lists, can be slow for large result sets.

**Example: Customers who ordered specific products:**
```sql
SELECT DISTINCT c.name, c.email
FROM customers c
WHERE c.id IN (
    SELECT o.customer_id
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    WHERE oi.product_id IN (1, 2, 3)
);

-- Customers who bought specific products
```

**Example: Employees not in certain departments:**
```sql
SELECT e.name, e.salary
FROM employees e
WHERE e.dept_id NOT IN (
    SELECT id FROM departments WHERE budget < 50000
);

-- Employees in well-funded departments
```

**Alternative:** JOIN often performs better for large datasets.

### Subqueries in FROM Clause

Use subquery results as a table in FROM clause.

**Why FROM subqueries?** Create derived tables for complex aggregations.

**How they work:** Subquery results treated as temporary table.

**When to use:** Multi-step transformations, complex aggregations.

**Example: Monthly sales summary:**
```sql
SELECT
    monthly_summary.month,
    monthly_summary.total_sales,
    monthly_summary.order_count,
    (monthly_summary.total_sales / monthly_summary.order_count) AS avg_order_value
FROM (
    SELECT
        DATE_TRUNC('month', o.order_date) AS month,
        SUM(o.amount) AS total_sales,
        COUNT(o.id) AS order_count
    FROM orders o
    WHERE o.order_date >= '2024-01-01'
    GROUP BY DATE_TRUNC('month', o.order_date)
) AS monthly_summary
ORDER BY month;
```

**Example: Customer ranking:**
```sql
SELECT
    ranked_customers.name,
    ranked_customers.total_spent,
    ranked_customers.rank
FROM (
    SELECT
        c.name,
        SUM(o.amount) AS total_spent,
        RANK() OVER (ORDER BY SUM(o.amount) DESC) AS rank
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.name
) AS ranked_customers
WHERE ranked_customers.rank <= 10;
```

**Best practice:** Use meaningful aliases for derived tables.

### Subquery Performance Considerations

**Why subqueries can be slow:** Multiple executions, lack of indexes on derived results.

**How to optimize:**
- Use JOINs for large datasets
- Ensure correlated subqueries have appropriate indexes
- Consider CTEs for readability and optimization

**When to avoid subqueries:**
- Large datasets with correlations
- Simple joins can replace them
- Performance-critical queries

**Alternative approaches:**
```sql
-- Instead of correlated subquery
SELECT c.name FROM customers c
WHERE (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) > 5;

-- Use JOIN with GROUP BY
SELECT c.name
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name
HAVING COUNT(*) > 5;
```

```

---

## Cross-Links

- **Advanced Joins**: [[SQL/02_Core/05_Window_Functions]]
- **Indexes**: [[SQL/02_Core/01_Indexes_Basics_and_BTree]]
- **Query Planning**: [[SQL/02_Core/04_Explain_Analyze_and_Query_Plans]]
- **Aggregates**: [[SQL/01_Foundations/03_Group_By_Having_and_Aggregates]]

## References

- [PostgreSQL SELECT Documentation](https://www.postgresql.org/docs/current/queries-select.html)
- [JOIN Examples](https://www.postgresql.org/docs/current/queries-join.html)
- [NULL Handling](https://www.postgresql.org/docs/current/functions-comparison.html)

---

**Status**: stable  
**Last Updated**: 2026-04-27  
**Lines**: 1,479