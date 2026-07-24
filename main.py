 interactive-plotly-chart-design
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DATA_FILE = BASE_DIR / "output" / "processed_cloud_data.csv"
RAW_DATA_FILE = BASE_DIR / "data" / "raw" / "cloud_data.csv"


@st.cache_data(show_spinner=False)
def load_data():
	data_file = PROCESSED_DATA_FILE if PROCESSED_DATA_FILE.exists() else RAW_DATA_FILE
	if not data_file.exists():
		raise FileNotFoundError(f"No dataset found at {PROCESSED_DATA_FILE} or {RAW_DATA_FILE}")
	return pd.read_csv(data_file), data_file


def main():
	st.set_page_config(page_title="InfraVision Dashboard", layout="wide")
	st.title("InfraVision Interactive Dashboard")
	st.caption("Interactive Plotly charts for cloud infrastructure billing data.")

	df, data_file = load_data()

	st.sidebar.header("Filters")
	services = sorted(df["CloudService"].dropna().unique()) if "CloudService" in df.columns else []
	selected_services = st.sidebar.multiselect("Cloud service", services, default=services)

	projects = sorted(df["ProjectID"].dropna().unique()) if "ProjectID" in df.columns else []
	selected_projects = st.sidebar.multiselect("Project", projects, default=projects)

	filtered = df.copy()
	if selected_services and "CloudService" in filtered.columns:
		filtered = filtered[filtered["CloudService"].isin(selected_services)]
	if selected_projects and "ProjectID" in filtered.columns:
		filtered = filtered[filtered["ProjectID"].isin(selected_projects)]

	metric_columns = [column for column in ["InfrastructureCost", "CPUUsage"] if column in filtered.columns]
	metric = st.sidebar.selectbox("Metric", metric_columns) if metric_columns else None
	group_options = [column for column in ["ProjectID", "CloudService", "BillingID"] if column in filtered.columns]
	group_by = st.sidebar.selectbox("Group by", group_options) if group_options else None

	col1, col2, col3 = st.columns(3)
	col1.metric("Rows", f"{len(filtered):,}")
	col2.metric("Projects", f"{filtered['ProjectID'].nunique():,}" if "ProjectID" in filtered.columns else "N/A")
	col3.metric("Data source", data_file.name)

	if filtered.empty or metric is None or group_by is None:
		st.warning("No rows match the selected filters or required columns are missing.")
		return

	agg = filtered.groupby(group_by, dropna=False)[metric].mean().reset_index()
	bar_chart = px.bar(
		agg,
		x=group_by,
		y=metric,
		color=group_by,
		title=f"Average {metric} by {group_by}",
	)
	bar_chart.update_traces(hovertemplate=f"{group_by}: %{{x}}<br>{metric}: %{{y:,.2f}}<extra></extra>")
	bar_chart.update_layout(showlegend=False, height=520)
	st.plotly_chart(bar_chart, use_container_width=True)

	left, right = st.columns(2)

	with left:
		scatter_x = "CPUUsage" if "CPUUsage" in filtered.columns else filtered.columns[0]
		scatter_y = "InfrastructureCost" if "InfrastructureCost" in filtered.columns else filtered.columns[0]
		scatter = px.scatter(
			filtered,
			x=scatter_x,
			y=scatter_y,
			color="CloudService" if "CloudService" in filtered.columns else None,
			hover_data=[column for column in ["BillingID", "ProjectID"] if column in filtered.columns],
			title="Infrastructure Cost vs CPU Usage",
		)
		scatter.update_traces(marker=dict(size=12, opacity=0.8))
		st.plotly_chart(scatter, use_container_width=True)

	with right:
		st.subheader("Filtered data preview")
		st.dataframe(filtered.head(10), use_container_width=True)

	st.download_button(
		label="Download filtered data as CSV",
		data=filtered.to_csv(index=False).encode("utf-8"),
		file_name="infra_vision_filtered_data.csv",
		mime="text/csv",
	)


if __name__ == "__main__":
	main()
=======
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, inspect

# STEP 1: Read CSV
# ============================

df = pd.read_csv("students.csv")
branch_df = pd.read_csv("branches.csv")
print(branch_df)

print("========== ORIGINAL DATA ==========")
print(df)

# ============================
# STEP 2: Shape
# ============================

print("\n========== SHAPE ==========")
print(df.shape)

# ============================
# STEP 3: Data Types Before Conversion
# ============================

print("\n========== DATA TYPES (BEFORE) ==========")
print(df.dtypes)

# ============================
# STEP 4: First 3 Rows
# ============================

print("\n========== FIRST 3 ROWS ==========")
print(df.head(3))

# ============================
# STEP 5: Filter Students
# ============================

print("\n========== STUDENTS WITH MARKS > 85 ==========")
high_marks = df[df["Marks"] > 85]
print(high_marks)

# ============================
# STEP 6: Average Marks
# ============================

print("\n========== AVERAGE MARKS ==========")
print(df["Marks"].mean())

# ============================
# STEP 7: Average Marks by Branch
# ============================

print("\n========== AVERAGE MARKS BY BRANCH ==========")
print(df.groupby("Branch")["Marks"].mean())

# ============================
# STEP 8: Save Report
# ============================

df.to_csv("report.csv", index=False)
print("\nreport.csv created successfully!")

# ============================
# STEP 9: Read JSON
# ============================

print("\n========== JSON DATA ==========")

json_df = pd.read_json("student.json")
print(json_df)

# ====================================================
# STEP 10: TYPE ENFORCEMENT
# ====================================================

print("\n========== BEFORE TYPE CONVERSION ==========")
print(df.dtypes)

# Convert Joining_Date to datetime
df["Joining_Date"] = pd.to_datetime(
    df["Joining_Date"],
    format="%Y-%m-%d"
)

# Convert Fees_Paid to float
df["Fees_Paid"] = (
    df["Fees_Paid"]
    .str.replace("₹", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float)
)

# Convert Hosteller to Boolean
df["Hosteller"] = df["Hosteller"].astype(bool)

print("\n========== AFTER TYPE CONVERSION ==========")
print(df.dtypes)

print("\n========== UPDATED DATA ==========")
print(df)

# ============================
# STEP 11: Save Updated Report
# ============================

df.to_csv("report.csv", index=False)

print("\nUpdated report.csv created successfully!")

# ============================
# STEP 12: Threshold Alerts
# ============================

print("\n========== THRESHOLD ALERTS ==========")

alerts = []

# Marks Threshold
for index, row in df.iterrows():
    if row["Marks"] < 35:
        alerts.append(f"{row['Name']} has very low marks: {row['Marks']}")
    elif row["Marks"] > 90:
        alerts.append(f"{row['Name']} has exceptionally high marks: {row['Marks']}")

# Fees Threshold
for index, row in df.iterrows():
    if row["Fees_Paid"] < 35000:
        alerts.append(f"{row['Name']} has unusually low fees paid: {row['Fees_Paid']}")

if alerts:
    for alert in alerts:
        print(alert)
else:
    print("No threshold alerts.")


# ============================
# STEP 13: Z-Score Anomaly Detection
# ============================

import numpy as np

print("\n========== ANOMALY DETECTION ==========")

mean = df["Marks"].mean()
std = df["Marks"].std()

df["Z_Score"] = (df["Marks"] - mean) / std

anomalies = df[np.abs(df["Z_Score"]) > 1]

if anomalies.empty:
    print("No anomalies detected.")
else:
    print(anomalies[["Name", "Marks", "Z_Score"]])

# ============================
# STEP 14: Save Anomalies
# ============================

anomalies.to_csv("anomalies.csv", index=False)

print("\nanomalies.csv created successfully!")    

# ============================
# ============================
# STEP 15: Create SQLite Database
# ============================

engine = create_engine("sqlite:///analytics.db")

print("\nDatabase created successfully!")

# ============================
# STEP 16: Store Data in Database
# ============================

df.to_sql(
    "students_cleaned",
    con=engine,
    if_exists="replace",
    index=False
)

print("students_cleaned table created successfully!")

# >>> PASTE THE NEW CODE HERE <<<

branch_df.to_sql(
    "branches",
    con=engine,
    if_exists="replace",
    index=False
)

print("branches table created successfully!")

from sqlalchemy import inspect

inspector = inspect(engine)
print(inspector.get_table_names())

# ============================
# STEP 17: Read Data from SQL
# ============================

query = "SELECT * FROM students_cleaned"

sql_df = pd.read_sql(query, engine)

print("\n========== DATA FROM DATABASE ==========")
print(sql_df)
# ============================
# STEP 18: SQL Query
# ============================

query = """
SELECT *
FROM students_cleaned
WHERE Marks > 85
"""

high_marks = pd.read_sql(query, engine)

print("\n========== STUDENTS WITH MARKS > 85 ==========")
print(high_marks)

# ============================
# STEP 19: Validate Schema
# ============================

inspector = inspect(engine)

columns = inspector.get_columns("students_cleaned")

print("\n========== DATABASE SCHEMA ==========")

for column in columns:
    print(f"{column['name']} : {column['type']}")

# ============================
# STEP 20: Execute SQL Files
# ============================

queries = [
    "queries/high_marks.sql",
    "queries/average_marks.sql",
    "queries/students_by_branch.sql",
    "queries/hostellers.sql"
]

for file in queries:
    print("\n==============================")
    print(file)
    print("==============================")

    with open(file, "r") as f:
        query = f.read()

    result = pd.read_sql(query, engine)

    print(result)    

# ============================
# STEP 21: SQL Filtering & Aggregation
# ============================

sql_files = [
    "queries/where_query.sql",
    "queries/having_query.sql",
    "queries/where_having_query.sql",
    "queries/order_by_query.sql"
]

for file in sql_files:
    print("\n==============================")
    print(file)
    print("==============================")

    with open(file, "r") as f:
        query = f.read()

    result = pd.read_sql(query, engine)

    print(result)    

# ============================
# STEP 20: Execute JOIN Queries
# ============================

join_files = [
    "queries/inner_join.sql",
    "queries/left_join.sql",
    "queries/outer_join.sql",
    "queries/unmatched.sql"
]

for file in join_files:
    print("\n==============================")
    print(file)
    print("==============================")

    with open(file, "r") as f:
        query = f.read()

    result = pd.read_sql(query, engine)

    print(result)    
# ============================
# STEP 21: Row Count Validation
# ============================

print("\n========== ROW COUNT VALIDATION ==========")

print("Students Table :", len(df))
print("Branches Table :", len(branch_df))

joined = pd.read_sql("""
SELECT *
FROM students_cleaned s
LEFT JOIN branches b
ON s.Branch = b.Branch
""", engine)

print("Joined Table :", len(joined))
 main
