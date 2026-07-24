import json
import os

import pandas as pd

INPUT_FILE = "output/feature_engineered_data.csv"
OUTPUT_FILE = "output/correlation_analysis_report.json"


def analyze_correlations(df: pd.DataFrame):
    numeric_df = df.select_dtypes(include=["number"]).copy()

    if numeric_df.shape[1] < 2:
        return {}, {"message": "Not enough numeric columns for correlation analysis."}

    pearson_corr = numeric_df.corr(method="pearson")
    spearman_corr = numeric_df.corr(method="spearman")

    strong_pairs = []
    for col1 in pearson_corr.columns:
        for col2 in pearson_corr.columns:
            if col1 >= col2:
                continue
            corr_value = pearson_corr.loc[col1, col2]
            if abs(corr_value) > 0.7:
                strong_pairs.append({"column_1": col1, "column_2": col2, "pearson": round(float(corr_value), 3)})

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "numeric_columns": list(numeric_df.columns),
        "strong_pairs": strong_pairs[:10],
        "pearson_summary": {
            "shape": list(pearson_corr.shape),
            "columns": list(pearson_corr.columns),
        },
        "spearman_summary": {
            "shape": list(spearman_corr.shape),
            "columns": list(spearman_corr.columns),
        },
        "interpretation": "Strong correlations indicate that variables move together; they do not prove causation.",
    }

    return report, {}


def main():
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    else:
        df = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 6, 8], "z": [5, 3, 2, 1]})

    report, _ = analyze_correlations(df)

    os.makedirs("output", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("CORRELATION AND RELATIONSHIP ANALYSIS")
    print("=" * 60)
    print("Correlation analysis completed")
    print(f"Report saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
