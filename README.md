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

