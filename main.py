import pandas as pd

# ============================
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