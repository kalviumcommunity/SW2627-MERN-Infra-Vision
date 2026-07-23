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

## SQL Views & Aggregation Layer Design

When the same metric is recomputed in dashboards, notebooks, and scripts, definitions drift. A clean data layer solves that by defining metrics once in SQL views and serving expensive summaries from pre-aggregated tables.

### Why This Matters

Without a shared layer, teams end up with conflicting definitions of revenue, activity, churn, and other business metrics. One dashboard includes refunds, another excludes them, and nobody can explain which number is correct. The goal is a single source of truth that every consumer uses.

### SQL Views as the Single Source of Truth

A SQL view behaves like a saved query. It does not store data; it stores logic. That means every dashboard or notebook querying the view uses the same metric definition.

Example view:

```sql
CREATE VIEW vw_active_customers AS
SELECT
	c.customer_id,
	c.customer_name,
	c.segment,
	COUNT(DISTINCT o.order_id) AS order_count_30d,
	SUM(o.order_amount) AS revenue_30d,
	MAX(o.order_date) AS last_order_date,
	DATEDIFF(CURRENT_DATE, MAX(o.order_date)) AS days_since_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
	AND o.order_date >= CURRENT_DATE - INTERVAL 30 DAY
WHERE c.deleted_at IS NULL
GROUP BY c.customer_id, c.customer_name, c.segment;
```

Use views to prevent metric drift:

- Define each shared metric once.
- Query the view everywhere instead of rewriting the logic.
- Update the view definition when the business rule changes.

### Naming Conventions

Use a simple prefix scheme so the data layer stays readable:

- `vw_` for views, such as `vw_monthly_revenue` or `vw_product_performance`
- One view per business concept, not one massive catch-all view
- Keep each view focused, maintainable, and easy to test

Avoid the anti-pattern of a single `vw_everything` object that joins too many tables and returns too many columns. Small, specific views are easier to reason about and safer to change.

### Pre-Aggregated Tables for Performance

Views are ideal for reusable logic, but they re-run their underlying query on each request. For large joins or dashboard workloads that refresh often, pre-aggregated tables are a better fit.

Example aggregated table:

```sql
CREATE TABLE agg_daily_revenue (
	aggregation_date DATE,
	product_line VARCHAR(100),
	total_revenue NUMERIC(12,2),
	order_count INTEGER,
	avg_order_value NUMERIC(10,2),
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO agg_daily_revenue
SELECT
	DATE(o.order_date) AS aggregation_date,
	p.product_line,
	SUM(o.order_amount) AS total_revenue,
	COUNT(DISTINCT o.order_id) AS order_count,
	AVG(o.order_amount) AS avg_order_value,
	CURRENT_TIMESTAMP AS updated_at
FROM orders o
JOIN products p ON o.product_id = p.id
GROUP BY DATE(o.order_date), p.product_line;
```

Use the `agg_` prefix for pre-computed tables. A naming pattern like `agg_daily_revenue`, `agg_hourly_metrics`, or `agg_monthly_churn` makes it clear that the data is summarized and refreshed on a schedule.

Always include an `updated_at` column so downstream users can see how fresh the data is.

### Refresh Strategy

Choose the refresh pattern based on volume and freshness requirements:

- Full refresh: truncate and reload, which is simple but slower for large tables
- Incremental refresh: only process new or changed data, which is faster but more complex
- Append-only: add new rows without rewriting historical data, which is efficient but needs careful duplicate handling

### Version Control for SQL Definitions

Store view and aggregation definitions as `.sql` files in the repository. That makes metric changes reviewable, traceable, and easy to roll back.

Suggested layout:

```text
database/views/vw_active_customers.sql
database/aggregations/agg_daily_revenue.sql
```

At the top of each file, document the purpose, the business metric it defines, who uses it, and the important column meanings.

### Clean Data Layer Checklist

- Every shared metric is defined once in a SQL view with the `vw_` prefix
- Expensive summaries are stored in `agg_` tables with `updated_at`
- Dashboards query views and aggregated tables instead of raw tables directly
- SQL definitions live in version control as `.sql` files with comments
- Refresh schedules are documented and automated
- Naming conventions are captured in a team conventions file

### Key Takeaway

If a metric matters to multiple consumers, define it once in a view. If the computation is too expensive to run live, pre-aggregate it into a table. That combination keeps dashboards trustworthy and fast.

## SQL-Based Insight Validation

When a metric exists in both Python and SQL, the two layers must agree. If Python says 1,000 active users and SQL says 1,200, you have computation drift: one layer is wrong, or both are using different rules.

### Why Validation Matters

Metrics often drift because teams define the same concept in different places. A churn rate in SQL may include one set of conditions while a Python notebook uses another. Without validation, both numbers can look plausible while quietly disagreeing.

### Common Drift Scenarios

Typical causes of disagreement include:

- Date handling differences between SQL date types and Python datetime objects
- NULL versus NaN behavior in joins and calculations
- Rounding differences between database logic and application logic
- Timezone mismatches between UTC and local time
- String case sensitivity differences across systems

### A Simple Validation Workflow

Validate the same metric in both layers and compare the outputs side by side:

1. Compute the metric in SQL.
2. Compute the same metric in Python.
3. Compare the results and measure the difference.
4. Investigate any mismatch that exceeds the allowed tolerance.
5. Fix the incorrect layer and validate again.

Example tolerance check:

```python
sql_value = 1200
python_value = 1000
tolerance = 0.01

if abs(sql_value - python_value) > tolerance:
	print("Validation failed: metric drift detected")
else:
	print("Validation passed")
```

### How To Investigate Differences

When SQL and Python disagree, narrow the scope first:

- Check whether the mismatch affects one row or all rows
- Trace one specific record manually from raw data to final metric
- Identify which layer matches the manual calculation
- Correct the wrong rule and document why it changed

If the issue is isolated, it is often a data quality problem. If the issue is systematic, it usually points to a logic mismatch.

### Automating Validation

Validation should run on a schedule, not only during debugging. Store validation outputs in a table or report, and alert the team when a metric crosses its threshold.

Good automation practices include:

- Run validation daily or after each pipeline refresh
- Store results with timestamps so drift can be tracked over time
- Send alerts when discrepancies exceed tolerance
- Document expected differences so known exceptions do not become false alarms

### Documentation Rules

Every validated metric should have a written definition of what matches, what can differ, and why. That documentation should explain any intentional mismatch, such as SQL including refunds while Python excludes them by design.

### Validation Checklist

- Shared metrics are computed the same way in SQL and Python
- Differences are measured against a clear tolerance
- Manual tracing is used to resolve disagreements
- Alerts exist for unexpected drift
- Expected exceptions are documented in version control

### Key Takeaway

If a metric matters, validate it across layers before anyone uses it for reporting. Cross-checking SQL and Python is how you catch silent drift before it reaches dashboards and decision-makers.
