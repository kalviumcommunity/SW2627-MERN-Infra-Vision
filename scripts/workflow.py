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

    print_profile_summary(report)

    save_profile_report(report, PROFILE_JSON)
    save_issues_report(report["issues"], ISSUES_CSV)

    print(f"\nProfiling report saved to: {PROFILE_JSON}")
    print(f"Issues report saved to: {ISSUES_CSV}")

    return report


def main():
    data = ingest_data(INPUT_FILE)
    profile_data(data)
    processed_data = process_data(data)
    output_results(processed_data, OUTPUT_FILE)


if __name__ == "__main__":
    main()