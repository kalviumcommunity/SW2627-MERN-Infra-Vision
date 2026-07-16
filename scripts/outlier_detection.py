import json
import os

import pandas as pd

INPUT_FILE = "output/processed_cloud_data.csv"
OUTPUT_FILE = "output/processed_cloud_data.csv"
REPORT_FILE = "output/outlier_detection_report.json"


def detect_outliers(series):
    cleaned = pd.to_numeric(series, errors="coerce").dropna()
    if cleaned.empty:
        return pd.Series([], dtype=bool), {}, {}

    mean = cleaned.mean()
    std = cleaned.std(ddof=0)
    z_scores = (cleaned - mean) / std if std else pd.Series(0, index=cleaned.index)
    q1 = cleaned.quantile(0.25)
    q3 = cleaned.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    z_mask = (z_scores.abs() > 3)
    iqr_mask = (cleaned < lower_bound) | (cleaned > upper_bound)

    return z_mask, {"q1": float(q1), "q3": float(q3), "iqr": float(iqr), "lower_bound": float(lower_bound), "upper_bound": float(upper_bound)}, {
        "z_outliers": int(z_mask.sum()),
        "iqr_outliers": int(iqr_mask.sum()),
    }


def main():
    df = pd.read_csv(INPUT_FILE)
    transformed_df = df.copy()

    numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    summary = []

    for col in numeric_columns:
        if col in ["BillingID"]:
            continue

        z_mask, bounds, counts = detect_outliers(df[col])
        if not z_mask.empty:
            transformed_df[f"{col}_is_outlier"] = 0
            transformed_df.loc[z_mask.index, f"{col}_is_outlier"] = z_mask.astype(int)
            transformed_df[col] = pd.to_numeric(transformed_df[col], errors="coerce")
            transformed_df[col] = transformed_df[col].clip(lower=bounds.get("lower_bound"), upper=bounds.get("upper_bound"))
            summary.append({
                "column": col,
                "method": "IQR + z-score",
                "action": "capped",
                "outlier_count": counts["iqr_outliers"],
                "reason": "values beyond IQR bounds were capped to preserve rows",
            })

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "summary": summary,
        "numeric_columns": numeric_columns,
    }

    os.makedirs("output", exist_ok=True)
    transformed_df.to_csv(OUTPUT_FILE, index=False)

    with open(REPORT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("OUTLIER DETECTION WITH STATISTICAL METHODS")
    print("=" * 60)
    print("Outlier detection completed")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
