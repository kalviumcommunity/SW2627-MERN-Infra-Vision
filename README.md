# InfraVision

## Project Overview

InfraVision is a data engineering project that validates, cleans, transforms, analyzes, and stores cloud infrastructure billing data. The project follows a complete data engineering workflow—from raw CSV files to a structured SQL database with reusable SQL queries for business analytics.

---

# Features

- Data Validation
- Missing Value Handling
- Data Profiling
- Data Dictionary Generation
- Duplicate Detection & Removal
- String Cleaning & Text Normalization
- Date & Time Transformation
- Outlier Detection
- Data Consistency Validation
- Feature Engineering
- Correlation Analysis
- Threshold-Based Anomaly Detection
- Statistical (Z-Score) Anomaly Detection
- SQLite Database Integration
- SQL Query Automation
- Business Metrics using SQL
- SQL Filtering, Grouping & Aggregation
- SQL Joins & Multi-Table Analysis
- Schema Validation
- Query Reusability using SQL Files

---

# NumPy Vectorized Computation Workflow

This project uses **NumPy vectorization** to perform efficient numerical computations on large datasets. Instead of processing one row at a time using Python loops, vectorized operations process entire arrays simultaneously, resulting in much faster execution.

## Min-Max Normalization

```python
import numpy as np

revenue_array = df["revenue"].values

normalized = (
    revenue_array - revenue_array.min()
) / (
    revenue_array.max() - revenue_array.min()
)

df["revenue_normalized"] = normalized
```

## Z-Score Normalization

```python
revenue_array = df["revenue"].values

z_scores = (
    revenue_array - revenue_array.mean()
) / revenue_array.std()

df["revenue_zscore"] = z_scores
```

---

# Technologies Used

- Python
- Pandas
- NumPy
- SQLite
- SQLAlchemy
- SQL
- JSON
- CSV

---

# Project Structure

```
InfraVision/
│
├── data/
│
├── output/
│
├── queries/
│   ├── high_marks.sql
│   ├── average_marks.sql
│   ├── students_by_branch.sql
│   ├── hostellers.sql
│   ├── where_query.sql
│   ├── having_query.sql
│   ├── where_having_query.sql
│   ├── order_by_query.sql
│   ├── inner_join.sql
│   ├── left_join.sql
│   ├── outer_join.sql
│   └── unmatched.sql
│
├── analytics.db
├── students.csv
├── student.json
├── branches.csv
├── main.py
├── requirements.txt
└── README.md
```

---


 SQL_Views_Aggregation_LayerDesign
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
======main
