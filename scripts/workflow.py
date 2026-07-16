 GroupBy-Aggregation-nd-segment-insights
import pandas as pd

from profiling import (
    profile_dataframe,
    save_profile_report,
    save_issues_report,
    print_profile_summary,
)

INPUT_FILE = "data/raw/cloud_data.csv"
OUTPUT_FILE = "output/processed_cloud_data.csv"
PROFILE_JSON = "output/profile_report.json"
ISSUES_CSV = "output/profile_issues.csv"


def ingest_data(filepath):
    """
    Read cloud operational data from a CSV file.
    """
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} records")
    return df


def process_data(df):
    """
    Clean the dataset.
    """
    df = df.drop_duplicates()
    df = df.fillna(0)
    print("Data cleaned successfully")
    return df


def output_results(df, filepath):
    """
    Save processed data to a CSV file.
    """
    df.to_csv(filepath, index=False)
    print(f"Processed data saved to {filepath}")


def profile_data(df):
    """
    Run profiling and generate data quality reports.
    """
    report = profile_dataframe(df)

    # Display summary in terminal
    print_profile_summary(report)

    # Save reports
    save_profile_report(report, PROFILE_JSON)
    save_issues_report(report["issues"], ISSUES_CSV)

    print(f"\nProfiling report saved to: {PROFILE_JSON}")
    print(f"Issues report saved to: {ISSUES_CSV}")

    return report

def segment_analysis(df):
    """
    Perform GroupBy and aggregation analysis.
    """

    print("\n========== SEGMENT ANALYSIS ==========")

    # Average CPU Usage by Cloud Service
    print("\nAverage CPU Usage by Cloud Service")
    print(df.groupby("CloudService")["CPUUsage"].mean())

    # Total Infrastructure Cost by Cloud Service
    print("\nTotal Infrastructure Cost by Cloud Service")
    print(df.groupby("CloudService")["InfrastructureCost"].sum())

    # Count Projects by Cloud Service
    print("\nProject Count by Cloud Service")
    print(df.groupby("CloudService")["ProjectID"].count())

    # Multiple Aggregations
    summary = df.groupby("CloudService").agg({
        "InfrastructureCost": "sum",
        "CPUUsage": "mean",
        "ProjectID": "count"
    })

    summary.columns = [
        "Total_Cost",
        "Average_CPU",
        "Project_Count"
    ]

    print("\nCloud Service Summary")
    print(summary)

    # Ranking
    summary["CPU_Rank"] = summary["Average_CPU"].rank(ascending=False)

    print("\nRanked Summary")
    print(summary.sort_values("Average_CPU", ascending=False))

    # Group by two columns
    print("\nCloud Service and Project Analysis")
    print(df.groupby(["CloudService", "ProjectID"])["InfrastructureCost"].sum())

    # Pivot Table
    pivot = pd.pivot_table(
        df,
        values="InfrastructureCost",
        index="CloudService",
        columns="ProjectID",
        aggfunc="sum"
    )

    print("\nPivot Table")
    print(pivot)

    # Transform
    df["Avg_CPU_By_Service"] = df.groupby(
        "CloudService"
    )["CPUUsage"].transform("mean")

    print("\nDataset with Avg CPU")
    print(df)

    # Apply
    print("\nHighest Infrastructure Cost")
    print(df.groupby("CloudService")["InfrastructureCost"].apply(lambda x: x.max()))


def main():
    # Step 1: Load the dataset
    data = ingest_data(INPUT_FILE)

    # Step 2: Profile the raw dataset before cleaning
    profile_data(data)

    # Step 3: Clean the dataset
    processed_data = process_data(data)

   processed_data = process_data(data)

   # Step 4: Segment Analysis
segment_analysis(processed_data)

# Step 5: Save cleaned dataset
output_results(processed_data, OUTPUT_FILE)


if __name__ == "__main__":
    main()
=======
from pathlib import Path
import subprocess
import sys

print("=" * 60)
print("INFRAVISION DATA PIPELINE")
print("=" * 60)

BASE_DIR = Path(__file__).resolve().parent.parent

initial_steps = [
    ("Step 1", "Data Validation", [sys.executable, "-m", "scripts.validate_data"]),
    ("Step 2", "Missing Value Imputation", [sys.executable, "-m", "scripts.missing_value_imputation"]),
    ("Step 3", "NumPy Vectorized Computation", [sys.executable, "-m", "scripts.vectorized_computation"]),
    ("Step 4", "Data Profiling", [sys.executable, "-m", "scripts.data_profiling"]),
    ("Step 5", "Data Dictionary", [sys.executable, "-m", "scripts.data_dictionary"]),
]

for label, title, command in initial_steps:
    print(f"\n{label} : {title}")
    subprocess.run(command, cwd=str(BASE_DIR), check=True)

extra_steps = [
    ("Step 6", "String Cleaning", [sys.executable, str(BASE_DIR / "scripts" / "string_cleaning.py")]),
    ("Step 7", "Date & Time Transformation", [sys.executable, str(BASE_DIR / "scripts" / "datetime_pipeline.py")]),
    ("Step 8", "Outlier Detection", [sys.executable, str(BASE_DIR / "scripts" / "outlier_detection.py")]),
    ("Step 9", "Validation Rules", [sys.executable, str(BASE_DIR / "scripts" / "validate_data_rules.py")]),
    ("Step 10", "Merge Validation", [sys.executable, str(BASE_DIR / "scripts" / "merge_validation.py")]),
    ("Step 11", "Feature Engineering", [sys.executable, str(BASE_DIR / "scripts" / "feature_engineering.py")]),
    ("Step 12", "Correlation Analysis", [sys.executable, str(BASE_DIR / "scripts" / "correlation_analysis.py")]),
    ("Step 13", "Deduplication", [sys.executable, str(BASE_DIR / "scripts" / "deduplication.py")]),
]

for label, title, command in extra_steps:
    print(f"\n{label} : {title}")
    subprocess.run(command, cwd=str(BASE_DIR), check=True)

print("\nPipeline Completed Successfully!")
 main
