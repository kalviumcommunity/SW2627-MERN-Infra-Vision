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
 business-visualisation-principles

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

## Business Visualisation Principles

Dashboard architecture is planned. The data layer is clean. The remaining task is to turn numbers into pictures that people understand instantly.

Every chart type exists for a reason. Bar charts compare categories, line charts show trends, histograms reveal distributions, and scatter plots expose correlations. Choosing the wrong chart type makes the audience misread the data.

### The Real Scenario

An analyst presents quarterly revenue as a pie chart. Six product lines appear as slices. The CEO asks which product grew the most, but a pie chart shows proportion, not change over time. The analyst switches to a table of numbers. The meeting stalls while everyone scans rows and columns. The insight is buried and the decision is delayed.

The fix is to match the chart type to the data relationship. Use a bar chart for comparison across categories, a line chart for trends over time, a histogram for distributions, a scatter plot for correlations, and a stacked bar chart for composition. Add complete labels and use a consistent colour palette so the audience can read the insight in seconds.

### Choosing the Right Chart Type

#### Bar Chart

Use bar charts for comparison across categories such as revenue by product line, sales by region, or headcount by department. Horizontal bars work better when labels are long. Vertical bars work better when comparing only a few items.

#### Line Chart

Use line charts when a metric changes over a continuous axis, usually time. Revenue per month, active users per week, and churn rate per quarter all fit this pattern. Never use a line chart for categorical data.

#### Histogram

Use histograms to show the distribution of values such as order value ranges, customer age, or response time. They reveal skew, outliers, and bimodal patterns that averages hide.

#### Scatter Plot

Use scatter plots to explore whether two variables are related, such as marketing spend versus revenue or price versus demand. Each dot is one observation, and clusters or outliers become easy to see.

#### Stacked Bar

Use stacked bars when showing composition and part-to-whole relationships, such as revenue by quarter stacked by product or headcount by year stacked by department. Keep the number of segments small so the chart stays readable.

### Complete Labelling

A chart without labels is just a picture without meaning. Every chart needs a title that describes what the chart shows, not what it is. It also needs labelled axes with units, a legend for multi-series charts, and data labels when the chart is small enough to support them.

Format numbers for human readability. Do not display 5200000 on an axis when $5.2M communicates the same meaning faster. Format dates as Jan 2024 for monthly charts instead of raw ISO dates.

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(products, revenue, color='#1f77b4')
ax.set_xlabel('Revenue ($)', fontsize=12)
ax.set_ylabel('Product Line', fontsize=12)
ax.set_title('Q4 Revenue by Product Line', fontsize=14, fontweight='bold')

ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))

plt.tight_layout()
plt.savefig('output/revenue_by_product.png', dpi=300, bbox_inches='tight')
```

### Consistent Colour Palette and Accessibility

If Product A is blue in one chart, it should stay blue in every chart on the dashboard. Consistent colour creates a visual language and prevents the viewer from re-learning the legend on every screen.

Define the palette once and reuse it everywhere.

```python
PALETTE = {
	'primary': '#1f77b4',
	'secondary': '#ff7f0e',
	'success': '#2ca02c',
	'danger': '#d62728',
	'neutral': '#7f7f7f'
}

CHART_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

ax.bar(categories, values, color=CHART_COLORS[:len(categories)])
```

Colour blindness accessibility matters too. Never rely on colour alone to convey meaning. Pair colour with shape, pattern, or text labels, and check whether the chart still works in greyscale.

### Annotations

Annotations turn charts into insight-delivery tools. Use them to highlight anomalies, thresholds, and events that explain the pattern.

```python
ax.annotate(
	'Peak Sales\n($6.2M)',
	xy=(peak_date, peak_value),
	xytext=(peak_date, peak_value + 500000),
	arrowprops=dict(arrowstyle='->', color='red', lw=2),
	fontsize=11,
	ha='center',
	bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7)
)

ax.axhline(y=5000000, color='green', linestyle='--', linewidth=2, label='Target')
ax.legend()
```

Reference lines add context. A target line transforms a chart from "here is what happened" into "here is what happened relative to what should have happened." That context is what turns data into insight.

### Bonus Resources

- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Data-to-Viz](https://www.data-to-viz.com/)
- [Colour Blindness Simulator](https://www.color-blindness.com/coblis-color-blindness-simulator/)
- [Edward Tufte's Visual Display of Quantitative Information](https://www.edwardtufte.com/tufte/books_vdqi)
=======
======main
 main
