import os
import pandas as pd

try:
	from .common import PROCESSED_DATA_FILE, RAW_DATA_FILE, ensure_output_dir, load_csv
except ImportError:
	from common import PROCESSED_DATA_FILE, RAW_DATA_FILE, ensure_output_dir, load_csv

def impute_missing_values(df):
	cleaned = df.copy()

	cleaned = cleaned.dropna(subset=["BillingID"])

	if "InfrastructureCost" in cleaned.columns:
		cleaned["InfrastructureCost"] = cleaned["InfrastructureCost"].fillna(cleaned["InfrastructureCost"].median())

	if "CPUUsage" in cleaned.columns:
		cleaned["CPUUsage"] = cleaned["CPUUsage"].fillna(cleaned["CPUUsage"].median())

	if "CloudService" in cleaned.columns and not cleaned["CloudService"].mode().empty:
		cleaned["CloudService"] = cleaned["CloudService"].fillna(cleaned["CloudService"].mode().iloc[0])

	return cleaned


def main():
	if not RAW_DATA_FILE.exists():
		raise FileNotFoundError(f"Input file not found: {RAW_DATA_FILE}")

	df = load_csv(RAW_DATA_FILE)

	print("\n===== ORIGINAL DATASET =====")
	print(df)
	print("\n===== BEFORE IMPUTATION =====")
	print(df.isnull().sum())

	cleaned = impute_missing_values(df)

	print("\n===== AFTER IMPUTATION =====")
	print(cleaned.isnull().sum())

	ensure_output_dir()
	cleaned.to_csv(PROCESSED_DATA_FILE, index=False)

	print("\nDataset saved successfully!")
	print("\n===== FINAL DATASET =====")
	print(cleaned)


if __name__ == "__main__":
	main()