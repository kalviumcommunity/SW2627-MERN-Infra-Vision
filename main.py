import pandas as pd

# -----------------------------
# STEP 1: Read CSV
# -----------------------------
df = pd.read_csv("students.csv")

print("Original Data")
print(df)

# -----------------------------
# STEP 2: Show Shape
# -----------------------------
print("\nShape:")
print(df.shape)

# -----------------------------
# STEP 3: Show Data Types
# -----------------------------
print("\nData Types:")
print(df.dtypes)

# -----------------------------
# STEP 4: First 3 Rows
# -----------------------------
print("\nFirst 3 Rows")
print(df.head(3))

# -----------------------------
# STEP 5: Filter Students
# -----------------------------
high_marks = df[df["Marks"] > 85]

print("\nStudents with Marks > 85")
print(high_marks)

# -----------------------------
# STEP 6: Average Marks
# -----------------------------
average = df["Marks"].mean()

print("\nAverage Marks")
print(average)

# -----------------------------
# STEP 7: Group By Branch
# -----------------------------
branch_average = df.groupby("Branch")["Marks"].mean()

print("\nAverage Marks by Branch")
print(branch_average)

# -----------------------------
# STEP 8: Save High Marks Report
# -----------------------------
high_marks.to_csv("report.csv", index=False)

print("\nreport.csv created successfully!")

# -----------------------------
# STEP 9: Read JSON
# -----------------------------
json_df = pd.read_json("students.json")

print("\nJSON Data")
print(json_df)

# -----------------------------
# STEP 10: Ingestion Report
# -----------------------------
print("\n========== INGESTION REPORT ==========")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\nColumn Types")
print(df.dtypes)

print("\nFirst 3 Rows")
print(df.head(3))