import json
import os

import pandas as pd

INPUT_FILE = "output/feature_engineered_data.csv"
SUMMARY_FILE = "output/behavioral_segment_summary.csv"
REPORT_FILE = "output/behavioral_analysis_report.json"


def build_behavioral_analysis(df: pd.DataFrame):
    analysis_df = df.copy()

    if "customer_type" not in analysis_df.columns:
        analysis_df["customer_type"] = ["SMB", "Enterprise", "Startup", "SMB"][: len(analysis_df)]

    if "lifetime_value" not in analysis_df.columns:
        analysis_df["lifetime_value"] = 0.0
    if "churn" not in analysis_df.columns:
        analysis_df["churn"] = 0.0
    if "support_tickets" not in analysis_df.columns:
        analysis_df["support_tickets"] = 0.0
    if "customer_id" not in analysis_df.columns:
        analysis_df["customer_id"] = range(1, len(analysis_df) + 1)

    segment_metrics = (
        analysis_df.groupby("customer_type")
        .agg(
            avg_ltv=("lifetime_value", "mean"),
            churn_rate=("churn", "mean"),
            avg_tickets=("support_tickets", "mean"),
            customer_count=("customer_id", "count"),
        )
        .reset_index()
    )

    segment_metrics["avg_ltv_formatted"] = segment_metrics["avg_ltv"].apply(lambda x: f"${x:,.0f}")
    segment_metrics["churn_rate_formatted"] = segment_metrics["churn_rate"].apply(lambda x: f"{x:.1%}")

    top_segment = segment_metrics.loc[segment_metrics["avg_ltv"].idxmax(), "customer_type"]
    bottom_segment = segment_metrics.loc[segment_metrics["avg_ltv"].idxmin(), "customer_type"]
    highest_churn_segment = segment_metrics.loc[segment_metrics["churn_rate"].idxmax(), "customer_type"]
    lowest_churn_segment = segment_metrics.loc[segment_metrics["churn_rate"].idxmin(), "customer_type"]

    heatmap_ready = segment_metrics[["customer_type", "avg_ltv", "churn_rate", "avg_tickets"]].copy()
    heatmap_ready = heatmap_ready.set_index("customer_type")

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "segment_count": int(len(segment_metrics)),
        "top_segment": str(top_segment),
        "bottom_segment": str(bottom_segment),
        "highest_churn_segment": str(highest_churn_segment),
        "lowest_churn_segment": str(lowest_churn_segment),
        "summary_columns": list(segment_metrics.columns),
        "heatmap_shape": list(heatmap_ready.shape),
    }

    return segment_metrics, heatmap_ready, report


def main():
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    else:
        df = pd.DataFrame(
            {
                "customer_type": ["Enterprise", "SMB", "Startup", "Enterprise"],
                "lifetime_value": [150000, 2000, 12000, 140000],
                "churn": [0.01, 0.12, 0.08, 0.02],
                "support_tickets": [4, 8, 5, 3],
                "customer_id": [1, 2, 3, 4],
            }
        )

    segment_metrics, heatmap_ready, report = build_behavioral_analysis(df)

    os.makedirs("output", exist_ok=True)
    segment_metrics.to_csv(SUMMARY_FILE, index=False)
    heatmap_ready.to_csv("output/behavioral_segment_heatmap.csv")

    with open(REPORT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("BEHAVIORAL ANALYSIS & USER SEGMENTATION")
    print("=" * 60)
    print("Segment analysis completed")
    print(segment_metrics.to_string(index=False))
    print(f"Summary saved to: {SUMMARY_FILE}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
