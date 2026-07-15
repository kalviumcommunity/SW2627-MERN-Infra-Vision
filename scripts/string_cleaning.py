import json
import os

import pandas as pd

INPUT_FILE = "output/processed_cloud_data.csv"
OUTPUT_FILE = "output/processed_cloud_data.csv"
REPORT_FILE = "output/string_cleaning_report.json"


def clean_text_column(series, lowercase=False, strip=True, remove_special=False, mapping=None):
    """Apply reusable text cleaning rules to a pandas Series."""
    result = series.astype("string").copy()

    if strip:
        result = result.str.strip()

    if remove_special:
        result = result.str.replace(r"[^a-zA-Z0-9 ]", "", regex=True)

    if mapping:
        result = result.replace(mapping)

    if lowercase:
        result = result.str.lower()

    return result.fillna("")


def main():
    df = pd.read_csv(INPUT_FILE)
    cleaned_df = df.copy()

    cloud_service_map = {
        "aws": "AWS",
        "amazon web services": "AWS",
        "azure": "AZURE",
        "microsoft azure": "AZURE",
        "gcp": "GCP",
        "google cloud platform": "GCP",
    }

    if "CloudService" in cleaned_df.columns:
        cleaned_df["CloudService"] = clean_text_column(
            cleaned_df["CloudService"],
            lowercase=False,
            strip=True,
            remove_special=False,
            mapping=cloud_service_map,
        )

    if "ProjectID" in cleaned_df.columns:
        cleaned_df["ProjectID"] = clean_text_column(
            cleaned_df["ProjectID"],
            lowercase=False,
            strip=True,
            remove_special=False,
        )

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "columns_cleaned": [col for col in ["CloudService", "ProjectID"] if col in cleaned_df.columns],
        "sample_values": {
            "before": df[[col for col in ["CloudService", "ProjectID"] if col in df.columns]].head(5).to_dict(orient="records"),
            "after": cleaned_df[[col for col in ["CloudService", "ProjectID"] if col in cleaned_df.columns]].head(5).to_dict(orient="records"),
        },
    }

    os.makedirs("output", exist_ok=True)
    cleaned_df.to_csv(OUTPUT_FILE, index=False)

    with open(REPORT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("STRING CLEANING AND TEXT NORMALISATION")
    print("=" * 60)
    print("Text cleaning completed")
    print(f"Cleaned data saved to: {OUTPUT_FILE}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
