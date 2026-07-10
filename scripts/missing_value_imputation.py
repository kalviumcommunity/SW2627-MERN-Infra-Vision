import pandas as pd
import os

# -------------------------------
# Load Dataset
# -------------------------------
df = pd.read_csv("data/raw/cloud_data.csv")

print("\n===== ORIGINAL DATASET =====")
print(df)

# -------------------------------
# Add Missing Values (For Testing)
# Remove these lines if your CSV
# already contains missing values
# -------------------------------

df.loc[1, "InfrastructureCost"] = None
df.loc[2, "CloudService"] = None
df.loc[3, "CPUUsage"] = None

# -------------------------------
# Missing Values Before
# -------------------------------

print("\n===== BEFORE IMPUTATION =====")
print(df.isnull().sum())

# -------------------------------
# Drop Missing BillingID
# -------------------------------

df = df.dropna(subset=["BillingID"])

# -------------------------------
# InfrastructureCost -> Median
# -------------------------------

median_cost = df["InfrastructureCost"].median()

df["InfrastructureCost"] = df["InfrastructureCost"].fillna(median_cost)

print(f"\nInfrastructureCost filled with Median = {median_cost}")

# -------------------------------
# CPUUsage -> Median
# -------------------------------

median_cpu = df["CPUUsage"].median()

df["CPUUsage"] = df["CPUUsage"].fillna(median_cpu)

print(f"CPUUsage filled with Median = {median_cpu}")

# -------------------------------
# CloudService -> Mode
# -------------------------------

mode_service = df["CloudService"].mode().iloc[0]

df["CloudService"] = df["CloudService"].fillna(mode_service)

print(f"CloudService filled with Mode = {mode_service}")

# -------------------------------
# Missing Values After
# -------------------------------

print("\n===== AFTER IMPUTATION =====")
print(df.isnull().sum())

# -------------------------------
# Save Dataset
# -------------------------------

os.makedirs("output", exist_ok=True)

df.to_csv("output/processed_cloud_data.csv", index=False)

print("\nDataset saved successfully!")

print("\n===== FINAL DATASET =====")
print(df)