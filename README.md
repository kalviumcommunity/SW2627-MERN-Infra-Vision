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

## Interactive Plotly Chart Design

Interactive charts let stakeholders explore findings themselves instead of waiting for a new export every time a question comes up. Plotly is a strong fit when you want hover tooltips, dropdown filters, zoom, pan, and date range selection to be part of the default experience.

### The Real Scenario

An analyst builds a revenue chart in matplotlib. A stakeholder notices a spike in March and asks for the exact value, then asks to filter by Q1, then asks to compare it to last year. Each answer requires a new chart or a manual lookup. The analyst ends up acting like a chart-generation service instead of an analyst.

The fix is to build the chart in Plotly. Hover reveals the exact value, zoom and pan let the user inspect the shape of the trend, and dropdown filters let them switch views instantly. The chart answers the first question and the follow-up questions without rebuilding anything.

### Hover Tooltips: Detail on Demand

Hover tooltips show detailed values when the user points at a data mark. That keeps the chart clean while still exposing exact values, dates, and supporting metrics on demand.

```python
import plotly.graph_objects as go

fig = go.Figure(data=go.Scatter(
	x=df['date'],
	y=df['revenue'],
	mode='lines+markers',
	hovertemplate=(
		'<b>%{x|%Y-%m-%d}</b><br>'
		'Revenue: $%{y:,.0f}<br>'
		'<extra></extra>'
	),
	line=dict(color='#1f77b4', width=2),
	marker=dict(size=8)
))

fig.update_layout(
	title='Daily Revenue Trend',
	xaxis_title='Date',
	yaxis_title='Revenue ($)',
	hovermode='x unified',
	height=500
)
```

The `hovertemplate` controls exactly what appears. `%{x|%Y-%m-%d}` formats the date, `%{y:,.0f}` formats the number, and `<extra></extra>` removes the default trace-name box.

### Dropdown Filters: Multiple Views, One Chart

A dropdown can switch between revenue, profit, and order count without reloading data. All traces are loaded once, and the menu only changes which trace is visible.

```python
fig = go.Figure()

fig.add_trace(go.Bar(x=products, y=revenue, name='Revenue',
					 marker=dict(color='#1f77b4'), visible=True))
fig.add_trace(go.Bar(x=products, y=profit, name='Profit',
					 marker=dict(color='#ff7f0e'), visible=False))
fig.add_trace(go.Bar(x=products, y=orders, name='Orders',
					 marker=dict(color='#2ca02c'), visible=False))

fig.update_layout(
	updatemenus=[dict(
		active=0,
		buttons=[
			dict(label='Revenue', method='update',
				 args=[{'visible': [True, False, False]},
					   {'title': 'Revenue by Product'}]),
			dict(label='Profit', method='update',
				 args=[{'visible': [False, True, False]},
					   {'title': 'Profit by Product'}]),
			dict(label='Orders', method='update',
				 args=[{'visible': [False, False, True]},
					   {'title': 'Orders by Product'}])
		]
	)]
)
```

Each button updates the visible traces and the chart title. Because the data is already in the browser, the switch is instant.

### Zoom, Pan, and Date Range Selection

Plotly charts include zoom and pan by default. Users can drag to zoom into a region, double-click to reset the view, and use the built-in date controls for common time windows.

```python
fig.update_xaxes(
	rangeselector=dict(
		buttons=list([
			dict(count=1, label='1M', step='month', stepmode='backward'),
			dict(count=3, label='3M', step='month', stepmode='backward'),
			dict(count=6, label='6M', step='month', stepmode='backward'),
			dict(count=1, label='YTD', step='year', stepmode='todate'),
			dict(step='all', label='All')
		])
	),
	rangeslider=dict(visible=True)
)
```

The range selector makes it easy to jump to common periods such as last month, last quarter, or year-to-date. The range slider gives the user a quick way to choose any custom window.

### Integrating Plotly With Streamlit

Plotly charts embed cleanly in Streamlit with `st.plotly_chart`, preserving hover, zoom, and pan interactions. That makes it easy to build a dashboard with sidebar filters and interactive charts in one application.

```python
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout='wide')
st.title('Sales Analytics Dashboard')

fig = go.Figure(data=go.Scatter(
	x=df['date'],
	y=df['revenue'],
	mode='lines+markers',
	hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
))
fig.update_layout(title='Revenue Trend', height=500)

st.plotly_chart(fig, use_container_width=True)

min_date = st.sidebar.date_input('Start Date')
max_date = st.sidebar.date_input('End Date')
```

Plotly charts can also be exported as standalone HTML with `fig.write_html('chart.html')`, which is useful when you want to share an interactive chart without needing Python or a live app.

### Key Takeaway

Use Plotly when the chart needs to answer follow-up questions without regeneration. Hover tooltips, dropdown filters, and built-in navigation controls make the chart interactive enough for exploration while still staying simple to share.

### Bonus Resources

- [Plotly Python Documentation](https://plotly.com/python/)
- [Plotly Hover Text and Formatting](https://plotly.com/python/hover-text-and-formatting/)
- [Streamlit Plotly Integration](https://docs.streamlit.io/library/api-reference/charts/st.plotly_chart)
- [Plotly Buttons and Dropdowns](https://plotly.com/python/dropdowns/)
- [Dash by Plotly](https://dash.plotly.com/)
