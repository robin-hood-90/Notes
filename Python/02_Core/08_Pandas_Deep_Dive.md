---
tags: [python, core, pandas, dataframe, series, groupby, merge, time-series]
aliases: ["Pandas", "DataFrame", "Series", "GroupBy", "Merge", "Time Series", "Pandas Internals"]
status: stable
updated: 2026-05-29
---

# Pandas Deep Dive

> [!summary] Goal
> Master pandas — Series and DataFrame internals, groupby operations, merge/join strategies, multi-indexing, time series, I/O patterns, and common pitfalls. Built on NumPy.

## Table of Contents

1. [DataFrame Internals](#dataframe-internals)
2. [GroupBy](#groupby)
3. [Merge and Join](#merge-and-join)
4. [Multi-Index](#multi-index)
5. [Time Series](#time-series)
6. [I/O](#io)
7. [Method Chaining](#method-chaining)
8. [Pitfalls](#pitfalls)

---

## DataFrame Internals

> [!info] A DataFrame is a dict of Series, each backed by a NumPy array (or ArrowChunkedArray in pandas 2.0+)
> Columns are stored in a BlockManager (pandas <2.0) or Arrow-backed columns (pandas 2.0+ with `dtype_backend="pyarrow"`).

```python
import pandas as pd
import numpy as np

# Creation
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Carol"],
    "age": [30, 25, 35],
    "salary": [70000, 50000, 90000],
})

# From NumPy
arr = np.random.randn(100, 3)
df = pd.DataFrame(arr, columns=["a", "b", "c"])

# From list of dicts
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
df = pd.DataFrame(data)

# Properties
df.shape          # (3, 3)
df.dtypes         # Column types
df.columns        # Index(['name', 'age', 'salary'])
df.index          # RangeIndex(start=0, stop=3, step=1)
df.values         # NumPy array (3 × 3)
df.info()         # Memory usage, dtypes, non-null count

# Selection
df["name"]                    # Series
df[["name", "age"]]           # DataFrame
df.loc[0]                     # Row by label (index)
df.iloc[0]                    # Row by integer position
df.loc[df["age"] > 25]        # Boolean indexing
df.query("age > 25")          # Query string

# Column operations
df["bonus"] = df["salary"] * 0.1     # New column
df["salary_log"] = np.log(df["salary"])
df.drop(columns=["bonus"])           # Drop column
```

---

## GroupBy

> [!info] GroupBy follows split-apply-combine: split data into groups, apply a function, combine results

```python
df = pd.DataFrame({
    "department": ["Engineering", "Engineering", "Sales", "Sales", "Engineering"],
    "name": ["Alice", "Bob", "Carol", "Dan", "Eve"],
    "salary": [100000, 80000, 60000, 70000, 120000],
    "years": [5, 3, 2, 4, 6],
})

# Basic groupby
df.groupby("department")["salary"].mean()
# department
# Engineering    100000.0
# Sales           65000.0

# Multiple aggregations
df.groupby("department").agg({
    "salary": ["mean", "std", "count"],
    "years": "max",
})

# Named aggregation
df.groupby("department").agg(
    avg_salary=("salary", "mean"),
    max_years=("years", "max"),
    headcount=("name", "count"),
)

# Transform — preserve shape (useful for normalisation)
df["salary_pct"] = df.groupby("department")["salary"].transform(
    lambda x: x / x.sum()
)

# Filter groups
df.groupby("department").filter(lambda g: g["salary"].mean() > 70000)

# Apply — most flexible (but slowest)
df.groupby("department").apply(lambda g: g.sort_values("salary"))
```

### GroupBy performance

```python
# Fast: built-in aggregations (C-optimized)
df.groupby("department")["salary"].sum()

# Slow: custom Python lambda
df.groupby("department")["salary"].apply(lambda x: x.sum() / len(x))

# Medium: transform with built-in
df.groupby("department")["salary"].transform("mean")
```

---

## Merge and Join

```python
employees = pd.DataFrame({
    "emp_id": [1, 2, 3],
    "name": ["Alice", "Bob", "Carol"],
    "dept_id": [10, 20, 10],
})

departments = pd.DataFrame({
    "dept_id": [10, 20, 30],
    "dept_name": ["Engineering", "Sales", "HR"],
})

# Inner join — only matching keys
merged = pd.merge(employees, departments, on="dept_id", how="inner")

# Left join — keep all employees
merged = pd.merge(employees, departments, on="dept_id", how="left")

# Right join — keep all departments
merged = pd.merge(employees, departments, on="dept_id", how="right")

# Outer join — keep everything
merged = pd.merge(employees, departments, on="dept_id", how="outer")

# Merge on different column names
employees.merge(departments, left_on="dept_id", right_on="dept_id")

# Index-based merge
employees.merge(departments, left_index=True, right_index=True)

# Concatenation
df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
df2 = pd.DataFrame({"a": [5, 6], "b": [7, 8]})
pd.concat([df1, df2], axis=0)      # Stack rows
pd.concat([df1, df2], axis=1)      # Side by side
```

---

## Multi-Index

```python
# MultiIndex DataFrame
arrays = [["A", "A", "B", "B"], [1, 2, 1, 2]]
index = pd.MultiIndex.from_arrays(arrays, names=["group", "subgroup"])
df = pd.DataFrame({"value": [10, 20, 30, 40]}, index=index)

# Selection
df.loc["A"]                     # All subgroups of A
df.loc[("A", 1)]                # Specific subgroup
df.xs(1, level="subgroup")      # All rows with subgroup=1

# Stack / unstack
df.unstack()                    # Subgroups to columns
df.stack()                      # Columns to rows

# Reset index
df.reset_index()                # Move index to columns
df.reset_index(level="group")   # Only one level
```

---

## Time Series

```python
# Create date range
dates = pd.date_range("2026-01-01", periods=100, freq="D")
df = pd.DataFrame({"value": np.random.randn(100)}, index=dates)

# Resampling
df.resample("W").mean()                 # Weekly mean
df.resample("M").agg({"value": ["sum", "mean"]})
df.resample("Q").first()                # Quarter start

# Rolling windows
df["rolling_mean"] = df["value"].rolling(window=7).mean()
df["rolling_std"] = df["value"].rolling(window=7).std()
df["expanding"] = df["value"].expanding().mean()

# Shifts and diffs
df["lag_1"] = df["value"].shift(1)      # Previous day
df["diff"] = df["value"].diff()         # Daily change
df["pct_change"] = df["value"].pct_change()  # Daily return

# Time zone
df.tz_localize("UTC")
df.tz_convert("America/New_York")

# Date filtering
df["2026-01"]                           # January 2026
df["2026-01-15":"2026-02-15"]           # Date range

# Time-based features
df.index.year
df.index.month
df.index.weekday
df.index.is_month_end
```

---

## I/O

```python
# CSV
df.to_csv("data.csv", index=False)
df = pd.read_csv("data.csv")

# CSV with options
df = pd.read_csv("data.csv",
    parse_dates=["date"],
    index_col="id",
    dtype={"age": "int32"},
    na_values=["NA", "null"],
)

# Parquet (fast, compressed, recommended for storage)
df.to_parquet("data.parquet")
df = pd.read_parquet("data.parquet")

# Excel
df.to_excel("data.xlsx", sheet_name="Sheet1")
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

# JSON
df.to_json("data.json", orient="records")
df = pd.read_json("data.json")

# SQL
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:pass@localhost/db")
df.to_sql("table_name", engine, if_exists="replace")
df = pd.read_sql("SELECT * FROM table_name", engine)

# Pickle
df.to_pickle("data.pkl")
df = pd.read_pickle("data.pkl")
```

---

## Method Chaining

```python
# Without chaining
df = pd.read_csv("data.csv")
df = df.dropna()
df = df[df["age"] > 0]
df = df.groupby("department")["salary"].mean()
df = df.reset_index()

# With chaining (pipe/assign)
result = (
    pd.read_csv("data.csv")
    .dropna()
    .query("age > 0")
    .groupby("department")
    .agg(avg_salary=("salary", "mean"))
    .reset_index()
    .assign(rank=lambda x: x["avg_salary"].rank(ascending=False))
)
```

---

## Pitfalls

### `SettingWithCopyWarning`

```python
# ❌ This may work on a view or a copy — unpredictable!
df[df["age"] > 25]["bonus"] = 1000

# ✅ Use .loc
df.loc[df["age"] > 25, "bonus"] = 1000
```

### Chained assignment

```python
df["new_col"] = df.groupby("dept")["salary"].transform("mean")
# If you modify `new_col` later, it may or may not affect the original
```

### Categorical data

```python
# String columns are memory-heavy for repeated values
# Convert to category:
df["department"] = df["department"].astype("category")
# Saves memory, enables optimized groupby
```

### `inplace=True` is deprecated

```python
# ❌ Deprecated
df.dropna(inplace=True)

# ✅ Preferred
df = df.dropna()
```

### Reading large CSV

```python
# Use chunks for large files
chunks = pd.read_csv("large.csv", chunksize=10000)
result = pd.concat([process(chunk) for chunk in chunks])

# Or specify dtypes to save memory
dtypes = {"col1": "int32", "col2": "category"}
df = pd.read_csv("large.csv", dtype=dtypes)
```

---

> [!question]- Interview Questions
>
> **Q: How does `groupby` work internally?**
> A: GroupBy follows split-apply-combine. Splitting occurs by hashing the keys and grouping rows into buckets. Applying runs the aggregation function per group in C (for built-in aggs) or Python (for custom). Combining concatenates results into a new DataFrame. Built-in aggregations (sum, mean, count) are highly optimized.
>
> **Q: What's the difference between `merge` and `join`?**
> A: `merge` uses column names for the join key (SQL-like). `join` uses the index. `merge` is more explicit and flexible. Under the hood, they both use the same algorithm. Use `merge` for column joins, `join` for index joins.
>
> **Q: How do you handle a `SettingWithCopyWarning`?**
> A: The warning indicates you may be modifying a view instead of the original DataFrame. Fix by using `.loc` for assignments, explicitly using `.copy()` when you need a separate DataFrame, or using `pd.options.mode.chained_assignment = None` to suppress (not recommended).

---

## Cross-Links

- [[Python/02_Core/07_NumPy_Deep_Dive]] for NumPy fundamentals
- [[Python/02_Core/09_Data_Visualization]] for plotting DataFrames
- [[Python/02_Core/10_Machine_Learning]] for sklearn with pandas
- [[Python/01_Foundations/08_File_IO_Serialization]] for file I/O basics
