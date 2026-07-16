import os
import pandas as pd

try:
    from .common import PROFILE_REPORT_FILE, PROCESSED_DATA_FILE, ensure_output_dir, load_csv
except ImportError:
    from common import PROFILE_REPORT_FILE, PROCESSED_DATA_FILE, ensure_output_dir, load_csv

def build_profile_report(df):
    lines = [
        "DATA PROFILING REPORT",
        "=" * 50,
        "",
        f"Dataset Shape: {df.shape}",
        "",
        "Data Types:",
        str(df.dtypes),
        "",
        "Missing Values:",
        str(df.isnull().sum()),
        "",
        "Summary Statistics:",
        str(df.describe()),
        "",
        "Duplicate Rows:",
        str(df.duplicated().sum()),
    ]
    return "\n".join(lines)


def main():
    if not PROCESSED_DATA_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {PROCESSED_DATA_FILE}")

    df = load_csv(PROCESSED_DATA_FILE)

    print("=" * 60)
    print("DATA PROFILING REPORT")
    print("=" * 60)
    print("\nDataset Shape")
    print(df.shape)
    print("\nData Types")
    print(df.dtypes)
    print("\nMissing Values")
    print(df.isnull().sum())
    print("\nSummary Statistics")
    print(df.describe())
    print("\nUnique Values")

    for col in df.columns:
        print(f"{col}: {df[col].nunique()}")

    print("\nDuplicate Rows")
    print(df.duplicated().sum())

    ensure_output_dir()
    PROFILE_REPORT_FILE.write_text(build_profile_report(df), encoding="utf-8")

    print(f"\nProfile report saved to {PROFILE_REPORT_FILE}")


if __name__ == "__main__":
    main()