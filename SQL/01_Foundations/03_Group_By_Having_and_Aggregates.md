---
tags: [sql, postgresql, foundations, group-by, aggregates, having]
aliases: ["GROUP BY", "Aggregates", "HAVING Clause"]
status: stable
updated: 2026-04-26
---

# GROUP BY, HAVING, and Aggregates

> [!summary] Model
> GROUP BY creates groups of rows with same values. Aggregate functions (COUNT, SUM, AVG, MIN, MAX) operate on groups. HAVING filters groups after aggregation. Master grouping for reports, statistics, and data analysis with proper NULL handling and advanced grouping sets.

## Table of Contents

1. [[#GROUP BY Basics]]
2. [[#Aggregate Functions]]
3. [[#HAVING Clause]]
4. [[#GROUPING SETS, CUBE, ROLLUP]]
5. [[#Aggregate Filtering]]
6. [[#Common Patterns]]
7. [[#Performance Considerations]]
8. [[#Best Practices]]
9. [[#Interview Questions]]

---

## GROUP BY Basics

### Basic GROUP BY

```sql
-- Group by single column
SELECT department, COUNT(*) as employee_count
FROM employees
GROUP BY department;

-- Group by multiple columns
SELECT department, job_title, COUNT(*) as count
FROM employees
GROUP BY department, job_title
ORDER BY department, job_title;

-- Group by expressions
SELECT EXTRACT(year FROM hire_date) as hire_year, COUNT(*)
FROM employees
GROUP BY EXTRACT(year FROM hire_date);
```

**Why use GROUP BY?** Combines rows with identical values into summary groups for analysis.

**How it works:** PostgreSQL sorts data by GROUP BY columns, then aggregates values for each group.

**When to use:** Reports, statistics, data analysis, finding patterns in datasets.

### GROUP BY Execution Order

```sql
-- Logical order:
SELECT department, COUNT(*)          -- 4. SELECT aggregates
FROM employees                       -- 1. FROM source
WHERE salary > 30000                 -- 2. WHERE filter rows
GROUP BY department                  -- 3. GROUP BY create groups
HAVING COUNT(*) > 5                  -- 4. HAVING filter groups
ORDER BY COUNT(*) DESC;              -- 5. ORDER BY sort results
```

**Why order matters?** WHERE filters individual rows before grouping; HAVING filters groups after.

**How PostgreSQL processes:** FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY.

**When to remember:** Writing complex queries, debugging aggregation issues.

### GROUP BY with NULL

```sql
-- NULL values form their own group
INSERT INTO employees (name, department) VALUES ('John', NULL);

SELECT department, COUNT(*) FROM employees GROUP BY department;
-- Results: IT: 5, HR: 3, NULL: 1

-- Count NULL departments
SELECT COUNT(*) as null_dept_count
FROM employees
WHERE department IS NULL;
```

**Why NULL grouping matters?** NULL values are treated as equal for grouping purposes.

**How it works:** All NULL values in GROUP BY column form a single group.

**When to handle:** Data quality checks, reports including missing data.

---

## Aggregate Functions

### Basic Aggregates

```sql
-- COUNT variations
SELECT COUNT(*) as total_rows FROM employees;                    -- All rows
SELECT COUNT(employee_id) as non_null_ids FROM employees;       -- Non-NULL values
SELECT COUNT(DISTINCT department) as unique_depts FROM employees; -- Unique values

-- Numeric aggregates
SELECT SUM(salary) as total_salary,
       AVG(salary) as avg_salary,
       MIN(salary) as min_salary,
       MAX(salary) as max_salary
FROM employees;

-- Statistical aggregates
SELECT STDDEV(salary) as salary_stddev,
       VARIANCE(salary) as salary_variance
FROM employees;
```

**Why use aggregates?** Summarize data across multiple rows - calculate totals, averages, extremes.

**How they work:** Operate on groups of rows, return single value per group.

**When to use:** Reports, dashboards, data analysis, KPI calculations.

### String Aggregates

```sql
-- STRING_AGG: Concatenate strings
SELECT department,
       STRING_AGG(name, ', ') as employee_names
FROM employees
GROUP BY department;

-- With ordering
SELECT department,
       STRING_AGG(name, ', ' ORDER BY name) as sorted_names
FROM employees
GROUP BY department;

-- ARRAY_AGG: Create arrays
SELECT department,
       ARRAY_AGG(name ORDER BY salary DESC) as high_earners
FROM employees
GROUP BY department;
```

**Why use string aggregates?** Combine multiple values into single string or array representation.

**How they work:** STRING_AGG joins values with delimiter; ARRAY_AGG creates PostgreSQL arrays.

**When to use:** CSV exports, JSON responses, list formatting.

### Aggregate Function List

| Function | Description | NULL Handling |
|----------|-------------|---------------|
| COUNT(*) | Count all rows | Includes NULL |
| COUNT(col) | Count non-NULL values | Ignores NULL |
| SUM(col) | Sum of values | Ignores NULL |
| AVG(col) | Average of values | Ignores NULL |
| MIN(col) | Minimum value | Ignores NULL |
| MAX(col) | Maximum value | Ignores NULL |
| STDDEV(col) | Standard deviation | Ignores NULL |
| VARIANCE(col) | Variance | Ignores NULL |
| STRING_AGG | Concatenate strings | Ignores NULL |
| ARRAY_AGG | Create array | Ignores NULL |

---

## HAVING Clause

### HAVING vs WHERE

```sql
-- WHERE: Filter before grouping
SELECT department, AVG(salary)
FROM employees
WHERE salary > 30000                    -- Individual rows
GROUP BY department;

-- HAVING: Filter after grouping
SELECT department, AVG(salary)
FROM employees
GROUP BY department
HAVING AVG(salary) > 50000;             -- Group aggregates

-- Combined
SELECT department, COUNT(*) as emp_count
FROM employees
WHERE hire_date > '2020-01-01'          -- Row filter
GROUP BY department
HAVING COUNT(*) > 5;                    -- Group filter
```

**Why use HAVING?** Filter groups based on aggregate calculations that WHERE can't access.

**How it works:** Applied after GROUP BY, can reference aggregate functions.

**When to use:** Filtering by group size, aggregate thresholds, statistical conditions.

### HAVING with Multiple Conditions

```sql
-- Multiple HAVING conditions
SELECT department, AVG(salary), COUNT(*)
FROM employees
GROUP BY department
HAVING AVG(salary) > 50000
   AND COUNT(*) >= 3
   AND MAX(salary) > 80000;

-- HAVING with subqueries
SELECT department, AVG(salary)
FROM employees
GROUP BY department
HAVING AVG(salary) > (SELECT AVG(salary) FROM employees);
```

**Why complex HAVING?** Precise control over which groups to include in results.

**How it works:** All conditions must be true for group to be included.

**When to use:** Advanced reporting, outlier detection, comparative analysis.

---

## GROUPING SETS, CUBE, ROLLUP

### ROLLUP (Subtotals)

```sql
-- Basic ROLLUP
SELECT department, job_title, SUM(salary)
FROM employees
GROUP BY ROLLUP (department, job_title);

-- Results include:
-- department, job_title subtotals
-- department subtotals (job_title = NULL)
-- Grand total (both = NULL)
```

**Why use ROLLUP?** Generate subtotals and grand totals automatically.

**How it works:** Creates hierarchical groupings from right to left.

**When to use:** Financial reports, hierarchical summaries.

### CUBE (All Combinations)

```sql
-- Basic CUBE
SELECT department, job_title, SUM(salary)
FROM employees
GROUP BY CUBE (department, job_title);

-- Results include all combinations:
-- (dept, job), (dept, NULL), (NULL, job), (NULL, NULL)
```

**Why use CUBE?** Generate all possible subtotal combinations.

**How it works:** Creates groupings for every combination of grouping columns.

**When to use:** Multi-dimensional analysis, pivot tables.

### GROUPING SETS (Custom Groups)

```sql
-- Custom grouping combinations
SELECT department, job_title, SUM(salary)
FROM employees
GROUP BY GROUPING SETS (
    (department, job_title),    -- Individual groups
    (department),               -- Department totals
    (job_title),                -- Job title totals
    ()                          -- Grand total
);

-- Equivalent to UNION of separate queries
```

**Why use GROUPING SETS?** Precise control over which subtotals to generate.

**How it works:** Specify exactly which grouping combinations you want.

**When to use:** Custom reports, specific subtotal requirements.

### GROUPING Function

```sql
-- Identify NULLs from ROLLUP/CUBE
SELECT
    department,
    job_title,
    SUM(salary),
    GROUPING(department) as dept_null,
    GROUPING(job_title) as job_null
FROM employees
GROUP BY ROLLUP (department, job_title);

-- Results show which columns are NULL due to rollup
```

**Why use GROUPING?** Distinguish between real NULLs and NULLs from rollup operations.

**How it works:** Returns 1 if column is NULL due to grouping, 0 otherwise.

**When to use:** Advanced reporting with rollup/cube operations.

---

## Aggregate Filtering

### FILTER Clause (PostgreSQL 9.4+)

```sql
-- Conditional aggregates
SELECT
    department,
    COUNT(*) as total_employees,
    COUNT(*) FILTER (WHERE salary > 50000) as high_earners,
    AVG(salary) FILTER (WHERE gender = 'F') as avg_female_salary
FROM employees
GROUP BY department;

-- Multiple filters
SELECT
    department,
    SUM(salary) FILTER (WHERE active = true) as active_salary,
    SUM(salary) FILTER (WHERE active = false) as inactive_salary
FROM employees
GROUP BY department;
```

**Why use FILTER?** Apply conditions to individual aggregate functions without subqueries.

**How it works:** WHERE condition applies only to that aggregate calculation.

**When to use:** Conditional statistics, pivot-like operations, complex reporting.

### FILTER vs CASE

```sql
-- FILTER approach (preferred)
SELECT department,
       AVG(salary) FILTER (WHERE gender = 'M') as male_avg,
       AVG(salary) FILTER (WHERE gender = 'F') as female_avg
FROM employees
GROUP BY department;

-- CASE approach (equivalent but verbose)
SELECT department,
       AVG(CASE WHEN gender = 'M' THEN salary END) as male_avg,
       AVG(CASE WHEN gender = 'F' THEN salary END) as female_avg
FROM employees
GROUP BY department;
```

**Why FILTER over CASE?** Cleaner syntax, better performance, clearer intent.

**How it works:** FILTER is optimized for aggregate conditions.

**When to use:** Multiple conditional aggregates on same data.

---

## Common Patterns

### Running Totals and Rankings

```sql
-- Running totals (though not strictly GROUP BY)
SELECT name, salary,
       SUM(salary) OVER (ORDER BY salary) as running_total
FROM employees;

-- But for grouped running totals:
SELECT department, name, salary,
       SUM(salary) OVER (PARTITION BY department ORDER BY salary) as dept_running_total
FROM employees;
```

**Why running totals?** Cumulative calculations within groups.

**How it works:** Window functions with PARTITION BY and ORDER BY.

**When to use:** Financial reports, progress tracking.

### Conditional Aggregation

```sql
-- Status counts in one query
SELECT
    department,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_count,
    COUNT(CASE WHEN status = 'inactive' THEN 1 END) as inactive_count,
    COUNT(CASE WHEN hire_date > '2023-01-01' THEN 1 END) as new_hires
FROM employees
GROUP BY department;

-- Percentage calculations
SELECT department,
       AVG(salary) as avg_salary,
       AVG(CASE WHEN gender = 'F' THEN salary END) as female_avg,
       ROUND(
           AVG(CASE WHEN gender = 'F' THEN salary END) / AVG(salary) * 100, 2
       ) as female_pct_of_avg
FROM employees
GROUP BY department;
```

**Why conditional aggregation?** Multiple statistics from single pass through data.

**How it works:** CASE expressions inside aggregates.

**When to use:** Reporting, dashboard metrics, comparative analysis.

### Grouping by Time Periods

```sql
-- Group by month
SELECT
    DATE_TRUNC('month', hire_date) as hire_month,
    COUNT(*) as hires
FROM employees
GROUP BY DATE_TRUNC('month', hire_date)
ORDER BY hire_month;

-- Group by week/year
SELECT
    EXTRACT(year FROM hire_date) as hire_year,
    EXTRACT(week FROM hire_date) as hire_week,
    COUNT(*) as hires
FROM employees
GROUP BY hire_year, hire_week
ORDER BY hire_year, hire_week;
```

**Why time grouping?** Temporal analysis and reporting.

**How it works:** Date functions create grouping keys.

**When to use:** Time-series analysis, trend reporting.

---

## Performance Considerations

### Index Usage

```sql
-- GROUP BY can use indexes
CREATE INDEX ON employees (department);  -- Helps GROUP BY department

SELECT department, COUNT(*)
FROM employees
GROUP BY department;  -- Uses index for sorting/grouping

-- But functions prevent index use
SELECT EXTRACT(year FROM hire_date), COUNT(*)
FROM employees
GROUP BY EXTRACT(year FROM hire_date);  -- No index usage
```

**Why indexes matter?** Avoid sorting for GROUP BY operations.

**How to optimize:** Index columns used in GROUP BY.

**When to index:** Frequent grouping columns, large tables.

### Hash vs Sort Grouping

```sql
-- PostgreSQL chooses strategy based on:
-- - Table size
-- - Available memory (work_mem)
-- - Index availability

-- Force hash aggregation (if beneficial)
SET enable_hashagg = on;
SET work_mem = '256MB';

-- Check plan
EXPLAIN SELECT department, COUNT(*)
FROM employees
GROUP BY department;
```

**Why strategy matters?** Hash aggregation can be faster for large groups.

**How PostgreSQL chooses:** Cost-based optimization.

**When to tune:** Slow GROUP BY queries, memory issues.

### Memory Considerations

```sql
-- Large groupings may spill to disk
SHOW work_mem;  -- Current limit

-- Increase for large aggregations
SET work_mem = '512MB';

-- Monitor memory usage
EXPLAIN (ANALYZE, BUFFERS)
SELECT department, STRING_AGG(name, ', ')
FROM employees
GROUP BY department;
```

**Why memory matters?** GROUP BY operations build hash tables or sort in memory.

**How to monitor:** Check work_mem usage in EXPLAIN BUFFERS.

**When to increase:** Hash aggregation spilling to disk.

---

## Best Practices

### 1. Include All Non-Aggregated Columns in GROUP BY

```sql
-- ✅ Correct
SELECT department, job_title, COUNT(*)
FROM employees
GROUP BY department, job_title;

-- ❌ Error: job_title not in GROUP BY
SELECT department, job_title, COUNT(*)
FROM employees
GROUP BY department;
```

### 2. Use HAVING for Aggregate Conditions

```sql
-- ✅ Correct: Filter groups
SELECT department, AVG(salary)
FROM employees
GROUP BY department
HAVING AVG(salary) > 50000;

-- ❌ Wrong: WHERE can't use aggregates
SELECT department, AVG(salary)
FROM employees
WHERE AVG(salary) > 50000  -- Error!
GROUP BY department;
```

### 3. Prefer FILTER over CASE for Aggregates

```sql
-- ✅ Preferred
SELECT department,
       AVG(salary) FILTER (WHERE gender = 'M') as male_avg
FROM employees
GROUP BY department;

-- ❌ Verbose alternative
SELECT department,
       AVG(CASE WHEN gender = 'M' THEN salary END) as male_avg
FROM employees
GROUP BY department;
```

### 4. Use Appropriate Grouping Constructs

```sql
-- ✅ ROLLUP for hierarchical totals
SELECT department, job_title, SUM(salary)
FROM employees
GROUP BY ROLLUP (department, job_title);

-- ✅ GROUPING SETS for specific combinations
SELECT department, job_title, SUM(salary)
FROM employees
GROUP BY GROUPING SETS ((department), (job_title), ());
```

### 5. Handle NULL Values Explicitly

```sql
-- ✅ Consider NULL in grouping
SELECT COALESCE(department, 'Unassigned') as dept, COUNT(*)
FROM employees
GROUP BY COALESCE(department, 'Unassigned');

-- ✅ Filter NULL groups if needed
SELECT department, COUNT(*)
FROM employees
WHERE department IS NOT NULL
GROUP BY department;
```

### 6. Optimize for Performance

```sql
-- ✅ Index grouping columns
CREATE INDEX ON employees (department, job_title);

-- ✅ Pre-aggregate for speed
CREATE MATERIALIZED VIEW dept_stats AS
SELECT department, COUNT(*), AVG(salary)
FROM employees
GROUP BY department;
```

### 7. Use Meaningful Column Aliases

```sql
-- ✅ Clear aliases
SELECT department,
       COUNT(*) as employee_count,
       AVG(salary) as avg_salary,
       MIN(hire_date) as earliest_hire
FROM employees
GROUP BY department;
```

### 8. Consider Query Structure

```sql
-- ✅ Logical flow
SELECT department,
       COUNT(*) as total_employees,
       AVG(salary) as avg_salary
FROM employees
WHERE active = true                    -- Filter first
GROUP BY department
HAVING COUNT(*) > 5                    -- Then filter groups
ORDER BY avg_salary DESC;              -- Finally sort
```

---

## Interview Questions

### Q1: What's the difference between WHERE and HAVING?

**Answer:** WHERE filters individual rows before grouping; HAVING filters groups after aggregation.

```sql
-- WHERE: Row-level filtering
SELECT department, COUNT(*)
FROM employees
WHERE salary > 30000        -- Applied to each row
GROUP BY department;

-- HAVING: Group-level filtering
SELECT department, COUNT(*)
FROM employees
GROUP BY department
HAVING COUNT(*) > 5;        -- Applied to each group
```

**Key points:**
- WHERE: Before GROUP BY, can't use aggregates
- HAVING: After GROUP BY, can use aggregates
- Performance: WHERE reduces data before grouping

### Q2: Explain ROLLUP, CUBE, and GROUPING SETS.

**Answer:**

**ROLLUP:** Creates hierarchical subtotals
```sql
SELECT dept, job, SUM(salary)
FROM employees
GROUP BY ROLLUP (dept, job);
-- Results: (dept,job), (dept,NULL), (NULL,NULL)
```

**CUBE:** Creates all possible combinations
```sql
SELECT dept, job, SUM(salary)
FROM employees
GROUP BY CUBE (dept, job);
-- Results: (dept,job), (dept,NULL), (NULL,job), (NULL,NULL)
```

**GROUPING SETS:** Custom subtotal combinations
```sql
SELECT dept, job, SUM(salary)
FROM employees
GROUP BY GROUPING SETS ((dept), (job), ());
-- Results: dept totals, job totals, grand total only
```

### Q3: How do aggregate functions handle NULL values?

**Answer:** Most aggregates ignore NULL values, except COUNT(*).

```sql
-- Sample data: salaries 1000, NULL, 2000
SELECT COUNT(*) as total_rows,        -- 3 (includes NULL rows)
       COUNT(salary) as non_null,     -- 2 (ignores NULL)
       SUM(salary) as total,          -- 3000 (ignores NULL)
       AVG(salary) as average         -- 1500 (ignores NULL)
FROM employees;
```

**Functions and NULL:**
- COUNT(*): Counts all rows
- COUNT(col): Counts non-NULL values
- SUM/AVG/MIN/MAX: Ignore NULL values
- STRING_AGG/ARRAY_AGG: Ignore NULL values

### Q4: What's the execution order of SQL clauses?

**Answer:** Logical processing order:

1. **FROM/JOIN** - Identify source tables
2. **WHERE** - Filter individual rows
3. **GROUP BY** - Create groups
4. **HAVING** - Filter groups
5. **SELECT** - Project columns and aggregates
6. **DISTINCT** - Remove duplicates
7. **ORDER BY** - Sort results
8. **LIMIT/OFFSET** - Restrict output

```sql
SELECT department, COUNT(*)     -- 5. SELECT
FROM employees                  -- 1. FROM
WHERE salary > 30000            -- 2. WHERE
GROUP BY department             -- 3. GROUP BY
HAVING COUNT(*) > 3             -- 4. HAVING
ORDER BY COUNT(*) DESC          -- 7. ORDER BY
LIMIT 5;                        -- 8. LIMIT
```

### Q5: Explain the FILTER clause for aggregates.

**Answer:** FILTER applies conditions to individual aggregate functions.

```sql
-- Without FILTER (requires subqueries)
SELECT dept,
       (SELECT AVG(salary) FROM employees WHERE dept = e.dept AND gender = 'M') male_avg,
       (SELECT AVG(salary) FROM employees WHERE dept = e.dept AND gender = 'F') female_avg
FROM (SELECT DISTINCT dept FROM employees) e;

-- With FILTER (single pass)
SELECT dept,
       AVG(salary) FILTER (WHERE gender = 'M') male_avg,
       AVG(salary) FILTER (WHERE gender = 'F') female_avg
FROM employees
GROUP BY dept;
```

**Benefits:**
- Cleaner syntax
- Better performance (single table scan)
- Easier to read and maintain

### Q6: How do you generate subtotals and grand totals?

**Answer:** Use ROLLUP, CUBE, or GROUPING SETS.

```sql
-- ROLLUP for hierarchical totals
SELECT department, job_title, SUM(salary)
FROM employees
GROUP BY ROLLUP (department, job_title);

-- CUBE for all combinations
SELECT department, region, SUM(sales)
FROM sales_data
GROUP BY CUBE (department, region);

-- GROUPING SETS for custom combinations
SELECT department, SUM(sales)
FROM sales_data
GROUP BY GROUPING SETS (department, ());
```

**Use GROUPING() to identify subtotal rows:**
```sql
SELECT department, job_title, SUM(salary),
       GROUPING(department) dept_total,
       GROUPING(job_title) job_total
FROM employees
GROUP BY ROLLUP (department, job_title);
```

### Q7: What's wrong with this query?

```sql
SELECT department, job_title, COUNT(*)
FROM employees
GROUP BY department;
```

**Answer:** Error - `job_title` appears in SELECT but not in GROUP BY.

**Correct version:**
```sql
-- Option 1: Add to GROUP BY
SELECT department, job_title, COUNT(*)
FROM employees
GROUP BY department, job_title;

-- Option 2: Use aggregate function
SELECT department, STRING_AGG(job_title, ', '), COUNT(*)
FROM employees
GROUP BY department;

-- Option 3: Remove from SELECT
SELECT department, COUNT(*)
FROM employees
GROUP BY department;
```

**Rule:** All non-aggregated columns in SELECT must be in GROUP BY.

### Q8: How do you optimize GROUP BY queries?

**Answer:** Several strategies:

```sql
-- 1. Index grouping columns
CREATE INDEX ON employees (department, job_title);

-- 2. Ensure sufficient work_mem
SET work_mem = '256MB';

-- 3. Use covering indexes
CREATE INDEX ON employees (department, salary);

-- 4. Pre-aggregate if possible
CREATE MATERIALIZED VIEW dept_summary AS
SELECT department, COUNT(*), AVG(salary)
FROM employees
GROUP BY department;

-- 5. Avoid functions in GROUP BY
-- Bad
SELECT EXTRACT(year FROM hire_date), COUNT(*)
FROM employees
GROUP BY EXTRACT(year FROM hire_date);

-- Good
SELECT hire_year, COUNT(*)
FROM (
    SELECT *, EXTRACT(year FROM hire_date) as hire_year
    FROM employees
) t
GROUP BY hire_year;
```

**Monitor with EXPLAIN ANALYZE** to see if hash aggregation or sort is used.

---

## Summary

**Key Takeaways:**

1. **GROUP BY**: Creates groups of rows with identical values for aggregation
2. **Aggregates**: COUNT, SUM, AVG, MIN, MAX operate on groups
3. **HAVING**: Filters groups after aggregation (vs WHERE for rows)
4. **ROLLUP/CUBE**: Generate subtotals and totals automatically
5. **FILTER**: Apply conditions to individual aggregates
6. **Performance**: Index grouping columns, monitor memory usage
7. **NULL Handling**: NULL values form their own group in GROUP BY

**Aggregation Pattern:**
```
SELECT grouping_columns, aggregate_functions
FROM table
WHERE row_conditions          -- Filter before grouping
GROUP BY grouping_columns     -- Create groups
HAVING group_conditions       -- Filter after grouping
ORDER BY sort_expressions;    -- Sort results
```

---

## Cross-Links

- **Basic SELECT**: [[SQL/01_Foundations/02_SQL_Basics_Select_Where_Join]]
- **Window Functions**: [[SQL/02_Core/05_Window_Functions]]
- **Performance**: [[SQL/02_Core/04_Explain_Analyze_and_Query_Plans]]

## References

- [PostgreSQL GROUP BY](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUPING)
- [Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [GROUPING SETS](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUPING-SETS)

---

**Status**: stable  
**Last Updated**: 2026-04-26  
**Lines**: 1,300