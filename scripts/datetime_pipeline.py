import json
import os

import pandas as pd

INPUT_FILE = "output/processed_cloud_data.csv"
OUTPUT_FILE = "output/processed_cloud_data.csv"
REPORT_FILE = "output/datetime_pipeline_report.json"


def parse_datetime_column(series):
    return pd.to_datetime(series, errors="coerce")


def main():
    df = pd.read_csv(INPUT_FILE)
    transformed_df = df.copy()

    if "TransactionDate" in transformed_df.columns:
        transformed_df["TransactionDate"] = parse_datetime_column(transformed_df["TransactionDate"])
        transformed_df["day_of_week"] = transformed_df["TransactionDate"].dt.day_name()
        transformed_df["dow_numeric"] = transformed_df["TransactionDate"].dt.dayofweek
        transformed_df["hour"] = transformed_df["TransactionDate"].dt.hour
        transformed_df["week_num"] = transformed_df["TransactionDate"].dt.isocalendar().week
        transformed_df["month"] = transformed_df["TransactionDate"].dt.month
        transformed_df["quarter"] = transformed_df["TransactionDate"].dt.quarter
        transformed_df["days_since_event"] = (
            pd.Timestamp.now().normalize() - transformed_df["TransactionDate"].dt.normalize()
        ).dt.days

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "parsed_columns": [col for col in ["TransactionDate"] if col in transformed_df.columns],
        "sample": transformed_df[[col for col in ["TransactionDate", "day_of_week", "hour", "week_num", "month", "quarter", "days_since_event"] if col in transformed_df.columns]].head(5).to_dict(orient="records"),
    }

    os.makedirs("output", exist_ok=True)
    transformed_df.to_csv(OUTPUT_FILE, index=False)

    with open(REPORT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("DATE AND TIME TRANSFORMATION PIPELINE")
    print("=" * 60)
    print("Datetime parsing and feature extraction completed")
    print(f"Transformed data saved to: {OUTPUT_FILE}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
