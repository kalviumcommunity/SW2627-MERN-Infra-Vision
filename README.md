# InfraVision

## Project Overview
InfraVision is a data engineering project that validates, cleans, profiles, and documents cloud infrastructure billing data.

## NumPy Vectorized Computation Workflow

This project is a good place to apply NumPy vectorization when a task needs to scale beyond Python loops. Looping over rows is easy to write, but it becomes slow on large datasets because Python has to interpret every iteration. NumPy moves the heavy computation into optimized C code, which is much faster for numeric work.

### Why Vectorization Matters

Python loops and per-row `.apply()` logic are fine for small data, but they do not scale well when a dataframe grows to hundreds of thousands or millions of rows. Vectorized NumPy expressions operate on entire arrays at once, which removes interpreter overhead and makes normalization, scoring, and ranking much faster.

### Example: Min-Max Normalization

```python
import numpy as np

# Slow: loop-based approach
normalized = []
for value in df['revenue']:
	normalized.append((value - df['revenue'].min()) / (df['revenue'].max() - df['revenue'].min()))

# Fast: NumPy vectorized approach
revenue_array = df['revenue'].values
normalized = (revenue_array - revenue_array.min()) / (revenue_array.max() - revenue_array.min())
df['revenue_normalized'] = normalized
```

### Example: Z-Score Normalization

```python
revenue_array = df['revenue'].values
z_scores = (revenue_array - revenue_array.mean()) / revenue_array.std()
df['revenue_zscore'] = z_scores
```

### Measure the Improvement

Time the loop version and the vectorized version to confirm the gain:

```python
import time

start = time.time()
# loop code here
loop_time = time.time() - start

start = time.time()
# NumPy code here
vec_time = time.time() - start

print(f"Loop: {loop_time:.3f}s")
print(f"NumPy: {vec_time:.3f}s")
print(f"Speedup: {loop_time / vec_time:.0f}x")
```

The main takeaway is simple: use Pandas for dataframe structure, but move numeric transformations into NumPy whenever performance matters.

## Distribution Analysis for Business Trends

After optimization, the next step is understanding whether a numeric column is symmetric, skewed, heavy-tailed, or multi-segment. This project now includes a distribution-analysis script that computes skewness and kurtosis, saves histogram plus KDE plots, and compares low-value and high-value segments for numeric columns in the processed dataset.

### What It Produces

- Skewness and kurtosis for every numeric column
- Histogram and KDE plots saved under `output/distribution/`
- A segment comparison chart for the first numeric column
- A JSON summary with business-facing interpretation notes

### Why It Matters

If a revenue-like column is heavily right-skewed, the mean can be misleading and the median becomes a better business summary. If the distribution looks bimodal or the low/high segments differ sharply, that usually points to different customer groups or product tiers that should be analyzed separately.

## Features
- Data Validation
- Missing Value Imputation
- Data Profiling
- Distribution Analysis
- Data Dictionary Generation

## Project Structure

```
data/
output/
scripts/
main.py
requirements.txt
README.md
```

## Run the Project

```bash
python scripts/workflow.py
streamlit run main.py
```

## Output Files

- output/intake_report.json
- output/processed_cloud_data.csv
- output/data_profile_report.txt
- output/distribution/distribution_analysis.json
- output/distribution/*.png
- output/data_dictionary.csv

## Analytical SQL Query Optimisation

Analytical queries often become slow because they pull too much data, join too early, and hide intent behind `SELECT *`. The patterns below keep dashboards fast as data grows from thousands to millions of rows.

### Why `SELECT *` Is a Performance Antipattern

`SELECT *` fetches every column from every row, even when you only need a few fields. That increases I/O, network traffic, and memory usage. It can also expose columns that should not be part of the query result.

Use explicit columns instead:

```sql
SELECT
	t.transaction_id,
	t.customer_id,
	t.amount,
	c.customer_name,
	c.country
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE t.year = 2024;
```

### Filter Early Before Joining

When possible, reduce the dataset before performing joins. This keeps intermediate results smaller and makes the query cheaper to execute.

```sql
SELECT t.transaction_id, t.amount, c.customer_name
FROM (
	SELECT transaction_id, customer_id, amount
	FROM transactions
	WHERE transaction_year = 2024
) t
JOIN customers c ON t.customer_id = c.id;
```

### Use CTEs for Readability

Common Table Expressions (CTEs) break complex logic into named steps. That makes queries easier to read, test, and maintain.

```sql
WITH recent_transactions AS (
	SELECT customer_id, amount, transaction_date
	FROM transactions
	WHERE transaction_date >= CURRENT_DATE - INTERVAL 90 DAY
),
customer_summary AS (
	SELECT customer_id, COUNT(*) AS transaction_count, SUM(amount) AS total_spent
	FROM recent_transactions
	GROUP BY customer_id
)
SELECT cs.customer_id, cs.transaction_count, cs.total_spent
FROM customer_summary cs
WHERE cs.total_spent > 10000;
```

### Measure What Changed

Optimization should be validated, not assumed. Use `EXPLAIN` or `EXPLAIN ANALYZE` to inspect execution plans and compare query runtime before and after changes.

### Checklist

- No `SELECT *` in production queries
- Filters applied before joins whenever possible
- Complex logic split into named CTEs
- Column names match aliases clearly
- Query tested against production-scale data
- High-cardinality filter columns indexed when appropriate

### Real-World Impact

A revenue dashboard query can often be reduced from tens of seconds to a few seconds by combining explicit columns, early filtering, and CTEs. The benefit compounds because each optimization reduces the amount of work the database has to do.

### Bonus Resources

- [SQL Query Optimization Techniques](https://use-the-index-luke.com/)
- [CTE Best Practices](https://modern-sql.com/use-case/select-from-cte)
- [Query Execution Plans](https://www.postgresql.org/docs/current/sql-explain.html)
- [Index Strategies](https://en.wikipedia.org/wiki/Database_index)
