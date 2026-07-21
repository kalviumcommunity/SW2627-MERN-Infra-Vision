import pandas as pd
import numpy as np
from sqlalchemy import create_engine, inspect

# STEP 1: Read CSV
# ============================

df = pd.read_csv("students.csv")

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