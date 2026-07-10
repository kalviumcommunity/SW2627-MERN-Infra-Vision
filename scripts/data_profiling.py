import pandas as pd
import os

# Load cleaned dataset
df = pd.read_csv("output/processed_cloud_data.csv")

print("=" * 60)
print("DATA PROFILING REPORT")
print("=" * 60)

# Dataset Shape
print("\nDataset Shape")
print(df.shape)

# Data Types
print("\nData Types")
print(df.dtypes)

# Missing Values
print("\nMissing Values")
print(df.isnull().sum())

# Summary Statistics
print("\nSummary Statistics")
print(df.describe())

# Unique Values
print("\nUnique Values")

for col in df.columns:
    print(f"{col}: {df[col].nunique()}")

# Duplicate Rows
print("\nDuplicate Rows")
print(df.duplicated().sum())

# Save report
os.makedirs("output", exist_ok=True)

with open("output/data_profile_report.txt", "w") as file:
    file.write("DATA PROFILING REPORT\n")
    file.write("=" * 50 + "\n\n")
    file.write(f"Dataset Shape: {df.shape}\n\n")
    file.write("Data Types:\n")
    file.write(str(df.dtypes))
    file.write("\n\nMissing Values:\n")
    file.write(str(df.isnull().sum()))
    file.write("\n\nSummary Statistics:\n")
    file.write(str(df.describe()))
    file.write("\n\nDuplicate Rows:\n")
    file.write(str(df.duplicated().sum()))

print("\nProfile report saved to output/data_profile_report.txt")